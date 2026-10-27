# Guía de Power Query M

## Orden de configuración

1. Crear `SalesPrepared` desde `SalesPrepared.m`.
2. Crear `SalesValid` y `SalesExceptions`, que referencian `SalesPrepared`.
3. Crear `ProductsPrepared` desde `ProductsPrepared.m`.
4. Crear `ProductsValid` y `ProductsExceptions`, que referencian `ProductsPrepared`.

Los nombres de consulta son importantes porque las queries derivadas usan esas referencias.

## Validación manual

- Confirmar que SalesPrepared tenga 3.500 filas.
- Confirmar que ProductsPrepared tenga 500 filas.
- Revisar que `revenue_check` sea TRUE en las filas válidas.
- Comprobar que `quality_status` sea `OK` para el dataset actual.
- Confirmar que SalesExceptions y ProductsExceptions tengan cero filas.
- Verificar que los CSV originales no se hayan sobrescrito.

## Por qué se conservan excepciones

La query preparada añade un estado de calidad en vez de borrar silenciosamente filas. Las queries `Valid` y `Exceptions` permiten cargar solo los registros aceptados sin perder la evidencia necesaria para investigar un problema.
