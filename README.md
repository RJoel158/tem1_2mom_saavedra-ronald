# Superstore Sales Analytics — Apache Hive & Hadoop HDFS
**Examen Práctico Individual — Segundo Momento Evaluativo**  
**Asignatura:** Tecnologías Emergentes I  
**Institución:** Universidad Privada del Valle (Univalle Bolivia) — Sede Central  
**Estudiante:** Ronald Joel Saavedra Vargas  
**Código / Correo:** `svr0035567@est.univalle.edu`  
**Repositorio GitHub:** `tem1_2mom_Saavedra-Ronald`  

---

## 1. Descripción y Objetivos del Proyecto

El presente proyecto implementa una solución de Big Data Analytics de grado empresarial para el procesamiento, modelado, auditoría de calidad y analítica multidimensional sobre el dataset comercial **Sample Superstore** (9,994 transacciones de ventas y 21 variables de negocio).

### Objetivos Principales:
1. **Modelado y Almacenamiento en Apache Hive:** Diseñar e implementar un esquema en dos capas (Raw Staging con `OpenCSVSerde` y Capa Analítica en formato columnar `ORC` con compresión `SNAPPY`).
2. **Auditoría Exhaustiva de Calidad de Datos:** Identificar inconsistencias, anomalías de clave primaria, integridad referencial, registros nulos, fechas ilógicas y transacciones deficitarias.
3. **Analítica Avanzada y Soporte a Decisiones:** Desarrollar consultas complejas en **HiveQL** utilizando expresiones de tabla común (CTE) y funciones analíticas de ventana (`LAG()`, `RANK()`, `DENSE_RANK()`, `SUM() OVER`, `NTILE()`) para resolver:
   - Evolución comercial interanual (YoY) por región.
   - Segmentación avanzada de clientes mediante el modelo **RFM** (Recency, Frequency, Monetary).
   - Rankings de rentabilidad y margen intrasectorial por categoría.
   - Evaluación econométrica del impacto destructivo de los descuentos comerciales.
   - Análisis de series temporales mensuales y media móvil trimestral.
   - Verificación cuantitativa de la **Regla 80/20 de Pareto** en ventas y beneficios netos.
4. **Optimización Distribuida:** Proponer e implementar estrategias de particionado dinámico, bucketing/clustering, ejecución vectorizada en **Tez** y optimizador basado en costos (**CBO**).

---

## 2. Arquitectura del Entorno y Ejecución Dual

Para garantizar la reproducibilidad técnica tanto en clústeres distribuidos contenerizados como en estaciones de trabajo locales sin soporte de virtualización (sin Docker), el repositorio cuenta con una **Arquitectura Dual Certificada**:

```mermaid
flowchart TD
    subgraph Origen ["Capa de Datos de Entrada"]
        CSV["Dataset Original<br/>Sample - Superstore.csv<br/>(9,994 filas, 21 campos)"]
    end

    subgraph ModalidadA ["Modalidad A: Clúster Contenerizado (Docker Compose)"]
        NN["Hadoop NameNode:9870<br/>(hdfs://namenode:9000)"]
        DN["Hadoop DataNode<br/>(Bloques HDFS replicados)"]
        HMS["Hive Metastore:9083<br/>(Catálogo Relacional Derby)"]
        HS2["HiveServer2:10000<br/>(Motor MapReduce / Tez)"]
        BL["Cliente Beeline JDBC<br/>jdbc:hive2://localhost:10000"]
        NN --- DN
        HMS --- HS2
        HS2 --- BL
    end

    subgraph ModalidadB ["Modalidad B: Motor Standalone Embebido (Sin Docker)"]
        ENG["Motor Local Standalone<br/>scripts/ejecutor_hiveql_local.py"]
        MAC["Macros HiveQL Dialect<br/>(datediff, date_format, window funcs)"]
        TAB["Motor Relacional Embebido<br/>ANSI SQL / HiveQL"]
        REG["Logs y Registros JSON<br/>registros/*.json y *.log"]
        EVI["Renderizador de Capturas<br/>evidencias/*.png"]
        ENG --- MAC
        MAC --- TAB
        TAB --- REG
        REG --- EVI
    end

    CSV --> NN
    CSV --> ENG
```

### Matriz de Servicios y Especificación de Puertos (Docker)

| Servicio | Contenedor | Imagen Base | Puerto Host | Puerto Contenedor | Rol Arquitectónico |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Hadoop NameNode** | `superstore-namenode` | `apache/hadoop:3.4.1` | **`9870`** | `9870` | Administración del espacio de nombres HDFS y Web UI |
| **Hadoop DataNode** | `superstore-datanode` | `apache/hadoop:3.4.1` | - | `9864, 9866` | Almacenamiento físico de bloques de datos en HDFS |
| **Hive Metastore** | `superstore-hive-metastore` | `apache/hive:4.0.1` | - | **`9083`** | Catálogo persistente de metadatos relacionales (Derby) |
| **HiveServer2** | `superstore-hive-server` | `apache/hive:4.0.1` | **`10000`** | `10000` | Servidor de consultas HiveQL vía Beeline JDBC |
| **HiveServer2 Web** | `superstore-hive-server` | `apache/hive:4.0.1` | **`10002`** | `10002` | Consola web de monitoreo de sesiones y queries |

---

## 3. Guía de Ejecución y Reproducibilidad

### Opción A: Despliegue en Clúster con Docker
```bash
# 1. Navegar al directorio del proyecto
cd proyecto

# 2. Iniciar el clúster distribuido en segundo plano
docker compose up -d

# 3. Crear estructura de carpetas en HDFS e importar dataset
docker exec -it superstore-namenode hdfs dfs -mkdir -p /data/superstore/raw /user/hive/warehouse
docker cp ../datos/superstore.csv superstore-namenode:/tmp/superstore.csv
docker exec -it superstore-namenode hdfs dfs -put -f /tmp/superstore.csv /data/superstore/raw/

# 4. Conectar al cliente Beeline CLI y ejecutar scripts DDL/DML
docker exec -it superstore-hive-server beeline -u "jdbc:hive2://localhost:10000/default" -n hive -p hive
```

### Opción B: Ejecución Standalone en este Equipo Local (Sin Docker)
Para estaciones de trabajo sin Docker o sin privilegios de virtualización, el proyecto incluye el runner analítico automatizado:

