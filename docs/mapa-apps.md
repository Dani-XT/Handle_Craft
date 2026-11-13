# Mapa de aplicaciones de Handle_Craft_2

## Dónde buscar cada funcionalidad

La carpeta superior (inventario, catálogo, compras o ventas) organiza las apps. Cada app es propietaria de sus modelos, formularios, vistas y templates. No hay una carpeta global views/articulos ni views/bodegas.

| App | Modelos / responsabilidad |
| --- | --- |
| sistema/categorias | Categoria: clasificación interna y visibilidad pública; única app propietaria |
| inventario/articulos | Articulo y PresentacionArticulo: identidad, SKU, unidad base y capacidades |
| inventario/unidades | UnidadMedida: código, magnitud y precisión |
| inventario/insumos | Insumo, Lote, UnidadSerializada |
| inventario/bodegas | Bodega, Ubicacion |
| inventario/movimientos | Existencia, ReservaInventario, OperacionInventario, DetalleOperacion, MovimientoStock |
| catalogo/productos | Producto, VarianteProducto, ImagenProducto, TipoProducto |
| catalogo/precios | ListaPrecio, PrecioArticulo: vigencias y tramos por cantidad |
| catalogo/cotizaciones | Cotizacion y DetalleCotizacion con instantáneas comerciales |
| catalogo/personalizaciones | Diseno, VersionDiseno, PersonalizacionDetalle, AprobacionDiseno |
| compras/proveedores | Proveedor, ContactoProveedor, ArticuloProveedor |
| compras/oc | OrdenCompra, DetalleOrdenCompra |
| compras/recepciones | RecepcionCompra, DetalleRecepcion: entrega parcial, aceptación y rechazo |
| ventas/clientes | Cliente, DireccionCliente, ContactoCliente |
| ventas/pedidos | Pedido, DetallePedido, HistorialEstadoPedido |
| ventas/despachos | Despacho, DetalleDespacho: consumo de reservas y salida de stock |
| ventas/pagos | Pago, AplicacionPago, Reembolso: registro de cobros y devoluciones |
| ventas/ventas | Venta, DetalleVenta: instantánea comercial de un pedido |
| core | BaseModel, bases abstractas de documentos, administración y utilidades compartidas |

Auth, landing y las aplicaciones de acceso/personal existentes conservan su ubicación. No se ha implementado producción: no se presupone que la empresa fabrique papel o bolsas.

## Ejemplo de navegación

```text
apps/sistema/categorias/
  models.py
  admin.py
  urls.py
  forms/categoria.py
  views/base.py
  views/list.py
  views/create.py
  views/update.py
  views/detail.py
  views/archive.py
  templates/categorias/list.html
  templates/categorias/form.html
  templates/categorias/detail.html
  templates/categorias/archive.html
```

Los archivos HTML antiguos de catálogo se conservan en templates/categorias/legacy. Las dos antiguas carpetas de apps de categorías salen del árbol activo y se guardan en el respaldo. Los alias de URL anteriores se resuelven dentro de la única app nueva. El listado interno está en /categorias/; ?visibilidad=publica filtra categorías publicables. La página administrativa sigue exigiendo permisos; para el sitio público utilizar Categoria.objects.publicas().

Las apps nuevas disponen de forms/registro.py, views/ y templates/<app>/ como lugares de trabajo. Sus modelos y servicios están implementados; no se han creado pantallas completas para esos flujos. Las vistas existentes ajenas a categorías permanecen como estaban. Los documentos y registros de stock se muestran en admin solo para lectura; las escrituras deben pasar por servicios.

## Compatibilidad de base de datos

Articulo se importa desde apps.inventario.articulos.models. Se conserva su etiqueta histórica apps_core para mantener tablas, claves foráneas, permisos y migraciones. Core ahora tiene etiqueta core y no contiene modelos concretos. Categoria se importa desde apps.sistema.categorias.models y conserva la etiqueta histórica inventario_categorias. Estas etiquetas no representan apps duplicadas.

No cambiar estas etiquetas manualmente. Las cadenas de relaciones apps_core.Articulo e inventario_categorias.Categoria son deliberadas. Las migraciones iniciales se trasladan junto con la entidad, sin recrear tablas ni reiniciar usuarios.

