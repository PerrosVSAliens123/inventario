"""
Sistema de Inventario Tecnológico - Servidores II (UNISON)
Aplicación Flask que registra, consulta, edita y elimina equipos en MySQL.
Incluye inicio de sesión con dos roles: administrador (control total)
y lector (solo consulta). La configuración se lee de variables de entorno (.env).
"""
import hmac
import os
import re
import socket
from functools import wraps

import pymysql
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "servidores-ii"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CAMPOS = ["nombre", "tipo", "marca", "numero_serie", "ubicacion", "estado"]

# Rol -> variable de entorno donde vive su contraseña (nunca en el código)
CLAVES = {"admin": "ADMIN_PASSWORD", "lector": "VIEWER_PASSWORD"}
RUTAS_PUBLICAS = {"login", "salud", "static"}


def conectar():
    """Abre una conexión con MySQL usando el nombre del servicio (db)."""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "app_inventario"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "inventario"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )


def opciones_enum(columna):
    """Lee los valores permitidos de una columna ENUM definida en init.sql.
    Así, los tipos y estados se adaptan editando solo el script SQL."""
    with conectar() as cx, cx.cursor() as cur:
        cur.execute(
            "SELECT COLUMN_TYPE FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'equipos' AND COLUMN_NAME = %s",
            (columna,),
        )
        fila = cur.fetchone()
    definicion = fila["COLUMN_TYPE"] if fila else "enum()"
    return [v.replace("''", "'") for v in re.findall(r"'((?:[^']|'')*)'", definicion)]


@app.context_processor
def datos_servidor():
    """Muestra la organización, el contenedor que atendió y el rol activo."""
    return {"contenedor": socket.gethostname(), "db_host": os.getenv("DB_HOST", "db"),
            "organizacion": os.getenv("ORGANIZACION", "Universidad de Sonora"),
            "rol": session.get("rol"), "es_admin": session.get("rol") == "admin"}


@app.before_request
def exigir_sesion():
    """Todo requiere sesión, salvo /login, /salud (la usa Jenkins) y los estáticos."""
    if request.endpoint in RUTAS_PUBLICAS:
        return None
    if session.get("rol") not in CLAVES:
        return redirect(url_for("login"))
    return None


def solo_admin(vista):
    """Protege en el servidor las rutas que modifican datos."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("Tu perfil es de solo lectura: no tienes permiso para esa acción.", "error")
            return redirect(url_for("inicio"))
        return vista(*args, **kwargs)
    return envoltura


@app.errorhandler(pymysql.err.OperationalError)
def error_bd(error):
    return render_template("error.html", detalle=str(error)), 503


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("rol") in CLAVES:
        return redirect(url_for("inicio"))
    if request.method == "POST":
        rol = request.form.get("rol", "")
        clave = request.form.get("clave", "")
        esperada = os.getenv(CLAVES[rol], "") if rol in CLAVES else ""
        if esperada and hmac.compare_digest(clave.encode(), esperada.encode()):
            session.clear()
            session["rol"] = rol
            flash("Sesión iniciada correctamente.", "ok")
            return redirect(url_for("inicio"))
        flash("Contraseña incorrecta.", "error")
    return render_template("login.html")


@app.route("/salir")
def salir():
    session.clear()
    flash("Sesión cerrada.", "ok")
    return redirect(url_for("login"))


@app.route("/")
def inicio():
    with conectar() as cx, cx.cursor() as cur:
        cur.execute("SELECT * FROM equipos ORDER BY id")
        equipos = cur.fetchall()
    return render_template("index.html", equipos=equipos)


def leer_formulario():
    datos = {campo: request.form.get(campo, "").strip() for campo in CAMPOS}
    faltantes = [c for c, v in datos.items() if not v]
    return datos, faltantes


@app.route("/nuevo", methods=["GET", "POST"])
@solo_admin
def nuevo():
    if request.method == "POST":
        datos, faltantes = leer_formulario()
        if faltantes:
            flash("Todos los campos son obligatorios.", "error")
            return render_template("formulario.html", equipo=datos, tipos=opciones_enum("tipo"), estados=opciones_enum("estado"), titulo="Registrar equipo")
        try:
            with conectar() as cx, cx.cursor() as cur:
                cur.execute(
                    "INSERT INTO equipos (nombre, tipo, marca, numero_serie, ubicacion, estado) "
                    "VALUES (%(nombre)s, %(tipo)s, %(marca)s, %(numero_serie)s, %(ubicacion)s, %(estado)s)",
                    datos,
                )
                cx.commit()
        except pymysql.err.IntegrityError:
            flash("Ya existe un equipo con ese número de serie.", "error")
            return render_template("formulario.html", equipo=datos, tipos=opciones_enum("tipo"), estados=opciones_enum("estado"), titulo="Registrar equipo")
        flash("Equipo registrado correctamente.", "ok")
        return redirect(url_for("inicio"))
    return render_template("formulario.html", equipo={}, tipos=opciones_enum("tipo"), estados=opciones_enum("estado"), titulo="Registrar equipo")


@app.route("/editar/<int:id_equipo>", methods=["GET", "POST"])
@solo_admin
def editar(id_equipo):
    if request.method == "POST":
        datos, faltantes = leer_formulario()
        datos["id"] = id_equipo
        if faltantes:
            flash("Todos los campos son obligatorios.", "error")
            return render_template("formulario.html", equipo=datos, tipos=opciones_enum("tipo"), estados=opciones_enum("estado"), titulo="Editar equipo")
        try:
            with conectar() as cx, cx.cursor() as cur:
                cur.execute(
                    "UPDATE equipos SET nombre=%(nombre)s, tipo=%(tipo)s, marca=%(marca)s, "
                    "numero_serie=%(numero_serie)s, ubicacion=%(ubicacion)s, estado=%(estado)s WHERE id=%(id)s",
                    datos,
                )
                cx.commit()
        except pymysql.err.IntegrityError:
            flash("Ya existe un equipo con ese número de serie.", "error")
            return render_template("formulario.html", equipo=datos, tipos=opciones_enum("tipo"), estados=opciones_enum("estado"), titulo="Editar equipo")
        flash("Equipo actualizado.", "ok")
        return redirect(url_for("inicio"))
    with conectar() as cx, cx.cursor() as cur:
        cur.execute("SELECT * FROM equipos WHERE id=%s", (id_equipo,))
        equipo = cur.fetchone()
    if not equipo:
        flash("El equipo no existe.", "error")
        return redirect(url_for("inicio"))
    return render_template("formulario.html", equipo=equipo, tipos=opciones_enum("tipo"), estados=opciones_enum("estado"), titulo="Editar equipo")


@app.route("/eliminar/<int:id_equipo>", methods=["POST"])
@solo_admin
def eliminar(id_equipo):
    with conectar() as cx, cx.cursor() as cur:
        cur.execute("DELETE FROM equipos WHERE id=%s", (id_equipo,))
        cx.commit()
    flash("Equipo eliminado.", "ok")
    return redirect(url_for("inicio"))


@app.route("/salud")
def salud():
    """Punto de verificación usado en las prácticas de automatización y respaldo (público)."""
    try:
        with conectar() as cx, cx.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM equipos")
            total = cur.fetchone()["total"]
        return jsonify(estado="ok", base_de_datos="conectada", equipos=total)
    except pymysql.err.MySQLError as e:
        return jsonify(estado="error", base_de_datos="sin conexión", detalle=str(e)), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
