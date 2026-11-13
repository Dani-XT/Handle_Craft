from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from auditlog.models import LogEntry
from apps.inventario.articulos.models import Articulo
from apps.sistema.categorias.models import Categoria
from apps.sistema.categorias.models import Categoria as CategoriaCatalogo
from apps.inventario.bodegas.models import Bodega, Ubicacion
from apps.inventario.insumos.models import Lote, UnidadSerializada, Insumo
from apps.catalogo.productos.models import Producto, VarianteProducto
from apps.catalogo.productos.services import publicar_producto
from apps.catalogo.productos.selectors import productos_publicos
from .models import Existencia, OperacionInventario, MovimientoStock
from .services import abrir_existencia, agregar_detalle, confirmar_operacion, reservar, liberar_reserva
from .selectors import stock_disponible


class InventarioTests(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nombre="Bolsas", slug="bolsas", publicada=True)
        self.art = Articulo.objects.create(sku="B01", nombre="Bolsa", categoria=self.cat, es_vendible=True)
        self.bodega = Bodega.objects.create(codigo="C", nombre="Central")
        self.ubicacion = Ubicacion.objects.create(bodega=self.bodega, codigo="A", nombre="A")
        self.e = abrir_existencia(articulo=self.art, ubicacion=self.ubicacion)

    def operacion(self, tipo, cantidad, origen=None, destino=None, reserva=None):
        op = OperacionInventario.objects.create(tipo=tipo, motivo="Prueba")
        agregar_detalle(operacion_id=op.pk, cantidad=cantidad, origen=origen, destino=destino, reserva=reserva)
        return op

    def entrada(self, cantidad=10):
        return confirmar_operacion(self.operacion("entrada", cantidad, destino=self.e).pk)

    def test_categoria_compartida_y_visibilidad(self):
        self.assertIs(Categoria, CategoriaCatalogo)
        Categoria.objects.create(nombre="Herramientas", slug="herramientas")
        self.assertEqual(Categoria.objects.internas().count(), 2)
        self.assertEqual(Categoria.objects.publicas().count(), 1)

    def test_ciclo_categorias(self):
        hija = Categoria.objects.create(nombre="Hija", slug="hija", parent=self.cat)
        self.cat.parent = hija
        with self.assertRaises(ValidationError):
            self.cat.full_clean()

    def test_entrada_idempotente(self):
        op = self.entrada()
        confirmar_operacion(op.pk)
        self.assertEqual(stock_disponible(self.art.pk), 10)
        self.assertEqual(MovimientoStock.objects.count(), 1)

    def test_salida_insuficiente_atomica(self):
        self.entrada(2)
        op = self.operacion("salida", 1, origen=self.e)
        agregar_detalle(operacion_id=op.pk, cantidad=2, origen=self.e)
        with self.assertRaises(ValidationError):
            confirmar_operacion(op.pk)
        self.assertEqual(stock_disponible(self.art.pk), 2)
        self.assertFalse(op.detalles.filter(movimientos__isnull=False).exists())

    def test_transferencia(self):
        self.entrada()
        ubicacion = Ubicacion.objects.create(bodega=self.bodega, codigo="B", nombre="B")
        destino = abrir_existencia(articulo=self.art, ubicacion=ubicacion)
        confirmar_operacion(self.operacion("transferencia", 4, self.e, destino).pk)
        self.e.refresh_from_db()
        destino.refresh_from_db()
        self.assertEqual((self.e.cantidad, destino.cantidad), (6, 4))
        self.assertEqual(stock_disponible(self.art.pk), 10)

    def test_unidades_sin_fracciones(self):
        with self.assertRaises(ValidationError):
            self.entrada(Decimal("0.5"))

    def test_stock_no_editable(self):
        self.e.cantidad = 10
        with self.assertRaises(ValidationError):
            self.e.save()

    def test_reserva_despacho_liberacion(self):
        self.entrada()
        reserva = reservar(existencia_id=self.e.pk, cantidad=5, referencia="P-1")
        self.assertEqual(stock_disponible(self.art.pk), 5)
        confirmar_operacion(self.operacion("salida", 3, origen=self.e, reserva=reserva).pk)
        self.assertEqual(stock_disponible(self.art.pk), 5)
        liberar_reserva(reserva.pk, 2)
        self.assertEqual(stock_disponible(self.art.pk), 7)

    def test_reserva_no_sobrevende(self):
        self.entrada(2)
        reservar(existencia_id=self.e.pk, cantidad=2, referencia="P-1")
        with self.assertRaises(ValidationError):
            reservar(existencia_id=self.e.pk, cantidad=1, referencia="P-2")
        with self.assertRaises(ValidationError):
            confirmar_operacion(self.operacion("salida", 1, origen=self.e).pk)

    def test_ubicacion_bloqueada_no_disponible(self):
        self.entrada()
        self.ubicacion.condicion = "bloqueada"
        self.ubicacion.save()
        self.assertEqual(stock_disponible(self.art.pk), 0)
        with self.assertRaises(ValidationError):
            confirmar_operacion(self.operacion("salida", 1, origen=self.e).pk)

    def test_serie_y_transferencia(self):
        art = Articulo.objects.create(sku="E1", nombre="Equipo", categoria=self.cat, seguimiento="serie")
        unidad = UnidadSerializada.objects.create(articulo=art, serial="S1", codigo_interno="E-1")
        origen = abrir_existencia(articulo=art, ubicacion=self.ubicacion, unidad_serializada=unidad)
        destino = abrir_existencia(articulo=art, ubicacion=Ubicacion.objects.create(bodega=self.bodega, codigo="B", nombre="B"), unidad_serializada=unidad)
        confirmar_operacion(self.operacion("entrada", 1, destino=origen).pk)
        with self.assertRaises((ValidationError, IntegrityError)):
            confirmar_operacion(self.operacion("entrada", 1, destino=destino).pk)
        confirmar_operacion(self.operacion("transferencia", 1, origen, destino).pk)
        self.assertEqual(stock_disponible(art.pk), 1)

    def test_lote_obligatorio_y_vencido(self):
        art = Articulo.objects.create(sku="L1", nombre="Tinta", categoria=self.cat, seguimiento="lote", unidad_medida_id="l")
        with self.assertRaises(ValidationError):
            abrir_existencia(articulo=art, ubicacion=self.ubicacion)
        lote = Lote.objects.create(articulo=art, codigo="L1", fecha_vencimiento=timezone.localdate()-timedelta(days=1))
        saldo = abrir_existencia(articulo=art, ubicacion=self.ubicacion, lote=lote)
        confirmar_operacion(self.operacion("entrada", Decimal("1.250"), destino=saldo).pk)
        self.assertEqual(stock_disponible(art.pk), 0)

    def test_cambio_unidad_prohibido_con_existencias(self):
        self.art.unidad_medida_id = "kg"
        with self.assertRaises(ValidationError):
            self.art.full_clean()

    def test_archivo_con_stock_prohibido(self):
        self.entrada()
        for obj in (self.art, self.bodega, self.ubicacion):
            with self.assertRaises(ValidationError):
                obj.archive()

    def test_borrado_logico_y_auditoria(self):
        insumo = Insumo.objects.create(articulo=self.art)
        insumo.delete()
        insumo.refresh_from_db()
        self.assertTrue(insumo.is_archived)
        self.assertTrue(LogEntry.objects.get_for_object(insumo).exists())

    def test_operacion_confirmada_inmutable(self):
        op = self.entrada()
        op.motivo = "Cambio"
        with self.assertRaises(ValidationError):
            op.save()
        detalle = op.detalles.get()
        detalle.cantidad = 2
        with self.assertRaises(ValidationError):
            detalle.save()

    def test_producto_comparte_stock(self):
        producto = Producto.objects.create(nombre="Bolsa", slug="bolsa", categoria=self.cat)
        with self.assertRaises(ValidationError):
            publicar_producto(producto.pk)
        variante = VarianteProducto.objects.create(producto=producto, articulo=self.art, color="Kraft", ancho_mm=100, alto_mm=200, fuelle_mm=0, gramaje_g_m2=90)
        variante.full_clean()
        from apps.catalogo.precios.models import ListaPrecio, PrecioArticulo
        lista = ListaPrecio.objects.create(codigo="PUBLICA", nombre="Pública", publica=True)
        PrecioArticulo.objects.create(lista=lista, articulo=self.art, cantidad_desde=1, precio_unitario=100, vigente_desde=timezone.localdate())
        publicar_producto(producto.pk)
        self.entrada(5)
        self.assertEqual(variante.articulo.stock_disponible, 5)
        self.assertEqual(list(productos_publicos()), [producto])
        self.cat.publicada = False
        self.cat.save()
        self.assertFalse(productos_publicos().exists())
