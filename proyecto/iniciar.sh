#!/usr/bin/env bash
# ==============================================================================
# Script de inicio y orquestacion del cluster Hadoop / Hive para Docker
# ==============================================================================
set -e

echo "[1/4] Iniciando contenedores Docker..."
docker compose up -d

echo "[2/4] Esperando inicializacion de servicios..."
sleep 15

echo "[3/4] Creando directorios HDFS y transfiriendo dataset..."
docker exec -it superstore-namenode hdfs dfs -mkdir -p /data/superstore/raw /user/hive/warehouse
docker cp ../datos/superstore.csv superstore-namenode:/tmp/superstore.csv
docker exec -it superstore-namenode hdfs dfs -put -f /tmp/superstore.csv /data/superstore/raw/

echo "[4/4] Clúster operativo y datos cargados exitosamente."
echo "NameNode Web UI:  http://localhost:9870"
echo "HiveServer2 JDBC: localhost:10000"