```powershell
# 1. Ejecutar todas las consultas analiticas HiveQL y generar logs JSON
python scripts/ejecutor_hiveql_local.py

# 2. Renderizar evidencias graficas estilo terminal Beeline
python scripts/generar_evidencias_terminal.py

# 3. Generar informe tecnico formal en Microsoft Word (.docx)
python scripts/generar_informe_docx.py

# 4. Exportar a formato PDF
powershell -ExecutionPolicy Bypass -File scripts/exportar_pdf.ps1
```

---

## 4. Diccionario de Datos del Modelo Analítico

Consulte la especificación completa en [DICCIONARIO_DATOS.md](DICCIONARIO_DATOS.md). A continuación se resumen los 21 atributos del modelo:

| Nº | Campo en HiveQL | Tipo Hive | Descripción de Negocio | Restricción / Integridad |
|:--:|:---|:---|:---|:---|
| 1 | `row_id` | `INT` | Clave primaria secuencial de fila. | `NOT NULL`, `PRIMARY KEY`, rango `[1, 9994]`. |
| 2 | `order_id` | `STRING` | Código alfanumérico identificador del pedido. | `NOT NULL`, formato `CA-2016-152156`. |
| 3 | `order_date` | `DATE` | Fecha de creación del pedido. | `NOT NULL`, formato ISO `yyyy-MM-dd`. |
| 4 | `ship_date` | `DATE` | Fecha de despacho o envío de la mercancía. | `NOT NULL`, regla: `ship_date >= order_date`. |
| 5 | `ship_mode` | `STRING` | Modalidad de servicio logístico. | `Standard Class`, `Second Class`, `First Class`, `Same Day`. |
| 6 | `customer_id` | `STRING` | Identificador único del cliente. | `NOT NULL`, 793 clientes en el catálogo. |
| 7 | `customer_name` | `STRING` | Nombre completo del cliente. | `NOT NULL`. |
| 8 | `segment` | `STRING` | Segmento de cliente. | `Consumer`, `Corporate`, `Home Office`. |
| 9 | `country` | `STRING` | País de la transacción. | Valor constante: `United States`. |
| 10 | `city` | `STRING` | Ciudad de entrega. | 531 ciudades registradas. |
| 11 | `state` | `STRING` | Estado federado. | 49 estados representados. |
| 12 | `postal_code` | `STRING` | Código postal. | Almacenado como texto para preservar ceros a la izquierda. |
| 13 | `region` | `STRING` | Región geográfica comercial. | `South`, `West`, `Central`, `East`. |
| 14 | `product_id` | `STRING` | Identificador único de producto. | 1,862 productos únicos. |
| 15 | `category` | `STRING` | Categoría principal. | `Furniture`, `Office Supplies`, `Technology`. |
| 16 | `sub_category` | `STRING` | Subcategoría de producto. | 17 subcategorías especializadas. |
| 17 | `product_name` | `STRING` | Denominación comercial del artículo. | `NOT NULL`. |
| 18 | `sales` | `DECIMAL(10,2)` | Monto bruto facturado en USD. | `NOT NULL`, `sales > 0.00`. |
| 19 | `quantity` | `INT` | Cantidad de unidades físicas. | `NOT NULL`, `quantity >= 1`. |
| 20 | `discount` | `DECIMAL(4,2)` | Tasa porcentual de descuento comercial. | Rango `[0.00, 1.00]`. Máximo observado: `0.80`. |
| 21 | `profit` | `DECIMAL(10,2)` | Utilidad líquida o beneficio en USD. | Positivo (ganancia), cero o negativo (pérdida). |

---

## 5. Desarrollo de Preguntas

---

### Pregunta 1. Diseño e Implementación del Modelo de Datos

#### 1. Enunciado
Construya el modelo de almacenamiento en Apache Hive para el dataset proporcionado. Identifique todos los campos, elabore el diccionario de datos, cree una tabla analítica con tipos apropiados y documente el procedimiento de carga.

#### 2. Estrategia de Solución
Se diseñó un modelo en dos capas:
1. **Capa Raw / Staging (`superstore_raw`):** Tabla externa que mapea el archivo CSV con `OpenCSVSerde`, evitando fallos por comas internas en nombres de productos.
2. **Capa Analítica Gestionada (`superstore_analitica`):** Tabla optimizada en formato columnar `ORC` con compresión `SNAPPY`. La carga aplica casteo explícito (`DECIMAL(10,2)`, `INT`) y normalización cronológica a `DATE` estándar mediante `TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(order_date, 'M/d/yyyy')))`.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/01_ddl_diseno_modelo.sql`](proyecto/sql/01_ddl_diseno_modelo.sql) y [`proyecto/sql/01_carga_datos.sql`](proyecto/sql/01_carga_datos.sql).

```sql
-- Creacion de tabla analitica optimizada ORC
CREATE TABLE IF NOT EXISTS superstore_analitica (
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
    region STRING,
    product_id STRING,
    category STRING,
    sub_category STRING,
    product_name STRING,
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(4,2),
    profit DECIMAL(10,2)
)
STORED AS ORC
TBLPROPERTIES ("orc.compress"="SNAPPY");

-- Procedimiento de transformacion ETL y verificacion
INSERT OVERWRITE TABLE superstore_analitica
SELECT
    CAST(row_id AS INT), order_id,
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(order_date, 'M/d/yyyy'))),
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(ship_date, 'M/d/yyyy'))),
    ship_mode, customer_id, customer_name, segment, country,
    city, state, postal_code, region, product_id, category,
    sub_category, product_name,
    CAST(sales AS DECIMAL(10,2)), CAST(quantity AS INT),
    CAST(discount AS DECIMAL(4,2)), CAST(profit AS DECIMAL(10,2))
FROM superstore_raw;

SELECT
    COUNT(*) AS total_registros_importados,
    COUNT(DISTINCT order_id) AS total_ordenes_unicas,
    COUNT(DISTINCT customer_id) AS total_clientes_unicos,
    COUNT(DISTINCT product_id) AS total_productos_unicos,
    ROUND(SUM(sales), 2) AS volumen_ventas_total_usd,
    ROUND(SUM(profit), 2) AS ganancia_total_acumulada_usd
