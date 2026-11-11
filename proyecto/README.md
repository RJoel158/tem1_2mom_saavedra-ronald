# Infraestructura y Despliegue del Clúster Apache Hive
**Laboratorio / Examen 2do Momento — Tecnologías Emergentes I**  
**Autor:** Ronald Joel Saavedra Vargas  
**Universidad Privada del Valle**  

Este directorio contiene los archivos de configuración declarativa para desplegar un clúster distribuido contenerizado en **Docker**, así como los scripts SQL necesarios para ejecutar el ciclo analítico en Apache Hive.

---

## 1. Servicios del Clúster Contenerizado

| Servicio | Contenedor | Imagen Base | Puerto Host | Descripción |
| :--- | :--- | :--- | :---: | :--- |
| **Hadoop NameNode** | `superstore-namenode` | `apache/hadoop:3.4.1` | `9870` | Administración de metadatos HDFS y Web UI |
| **Hadoop DataNode** | `superstore-datanode` | `apache/hadoop:3.4.1` | - | Almacenamiento distribuido de bloques |
| **Hive Metastore** | `superstore-hive-metastore` | `apache/hive:4.0.1` | `9083` | Catálogo relacional de esquemas (Derby) |
| **HiveServer2** | `superstore-hive-server` | `apache/hive:4.0.1` | `10000`, `10002` | Servidor JDBC/ODBC Beeline y Consola Web |

---

## 2. Instrucciones de Ejecución

### Opción A: Despliegue con Docker (En equipos con soporte Docker)
```bash
# 1. Levantar el cluster
docker compose up -d

# 2. Conectar a Beeline
docker exec -it superstore-hive-server beeline -u "jdbc:hive2://localhost:10000/default" -n hive -p hive

# 3. Ejecutar consultas
!run /data/sql/01_ddl_diseno_modelo.sql
!run /data/sql/01_carga_datos.sql
!run /data/sql/02_auditoria_calidad.sql
```

### Opción B: Ejecución Standalone sin Docker (En este equipo local)
Para equipos sin virtualización o sin Docker instalado, se incluye el motor standalone en `scripts/ejecutor_hiveql_local.py`:
```powershell
python scripts/ejecutor_hiveql_local.py
```
Dicho script ejecuta las consultas exactas HiveQL mediante un motor relacional embebido compatible con ANSI SQL y funciones de ventana, registrando logs en `registros/` y evidencias en `evidencias/`.
