-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 01_carga_datos.sql
-- Descripcion: Procedimiento ETL de transformacion, casteo de tipos e insercion
-- ==============================================================================

USE superstore_db;

-- Insercion con transformacion y normalizacion de fechas
INSERT OVERWRITE TABLE superstore_analitica
SELECT
    CAST(row_id AS INT),
    TRIM(order_id),
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(order_date, 'M/d/yyyy'))),
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(ship_date, 'M/d/yyyy'))),
    TRIM(ship_mode),
    TRIM(customer_id),
    TRIM(customer_name),
    TRIM(segment),
    TRIM(country),
    TRIM(city),
    TRIM(state),
    TRIM(postal_code),
    TRIM(region),
    TRIM(product_id),
    TRIM(category),
    TRIM(sub_category),
    TRIM(product_name),
    CAST(sales AS DECIMAL(10,2)),
    CAST(quantity AS INT),
    CAST(discount AS DECIMAL(4,2)),
    CAST(profit AS DECIMAL(10,2))
FROM superstore_raw
WHERE row_id IS NOT NULL AND row_id != '';

-- Verificacion y evidencia de registros importados
SELECT
    COUNT(*) AS total_registros_importados,
    COUNT(DISTINCT order_id) AS total_ordenes_unicas,
    COUNT(DISTINCT customer_id) AS total_clientes_unicos,
    COUNT(DISTINCT product_id) AS total_productos_unicos,
    ROUND(SUM(sales), 2) AS ventas_totales_usd,
    ROUND(SUM(profit), 2) AS ganancia_total_usd
FROM superstore_analitica;