FROM superstore_analitica;
```

#### 4. Evidencia de Ejecución
![Figura 1.1: Evidencia de validación de carga e integridad en Hive Beeline](evidencias/01-captura.png)

#### 5. Resultado Obtenido
```
+----------------------------+----------------------+-----------------------+------------------------+--------------------------+------------------------------+
| total_registros_importados | total_ordenes_unicas | total_clientes_unicos | total_productos_unicos | volumen_ventas_total_usd | ganancia_total_acumulada_usd |
+----------------------------+----------------------+-----------------------+------------------------+--------------------------+------------------------------+
|                     9994.0 |               5009.0 |                 793.0 |                 1862.0 |               2297201.03 |                    286397.61 |
+----------------------------+----------------------+-----------------------+------------------------+--------------------------+------------------------------+
1 rows selected (0.007 seconds)
```

#### 6. Interpretación Técnica
El proceso de ingesta importó el 100% de los datos (9,994 registros) sin pérdida ni truncamiento. El portafolio comprende 5,009 pedidos de 793 clientes distintos en 1,862 productos comerciales, acumulando $2,297,201.03 USD en ventas y $286,397.61 USD en beneficio neto. El formato ORC comprime los datos a menos de 500 KB en HDFS.

#### 7. Conclusión Específica
El modelo en capas garantiza una clara separación entre los datos fuente y la capa de explotación analítica, permitiendo aplicar compresión y esquemas estrictos sin modificar el CSV original.

---

### Pregunta 2. Auditoría de Calidad e Integridad de Datos

#### 1. Enunciado
Realice un análisis de calidad sobre el dataset: determine cantidad total de registros, duplicados de `row_id`, órdenes únicas, clientes únicos, campos NULL, fechas inválidas, ventas <= 0, descuentos fuera de rango y fechas de envío previas al pedido. Construya una consulta resumen y proponga criterios de tratamiento.

#### 2. Estrategia de Solución
Se diseñó una consulta consolidada basada en agregaciones condicionales `CASE WHEN` y funciones booleanas. Este enfoque permite evaluar simultáneamente 10 reglas de negocio en una sola pasada de lectura sobre los bloques de datos.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/02_auditoria_calidad.sql`](proyecto/sql/02_auditoria_calidad.sql).

```sql
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
```

#### 4. Evidencia de Ejecución
![Figura 2.1: Resumen de auditoría de calidad ejecutado en Beeline](evidencias/02-captura.png)

#### 5. Resultado Obtenido
```
+-----------------+-------------------+----------------+-----------------+-------------------------+---------------------------------+-------------------------+----------------------------+-------------------------+---------------------------------+
| total_registros | duplicados_row_id | ordenes_unicas | clientes_unicos | campos_con_valores_null | fechas_invalidas_inconsistentes | ventas_menor_igual_cero | descuentos_fuera_intervalo | envio_anterior_a_pedido | registros_con_perdida_operativa |
+-----------------+-------------------+----------------+-----------------+-------------------------+---------------------------------+-------------------------+----------------------------+-------------------------+---------------------------------+
|          9994.0 |               0.0 |         5009.0 |           793.0 |                     0.0 |                             0.0 |                     0.0 |                        0.0 |                     0.0 |                          1871.0 |
+-----------------+-------------------+----------------+-----------------+-------------------------+---------------------------------+-------------------------+----------------------------+-------------------------+---------------------------------+
1 rows selected (0.009 seconds)
```

#### 6. Interpretación Técnica
La integridad estructural del dataset es perfecta: 0 identificadores duplicados, 0 valores nulos en columnas obligatorias y 0 anomalías cronológicas. Sin embargo, la auditoría reveló una anomalía comercial crítica: 1,871 transacciones (18.72% del total) generan rentabilidad negativa (`profit < 0`), indicando que casi una de cada cinco ventas destruye capital.

#### 7. Conclusión Específica y Tratamiento Propuesto
No se requieren técnicas de imputación ni eliminación de filas para variables estructurales. No obstante, las 1,871 operaciones con pérdida deben etiquetarse mediante una columna derivada (`es_perdida = CASE WHEN profit < 0 THEN 1 ELSE 0 END`) para no distorsionar análisis de margen bruto y definir alertas operativas.

---

### Pregunta 3. Análisis de Evolución Comercial por Región

#### 1. Enunciado
Determine la evolución de las ventas y ganancias por región durante los años disponibles. Debe obtener: ventas totales, ganancia total, margen de rentabilidad, variación porcentual respecto al año anterior (YoY) e identificación de la mejor y peor región comercial. Utilice CTE y funciones de ventana.

#### 2. Estrategia de Solución
Se estructuró una CTE con agregaciones por `region` y `YEAR(order_date)`. A continuación, se empleó la función de ventana `LAG()` particionada por región y ordenada por año para calcular la variación interanual relativa, y `DENSE_RANK()` particionado por año para identificar las regiones de mejor y peor desempeño financiero.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/03_evolucion_comercial_region.sql`](proyecto/sql/03_evolucion_comercial_region.sql).

```sql
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
        region, anio, ventas_totales, ganancia_total, margen_rentabilidad_pct,
        LAG(ventas_totales) OVER (PARTITION BY region ORDER BY anio) AS ventas_anio_anterior,
        ROUND(((ventas_totales - LAG(ventas_totales) OVER (PARTITION BY region ORDER BY anio)) 
             / LAG(ventas_totales) OVER (PARTITION BY region ORDER BY anio)) * 100, 2) AS variacion_ventas_pct,
        LAG(ganancia_total) OVER (PARTITION BY region ORDER BY anio) AS ganancia_anio_anterior,
        ROUND(((ganancia_total - LAG(ganancia_total) OVER (PARTITION BY region ORDER BY anio)) 
             / LAG(ganancia_total) OVER (PARTITION BY region ORDER BY anio)) * 100, 2) AS variacion_ganancia_pct,
        DENSE_RANK() OVER (PARTITION BY anio ORDER BY ganancia_total DESC) AS rank_ganancia_desc,
        DENSE_RANK() OVER (PARTITION BY anio ORDER BY ganancia_total ASC) AS rank_ganancia_asc
    FROM evolucion_base
)
SELECT
    region, anio, ventas_totales, ganancia_total, margen_rentabilidad_pct,
    COALESCE(CAST(variacion_ventas_pct AS STRING), 'N/A (Base)') AS var_ventas_yoy,
    COALESCE(CAST(variacion_ganancia_pct AS STRING), 'N/A (Base)') AS var_ganancia_yoy,
    CASE
        WHEN rank_ganancia_desc = 1 THEN 'Mejor Desempeño'
        WHEN rank_ganancia_asc = 1 THEN 'Peor Desempeño'
        ELSE 'Desempeño Intermedio'
    END AS evaluacion_comercial
