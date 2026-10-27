# Data Dictionary

## sales.csv — 3.500 registros
- `order_id` (text): identificador único del pedido.
- `customer_id` (text): identificador de cliente.
- `order_date` (date): fecha de compra.
- `category` (category): categoría de venta.
- `channel` (category): canal atribuido.
- `country` (category): país.
- `city` (text): ciudad.
- `quantity` (integer): unidades vendidas.
- `unit_price` (decimal): precio unitario.
- `discount_rate` (decimal): descuento, entre 0 y 0,20.
- `net_revenue` (decimal): ingresos netos.
- `cost` (decimal): costo estimado.
- `payment_method` (category): método de pago.
- `device` (category): dispositivo.

## products.csv — 500 productos
- `product_id` (text): identificador único de producto.
- `product_name` (text): nombre.
- `category` (category): categoría del catálogo.
- `brand` (category): marca ficticia.
- `active` (Yes/No): estado del producto.

## Limitación de relación

El CSV de ventas no contiene `product_id`; solo se puede comparar el mix de categorías entre ventas y catálogo. Los datos son sintéticos.
