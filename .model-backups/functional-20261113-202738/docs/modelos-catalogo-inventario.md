# Modelos de Handle_Craft_2

Se conserva la arquitectura original: apps pequeñas por entidad y un models.py en cada app. No se modifican Auth, landing ni los HTML.

## Ubicación y responsabilidades

| Archivo | Entidades |
| --- | --- |
| apps/core/models.py | BaseModel, Articulo |
| apps/inventario/categorias/models.py | Categoria compartida |
| apps/inventario/insumos/models.py | Insumo, Lote, UnidadSerializada |
| apps/inventario/bodegas/models.py | Bodega, Ubicacion |
| apps/inventario/movimientos/models.py | Existencia, ReservaInventario, OperacionInventario, DetalleOperacion, MovimientoStock |
| apps/catalogo/productos/models.py | TipoProducto, Producto, VarianteProducto, ImagenProducto |

apps/catalogo/categorias/models.py reexporta Categoria por compatibilidad. No declara otro modelo ni crea otra tabla. Sus vistas administrativas siguen separadas de las vistas de inventario. No se creó una app adicional de categorías en sistema.

## Categorías

Categoria.objects.internas() muestra todas las categorías no archivadas. Categoria.objects.publicas() muestra las mismas filtradas por publicada=True. Nombre, descripción, imagen, slug, orden y parent sirven para ambas interfaces. La visibilidad de cada categoría es independiente de su padre; no se hereda automáticamente.

La categoría no impone que sus elementos sean consumibles o serializados. Eso depende del artículo. El producto puede tener una categoría comercial distinta de la categoría interna del artículo, ambas de la misma tabla. Publicar una categoría no publica automáticamente sus productos.

## Artículos, insumos y catálogo

Articulo mantiene SKU único, categoría interna, unidad de medida, seguimiento y capacidades (vendible, comprable, consumible en producción). Insumo es una ficha adicional uno a uno para marca, modelo e instrucciones de almacenamiento; no tiene otro SKU ni stock separado. Una variante comercial utiliza ese mismo Articulo. Por eso un insumo también puede venderse sin duplicar inventario.

Seguimiento admite cantidad, lote o serie. Un consumible puede necesitar un lote o incluso una serie. UnidadSerializada tiene serial único por artículo y código interno global único. Su lote opcional identifica su procedencia. Existencia serializada referencia la unidad y no repite el lote. Las unidades no admiten fracciones; kg, m y l permiten tres decimales.

Cada producto tiene variantes de bolsa con dimensiones útiles en mm, gramaje, color, asa, carga máxima verificada opcional y precio neto base en CLP. Fuelle cero representa una bolsa sin fuelle. El mínimo debe ser múltiplo de venta. TipoProducto se conserva como clasificación comercial adicional. Las cotizaciones mantienen sus importes y especificaciones históricos; cambiar el precio base no debe recalcular cotizaciones emitidas.

## Stock y servicios

Existencia guarda cantidad física por artículo, ubicación y trazabilidad. stock_disponible(articulo_id, bodega_id=None) descuenta reservas pendientes y excluye almacenes inactivos, cuarentena, bloqueos, trazabilidad archivada y lotes vencidos. Disponible también se consulta desde Articulo o VarianteProducto; no hay un segundo contador en productos.

No se debe editar cantidad ni usar update/bulk_update para cambiar inventario. Usar los servicios de apps/inventario/movimientos/services.py:

1. abrir_existencia: crea una combinación válida con saldo cero.
2. Crear OperacionInventario en borrador con tipo y motivo.
3. agregar_detalle: relaciona origen/destino y cantidad.
4. confirmar_operacion: valida, bloquea artículos y saldos en orden, registra movimientos y confirma todo en una transacción. Repetir la confirmación del mismo ID no duplica stock.
5. reservar, liberar_reserva: gestionan compromisos. Para despachar una reserva, asociarla al detalle de salida.
6. cancelar_operacion: solo para borradores. Lo confirmado se corrige mediante una operación compensatoria (campo corrige).

Ejemplo de entrada:

```python
from apps.inventario.movimientos.models import OperacionInventario
from apps.inventario.movimientos.services import abrir_existencia, agregar_detalle, confirmar_operacion

saldo = abrir_existencia(articulo=articulo, ubicacion=ubicacion, actor=request.user)
operacion = OperacionInventario.objects.create(tipo="entrada", motivo="Recepción de compra", created_by=request.user)
agregar_detalle(operacion_id=operacion.pk, destino=saldo, cantidad=100, actor=request.user)
confirmar_operacion(operacion.pk, request.user)
```

La reserva usa una referencia documental de texto: todavía no es una integración completa con pedidos. Cuando se implemente ese flujo debe añadirse la relación al detalle de pedido y validar lo reservado contra la cantidad pedida. Las reservas no caducan solas: deben liberarse explícitamente.

## Validación, archivado y auditoría

BaseModel conserva created_at/updated_at y responsables. save ejecuta full_clean para los modelos que lo heredan. archive(actor) conserva los registros; delete individual archiva y el borrado masivo está deshabilitado. No archivar artículos/bodegas/ubicaciones con stock. Los registros de operaciones confirmadas y movimientos se conservan; el admin de inventario transaccional es de solo lectura.

Auditlog registra cambios de los modelos BaseModel y obtiene el usuario HTTP del middleware existente. Las tareas fuera de HTTP deben usar auditlog.context.set_actor además de pasar actor al servicio para obtener ambas trazas. No usar bulk_create/bulk_update/update, SQL directo o alteraciones manuales para saltarse validaciones y señales. El historial no sustituye el libro de movimientos de stock.

## Alcance y comprobaciones

Se regeneran únicamente las migraciones de estos dominios y cotizaciones por sus dependencias, para una base nueva. La base anterior y archivos reemplazados se respaldan antes de aplicar. Auth y landing conservan sus migraciones. Crear nuevamente el administrador tras el reinicio.

Hay pruebas de movimientos, reservas, series, lotes, visibilidad, archivado, auditoría y publicación. Para producción con varios usuarios hay que ejecutar pruebas de concurrencia sobre PostgreSQL: SQLite no implementa los bloqueos de fila. Las validaciones entre tablas no deben considerarse protegidas frente a SQL externo.

No se rediseñan plantillas. Se corrige el formulario existente de categoría y se registran los maestros en admin. Las pantallas transaccionales todavía deben invocar los servicios; los HTML actuales pueden no mostrar todos los campos nuevos. Tampoco se implementan aquí facturación, compras completas, fabricación, conciliación de costos ni un nuevo flujo de autenticación.

Comandos de validación: manage.py check; manage.py makemigrations --check --dry-run; manage.py test apps.inventario.movimientos.tests.