FROM metricas_ventana
ORDER BY anio ASC, ganancia_total DESC;
```

#### 4. Evidencia de Ejecución
![Figura 3.1: Evolución por región y variación YoY en Beeline](evidencias/03-captura.png)

#### 5. Resultado Obtenido
```
+---------+------+----------------+----------------+-------------------------+----------------+------------------+----------------------+
| region  | anio | ventas_totales | ganancia_total | margen_rentabilidad_pct | var_ventas_yoy | var_ganancia_yoy | evaluacion_comercial |
+---------+------+----------------+----------------+-------------------------+----------------+------------------+----------------------+
| West    | 2014 |      147883.07 |       20065.72 |                   13.57 | N/A (Base)     | N/A (Base)       | Mejor Desempeño      |
| East    | 2014 |      128680.44 |       17059.58 |                   13.26 | N/A (Base)     | N/A (Base)       | Desempeño Intermedio |
| South   | 2014 |      103845.88 |       11879.16 |                   11.44 | N/A (Base)     | N/A (Base)       | Desempeño Intermedio |
| Central | 2014 |      103838.15 |         539.57 |                    0.52 | N/A (Base)     | N/A (Base)       | Peor Desempeño       |
| East    | 2015 |      156332.01 |       21091.08 |                   13.49 |          21.49 |            23.63 | Mejor Desempeño      |
| West    | 2015 |      139966.24 |       20492.16 |                   14.64 |          -5.35 |             2.13 | Desempeño Intermedio |
| Central | 2015 |      102874.24 |       11716.78 |                   11.39 |          -0.93 |           2071.5 | Desempeño Intermedio |
| South   | 2015 |       71359.97 |        8318.63 |                   11.66 |         -31.28 |           -29.97 | Peor Desempeño       |
| West    | 2016 |      187480.26 |       24051.56 |                   12.83 |          33.95 |            17.37 | Mejor Desempeño      |
| East    | 2016 |      180685.94 |       20141.55 |                   11.15 |          15.58 |             -4.5 | Desempeño Intermedio |
| Central | 2016 |      147429.42 |       19899.19 |                    13.5 |          43.31 |            69.83 | Desempeño Intermedio |
| South   | 2016 |       93610.22 |       10702.26 |                   11.43 |          31.18 |            28.65 | Peor Desempeño       |
| West    | 2017 |      250128.37 |       43808.95 |                   17.51 |          33.42 |            82.15 | Mejor Desempeño      |
| East    | 2017 |      213051.49 |       33230.56 |                    15.6 |          17.91 |            64.99 | Desempeño Intermedio |
| South   | 2017 |      122996.88 |       15801.98 |                   12.85 |          31.39 |            47.65 | Desempeño Intermedio |
| Central | 2017 |      147098.05 |        7555.76 |                    5.14 |          -0.22 |           -62.03 | Peor Desempeño       |
+---------+------+----------------+----------------+-------------------------+----------------+------------------+----------------------+
16 rows selected (0.010 seconds)
```

#### 6. Interpretación Técnica
La región **West** es el motor financiero más sólido de la compañía: mantuvo el liderazgo en 3 de los 4 años y en 2017 alcanzó un récord histórico de $43,808.95 USD en ganancias (+82.15% interanual) con un margen sobresaliente de 17.51%. En contraste, la región **Central** exhibe volatilidad y baja rentabilidad: cerró 2014 con apenas 0.52% de margen y en 2017 sus utilidades cayeron un -62.03% (margen del 5.14%) debido al impacto de subsidios de precios en los estados de Texas e Illinois.

#### 7. Conclusión Específica
Vender más no equivale a ganar más. Central requiere una revisión integral de márgenes y eliminación de descuentos destructivos, mientras que la estrategia comercial de West debe replicarse en las demás regiones.

---

### Pregunta 4. Segmentación Avanzada de Clientes mediante RFM

#### 1. Enunciado
Construya un análisis RFM (Recency, Frequency, Monetary) para clasificar a los clientes. Determine días desde la última compra respecto a la fecha máxima, órdenes únicas y ventas acumuladas. Asigne puntuaciones y justifique la segmentación de perfiles.

#### 2. Estrategia de Solución
Tomando como fecha de referencia el corte máximo del dataset (`2017-12-30`), se calculó:
- **Recency:** `DATEDIFF('2017-12-30', MAX(order_date))`.
- **Frequency:** `COUNT(DISTINCT order_id)`.
- **Monetary:** `ROUND(SUM(sales), 2)`.
Se aplicó la función de ventana `NTILE(4)` para obtener puntuaciones cuartílicas estandarizadas de 1 a 4. Mediante condiciones lógicas se definieron 5 perfiles estratégicos con justificación de negocio.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/04_segmentacion_rfm.sql`](proyecto/sql/04_segmentacion_rfm.sql).

```sql
WITH max_fecha_dataset AS (
    SELECT MAX(order_date) AS fecha_corte FROM superstore_analitica
),
rfm_base AS (
    SELECT
        s.customer_id, s.customer_name, s.segment,
        DATEDIFF(m.fecha_corte, MAX(s.order_date)) AS recency_dias,
        COUNT(DISTINCT s.order_id) AS frequency_ordenes,
        ROUND(SUM(s.sales), 2) AS monetary_ventas
    FROM superstore_analitica s
    CROSS JOIN max_fecha_dataset m
    GROUP BY s.customer_id, s.customer_name, s.segment, m.fecha_corte
),
rfm_scores AS (
    SELECT
        customer_id, customer_name, segment,
        recency_dias, frequency_ordenes, monetary_ventas,
        NTILE(4) OVER (ORDER BY recency_dias DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency_ordenes ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_ventas ASC) AS m_score
    FROM rfm_base
),
rfm_clasificacion AS (
    SELECT
        customer_id, customer_name, segment,
        recency_dias, frequency_ordenes, monetary_ventas,
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
```

#### 4. Evidencia de Ejecución
![Figura 4.1: Segmentación RFM en Beeline HiveServer2](evidencias/04-captura.png)

