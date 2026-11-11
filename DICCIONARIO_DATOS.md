# Diccionario de Datos — Superstore Sales Dataset
**Materia:** Tecnologías Emergentes I  
**Evaluación:** Examen Práctico Individual - 2do Momento  
**Universidad:** Universidad Privada del Valle (Univalle Bolivia)  
**Autor:** Ronald Joel Saavedra Vargas  
**Dataset:** Sample - Superstore (`superstore.csv`)  
**Total Registros:** 9,994 filas | **Total Columnas:** 21 atributos  

---

## 1. Especificación Técnica de Atributos

| Nº | Campo Original | Nombre en HiveQL | Tipo de Dato Hive | Descripción Funcional y de Negocio | Restricciones de Integridad / Valores Válidos | Valor de Ejemplo |
|:--:|:---|:---|:---|:---|:---|:---|
| **1** | `Row ID` | `row_id` | `INT` | Identificador único secuencial de cada registro de venta. | `PRIMARY KEY`, `NOT NULL`, rango `[1, 9994]`, sin duplicados. | `1` |
| **2** | `Order ID` | `order_id` | `STRING` | Código alfanumérico identificador del pedido. Puede contener múltiples filas de productos. | `NOT NULL`, formato `[País]-[Año]-[Número]` (ej. `CA-2016-152156`). | `CA-2016-152156` |
| **3** | `Order Date` | `order_date` | `DATE` | Fecha de emisión de la orden de compra por el cliente. | `NOT NULL`, normalizado a ISO `yyyy-MM-dd`. Rango `2014-01-03` a `2017-12-30`. | `2016-11-08` |
| **4** | `Ship Date` | `ship_date` | `DATE` | Fecha de despacho o envío de la mercancía. | `NOT NULL`, restricción cronológica: `ship_date >= order_date`. | `2016-11-11` |
| **5** | `Ship Mode` | `ship_mode` | `STRING` | Modalidad o nivel de servicio logístico seleccionado. | Valores discretos: `Standard Class`, `Second Class`, `First Class`, `Same Day`. | `Second Class` |
| **6** | `Customer ID` | `customer_id` | `STRING` | Identificador alfanumérico único del cliente. | `NOT NULL`, 793 clientes únicos en la base de datos. | `CG-12520` |
| **7** | `Customer Name` | `customer_name` | `STRING` | Nombre y apellido del comprador registrado. | `NOT NULL`, longitud variable. | `Claire Gute` |
| **8** | `Segment` | `segment` | `STRING` | Clasificación del mercado objetivo del cliente. | Valores permitidos: `Consumer`, `Corporate`, `Home Office`. | `Consumer` |
| **9** | `Country` | `country` | `STRING` | País de la transacción y entrega comercial. | Valor constante en este dataset: `United States`. | `United States` |
| **10** | `City` | `city` | `STRING` | Ciudad geográfica de entrega del pedido. | `NOT NULL`, 531 ciudades registradas. | `Henderson` |
| **11** | `State` | `state` | `STRING` | Estado federado o provincia estadounidense. | `NOT NULL`, 49 estados representados. | `Kentucky` |
| **12** | `Postal Code` | `postal_code` | `STRING` | Código postal asignado al destino de envío. | Se almacena como `STRING` para preservar códigos de 5 dígitos con ceros iniciales. | `42420` |
| **13** | `Region` | `region` | `STRING` | Macro-región comercial asignada a la sucursal. | Valores discretos: `South`, `West`, `Central`, `East`. | `South` |
| **14** | `Product ID` | `product_id` | `STRING` | Código alfanumérico único del producto. | `NOT NULL`, 1,862 productos únicos en inventario. | `FUR-BO-10001798` |
| **15** | `Category` | `category` | `STRING` | Categoría principal de inventario. | Valores discretos: `Furniture`, `Office Supplies`, `Technology`. | `Furniture` |
| **16** | `Sub-Category` | `sub_category` | `STRING` | Subdivisión especializada del producto. | 17 subcategorías (ej. `Bookcases`, `Chairs`, `Labels`, `Tables`, `Binders`). | `Bookcases` |
| **17** | `Product Name` | `product_name` | `STRING` | Denominación y descripción comercial del artículo. | `NOT NULL`, descripción de texto libre. | `Bush Somerset Collection Bookcase` |
| **18** | `Sales` | `sales` | `DECIMAL(10,2)` | Monto bruto facturado de la venta en dólares (USD). | `NOT NULL`, regla estricta: `sales > 0.00`. Rango `[0.44, 22638.48]`. | `261.96` |
| **19** | `Quantity` | `quantity` | `INT` | Número de unidades físicas despachadas. | `NOT NULL`, regla estricta: `quantity >= 1`. Rango `[1, 14]`. | `2` |
| **20** | `Discount` | `discount` | `DECIMAL(4,2)` | Tasa de descuento aplicada a la transacción. | Rango porcentual: `[0.00, 1.00]`. Máximo observado en dataset: `0.80` (80%). | `0.00` |
| **21** | `Profit` | `profit` | `DECIMAL(10,2)` | Ganancia neta o rentabilidad en dólares (USD). | Puede asumir valores positivos (beneficio), cero o negativos (pérdida). | `41.91` |

---

## 2. Métricas y Estadísticas Generales del Dataset

- **Período de Análisis Temporal:** Del `2014-01-03` al `2017-12-30` (4 años completos).
- **Facturación Bruta Acumulada:** \$2,297,200.86 USD.
- **Utilidad Neta Acumulada:** \$286,397.02 USD.
- **Margen de Rentabilidad Promedio Ponderado:** 12.47%.
- **Transacciones Rentables (`Profit > 0`):** 8,058 filas (80.63%).
- **Transacciones en Punto de Equilibrio (`Profit == 0`):** 65 filas (0.65%).
- **Transacciones con Pérdidas Operativas (`Profit < 0`):** 1,871 filas (18.72%).
