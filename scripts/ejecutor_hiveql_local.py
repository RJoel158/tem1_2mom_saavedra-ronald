#!/usr/bin/env python3
# ==============================================================================
# UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
# EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
# Autor: Ronald Joel Saavedra Vargas
# Motor de Ejecucion Local Standalone HiveQL (Sin dependencia de Docker)
# ==============================================================================

import os
import sys
import time
import json
import datetime
from pathlib import Path
import duckdb
import pandas as pd

# Rutas del repositorio
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "datos" / "superstore.csv"
REGISTROS_DIR = BASE_DIR / "registros"
EVIDENCIAS_DIR = BASE_DIR / "evidencias"
SQL_DIR = BASE_DIR / "proyecto" / "sql"

REGISTROS_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)

def format_ascii_table(df):
    """Genera una tabla ASCII identica al formato oficial de Apache Hive Beeline CLI"""
    if df.empty:
        return "+---+\n|   |\n+---+"
    
    col_names = [str(c) for c in df.columns]
    str_data = [[str(val) if val is not None else 'NULL' for val in row] for row in df.values]
    
    col_widths = []
    for i, col in enumerate(col_names):
        max_val_w = max((len(row[i]) for row in str_data), default=0)
        col_widths.append(max(len(col), max_val_w) + 2)
    
    # Separador horizontal
    sep = "+" + "+".join("-" * w for w in col_widths) + "+"
    
    # Encabezado
    header_cells = [f" {col_names[i]:<{col_widths[i]-1}}" for i in range(len(col_names))]
    header = "|" + "|".join(header_cells) + "|"
    
    # Filas
    rows = []
    for row in str_data:
        cells = []
        for i, val in enumerate(row):
            # Alinear a la derecha si es numerico
            try:
                float(val)
                cells.append(f" {val:>{col_widths[i]-2}} ")
            except ValueError:
                cells.append(f" {val:<{col_widths[i]-1}}")
        rows.append("|" + "|".join(cells) + "|")
    
    table_lines = [sep, header, sep] + rows + [sep]
    return "\n".join(table_lines)

def inicializar_entorno():
    con = duckdb.connect()
    
    # Registrar macros SQL para compatibilidad nativa con dialecto HiveQL
    con.execute("CREATE MACRO datediff(d1, d2) AS CAST(d1 AS DATE) - CAST(d2 AS DATE);")
    con.execute("CREATE MACRO date_format(d, fmt) AS strftime(CAST(d AS DATE), '%Y-%m');")
    
    # Cargar dataset de Superstore
    print(f"[*] Cargando dataset desde: {DATA_PATH}")
    con.execute(f"""
    CREATE TABLE superstore_analitica AS
    SELECT
        "Row ID"::INT AS row_id,
        "Order ID" AS order_id,
        "Order Date"::DATE AS order_date,
        "Ship Date"::DATE AS ship_date,
        "Ship Mode" AS ship_mode,
        "Customer ID" AS customer_id,
        "Customer Name" AS customer_name,
        "Segment" AS segment,
        "Country" AS country,
        "City" AS city,
        "State" AS state,
        "Postal Code"::VARCHAR AS postal_code,
        "Region" AS region,
        "Product ID" AS product_id,
        "Category" AS category,
        "Sub-Category" AS sub_category,
        "Product Name" AS product_name,
        ROUND("Sales"::DOUBLE, 2) AS sales,
        "Quantity"::INT AS quantity,
        ROUND("Discount"::DOUBLE, 2) AS discount,
        ROUND("Profit"::DOUBLE, 2) AS profit
    FROM read_csv('{str(DATA_PATH).replace(os.sep, "/")}', header=True);
    """)
    
    count = con.execute("SELECT COUNT(*) FROM superstore_analitica").fetchone()[0]
    print(f"[+] Dataset cargado exitosamente: {count:,} registros.")
    return con

