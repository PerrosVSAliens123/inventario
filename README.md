# Sistema de Inventario Tecnológico

Organización: Preparatoria Cobach (datos de ejemplo ficticios)

Equipo 4, Servidores II, Universidad de Sonora. Autor: Diego Leyva Mendoza

## Requisitos

Ubuntu Server con Docker, Docker Compose y Git.

## Recrear el sistema desde cero

1. Clonar el repositorio: `git clone https://github.com/PerrosVSAliens123/inventario.git` y entrar con `cd inventario`
2. Crear el archivo de variables: `cp .env.example .env` y editar `.env` con contraseñas propias (`nano .env`)
3. Levantar los servicios: `docker compose up -d` (la primera vez descarga imágenes y crea la base con `db/init.sql`)
4. Verificar: `docker compose ps` (db debe estar healthy) y `curl http://localhost/salud`
5. Abrir en el navegador `http://IP-DEL-SERVIDOR`

## Respaldo y recuperación

- Generar respaldo: `./respaldar.sh` (queda en `~/respaldos`)
- Restaurar: `docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD"' < ~/respaldos/inventario_FECHA.sql`

## Componentes

- Imagen de la aplicación: `diegoleyva/inventario-app:1.0` (Docker Hub)
- Validación automática: `Jenkinsfile` (Jenkins)
- El archivo `.env` real nunca se sube al repositorio
