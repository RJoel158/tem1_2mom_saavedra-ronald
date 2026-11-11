-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 02_auditoria_calidad.sql
-- Descripcion: Auditoria integral de calidad, integridad referencial y reglas de negocio
-- ==============================================================================

USE superstore_db;

-- 1. Resumen consolidado de auditoria de calidad de datos
SELECT
    COUNT(*) AS total_registros,
    COUNT(row_id) - COUNT(DISTINCT row_id) AS duplicados_row_id,
    COUNT(DISTINCT order_id) AS ordenes_unicas,
    COUNT(DISTINCT customer_id) AS clientes_unicos,
    SUM(CASE WHEN row_id IS NULL OR order_id IS NULL OR order_date IS NULL OR 
                  customer_id IS NULL OR product_id IS NULL OR sales IS NULL OR 
                  profit IS NULL THEN 1 ELSE 0 END) AS campos_con_valores_null,
    SUM(CASE WHEN order_date IS NULL OR ship_date IS NULL THEN 1 ELSE 0 END) AS fechas_invalidas_inconsistentes,
    SUM(CASE WHEN sales <= 0 THEN 1 ELSE 0 END) AS ventas_menor_igual_cero,
    SUM(CASE WHEN discount < 0.0 OR discount > 1.0 THEN 1 ELSE 0 END) AS descuentos_fuera_intervalo,
    SUM(CASE WHEN ship_date < order_date THEN 1 ELSE 0 END) AS envio_anterior_a_pedido,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS registros_con_perdida_operativa
FROM superstore_analitica;

-- 2. Verificacion adicional de rangos de descuento y rentabilidad por segmento
SELECT
    segment,
    COUNT(*) AS total_operaciones,
    ROUND(MIN(discount), 2) AS desc_minimo,
    ROUND(MAX(discount), 2) AS desc_maximo,
    ROUND(AVG(discount), 4) AS desc_promedio,
    ROUND(MIN(profit), 2) AS peor_perdida_usd,
    ROUND(MAX(profit), 2) AS mayor_ganancia_usd,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS transacciones_deficitarias
FROM superstore_analitica
GROUP BY segment
ORDER BY total_operaciones DESC;