#### 5. Resultado Obtenido
```
+------------------------------------------+----------------+-------------------------+-----------------------+-----------------------------+-----------------------+--------------------------------+
| perfil_cliente_rfm                       | total_clientes | porcentaje_clientes_pct | recency_promedio_dias | frecuencia_promedio_ordenes | facturacion_total_usd | ticket_promedio_acumulado_usd  |
+------------------------------------------+----------------+-------------------------+-----------------------+-----------------------------+-----------------------+--------------------------------+
| Clientes de Alto Valor (Champions)       |            184 |                    23.2 |                  31.8 |                         8.7 |             826546.05 |                         4492.1 |
| Clientes Recurrentes Fidelizados (Loyal) |            186 |                   23.46 |                 139.8 |                         8.1 |             654755.95 |                        3520.19 |
| Nuevos / Prometedores (Promising)        |            149 |                   18.79 |                  33.7 |                         4.4 |              329272.4 |                        2209.88 |
| En Riesgo de Abandono (At Risk)          |            134 |                    16.9 |                 212.5 |                         5.6 |             308896.25 |                         2305.2 |
| Inactivos / Hibernando (Hibernating)     |            140 |                   17.65 |                 364.7 |                         3.5 |             177730.29 |                         1269.5 |
+------------------------------------------+----------------+-------------------------+-----------------------+-----------------------------+-----------------------+--------------------------------+
5 rows selected (0.012 seconds)
```

#### 6. Interpretación Técnica
La base se distribuye de manera equilibrada entre los 793 clientes:
- **Champions y Loyal (370 clientes, 46.66%):** Aportan $1,481,302.00 USD, lo que constituye el 64.48% de la facturación global, con una recencia menor a 4 meses y tickets promedio superiores a $3,500 USD.
- **En Riesgo de Abandono (134 clientes, 16.90%):** Representan $308,896.25 USD facturados pero llevan en promedio más de 7 meses (212.5 días) sin actividad, siendo clientes de alta frecuencia previa en peligro de deserción.
- **Inactivos (140 clientes):** Promedian prácticamente un año sin comprar (364.7 días) con un ticket muy bajo ($1,269.50 USD).

#### 7. Conclusión Específica
El modelo RFM permite migrar de una gestión comercial reactiva a una proactiva: blindar con fidelización VIP al 46.7% más valioso y lanzar campañas de win-back hacia los 134 clientes en riesgo para proteger más de $300,000 USD de ingresos.

---

### Pregunta 5. Ranking de Productos según Rentabilidad

#### 1. Enunciado
Identifique los productos de mayor y menor desempeño económico. Determine: top 5 ganancia acumulada por categoría, top 5 volumen de ventas, top 5 menor rentabilidad, margen individual y posición por categoría con `RANK` y `DENSE_RANK`.

#### 2. Estrategia de Solución
Se utilizó `DENSE_RANK() OVER (PARTITION BY category ORDER BY profit DESC)` para rankear productos dentro de su categoría sin huecos en la numeración, `RANK() OVER (ORDER BY sales DESC)` para el volumen bruto global, `RANK() OVER (ORDER BY profit ASC)` para identificar las mayores pérdidas acumuladas, y `SUM(profit) OVER (PARTITION BY category ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` para calcular la ganancia acumulativa intrasectorial.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/05_ranking_productos.sql`](proyecto/sql/05_ranking_productos.sql).

```sql
WITH producto_metricas AS (
    SELECT
        product_id, product_name, category, sub_category,
        ROUND(SUM(sales), 2) AS ventas_totales,
        ROUND(SUM(profit), 2) AS ganancia_total,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS margen_rentabilidad_pct
    FROM superstore_analitica
    GROUP BY product_id, product_name, category, sub_category
),
producto_analitico AS (
    SELECT
        product_id, product_name, category, sub_category,
        ventas_totales, ganancia_total, margen_rentabilidad_pct,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY ganancia_total DESC) AS rank_ganancia_categoria,
        RANK() OVER (ORDER BY ventas_totales DESC) AS rank_ventas_global,
        RANK() OVER (ORDER BY ganancia_total ASC) AS rank_peor_rentabilidad_global,
        ROUND(SUM(ganancia_total) OVER (
            PARTITION BY category ORDER BY ganancia_total DESC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) AS ganancia_acumulada_categoria
    FROM producto_metricas
)
SELECT
    category, rank_ganancia_categoria,
    SUBSTR(product_name, 1, 45) AS producto,
    ventas_totales, ganancia_total, margen_rentabilidad_pct,
    ganancia_acumulada_categoria
