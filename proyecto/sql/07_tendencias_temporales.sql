-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 07_tendencias_temporales.sql
-- Descripcion: Analisis mensual de ventas y ganancias, variacion MoM, YoY y media movil
-- ==============================================================================

USE superstore_db;

WITH serie_mensual AS (
    SELECT
        DATE_FORMAT(order_date, 'yyyy-MM') AS anio_mes,
        ROUND(SUM(sales), 2) AS ventas_mes,
        ROUND(SUM(profit), 2) AS ganancia_mes
    FROM superstore_analitica
    GROUP BY DATE_FORMAT(order_date, 'yyyy-MM')
),
metricas_temporales AS (
    SELECT
        anio_mes,
        ventas_mes,
        ganancia_mes,
        ROUND((ganancia_mes / ventas_mes) * 100, 2) AS margen_mes_pct,
        -- Variacion respecto al mes inmediato anterior (MoM)
        LAG(ventas_mes, 1) OVER (ORDER BY anio_mes) AS ventas_mes_anterior,
        ROUND(
            ((ventas_mes - LAG(ventas_mes, 1) OVER (ORDER BY anio_mes)) 
             / LAG(ventas_mes, 1) OVER (ORDER BY anio_mes)) * 100, 2
        ) AS variacion_mom_pct,
        -- Comparacion con el mismo mes del año anterior (YoY - 12 periodos atras)
        LAG(ventas_mes, 12) OVER (ORDER BY anio_mes) AS ventas_mismo_mes_anio_anterior,
        ROUND(
            ((ventas_mes - LAG(ventas_mes, 12) OVER (ORDER BY anio_mes)) 
             / LAG(ventas_mes, 12) OVER (ORDER BY anio_mes)) * 100, 2
        ) AS variacion_yoy_pct,
        -- Promedio movil trimestral (3 meses: 2 precedentes + actual)
        ROUND(AVG(ventas_mes) OVER (
            ORDER BY anio_mes 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2) AS promedio_movil_3_meses,
        -- Rankings para identificar picos y caidas
        DENSE_RANK() OVER (ORDER BY ventas_mes DESC) AS rank_pico_ventas,
        DENSE_RANK() OVER (ORDER BY ventas_mes ASC) AS rank_valle_ventas
    FROM serie_mensual
)
SELECT
    anio_mes,
    ventas_mes,
    ganancia_mes,
    margen_mes_pct,
    COALESCE(CAST(variacion_mom_pct AS STRING), 'N/A') AS var_mom_pct,
    COALESCE(CAST(variacion_yoy_pct AS STRING), 'N/A') AS var_yoy_pct,
    promedio_movil_3_meses,
    CASE
        WHEN rank_pico_ventas <= 3 THEN CONCAT('Pico: Top ', CAST(rank_pico_ventas AS STRING), ' Mayor Venta')
        WHEN rank_valle_ventas <= 3 THEN CONCAT('Valle: Top ', CAST(rank_valle_ventas AS STRING), ' Menor Venta')
        ELSE 'Normal'
    END AS clasificacion_temporal
FROM metricas_temporales
ORDER BY anio_mes ASC;
