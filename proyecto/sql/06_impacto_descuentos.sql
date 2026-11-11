-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 06_impacto_descuentos.sql
-- Descripcion: Evaluacion del impacto de los descuentos comerciales sobre la rentabilidad
-- ==============================================================================

USE superstore_db;

WITH transacciones_clasificadas AS (
    SELECT
        row_id,
        category,
        sub_category,
        sales,
        discount,
        profit,
        CASE
            WHEN discount = 0.00 THEN '1. Sin descuento (0%)'
            WHEN discount > 0.00 AND discount <= 0.20 THEN '2. Descuento bajo (0% - 20%]'
            WHEN discount > 0.20 AND discount <= 0.50 THEN '3. Descuento medio (20% - 50%]'
            WHEN discount > 0.50 THEN '4. Descuento alto (> 50%)'
        END AS rango_descuento
    FROM superstore_analitica
)
-- 1. Analisis consolidado por rango de descuento
SELECT
    rango_descuento,
    COUNT(*) AS total_transacciones,
    ROUND(SUM(sales), 2) AS ventas_totales_usd,
    ROUND(SUM(profit), 2) AS ganancia_total_usd,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margen_rentabilidad_pct,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS registros_con_perdidas,
    ROUND((SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS pct_operaciones_no_rentables,
    ROUND(AVG(discount) * 100, 2) AS descuento_promedio_pct
FROM transacciones_clasificadas
GROUP BY rango_descuento
ORDER BY rango_descuento ASC;

-- 2. Subcategorias comerciales mas perjudicadas bajo politica de descuentos agresivos (> 20%)
SELECT
    category,
    sub_category,
    COUNT(*) AS transacciones_afectadas,
    ROUND(SUM(sales), 2) AS ventas_en_riesgo_usd,
    ROUND(SUM(profit), 2) AS perdida_neta_acumulada_usd,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margen_destructivo_pct,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS transacciones_con_perdida,
    ROUND((SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS tasa_perdida_pct
FROM transacciones_clasificadas
WHERE discount > 0.20
GROUP BY category, sub_category
HAVING SUM(profit) < 0
ORDER BY perdida_neta_acumulada_usd ASC;
