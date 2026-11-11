-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: optimizacion_hive.sql
-- Descripcion: Estrategias avanzadas de optimizacion de rendimiento en Apache Hive
-- ==============================================================================

USE superstore_db;

-- 1. Habilitacion de Motor de Ejecucion Distribuido Tez y Optimizador Basado en Costos (CBO)
SET hive.execution.engine=tez;
SET hive.cbo.enable=true;
SET hive.compute.query.using.stats=true;
SET hive.stats.autogather=true;

-- 2. Habilitacion de Ejecucion Vectorizada (Vectorized Query Execution)
-- Permite procesar lotes de 1024 filas simultaneamente en memoria cache L1/L2
SET hive.vectorized.execution.enabled=true;
SET hive.vectorized.execution.reduce.enabled=true;

-- 3. Optimizacion de Joins mediante MapJoin (Broadcast Join automatico en memoria)
SET hive.auto.convert.join=true;
SET hive.auto.convert.join.noconditionaltask=true;
SET hive.auto.convert.join.noconditionaltask.size=20971520; -- 20 MB

-- 4. Particionado Dinamico y Bucketing (Clustering)
-- Se diseña una tabla particionada por Region y distribuida por Hash de Customer_ID en 4 Buckets
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;
SET hive.enforce.bucketing=true;

DROP TABLE IF EXISTS superstore_optimizada_part_bucket;

CREATE TABLE IF NOT EXISTS superstore_optimizada_part_bucket (
    row_id INT,
    order_id STRING,
    order_date DATE,
    ship_date DATE,
    ship_mode STRING,
    customer_id STRING,
    customer_name STRING,
    segment STRING,
    country STRING,
    city STRING,
    state STRING,
    postal_code STRING,
    product_id STRING,
    category STRING,
    sub_category STRING,
    product_name STRING,
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(4,2),
    profit DECIMAL(10,2)
)
COMMENT 'Tabla analitica particionada por Region y con Bucketing por Customer ID'
PARTITIONED BY (region STRING)
CLUSTERED BY (customer_id) SORTED BY (order_date ASC) INTO 4 BUCKETS
STORED AS ORC
TBLPROPERTIES (
    "orc.compress"="SNAPPY",
    "orc.create.index"="true",
    "orc.stripe.size"="67108864"
);

-- Insercion en tabla optimizada con particion dinamica
INSERT OVERWRITE TABLE superstore_optimizada_part_bucket PARTITION(region)
SELECT
    row_id,
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    product_id,
    category,
    sub_category,
    product_name,
    sales,
    quantity,
    discount,
    profit,
    region
FROM superstore_analitica;

-- 5. Calculo de Estadisticas de Columna para CBO (Cost-Based Optimizer)
ANALYZE TABLE superstore_optimizada_part_bucket COMPUTE STATISTICS;
ANALYZE TABLE superstore_optimizada_part_bucket COMPUTE STATISTICS FOR COLUMNS sales, profit, discount, customer_id;