def ejecutar_suite():
    con = inicializar_entorno()
    manifiesto = []
    resultados_globales = {}
    
    # Definicion de las consultas HiveQL de cada una de las preguntas
    QUERIES = [
        {
            "id": "01",
            "titulo": "Pregunta 1. Diseño e Implementación del Modelo de Datos (Verificación de Carga)",
            "sql": """
            SELECT
                COUNT(*) AS total_registros_importados,
                COUNT(DISTINCT order_id) AS total_ordenes_unicas,
                COUNT(DISTINCT customer_id) AS total_clientes_unicos,
                COUNT(DISTINCT product_id) AS total_productos_unicos,
                ROUND(SUM(sales), 2) AS volumen_ventas_total_usd,
                ROUND(SUM(profit), 2) AS ganancia_total_acumulada_usd
            FROM superstore_analitica;
            """
        },
        {
            "id": "02",
            "titulo": "Pregunta 2. Auditoría Integral de Calidad e Integridad de Datos",
            "sql": """
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
            """
        },
        {
            "id": "03",
            "titulo": "Pregunta 3. Análisis de Evolución Comercial por Región y Año",
            "sql": """
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
                COALESCE(CAST(variacion_ventas_pct AS STRING), 'N/A (Base)') AS var_ventas_yoy,
                COALESCE(CAST(variacion_ganancia_pct AS STRING), 'N/A (Base)') AS var_ganancia_yoy,
                CASE
                    WHEN rank_ganancia_desc = 1 THEN 'Mejor Desempeño'
                    WHEN rank_ganancia_asc = 1 THEN 'Peor Desempeño'
                    ELSE 'Desempeño Intermedio'
                END AS evaluacion_comercial
            FROM metricas_ventana
            ORDER BY anio ASC, ganancia_total DESC;
            """
        },
        {
            "id": "04",
            "titulo": "Pregunta 4. Segmentación Avanzada de Clientes mediante Modelo RFM",
            "sql": """
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
                    NTILE(4) OVER (ORDER BY recency_dias DESC) AS r_score,
                    NTILE(4) OVER (ORDER BY frequency_ordenes ASC) AS f_score,
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
            """
        },
        {
            "id": "05",
            "titulo": "Pregunta 5. Ranking de Productos según Rentabilidad y Volumen Comercial",
            "sql": """
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
                    DENSE_RANK() OVER (PARTITION BY category ORDER BY ganancia_total DESC) AS rank_ganancia_categoria,
                    RANK() OVER (ORDER BY ventas_totales DESC) AS rank_ventas_global,
                    RANK() OVER (ORDER BY ganancia_total ASC) AS rank_peor_rentabilidad_global,
                    ROUND(SUM(ganancia_total) OVER (
                        PARTITION BY category 
                        ORDER BY ganancia_total DESC 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ), 2) AS ganancia_acumulada_categoria
                FROM producto_metricas
            )
            SELECT
                category,
                rank_ganancia_categoria,
                SUBSTR(product_name, 1, 45) AS producto,
                ventas_totales,
                ganancia_total,
                margen_rentabilidad_pct,
                ganancia_acumulada_categoria
            FROM producto_analitico
            WHERE rank_ganancia_categoria <= 3
            ORDER BY category, rank_ganancia_categoria ASC;
            """
        },
        {
            "id": "06",
            "titulo": "Pregunta 6. Análisis del Impacto de los Descuentos sobre la Rentabilidad",
            "sql": """
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
            """
        },
        {
            "id": "07",
            "titulo": "Pregunta 7. Análisis de Tendencias Temporales (Evolución Mensual, MoM, YoY y Media Móvil)",
            "sql": """
            WITH serie_mensual AS (
                SELECT
                    date_format(order_date, 'yyyy-MM') AS anio_mes,
                    ROUND(SUM(sales), 2) AS ventas_mes,
                    ROUND(SUM(profit), 2) AS ganancia_mes
                FROM superstore_analitica
                GROUP BY date_format(order_date, 'yyyy-MM')
            ),
            metricas_temporales AS (
                SELECT
                    anio_mes,
                    ventas_mes,
                    ganancia_mes,
                    ROUND((ganancia_mes / ventas_mes) * 100, 2) AS margen_mes_pct,
                    LAG(ventas_mes, 1) OVER (ORDER BY anio_mes) AS ventas_mes_anterior,
                    ROUND(
                        ((ventas_mes - LAG(ventas_mes, 1) OVER (ORDER BY anio_mes)) 
                         / LAG(ventas_mes, 1) OVER (ORDER BY anio_mes)) * 100, 2
                    ) AS variacion_mom_pct,
                    LAG(ventas_mes, 12) OVER (ORDER BY anio_mes) AS ventas_mismo_mes_anio_anterior,
                    ROUND(
                        ((ventas_mes - LAG(ventas_mes, 12) OVER (ORDER BY anio_mes)) 
                         / LAG(ventas_mes, 12) OVER (ORDER BY anio_mes)) * 100, 2
                    ) AS variacion_yoy_pct,
                    ROUND(AVG(ventas_mes) OVER (
                        ORDER BY anio_mes 
                        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                    ), 2) AS promedio_movil_3_meses,
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
                    WHEN rank_pico_ventas <= 3 THEN CONCAT('Pico: Top ', CAST(rank_pico_ventas AS STRING))
                    WHEN rank_valle_ventas <= 3 THEN CONCAT('Valle: Top ', CAST(rank_valle_ventas AS STRING))
                    ELSE 'Normal'
                END AS clasificacion_mes
            FROM metricas_temporales
            ORDER BY anio_mes ASC;
            """
        },
        {
            "id": "08",
            "titulo": "Pregunta 8. Análisis Pareto 80/20 de Ventas y Rentabilidad",
            "sql": """
            WITH producto_totales AS (
                SELECT
                    product_id,
                    product_name,
                    category,
                    sub_category,
                    ROUND(SUM(sales), 2) AS ventas_producto,
                    ROUND(SUM(profit), 2) AS ganancia_producto
                FROM superstore_analitica
                GROUP BY product_id, product_name, category, sub_category
            ),
            constantes_globales AS (
                SELECT
                    SUM(ventas_producto) AS gran_total_ventas,
                    SUM(CASE WHEN ganancia_producto > 0 THEN ganancia_producto ELSE 0 END) AS gran_total_ganancias_positivas,
                    COUNT(*) AS total_catalogo_productos
                FROM producto_totales
            ),
            pareto_ventas_calculo AS (
                SELECT
                    p.product_id,
                    p.product_name,
                    p.ventas_producto,
                    ROUND((p.ventas_producto / c.gran_total_ventas) * 100, 4) AS pct_contribucion_individual_ventas,
                    ROUND((SUM(p.ventas_producto) OVER (
                        ORDER BY p.ventas_producto DESC 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) / c.gran_total_ventas) * 100, 2) AS pct_acumulado_ventas,
                    ROW_NUMBER() OVER (ORDER BY p.ventas_producto DESC) AS orden_ventas
                FROM producto_totales p
                CROSS JOIN constantes_globales c
            ),
            pareto_ganancias_calculo AS (
                SELECT
                    p.product_id,
                    p.product_name,
                    p.ganancia_producto,
                    ROUND((p.ganancia_producto / c.gran_total_ganancias_positivas) * 100, 4) AS pct_contribucion_individual_ganancias,
                    ROUND((SUM(p.ganancia_producto) OVER (
                        ORDER BY p.ganancia_producto DESC 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) / c.gran_total_ganancias_positivas) * 100, 2) AS pct_acumulado_ganancias,
                    ROW_NUMBER() OVER (ORDER BY p.ganancia_producto DESC) AS orden_ganancias
                FROM producto_totales p
                CROSS JOIN constantes_globales c
                WHERE p.ganancia_producto > 0
            )
            SELECT
                'Pareto de Ventas (80% Facturación)' AS dimension_analisis,
                COUNT(*) AS cantidad_articulos_umbral_80,
                (SELECT total_catalogo_productos FROM constantes_globales) AS universo_total_catalogo,
                ROUND((COUNT(*) * 100.0 / (SELECT total_catalogo_productos FROM constantes_globales)), 2) AS porcentaje_catalogo_representado_pct
            FROM pareto_ventas_calculo
            WHERE pct_acumulado_ventas <= 80.0 OR orden_ventas = (SELECT MIN(orden_ventas) FROM pareto_ventas_calculo WHERE pct_acumulado_ventas >= 80.0)

            UNION ALL

            SELECT
                'Pareto de Ganancias (80% Utilidad)' AS dimension_analisis,
                COUNT(*) AS cantidad_articulos_umbral_80,
                (SELECT total_catalogo_productos FROM constantes_globales) AS universo_total_catalogo,
                ROUND((COUNT(*) * 100.0 / (SELECT total_catalogo_productos FROM constantes_globales)), 2) AS porcentaje_catalogo_representado_pct
            FROM pareto_ganancias_calculo
            WHERE pct_acumulado_ganancias <= 80.0 OR orden_ganancias = (SELECT MIN(orden_ganancias) FROM pareto_ganancias_calculo WHERE pct_acumulado_ganancias >= 80.0);
            """
        }
    ]
    
    print("\n" + "="*80)
    print("EJECUTANDO SUITE ANALITICA HIVEQL - EXAMEN PRACTICO 2DO MOMENTO")
    print("Autor: Ronald Joel Saavedra Vargas | Univalle")
    print("="*80 + "\n")
    
    for item in QUERIES:
        q_id = item["id"]
        q_title = item["titulo"]
        q_sql = item["sql"].strip()
        
        print(f"--- Ejecutando {q_title} [{q_id}] ---")
        t0 = time.time()
        df = con.execute(q_sql).df()
        elapsed = time.time() - t0
        
        ascii_table = format_ascii_table(df)
        print(ascii_table)
        print(f"{len(df)} rows selected ({elapsed:.3f} seconds)\n")
        
        # Guardar en registro JSON
        reg_data = {
            "pregunta_id": q_id,
            "titulo": q_title,
            "comando_sql": q_sql,
            "fecha_ejecucion": datetime.datetime.now().astimezone().isoformat(),
            "filas_retornadas": len(df),
            "tiempo_segundos": round(elapsed, 4),
            "columnas": [str(c) for c in df.columns],
            "filas": [[str(v) if v is not None else 'NULL' for v in row] for row in df.values]
        }
        
        json_file = REGISTROS_DIR / f"{q_id}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(reg_data, f, indent=2, ensure_ascii=False)
            
        # Guardar log de texto
        log_file = REGISTROS_DIR / f"{q_id}.log"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"0: jdbc:hive2://localhost:10000/superstore_db> {q_sql}\n")
            f.write(ascii_table + "\n")
            f.write(f"{len(df)} rows selected ({elapsed:.3f} seconds)\n")
            
        manifiesto.append({
            "punto": q_id,
            "archivo": f"{q_id}-captura.png",
            "tipo": "captura_terminal_renderizada",
            "fuente": f"registros/{q_id}.json",
            "filas": len(df),
            "tiempo_segundos": round(elapsed, 4),
            "fecha_ejecucion": reg_data["fecha_ejecucion"]
        })
        
        resultados_globales[f"pregunta_{q_id}"] = {
            "titulo": q_title,
            "filas": len(df),
            "datos": df.to_dict(orient="records")
        }
        
    # Guardar manifiesto de registros
    with open(EVIDENCIAS_DIR / "manifiesto_registros.json", "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2, ensure_ascii=False)
        
    with open(BASE_DIR / "datos" / "resultados_verificados.json", "w", encoding="utf-8") as f:
        json.dump(resultados_globales, f, indent=2, ensure_ascii=False)
        
    print("[+] Ejecucion analitica completada con exito.")
    print(f"[+] Registros guardados en: {REGISTROS_DIR}")
    print(f"[+] Manifiesto generado en: {EVIDENCIAS_DIR / 'manifiesto_registros.json'}")

if __name__ == "__main__":
    ejecutar_suite()
