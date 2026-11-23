#!/bin/bash
# Genera un respaldo lógico de la base "inventario" en ~/respaldos
set -e
cd "$(dirname "$0")"
mkdir -p ~/respaldos
ARCHIVO=~/respaldos/inventario_$(date +%F_%H%M).sql
docker compose exec -T db sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --databases inventario' > "$ARCHIVO"
echo "Respaldo creado: $ARCHIVO"
