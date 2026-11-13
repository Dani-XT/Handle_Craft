import uuid
from decimal import Decimal
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.apps import apps
from apps.inventario.articulos.models import Articulo
from apps.sistema.categorias.models import Categoria
from apps.inventario.bodegas.models import Bodega, Ubicacion
from apps.inventario.movimientos.models import OperacionInventario
from apps.inventario.movimientos.services import abrir_existencia, reservar
from apps.inventario.movimientos.selectors import stock_disponible
from apps.compras.proveedores.models import Proveedor
from apps.compras.oc.models import OrdenCompra, DetalleOrdenCompra
from apps.compras.oc.services import confirmar_orden
from apps.compras.recepciones.models import RecepcionCompra, DetalleRecepcion
from apps.compras.recepciones.services import confirmar_recepcion
from apps.ventas.clientes.models import Cliente
from apps.ventas.despachos.models import Despacho, DetalleDespacho
from apps.ventas.despachos.services import confirmar_despacho
from apps.ventas.pagos.models import Pago
from apps.ventas.pagos.services import confirmar_pago, aplicar_pago, reembolsar, pagado_pedido
from apps.catalogo.precios.models import ListaPrecio, PrecioArticulo
from apps.catalogo.precios.services import guardar_precio
from apps.catalogo.precios.selectors import precio_para
from apps.ventas.ventas.services import registrar_venta
from .models import Pedido, DetallePedido
from .services import confirmar_pedido, crear_desde_cotizacion


class FlujoComercialTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Bolsas", slug="bolsas", publicada=True)
        self.articulo = Articulo.objects.create(sku="B1", nombre="Bolsa", categoria=self.categoria, es_vendible=True)
        bodega = Bodega.objects.create(codigo="C", nombre="Central")
        ubicacion = Ubicacion.objects.create(bodega=bodega, codigo="A", nombre="A")
        self.saldo = abrir_existencia(articulo=self.articulo, ubicacion=ubicacion)
        proveedor = Proveedor.objects.create(nombre="Proveedor", identificacion="PR1", email="proveedor@example.com")
        self.orden = OrdenCompra.objects.create(proveedor=proveedor, direccion_entrega="Central")
        self.linea_compra = DetalleOrdenCompra.objects.create(orden=self.orden, articulo=self.articulo, sku="B1", descripcion="Bolsa", cantidad=10, precio_unitario=50)
        confirmar_orden(self.orden.pk)
        self.cliente = Cliente.objects.create(nombre="Cliente", email="cliente@example.com")
        self.pedido = Pedido.objects.create(cliente=self.cliente, nombre_cliente="Cliente", direccion_entrega="Destino")
        self.linea = DetallePedido.objects.create(pedido=self.pedido, articulo=self.articulo, sku="B1", descripcion="Bolsa", cantidad=5, precio_unitario=100)
        confirmar_pedido(self.pedido.pk)

    def recibir(self, cantidad):
        recepcion = RecepcionCompra.objects.create(orden=self.orden, documento_proveedor="GUIA")
        DetalleRecepcion.objects.create(recepcion=recepcion, detalle_orden=self.linea_compra, destino=self.saldo, cantidad_aceptada=cantidad)
        return confirmar_recepcion(recepcion.pk)

    def test_recepcion_parcial_idempotente(self):
        recepcion = self.recibir(4)
        confirmar_recepcion(recepcion.pk)
        self.recibir(6)
        self.assertEqual(stock_disponible(self.articulo.pk), 10)
        with self.assertRaises(ValidationError):
            self.recibir(1)
        self.assertEqual(stock_disponible(self.articulo.pk), 10)

    def test_recepcion_rechazo_no_ingresa_stock(self):
        recepcion = RecepcionCompra.objects.create(orden=self.orden, documento_proveedor="GUIA")
        DetalleRecepcion.objects.create(recepcion=recepcion, detalle_orden=self.linea_compra, cantidad_rechazada=2, motivo_rechazo="Dañadas")
        confirmar_recepcion(recepcion.pk)
        self.assertEqual(stock_disponible(self.articulo.pk), 0)
        recepcion.refresh_from_db()
        self.assertIsNone(recepcion.operacion_id)

    def test_pedido_reserva_despacho_parcial(self):
        self.recibir(10)
        reserva = reservar(existencia_id=self.saldo.pk, cantidad=5, referencia="Pedido", detalle_pedido_id=self.linea.pk)
        with self.assertRaises(ValidationError):
            reservar(existencia_id=self.saldo.pk, cantidad=1, referencia="Exceso", detalle_pedido_id=self.linea.pk)
        despacho = Despacho.objects.create(pedido=self.pedido, direccion_entrega="Destino")
        DetalleDespacho.objects.create(despacho=despacho, detalle_pedido=self.linea, reserva=reserva, cantidad=3)
        confirmar_despacho(despacho.pk)
        confirmar_despacho(despacho.pk)
        reserva.refresh_from_db()
        self.assertEqual(reserva.despachada, 3)
        self.assertEqual(stock_disponible(self.articulo.pk), 5)
        self.saldo.refresh_from_db()
        self.assertEqual(self.saldo.cantidad, 7)

    def test_despacho_fallido_revierte_operacion(self):
        self.recibir(10)
        reserva = reservar(existencia_id=self.saldo.pk, cantidad=2, referencia="Pedido", detalle_pedido_id=self.linea.pk)
        despacho = Despacho.objects.create(pedido=self.pedido, direccion_entrega="Destino")
        DetalleDespacho.objects.create(despacho=despacho, detalle_pedido=self.linea, reserva=reserva, cantidad=3)
        antes = OperacionInventario.objects.count()
        with self.assertRaises(ValidationError):
            confirmar_despacho(despacho.pk)
        self.assertEqual(OperacionInventario.objects.count(), antes)
        self.saldo.refresh_from_db()
        self.assertEqual(self.saldo.cantidad, 10)

    def test_documentos_confirmados_no_editables(self):
        self.linea.cantidad = 9
        with self.assertRaises(ValidationError):
            self.linea.save()
        self.pedido.refresh_from_db()
        self.pedido.direccion_entrega = "Otra"
        with self.assertRaises(ValidationError):
            self.pedido.save()

    def test_pago_abono_reembolso_idempotente(self):
        pago = Pago.objects.create(cliente=self.cliente, importe=600, metodo="transferencia")
        confirmar_pago(pago.pk)
        clave = uuid.uuid4()
        aplicacion = aplicar_pago(pago_id=pago.pk, pedido_id=self.pedido.pk, importe=400, clave=clave)
        self.assertEqual(aplicar_pago(pago_id=pago.pk, pedido_id=self.pedido.pk, importe=400, clave=clave).pk, aplicacion.pk)
        with self.assertRaises(ValidationError):
            aplicar_pago(pago_id=pago.pk, pedido_id=self.pedido.pk, importe=101, clave=uuid.uuid4())
        reembolso_clave = uuid.uuid4()
        reembolsar(aplicacion_id=aplicacion.pk, importe=100, motivo="Devolución", clave=reembolso_clave)
        reembolsar(aplicacion_id=aplicacion.pk, importe=100, motivo="Devolución", clave=reembolso_clave)
        self.assertEqual(pagado_pedido(self.pedido.pk), 300)
        with self.assertRaises(ValidationError):
            reembolsar(aplicacion_id=aplicacion.pk, importe=301, motivo="Exceso", clave=uuid.uuid4())

    def test_pago_de_otro_cliente_rechazado(self):
        otro = Cliente.objects.create(nombre="Otro", email="otro@example.com")
        pago = Pago.objects.create(cliente=otro, importe=100, metodo="efectivo")
        confirmar_pago(pago.pk)
        with self.assertRaises(ValidationError):
            aplicar_pago(pago_id=pago.pk, pedido_id=self.pedido.pk, importe=100, clave=uuid.uuid4())

    def test_precios_volumen_y_solapamiento(self):
        lista = ListaPrecio.objects.create(codigo="P", nombre="Pública", publica=True)
        hoy = timezone.localdate()
        base = guardar_precio(PrecioArticulo(lista=lista, articulo=self.articulo, cantidad_desde=1, precio_unitario=100, vigente_desde=hoy))
        volumen = guardar_precio(PrecioArticulo(lista=lista, articulo=self.articulo, cantidad_desde=100, precio_unitario=80, vigente_desde=hoy))
        self.assertEqual(precio_para(self.articulo.pk, 99).pk, base.pk)
        self.assertEqual(precio_para(self.articulo.pk, 100).pk, volumen.pk)
        with self.assertRaises(ValidationError):
            guardar_precio(PrecioArticulo(lista=lista, articulo=self.articulo, cantidad_desde=1, precio_unitario=90, vigente_desde=hoy+timedelta(days=1)))

    def test_venta_conserva_importes(self):
        venta = registrar_venta(self.pedido.pk)
        self.assertEqual(venta.total, 500)
        self.assertEqual(registrar_venta(self.pedido.pk).pk, venta.pk)
        self.assertEqual(venta.detalles.get().sku, "B1")

    def test_una_app_categoria_y_rutas(self):
        self.assertEqual(apps.get_app_config("inventario_categorias").name, "apps.sistema.categorias")
        self.assertFalse(apps.is_installed("apps.catalogo.categorias"))
        self.assertFalse(apps.is_installed("apps.inventario.categorias"))
        for name in ("categorias-list", "categorias-catalogo-list", "categorias-inventario-list"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)

    def test_cotizacion_aceptada_se_convierte_una_vez(self):
        from apps.catalogo.cotizaciones.models import Cotizacion, DetalleCotizacion
        from apps.catalogo.productos.models import Producto, VarianteProducto
        usuario = get_user_model().objects.create(username="cliente", email="cliente@example.com")
        cotizacion = Cotizacion.objects.create(cliente=self.cliente, solicitante=usuario, nombre_cliente="Cliente", email_cliente="cliente@example.com", direccion_cliente="Destino", fecha_vencimiento=timezone.localdate()+timedelta(days=7), estado="aceptada")
        producto = Producto.objects.create(nombre="Bolsa", slug="bolsa", categoria=self.categoria)
        variante = VarianteProducto.objects.create(producto=producto, articulo=self.articulo, color="Kraft", ancho_mm=100, alto_mm=200, fuelle_mm=0, gramaje_g_m2=90)
        DetalleCotizacion.objects.create(cotizacion=cotizacion, variante=variante, sku="B1", descripcion="Bolsa", cantidad=3, precio_unitario=100, tasa_impuesto=0)
        pedido = crear_desde_cotizacion(cotizacion.pk)
        self.assertEqual(pedido.total, 300)
        self.assertEqual(crear_desde_cotizacion(cotizacion.pk).pk, pedido.pk)

    def test_personalizacion_version_aprobada_inmutable(self):
        from apps.catalogo.personalizaciones.models import Diseno, VersionDiseno, PersonalizacionDetalle
        from apps.catalogo.personalizaciones.services import aprobar_diseno
        from apps.catalogo.cotizaciones.models import Cotizacion, DetalleCotizacion
        from apps.catalogo.productos.models import Producto, VarianteProducto
        usuario = get_user_model().objects.create(username="propietario", email="propietario@example.com")
        self.cliente.usuario = usuario
        self.cliente.save()
        cotizacion = Cotizacion.objects.create(cliente=self.cliente, solicitante=usuario, nombre_cliente="Cliente", email_cliente="cliente@example.com", direccion_cliente="Destino", fecha_vencimiento=timezone.localdate())
        producto = Producto.objects.create(nombre="Bolsa", slug="bolsa", categoria=self.categoria)
        variante = VarianteProducto.objects.create(producto=producto, articulo=self.articulo, color="Kraft", ancho_mm=100, alto_mm=200, fuelle_mm=0, gramaje_g_m2=90)
        linea = DetalleCotizacion.objects.create(cotizacion=cotizacion, variante=variante, sku="B1", descripcion="Bolsa", cantidad=1, precio_unitario=100, tasa_impuesto=0)
        diseno = Diseno.objects.create(cliente=self.cliente, nombre="Logo")
        version = VersionDiseno.objects.create(diseno=diseno, numero=1, archivo="fixture/logo.png")
        personalizacion = PersonalizacionDetalle.objects.create(detalle_cotizacion=linea, version=version, posicion="Frente", ancho_mm=50, alto_mm=50, colores=["negro"], tecnica="Impresión")
        cotizacion.estado = "aceptada"
        cotizacion.save()
        with self.assertRaises(ValidationError):
            crear_desde_cotizacion(cotizacion.pk)
        aprobacion = aprobar_diseno(personalizacion.pk, usuario)
        self.assertEqual(crear_desde_cotizacion(cotizacion.pk).estado, "confirmada")
        self.assertEqual(aprobar_diseno(personalizacion.pk, usuario).pk, aprobacion.pk)
        personalizacion.ancho_mm = 60
        with self.assertRaises(ValidationError):
            personalizacion.save()
        version.archivo = "fixture/otro.png"
        with self.assertRaises(ValidationError):
            version.save()

    def test_vistas_categoria_autenticadas(self):
        usuario = get_user_model().objects.create(username="adminprueba", email="admin@example.com", is_staff=True, is_superuser=True)
        self.client.force_login(usuario)
        for name, kwargs in [("categorias-list", {}), ("categorias-create", {}), ("categorias-update", {"pk": self.categoria.pk}), ("categorias-detail", {"pk": self.categoria.pk})]:
            self.assertEqual(self.client.get(reverse(name, kwargs=kwargs)).status_code, 200)

    def test_landing_permanece_accesible(self):
        self.assertEqual(self.client.get(reverse("landing")).status_code, 200)
