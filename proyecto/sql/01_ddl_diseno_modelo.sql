-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 01_ddl_diseno_modelo.sql
-- Descripcion: Creacion de la base de datos analitica y tablas Raw / Analitica
-- ==============================================================================

-- 1. Creacion de la base de datos del proyecto
CREATE DATABASE IF NOT EXISTS superstore_db
COMMENT 'Base de datos analitica Superstore Sales - Examen 2do Momento'
LOCATION '/user/hive/warehouse/superstore_db.db';

USE superstore_db;

-- 2. Creacion de tabla externa Staging (Capa Raw) para ingesta de CSV original
DROP TABLE IF EXISTS superstore_raw;

CREATE EXTERNAL TABLE IF NOT EXISTS superstore_raw (
    row_id STRING COMMENT 'ID secuencial de fila',
    order_id STRING COMMENT 'Codigo identificador de orden',
    order_date STRING COMMENT 'Fecha de pedido en formato M/d/yyyy',
    ship_date STRING COMMENT 'Fecha de envio en formato M/d/yyyy',
    ship_mode STRING COMMENT 'Modalidad logistica de envio',
    customer_id STRING COMMENT 'Codigo unico del cliente',
    customer_name STRING COMMENT 'Nombre del cliente',
    segment STRING COMMENT 'Segmento de cliente',
    country STRING COMMENT 'Pais de transaccion',
    city STRING COMMENT 'Ciudad de despacho',
    state STRING COMMENT 'Estado federado',
    postal_code STRING COMMENT 'Codigo postal',
    region STRING COMMENT 'Region comercial',
    product_id STRING COMMENT 'Codigo unico del producto',
    category STRING COMMENT 'Categoria general del producto',
    sub_category STRING COMMENT 'Subcategoria de producto',
    product_name STRING COMMENT 'Nombre comercial del producto',
    sales STRING COMMENT 'Ventas brutas en formato texto',
    quantity STRING COMMENT 'Cantidad de articulos',
    discount STRING COMMENT 'Tasa de descuento comercial',
    profit STRING COMMENT 'Beneficio o ganancia neta'
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/data/superstore/raw'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 3. Creacion de tabla analitica optimizada (Capa Analitica) en formato columnar ORC
DROP TABLE IF EXISTS superstore_analitica;

CREATE TABLE IF NOT EXISTS superstore_analitica (
    row_id INT COMMENT 'Clave primaria secuencial de linea de venta',
    order_id STRING COMMENT 'Identificador unico del pedido',
    order_date DATE COMMENT 'Fecha normalizada del pedido (yyyy-MM-dd)',
    ship_date DATE COMMENT 'Fecha normalizada de envio (yyyy-MM-dd)',
    ship_mode STRING COMMENT 'Clase de envio',
    customer_id STRING COMMENT 'Identificador de cliente',
    customer_name STRING COMMENT 'Nombre completo del cliente',
    segment STRING COMMENT 'Segmento comercial',
    country STRING COMMENT 'Pais de despacho',
    city STRING COMMENT 'Ciudad de entrega',
    state STRING COMMENT 'Estado de entrega',
    postal_code STRING COMMENT 'Codigo postal de entrega',
    region STRING COMMENT 'Region geografica comercial',
    product_id STRING COMMENT 'Identificador de producto',
    category STRING COMMENT 'Categoria comercial',
    sub_category STRING COMMENT 'Subcategoria comercial',
    product_name STRING COMMENT 'Descripcion comercial de producto',
    sales DECIMAL(10,2) COMMENT 'Monto facturado en USD',
    quantity INT COMMENT 'Unidades comercializadas',
    discount DECIMAL(4,2) COMMENT 'Porcentaje de descuento otorgado',
    profit DECIMAL(10,2) COMMENT 'Utilidad neta obtenida en USD'
)
COMMENT 'Tabla analitica optimizada para consultas analiticas avanzadas'
STORED AS ORC
TBLPROPERTIES (
    "orc.compress"="SNAPPY",
    "orc.create.index"="true",
    "orc.stripe.size"="67108864",
    "orc.row.index.stride"="10000"
);