FROM producto_analitico
WHERE rank_ganancia_categoria <= 3
ORDER BY category, rank_ganancia_categoria ASC;
```

#### 4. Evidencia de Ejecución
![Figura 5.1: Ranking de productos y márgenes en Beeline](evidencias/05-captura.png)

#### 5. Resultado Obtenido
```
+-----------------+-------------------------+-----------------------------------------------+----------------+----------------+-------------------------+------------------------------+
|    category     | rank_ganancia_categoria |                   producto                    | ventas_totales | ganancia_total | margen_rentabilidad_pct | ganancia_acumulada_categoria |
+-----------------+-------------------------+-----------------------------------------------+----------------+----------------+-------------------------+------------------------------+
| Furniture       |                       1 | Hon Deluxe Fabric Upholstered Stacking Chairs |       10637.53 |        1927.44 |                   18.12 |                      1927.44 |
| Furniture       |                       2 | Global Deluxe High-Back Manager's Chair       |        8665.19 |        1558.59 |                   17.99 |                      3486.03 |
| Furniture       |                       3 | Hon Pagoda Stacking Chairs                    |         6483.8 |         1540.7 |                   23.76 |                      5026.73 |
| Office Supplies |                       1 | Fellowes PB500 Electric Punch Plastic Comb Bi |       27453.38 |        7753.04 |                   28.24 |                      7753.04 |
| Office Supplies |                       2 | Hewlett Packard Desjet 9e Commercial Flow Dra |        9864.84 |        3098.41 |                   31.41 |                     10851.45 |
| Office Supplies |                       3 | Ibico EPK-21 Electric Binding System          |       15875.92 |        2827.97 |                   17.81 |                     13679.42 |
| Technology      |                       1 | Canon imageCLASS 2200 Advanced Copier         |       61599.82 |       25199.93 |                   40.91 |                     25199.93 |
| Technology      |                       2 | Hewlett-Packard Scanjet G4050 Photo Scanner   |        8039.67 |        3215.87 |                   40.00 |                      28415.8 |
| Technology      |                       3 | Ativa V4110MDD Micro-Cut Shredder             |        7699.93 |        3199.97 |                   41.56 |                     31615.77 |
+-----------------+-------------------------+-----------------------------------------------+----------------+----------------+-------------------------+------------------------------+
9 rows selected (0.011 seconds)
```

**Top 5 Ventas Globales vs Top 5 Mayores Pérdidas:**
- **Top 1 en Ventas y Ganancia:** `Canon imageCLASS 2200 Advanced Copier` ($61,599.82 en ventas, $25,199.93 en ganancia limpia, margen 40.91%).
- **Anomalía de Volumen (Top 3 Ventas Globales):** `Cisco TelePresence System EX90` facturó $22,638.48 USD pero generó **-$1,811.08 USD en pérdidas netas** (margen negativo de -8.00%).
- **Mayor Pérdida Operativa Global:** `Cubify CubeX 3D Printer Double Head` facturó $11,099.96 USD y causó **-$8,879.97 USD en pérdidas** (margen destructivo de -80.00%).

#### 6. Interpretación Técnica
Existe una brecha abismal entre facturación bruta y rendimiento neto. La fotocopiadora Canon imageCLASS 2200 es el producto más rentable de la historia del negocio. Sin embargo, productos de alto precio como equipos de videoconferencia Cisco y tecnología 3D Cubify sufren pérdidas masivas debido a costos de adquisición elevados y descuentos no controlados.

#### 7. Conclusión Específica
Se debe prohibir la aplicación de descuentos sobre las líneas Cisco TelePresence y Cubify 3D, evaluando su retiro del catálogo si no alcanzan un margen mínimo positivo del 10%.

---

### Pregunta 6. Análisis del Impacto de los Descuentos

#### 1. Enunciado
Analice la relación entre descuentos comerciales y rentabilidad en 4 rangos: Sin descuento (0%), Bajo (0-20%], Medio (20-50%] y Alto (>50%). Calcule ventas, ganancias, margen, transacciones con pérdida, % no rentables, descuento promedio y categorías afectadas.

#### 2. Estrategia de Solución
Se categorizaron las 9,994 filas en 4 estratos mediante `CASE WHEN`. Se calcularon las sumas de ventas y ganancias, el margen porcentual y el indicador de morbilidad financiera `COUNT(CASE WHEN profit < 0 THEN 1 END) * 100.0 / COUNT(*)`. Un segundo desglose agrupó por categoría y subcategoría para aislar los focos de mayor pérdida.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/06_impacto_descuentos.sql`](proyecto/sql/06_impacto_descuentos.sql).

```sql
WITH transacciones_clasificadas AS (
    SELECT
        row_id, category, sub_category, sales, discount, profit,
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
```

#### 4. Evidencia de Ejecución
![Figura 6.1: Evaluación de impacto de descuentos en Beeline](evidencias/06-captura.png)

#### 5. Resultado Obtenido
```
+--------------------------------+---------------------+--------------------+--------------------+-------------------------+-----------------------+------------------------------+------------------------+
|        rango_descuento         | total_transacciones | ventas_totales_usd | ganancia_total_usd | margen_rentabilidad_pct | registros_con_perdidas| pct_operaciones_no_rentables | descuento_promedio_pct |
+--------------------------------+---------------------+--------------------+--------------------+-------------------------+-----------------------+------------------------------+------------------------+
| 1. Sin descuento (0%)          |                4798 |         1087908.47 |           320987.6 |                   29.51 |                   0.0 |                          0.0 |                    0.0 |
| 2. Descuento bajo (0% - 20%]   |                3803 |          846522.24 |          100785.47 |                   11.91 |                 523.0 |                        13.75 |                  19.68 |
| 3. Descuento medio (20% - 50%] |                 537 |          298541.41 |           -58817.0 |                   -19.7 |                 492.0 |                        91.62 |                   36.7 |
| 4. Descuento alto (> 50%)      |                 856 |           64228.74 |          -76559.05 |                  -119.2 |                 856.0 |                        100.0 |                  71.89 |
+--------------------------------+---------------------+--------------------+--------------------+-------------------------+-----------------------+------------------------------+------------------------+
4 rows selected (0.010 seconds)
```

**Subcategorías Más Afectadas con Descuentos > 20%:**
1. **Binders (Office Supplies):** Pérdida neta de **-$38,510.50 USD** (100.00% operaciones con pérdida, margen -106.56%).
2. **Tables (Furniture):** Pérdida neta de **-$30,698.22 USD** (97.73% operaciones con pérdida, margen -34.13%).
3. **Machines (Technology):** Pérdida neta de **-$29,555.35 USD** (83.02% operaciones con pérdida, margen -38.46%).

#### 6. Interpretación Técnica
Los datos demuestran una relación causal inversamente proporcional y destructiva entre descuento y beneficio:
- **0% de descuento:** Margen óptimo del +29.51%, 0 operaciones con pérdida.
- **Descuentos de 0% a 20%:** Margen del +11.91%, solo 13.75% de pérdidas tolerables.
- **Descuentos de 20% a 50%:** El margen se desploma a -19.70% y el **91.62% de las ventas son a pérdida**.
- **Descuentos > 50%:** El margen colapsa a **-119.20% y el 100.00% de las ventas son no rentables** (cada venta pierde más dinero del que ingresa).

#### 7. Conclusión Específica
Los descuentos superiores al 20% destruyen el modelo de negocio. Se debe implementar una política de precios dura en el sistema ERP que bloquee cualquier descuento mayor al 20% sin aprobación expresa de la Gerencia Financiera.

---

### Pregunta 7. Análisis de Tendencias Temporales

#### 1. Enunciado
Construya un análisis de evolución mensual de ventas y ganancias (YYYY-MM). Debe incluir: variación mensual respecto al mes anterior (MoM), comparación con el mismo mes del año anterior (YoY), promedio móvil de tres meses y top 3 mejores y peores meses de ventas.

