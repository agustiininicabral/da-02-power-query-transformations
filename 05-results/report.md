# Reporte — Power Query Transformations

## Objetivo

Preparar datos de ventas y catálogo mediante pasos de Power Query M que puedan revisarse, actualizarse y reutilizarse. El flujo distingue entre preparación, validación y salida limpia.

## KPIs del dataset sintético

| KPI | Resultado |
|---|---:|
| Registros de ventas | 3.500 |
| Productos en catálogo | 500 |
| Clientes únicos | 877 |
| Unidades vendidas | 10.602 |
| Ingresos netos | 608.810,14 |
| Costo estimado | 364.075,27 |
| Margen bruto estimado | 244.734,87 |
| Tasa de margen estimada | 40,20% |
| Descuento medio por registro | 6,96% |

Los importes son unidades monetarias sintéticas.

## Flujo de transformación

1. Importar CSV con UTF-8 y promover encabezados.
2. Limpiar espacios en texto sin convertir nulos en la cadena literal `nan`.
3. Convertir fechas y números con `try ... otherwise null`, para que los errores puedan clasificarse.
4. Calcular `expected_net_revenue` y comprobar la coherencia del campo original.
5. Añadir `quality_status` con reglas de campos obligatorios, cantidades, descuentos e importes.
6. Separar filas válidas y excepciones en queries diferentes para que los errores sean visibles.

## Insights

1. Infantil registra el mayor ingreso (105.711,81; 17,36%), seguida por OTC (104.438,16; 17,16%) y Perfumería (103.784,47; 17,05%). Las tres representan aproximadamente 51,56% del ingreso.
2. Paid Social registra 95.217,15, apenas por encima de Email con 94.856,04. La diferencia es pequeña y no demuestra mayor rentabilidad.
3. El margen estimado global es 40,20%. No incluye gastos operativos ni de adquisición.
4. El dataset publicado pasa las reglas básicas: 3.500 ventas y 500 productos, sin celdas vacías, IDs duplicados, cantidades no positivas, descuentos fuera de rango ni errores en la fórmula de ingresos netos.

## Recomendaciones

- Cargar las excepciones en una tabla de revisión para resolverlas antes de publicar el modelo.
- Agregar `product_id` a ventas para poder hacer relaciones a nivel de producto.
- Mantener los pasos M versionados y validar recuentos antes/después de cada actualización.
- Usar medidas separadas para ingresos, costo y margen; no interpretar el margen bruto como beneficio neto.

## Limitaciones

Los datos son ficticios. Los resultados no representan una empresa real. La relación entre ventas y catálogo solo puede analizarse por categoría porque ventas no contiene `product_id`. El archivo M requiere editar las rutas locales antes de ejecutarse en Power Query.