UnidadMedida deja de ser una lista fija del artículo: es una tabla. Articulo.unidad_medida es una relación; para asignar un código usar unidad_medida_id="un". Se crean un, kg, m y l en una migración de datos. Las unidades con artículos no pueden cambiar de precisión o magnitud. Una presentación es específica del artículo; cantidad_base describe cuántas unidades base contiene, sin conversión automática de documentos.

El precio_base de cada variante se copia a PrecioArticulo antes de eliminarlo. La fecha 2000-01-01 es un límite inicial técnico para esos precios migrados, no evidencia de su vigencia histórica. Ajustar su vigencia al administrar precios. precio_para selecciona el tramo aplicable; publicar_producto requiere un precio público vigente. No hay dos campos que compitan como fuente del precio.

## Servicios de escritura

| App | Servicios |
| --- | --- |
| movimientos | abrir_existencia, agregar_detalle, confirmar_operacion, reservar, liberar_reserva, cancelar_operacion |
| precios | guardar_precio |
| productos | publicar_producto |
| oc | confirmar_orden |
| recepciones | confirmar_recepcion |
| pedidos | confirmar_pedido, crear_desde_cotizacion |
| despachos | confirmar_despacho |
| pagos | confirmar_pago, aplicar_pago, reembolsar, pagado_pedido |
| personalizaciones | aprobar_diseno |
| ventas | registrar_venta |

Recepciones y despachos generan operaciones de stock y se confirman en una transacción. Repetir la confirmación del mismo documento no duplica stock. Una orden admite recepciones parciales y un pedido admite despachos parciales. Las cantidades aceptadas/despachadas acumuladas no pueden superar la línea original.

Para reservar para un pedido, pasar detalle_pedido_id a reservar; se valida que el artículo corresponda y que la suma comprometida no supere lo pedido. Se conserva la posibilidad de reservas manuales con referencia documental para otros compromisos y para los datos anteriores. Los despachos comerciales exigen reserva vinculada al detalle de pedido.

Los pagos son registros internos, no ejecutan transferencias bancarias. aplicar_pago y reembolsar reciben una clave UUID de idempotencia que el llamador debe reutilizar si reintenta la misma solicitud. Un abono no puede exceder ni el pago disponible ni el saldo del pedido. Un reembolso devuelve importes aplicados; no es una devolución física de mercancía ni repone stock.

crear_desde_cotizacion exige cotización aceptada y cliente. Copia cantidades, importes y especificaciones, y no confirma pedidos con personalizaciones pendientes de aprobación. El diseño se versiona sin sobrescribir archivos; su aprobación fija la versión, tamaño, técnica y posición. Esto almacena el diseño, no genera un mockup visual ni procesa archivos de impresión.

Venta es una instantánea completa del pedido (una por pedido en este alcance). No es emisión tributaria de documentos ni facturación electrónica. Cotizaciones y ventas conservan importes netos e impuesto explícito. No se supone automáticamente una tasa fiscal.

## Integridad y límites

Los documentos y sus detalles se congelan al confirmar. BaseModel valida en save y permite archivado lógico; las confirmaciones se ejecutan mediante servicios. Pasar actor para registrar responsables. Auditlog utiliza el usuario del middleware HTTP; en tareas fuera de HTTP usar también auditlog.context.set_actor.

No escribir stock, reservas o importes aplicados mediante update, bulk_update, SQL externo o escrituras directas que eviten los servicios: omiten validaciones, bloqueos y auditoría. Las reglas entre tablas se garantizan en esos servicios y las restricciones compatibles se refuerzan en la base.

Las pruebas funcionales se ejecutaron sobre SQLite, incluyendo migración desde datos antiguos. Antes de un despliegue multiusuario, validar concurrencia sobre PostgreSQL; SQLite no ofrece los bloqueos de fila requeridos. Permisos y pantallas de los nuevos flujos aún deben implementarse; los servicios no reemplazan la autorización de las futuras vistas/API.

Faltan procesos que requieren decisiones del negocio: cancelación comercial con compensación de reservas/pagos, devoluciones físicas, producción o impresión subcontratada, costos de inventario y facturación externa. No se presentaron esos procesos como implementados.

## Verificación

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test apps.inventario.movimientos.tests apps.ventas.pedidos.tests --settings=config.testing
```

config/testing.py usa una clave exclusiva de pruebas. El servidor debe seguir usando config.settings y la SECRET_KEY de su entorno.