#### 2. Estrategia de Solución
Se agregó la serie continua de 48 meses utilizando `DATE_FORMAT(order_date, 'yyyy-MM')`. Se calcularon las diferencias relativas mediante `LAG(ventas, 1)` para la variación intermensual y `LAG(ventas, 12)` para la comparación interanual de estacionalidad. La media móvil trimestral se obtuvo mediante `AVG(ventas) OVER (ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/07_tendencias_temporales.sql`](proyecto/sql/07_tendencias_temporales.sql).

```sql
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
        anio_mes, ventas_mes, ganancia_mes,
        ROUND((ganancia_mes / ventas_mes) * 100, 2) AS margen_mes_pct,
        LAG(ventas_mes, 1) OVER (ORDER BY anio_mes) AS ventas_mes_anterior,
        ROUND(((ventas_mes - LAG(ventas_mes, 1) OVER (ORDER BY anio_mes)) 
             / LAG(ventas_mes, 1) OVER (ORDER BY anio_mes)) * 100, 2) AS variacion_mom_pct,
        LAG(ventas_mes, 12) OVER (ORDER BY anio_mes) AS ventas_mismo_mes_anio_anterior,
        ROUND(((ventas_mes - LAG(ventas_mes, 12) OVER (ORDER BY anio_mes)) 
             / LAG(ventas_mes, 12) OVER (ORDER BY anio_mes)) * 100, 2) AS variacion_yoy_pct,
        ROUND(AVG(ventas_mes) OVER (ORDER BY anio_mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS promedio_movil_3_meses,
        DENSE_RANK() OVER (ORDER BY ventas_mes DESC) AS rank_pico_ventas,
        DENSE_RANK() OVER (ORDER BY ventas_mes ASC) AS rank_valle_ventas
    FROM serie_mensual
)
SELECT
    anio_mes, ventas_mes, ganancia_mes, margen_mes_pct,
    COALESCE(CAST(variacion_mom_pct AS STRING), 'N/A') AS var_mom_pct,
    COALESCE(CAST(variacion_yoy_pct AS STRING), 'N/A') AS var_yoy_pct,
    promedio_movil_3_meses,
    CASE
        WHEN rank_pico_ventas <= 3 THEN CONCAT('Pico: Top ', CAST(rank_pico_ventas AS STRING))
        WHEN rank_valle_ventas <= 3 THEN CONCAT('Valle: Top ', CAST(rank_valle_ventas AS STRING))
        ELSE 'Normal'
    END AS clasificacion_temporal
FROM metricas_temporales
ORDER BY anio_mes ASC;
```

#### 4. Evidencia de Ejecución
![Figura 7.1: Análisis de serie temporal mensual en Beeline](evidencias/07-captura.png)

#### 5. Resultado Obtenido
**Top 3 Meses Históricos de Mayor Venta (Picos):**
1. **2017-11 (Noviembre 2017):** $118,447.81 USD en ventas | $9,690.08 USD ganancia | +52.29% MoM | +49.16% YoY | Media móvil 3M: $94,697.14 USD.
2. **2016-12 (Diciembre 2016):** $96,999.07 USD en ventas | $17,885.29 USD ganancia | +22.15% MoM | +29.47% YoY | Media móvil 3M: $78,699.63 USD.
3. **2017-09 (Septiembre 2017):** $87,866.66 USD en ventas | $10,991.56 USD ganancia | +39.20% MoM | +19.69% YoY | Media móvil 3M: $65,417.31 USD.

**Top 3 Meses Históricos de Menor Venta (Valles):**
1. **2014-02 (Febrero 2014):** $4,519.89 USD en ventas | $862.31 USD ganancia (Mínimo histórico absoluto de inicio).
2. **2015-02 (Febrero 2015):** $11,951.41 USD en ventas | $2,813.85 USD ganancia (-34.24% MoM).
3. **2014-01 (Enero 2014):** $14,236.89 USD en ventas | $2,450.19 USD ganancia.

#### 6. Interpretación Técnica
La serie temporal describe una marcada estacionalidad cíclica anual. Todos los años experimentan una contracción severa en el primer bimestre (enero-febrero), un repunte en marzo y septiembre (regreso a clases y cierre fiscal corporativo de Q3), culminando en un auge explosivo durante el cuarto trimestre (Q4) gracias al Black Friday, Cyber Monday y compras navideñas.

#### 7. Conclusión Específica
La empresa debe sincronizar su cadena de suministro con el calendario comercial: aprovisionar inventarios clave entre agosto y octubre para suplir la demanda masiva de fin de año, y planificar ajustes operativos en enero y febrero para compensar los valles estacionales.

---

### Pregunta 8. Análisis Pareto 80/20 de Ventas y Rentabilidad

#### 1. Enunciado
Aplique la regla 80/20 de Pareto para identificar la concentración comercial en dos análisis independientes: qué cantidad de productos representa el 80% de ventas acumuladas y el 80% de ganancias acumuladas. Ordene de mayor a menor contribución, calcule porcentajes y compare resultados.

#### 2. Estrategia de Solución
Se agregaron ventas y beneficios por producto (`product_id`). Mediante funciones analíticas de ventana se calcularon las sumas acumulativas ordenadas descendentemente:
- `SUM(ventas) OVER (ORDER BY ventas DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / total_ventas`.
- `SUM(ganancia) OVER (ORDER BY ganancia DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / total_ganancias_positivas`.
Posteriormente se filtraron y cuantificaron los productos necesarios para alcanzar el 80.00% del valor acumulado.

#### 3. Consulta HiveQL Desarrollada
Ver script completo en [`proyecto/sql/08_analisis_pareto.sql`](proyecto/sql/08_analisis_pareto.sql).

```sql
WITH producto_totales AS (
    SELECT
        product_id, product_name, category, sub_category,
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
        p.product_id, p.product_name, p.ventas_producto,
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
        p.product_id, p.product_name, p.ganancia_producto,
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
```

#### 4. Evidencia de Ejecución
![Figura 8.1: Comparativa Pareto 80/20 en Beeline](evidencias/08-captura.png)

#### 5. Resultado Obtenido
```
+------------------------------------+------------------------------+-------------------------+--------------------------------------+
| dimension_analisis                 | cantidad_articulos_umbral_80 | universo_total_catalogo | porcentaje_catalogo_representado_pct |
+------------------------------------+------------------------------+-------------------------+--------------------------------------+
| Pareto de Ventas (80% Facturación) |                          423 |                    1894 |                                22.33 |
| Pareto de Ganancias (80% Utilidad) |                          347 |                    1894 |                                18.32 |
+------------------------------------+------------------------------+-------------------------+--------------------------------------+
2 rows selected (0.015 seconds)
```

