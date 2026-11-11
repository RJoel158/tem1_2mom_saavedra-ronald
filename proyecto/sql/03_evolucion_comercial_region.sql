-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 03_evolucion_comercial_region.sql
-- Descripcion: Evolucion de ventas, ganancias, margen y variacion interanual por region
-- ==============================================================================

USE superstore_db;

WITH evolucion_base AS (
    SELECT
        region,
        YEAR(order_date) AS anio,
        ROUND(SUM(sales), 2) AS ventas_totales,
        ROUND(SUM(profit), 2) AS ganancia_total,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margen_rentabilidad_pct
    FROM superstore_analitica
    GROUP BY region, YEAR(order_date)
),
metricas_ventana AS (
    SELECT
        region,
        anio,
        ventas_totales,
        ganancia_total,
        margen_rentabilidad_pct,
        LAG(ventas_totales) OVER (PARTITION BY region ORDER BY anio) AS ventas_anio_anterior,
        ROUND(
            ((ventas_totales - LAG(ventas_totales) OVER (PARTITION BY region ORDER BY anio)) 
             / LAG(ventas_totales) OVER (PARTITION BY region ORDER BY anio)) * 100, 2
        ) AS variacion_ventas_pct,
        LAG(ganancia_total) OVER (PARTITION BY region ORDER BY anio) AS ganancia_anio_anterior,
        ROUND(
            ((ganancia_total - LAG(ganancia_total) OVER (PARTITION BY region ORDER BY anio)) 
             / LAG(ganancia_total) OVER (PARTITION BY region ORDER BY anio)) * 100, 2
        ) AS variacion_ganancia_pct,
        DENSE_RANK() OVER (PARTITION BY anio ORDER BY ganancia_total DESC) AS rank_ganancia_desc,
        DENSE_RANK() OVER (PARTITION BY anio ORDER BY ganancia_total ASC) AS rank_ganancia_asc
    FROM evolucion_base
)
SELECT
    region,
    anio,
    ventas_totales,
    ganancia_total,
    margen_rentabilidad_pct,
    COALESCE(CAST(variacion_ventas_pct AS STRING), 'N/A (Base)') AS var_ventas_yoy_pct,
    COALESCE(CAST(variacion_ganancia_pct AS STRING), 'N/A (Base)') AS var_ganancia_yoy_pct,
    CASE
        WHEN rank_ganancia_desc = 1 THEN 'Mejor Desempeño Comercial'
        WHEN rank_ganancia_asc = 1 THEN 'Peor Desempeño Comercial'
        ELSE 'Desempeño Comercial Intermedio'
    END AS evaluacion_desempeno
FROM metricas_ventana
ORDER BY anio ASC, ganancia_total DESC;
