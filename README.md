# Power Query Transformations

Proyecto de portfolio de Data Analytics centrado en limpieza reproducible con Power Query M. Incluye queries para ventas y catálogo, separación de filas válidas/excepciones y documentación de las reglas.

## Dataset

- `02-data/raw/sales.csv`: 3.500 registros de ventas sintéticas.
- `02-data/raw/products.csv`: catálogo de 500 productos.
- `02-data/raw/DATA_DICTIONARY.md`: columnas y relaciones conocidas.

## Ejecutar en Power Query

1. Abrí Excel o Power BI Desktop y creá una consulta en blanco.
2. Abrí el Editor avanzado y pegá el contenido de cada archivo de `03-work/power-query/`.
3. En `SalesPrepared.m` y `ProductsPrepared.m`, reemplazá las rutas de ejemplo por las rutas absolutas a los CSV del repositorio.
4. Nombrá las consultas exactamente como sus archivos, sin la extensión `.m`: `SalesPrepared`, `SalesValid`, `SalesExceptions`, `ProductsPrepared`, `ProductsValid` y `ProductsExceptions`.
5. Cargá `SalesValid` y `ProductsValid` al modelo. Revisá `SalesExceptions` y `ProductsExceptions` antes de excluir registros.
6. Actualizá las consultas y comprobá los recuentos de filas.

## Transformaciones incluidas

- Promoción de encabezados.
- Limpieza de espacios en columnas de texto y normalización de Yes/No.
- Conversión tolerante de fechas y valores numéricos; los errores se convierten en null para poder clasificarlos.
- Recalculo de ingresos netos esperados y comparación con `net_revenue`.
- Clasificación de filas por campos requeridos, cantidad, precios, descuentos y coherencia de ingresos.
- Separación de filas válidas y excepciones sin modificar los CSV originales.

El dataset actual debe producir 3.500 ventas válidas y 500 productos válidos, sin filas de excepción. Si el origen cambia, las consultas de excepciones permiten inspeccionar los problemas en lugar de ocultarlos. GitHub Actions valida los CSV y las referencias estáticas entre queries, pero no ejecuta Power Query M; la actualización real debe verificarse en Excel o Power BI Desktop.

## Reglas principales

- `order_id` y `customer_id` no pueden estar vacíos.
- Fecha válida y cantidad mayor que cero.
- Precio, costo e ingreso neto no negativos.
- Descuento entre 0 y 20%.
- `net_revenue` debe coincidir con cantidad × precio unitario × (1 − descuento), con tolerancia de 0,01.
- El catálogo requiere ID, nombre, categoría, marca y estado Yes/No.

## Resultados

Ver [05-results/report.md](05-results/report.md) para KPIs e insights del dataset sintético.

## Limitaciones

Los datos son ficticios. El archivo de ventas no contiene `product_id`, por lo que no permite relacionar cada pedido con un producto individual. El margen calculado es una aproximación y no equivale a beneficio neto.

## Estructura

- `01-requirements/`: hipótesis y alcance.
- `02-data/raw/`: CSV originales y diccionario.
- `03-work/power-query/`: consultas M reutilizables.
- `03-work/sql/`: consultas SQL complementarias.
- `05-results/report.md`: métricas y limitaciones.

## Licencia

MIT.
