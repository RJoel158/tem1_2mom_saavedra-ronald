-- ==============================================================================
-- UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
-- EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
-- Autor: Ronald Joel Saavedra Vargas
-- Script: 04_segmentacion_rfm.sql
-- Descripcion: Segmentacion avanzada de clientes mediante modelo RFM (Recency, Frequency, Monetary)
-- ==============================================================================

USE superstore_db;

WITH max_fecha_dataset AS (
    SELECT MAX(order_date) AS fecha_corte FROM superstore_analitica
),
rfm_base AS (
    SELECT
        s.customer_id,
        s.customer_name,
        s.segment,
        DATEDIFF(m.fecha_corte, MAX(s.order_date)) AS recency_dias,
        COUNT(DISTINCT s.order_id) AS frequency_ordenes,
        ROUND(SUM(s.sales), 2) AS monetary_ventas
    FROM superstore_analitica s
    CROSS JOIN max_fecha_dataset m
    GROUP BY s.customer_id, s.customer_name, s.segment, m.fecha_corte
),
rfm_scores AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        recency_dias,
        frequency_ordenes,
        monetary_ventas,
        -- Puntuacion R: Menor recency dias = Mayor puntaje (NTILE ordenado DESC)
        NTILE(4) OVER (ORDER BY recency_dias DESC) AS r_score,
        -- Puntuacion F: Mayor frecuencia = Mayor puntaje
        NTILE(4) OVER (ORDER BY frequency_ordenes ASC) AS f_score,
        -- Puntuacion M: Mayor volumen facturado = Mayor puntaje
        NTILE(4) OVER (ORDER BY monetary_ventas ASC) AS m_score
    FROM rfm_base
),
rfm_clasificacion AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        recency_dias,
        frequency_ordenes,
        monetary_ventas,
        r_score,
        f_score,
        m_score,
        (r_score + f_score + m_score) AS score_total_rfm,
        CASE
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Clientes de Alto Valor (Champions)'
            WHEN f_score >= 3 AND m_score >= 2 THEN 'Clientes Recurrentes Fidelizados (Loyal)'
            WHEN r_score <= 2 AND f_score >= 2 THEN 'En Riesgo de Abandono (At Risk)'
            WHEN r_score >= 3 AND f_score < 3 THEN 'Nuevos / Prometedores (Promising)'
            ELSE 'Inactivos / Hibernando (Hibernating)'
        END AS perfil_cliente_rfm
    FROM rfm_scores
)
-- 1. Resumen consolidado por perfil de cliente
SELECT
    perfil_cliente_rfm,
    COUNT(*) AS total_clientes,
    ROUND(COUNT(*) * 100.0 / 793, 2) AS porcentaje_clientes_pct,
    ROUND(AVG(recency_dias), 1) AS recency_promedio_dias,
    ROUND(AVG(frequency_ordenes), 1) AS frecuencia_promedio_ordenes,
    ROUND(SUM(monetary_ventas), 2) AS facturacion_total_usd,
    ROUND(AVG(monetary_ventas), 2) AS ticket_promedio_acumulado_usd
FROM rfm_clasificacion
GROUP BY perfil_cliente_rfm
ORDER BY facturacion_total_usd DESC;
