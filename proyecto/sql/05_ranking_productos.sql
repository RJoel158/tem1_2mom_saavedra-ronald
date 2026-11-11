-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 05_ranking_productos.sql
-- Descripcion: Ranking y clasificacion de productos por rentabilidad, volumen y categoria
-- ==============================================================================

USE superstore_db;

WITH producto_metricas AS (
    SELECT
        product_id,
        product_name,
        category,
        sub_category,
        ROUND(SUM(sales), 2) AS ventas_totales,
        ROUND(SUM(profit), 2) AS ganancia_total,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margen_rentabilidad_pct
    FROM superstore_analitica
    GROUP BY product_id, product_name, category, sub_category
),
producto_analitico AS (
    SELECT
        product_id,
        product_name,
        category,
        sub_category,
        ventas_totales,
        ganancia_total,
        margen_rentabilidad_pct,
        -- Posicion por rentabilidad dentro de su categoria
        DENSE_RANK() OVER (PARTITION BY category ORDER BY ganancia_total DESC) AS rank_ganancia_categoria,
        -- Posicion por volumen de ventas global
        RANK() OVER (ORDER BY ventas_totales DESC) AS rank_ventas_global,
        -- Posicion por menor desempeno / perdidas globales
        RANK() OVER (ORDER BY ganancia_total ASC) AS rank_peor_rentabilidad_global,
        -- Agregacion acumulativa de ganancia por categoria
        ROUND(SUM(ganancia_total) OVER (
            PARTITION BY category 
            ORDER BY ganancia_total DESC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) AS ganancia_acumulada_categoria
    FROM producto_metricas
)
-- 1. Top 5 productos con mayor ganancia acumulada por categoria
SELECT
    category,
    rank_ganancia_categoria,
    product_name,
    ventas_totales,
    ganancia_total,
    margen_rentabilidad_pct,
    ganancia_acumulada_categoria
FROM producto_analitico
WHERE rank_ganancia_categoria <= 5
ORDER BY category, rank_ganancia_categoria ASC;

-- 2. Top 5 productos con mayor volumen de ventas a nivel global
SELECT
    rank_ventas_global,
    product_name,
    category,
    sub_category,
    ventas_totales,
    ganancia_total,
    margen_rentabilidad_pct
FROM producto_analitico
WHERE rank_ventas_global <= 5
ORDER BY rank_ventas_global ASC;

-- 3. Top 5 productos con menor rentabilidad (mayores perdidas operativas)
SELECT
    rank_peor_rentabilidad_global,
    product_name,
    category,
    sub_category,
    ventas_totales,
    ganancia_total,
    margen_rentabilidad_pct
FROM producto_analitico
WHERE rank_peor_rentabilidad_global <= 5
ORDER BY rank_peor_rentabilidad_global ASC;