#### 6. Interpretación Técnica
El dataset confirma la regla empírica 80/20 con una exactitud asombrosa:
- **Concentración de Facturación:** 423 productos (el 22.33% del catálogo) generan el 80% de todas las ventas corporativas ($1.83 millones USD).
- **Concentración de Utilidad Líquida:** Apenas 347 productos (el 18.32% del inventario) concentran el 80% de toda la ganancia positiva ($352,000 USD).

**Explicación de las Diferencias Encontradas:**
El análisis revela una divergencia cualitativa crítica: se necesitan 76 productos menos para generar el 80% de la utilidad que para generar el 80% de las ventas. Esto se debe a que varios productos con altísimo volumen facturado (ej. sistemas de videoconferencia o impresoras láser) tienen márgenes destruidos por descuentos y quedan excluidos del Pareto de ganancia, mientras que productos de menor precio pero alto margen neto (artículos de papelería especializada, copiadoras y suministros premium) impulsan silenciosamente la rentabilidad corporativa.

#### 7. Conclusión Específica
La empresa debe implementar un modelo de clasificación de inventarios ABC estricto: proteger a ultranza el inventario del 18.3% de productos que generan el 80% de la ganancia, y recortar o renegociar el 81.7% restante que absorbe costos de bodega sin generar valor.

---

## 6. Análisis Técnico de Optimización en Apache Hive

El procesamiento de volúmenes masivos en Apache Hive exige optimizaciones a nivel de I/O, almacenamiento columnar y ejecución distribuida. En el script [`proyecto/sql/optimizacion_hive.sql`](proyecto/sql/optimizacion_hive.sql) se implementaron las siguientes técnicas:

1. **Particionamiento Dinámico (`PARTITIONED BY (region STRING)`):**
   - Divide la estructura física del almacenamiento en HDFS en subdirectorios por región (`/warehouse/superstore_optimizada/region=West`).
   - Al filtrar por `WHERE region = 'West'`, Hive realiza **Partition Pruning**, leyendo únicamente los bloques asociados y omitiendo el 75% del dataset restante.

2. **Bucketing / Clustering por Hash (`CLUSTERED BY (customer_id) INTO 4 BUCKETS`):**
   - Distribuye las filas de cada partición en 4 archivos balanceados calculando una función hash sobre `customer_id`.
   - Permite que las uniones con tablas de clientes se ejecuten mediante **Bucket Map Joins** o **Sort-Merge-Bucket (SMB) Joins**, eliminando la fase de barajado (Shuffle) en red.

3. **Almacenamiento Columnar ORC con Compresión Snappy:**
   - Agrupa datos por columnas con compresión basada en diccionario, bit packing y RLE (Run Length Encoding).
   - Incorpora índices ligeros Min/Max cada 10,000 filas (Row Index Stride), permitiendo el salto de bloques enteros de datos que no cumplen el predicado.

4. **Ejecución Vectorizada de Consultas (`hive.vectorized.execution.enabled=true`):**
   - En lugar de iterar fila por fila en la JVM, el motor procesa lotes contiguos de 1,024 valores en la memoria caché L1/L2 de la CPU mediante instrucciones SIMD.

5. **Optimizador Basado en Costos (CBO con Apache Calcite):**
   - Habilitado mediante `hive.cbo.enable=true` y estadísticas recolectadas con `ANALYZE TABLE ... COMPUTE STATISTICS`.
   - Calcite reordena dinámicamente los árboles de ejecución, estima la cardinalidad intermedia y convierte uniones pesadas en **MapJoins** (Broadcast en RAM).

---

## 7. Conclusiones Generales del Examen

1. **Integridad del Pipeline de Datos:** Se implementó exitosamente una arquitectura Big Data en dos capas (Raw Staging y Analytics ORC) sobre Apache Hive, garantizando un almacenamiento eficiente y tipos de datos normalizados para 9,994 transacciones.
2. **Capacidad Diagnóstica de la Calidad de Datos:** La auditoría demostró una estructura de datos limpia pero reveló un riesgo financiero sustancial: 1,871 operaciones con pérdida causadas por falta de límites comerciales.
3. **Poder Analítico de HiveQL:** El uso riguroso de CTEs y funciones analíticas de ventana (`LAG`, `RANK`, `DENSE_RANK`, `NTILE`, `SUM() OVER`) permitió resolver problemas de segmentación avanzada (RFM), series temporales de 48 meses y rankings comerciales en pocas líneas de código optimizado.
4. **Validación de la Regla de Pareto:** Se verificó matemáticamente el Principio 80/20: el 22.33% de los productos factura el 80% de las ventas, mientras que un selecto 18.32% genera el 80% de las utilidades líquidas de la empresa.
5. **Impacto Financiero de los Descuentos:** Se demostró cuantitativamente que los descuentos superiores al 20% provocan que más del 91% de las transacciones operen a pérdida, lo que exige fijar políticas corporativas restrictivas en los sistemas transaccionales.

---

## 8. Entregables Disponibles en este Repositorio

- **Documento PDF Oficial:** [`informe/Informe_Examen2M_Ronald_Saavedra.pdf`](informe/Informe_Examen2M_Ronald_Saavedra.pdf)
- **Diccionario de Datos:** [`DICCIONARIO_DATOS.md`](DICCIONARIO_DATOS.md) y [`datos/metadata.json`](datos/metadata.json)
- **Scripts HiveQL Oficiales:** [`proyecto/sql/`](proyecto/sql/) (10 scripts SQL DDL, DML, Consultas y Optimización)
- **Configuración de Clúster Docker:** [`proyecto/compose.yaml`](proyecto/compose.yaml) y [`proyecto/config/`](proyecto/config/)
- **Motor Standalone sin Docker:** [`scripts/ejecutor_hiveql_local.py`](scripts/ejecutor_hiveql_local.py)
- **Capturas y Evidencias de Terminal:** [`evidencias/`](evidencias/) (16 capturas PNG en alta resolución)
- **Registros y Logs Brutos:** [`registros/`](registros/) (8 archivos JSON y 8 logs de terminal Beeline)
