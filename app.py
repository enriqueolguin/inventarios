"""
============================================================
 NeumoCRUD v2 — Registro de Equipos de Cómputo
 Flask + PyMySQL + Flask-Login (roles y permisos RBAC)
============================================================
"""
import csv
import hmac
import io
import os
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
import pymysql
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    Response, send_file, session, abort,
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------------------------------------------
# Configuración
# ----------------------------------------------------------
load_dotenv()

app = Flask(__name__)

# Clave de sesión: se toma de .env; si no existe, se genera aleatoria.
# (Con clave aleatoria las sesiones se invalidan al reiniciar el servidor.)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Cookies de sesión endurecidas
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,    # el JS del navegador no puede leer la cookie
    SESSION_COOKIE_SAMESITE="Lax",   # mitiga CSRF básico entre sitios
    SESSION_COOKIE_SECURE=False,     # cambiar a True si se sirve por HTTPS
    PERMANENT_SESSION_LIFETIME=3600, # la sesión dura 1 hora
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"          # redirige aquí si no hay sesión
login_manager.login_message = "Inicia sesión para acceder al sistema."
login_manager.login_message_category = "error"


# ----------------------------------------------------------
# Protección CSRF: token por sesión validado en todo POST
# ----------------------------------------------------------
def csrf_token():
    """Devuelve el token CSRF de la sesión (lo crea si no existe)."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def verificar_csrf():
    """Rechaza cualquier POST sin token CSRF válido."""
    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        esperado = session.get("_csrf_token", "")
        if not token or not hmac.compare_digest(token, esperado):
            abort(400, "Token CSRF inválido o ausente.")


# Límite de intentos de login (anti fuerza bruta), en memoria
intentos_login = defaultdict(deque)


# ----------------------------------------------------------
# Conexión a MySQL
# ----------------------------------------------------------
def get_db_connection():
    """Abre y devuelve una conexión a la base de datos MySQL."""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registro_equipos"),
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
    )


def db_query(sql, params=(), one=False):
    """Ejecuta un SELECT y devuelve filas (dict) o una fila."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone() if one else cursor.fetchall()
    finally:
        conn.close()


def db_execute(sql, params=()):
    """Ejecuta INSERT/UPDATE/DELETE con commit y devuelve lastrowid."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            new_id = cursor.lastrowid
        conn.commit()
        return new_id
    finally:
        conn.close()


def registrar_bitacora(accion, detalle=None, username=None, usuario_id=None):
    """Registra una acción en la bitácora."""
    uid = usuario_id if usuario_id is not None else (
        current_user.id if current_user.is_authenticated else None
    )
    uname = username or (
        current_user.username if current_user.is_authenticated else "anonimo"
    )
    db_execute(
        "INSERT INTO bitacora (usuario_id, username, accion, detalle) "
        "VALUES (%s, %s, %s, %s)",
        (uid, uname, accion, detalle),
    )


# ----------------------------------------------------------
# Modelo de usuario (Flask-Login)
# ----------------------------------------------------------
class Usuario(UserMixin):
    def __init__(self, fila):
        self.id = str(fila["id"])
        self.nombre = fila["nombre"]
        self.username = fila["username"]
        self.email = fila.get("email")
        self.rol_id = fila["rol_id"]
        self.rol_nombre = fila["rol_nombre"]
        self.activo = bool(fila["activo"])
        # Conjunto de claves de permiso del rol, ej: {"equipos.crear", ...}
        self.permisos = set(fila["permisos"].split(",")) if fila.get("permisos") else set()

    def puede(self, permiso):
        return permiso in self.permisos


@login_manager.user_loader
def cargar_usuario(user_id):
    fila = db_query(
        """
        SELECT u.*, r.nombre AS rol_nombre,
               GROUP_CONCAT(p.clave) AS permisos
        FROM usuarios u
        JOIN roles r ON r.id = u.rol_id
        LEFT JOIN roles_permisos rp ON rp.rol_id = r.id
        LEFT JOIN permisos p ON p.id = rp.permiso_id
        WHERE u.id = %s
        GROUP BY u.id
        """,
        (user_id,),
        one=True,
    )
    return Usuario(fila) if fila else None


# ----------------------------------------------------------
# Decoradores
# ----------------------------------------------------------
def permiso_requerido(permiso):
    """Protege una ruta: exige sesión + permiso específico."""
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envuelto(*args, **kwargs):
            if not current_user.puede(permiso):
                flash("No tienes permisos para realizar esa acción.", "error")
                return redirect(url_for("index"))
            return vista(*args, **kwargs)
        return envuelto
    return decorador


# ----------------------------------------------------------
# Contexto global para plantillas
# ----------------------------------------------------------
@app.context_processor
def inyectar_usuario():
    """Expone current_user/permisos en todas las plantillas."""
    return {
        "puede": current_user.puede if current_user.is_authenticated else (lambda p: False),
        "now": datetime.now(),
    }


@app.template_filter("badges")
def badge_class(estado):
    """Clase CSS según el estado del equipo."""
    return {
        "Nuevo": "badge-nuevo",
        "Bueno": "badge-bueno",
        "Regular": "badge-regular",
        "En reparación": "badge-reparacion",
        "Dado de baja": "badge-baja",
    }.get(estado, "badge-bueno")


@app.template_filter("tipos")
def icono_tipo(tipo):
    """Emoji según el tipo de equipo."""
    return {
        "Laptop": "💻",
        "Desktop": "🖥️",
        "Servidor": "🗄️",
        "All-in-One": "🖥️",
        "Tablet": "📱",
        "Otro": "🖨️",
    }.get(tipo, "💻")


# ==========================================================
# AUTENTICACIÓN
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Inicio de sesión. Sin registro público: solo usuarios de la BD."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Anti fuerza bruta: máx. 5 intentos fallidos por minuto y usuario
        clave = username.lower()
        ahora = time.time()
        intentos = intentos_login[clave]
        while intentos and ahora - intentos[0] > 60:
            intentos.popleft()
        if len(intentos) >= 5:
            flash("Demasiados intentos. Espera un minuto e inténtalo de nuevo.", "error")
            return render_template("login.html"), 429

        fila = db_query(
            """
            SELECT u.*, r.nombre AS rol_nombre,
                   GROUP_CONCAT(p.clave) AS permisos
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            LEFT JOIN roles_permisos rp ON rp.rol_id = r.id
            LEFT JOIN permisos p ON p.id = rp.permiso_id
            WHERE u.username = %s
            GROUP BY u.id
            """,
            (username,),
            one=True,
        )

        if fila is None or not check_password_hash(fila["password_hash"], password):
            intentos.append(ahora)
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("login.html"), 401

        if not fila["activo"]:
            intentos.append(ahora)
            flash("Tu cuenta está desactivada. Contacta al administrador.", "error")
            return render_template("login.html"), 403

        intentos_login.pop(clave, None)
        usuario = Usuario(fila)
        login_user(usuario)

        db_execute(
            "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s",
            (usuario.id,),
        )
        registrar_bitacora(
            "inicio_sesion", "Acceso al sistema", username=usuario.username
        )
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    registrar_bitacora("cierre_sesion", "Salió del sistema")
    logout_user()
    flash("Sesión cerrada correctamente.", "exito")
    return redirect(url_for("login"))


@app.route("/cambiar-password", methods=["GET", "POST"])
@login_required
def cambiar_password():
    """Cambio de contraseña propia (todos los roles)."""
    if request.method == "POST":
        actual = request.form.get("password_actual", "")
        nueva = request.form.get("password_nueva", "")
        confirma = request.form.get("password_confirmar", "")

        fila = db_query(
            "SELECT password_hash FROM usuarios WHERE id = %s",
            (current_user.id,),
            one=True,
        )
        if not check_password_hash(fila["password_hash"], actual):
            flash("La contraseña actual no es correcta.", "error")
        elif len(nueva) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "error")
        elif nueva != confirma:
            flash("La confirmación no coincide con la nueva contraseña.", "error")
        else:
            db_execute(
                "UPDATE usuarios SET password_hash = %s WHERE id = %s",
                (generate_password_hash(nueva), current_user.id),
            )
            registrar_bitacora("cambio_password", "Cambió su propia contraseña")
            flash("Contraseña actualizada correctamente.", "exito")
            return redirect(url_for("index"))

    return render_template("cambiar_password.html")


# ==========================================================
# INVENTARIO (equipos)
# ==========================================================
@app.route("/")
@login_required
def index():
    """Lista todos los equipos (READ)."""
    equipos = db_query("SELECT * FROM equipos ORDER BY updated_at DESC, id DESC")
    return render_template("index.html", equipos=equipos)


def validar_formulario(form):
    """Valida los campos del formulario. Devuelve (errores, datos)."""
    errores = []
    campos_obligatorios = {
        "nombre_equipo": "El nombre del equipo es obligatorio.",
        "marca": "La marca es obligatoria.",
        "modelo": "El modelo es obligatorio.",
        "numero_serie": "El número de serie es obligatorio.",
        "tipo": "El tipo de equipo es obligatorio.",
        "procesador": "El procesador es obligatorio.",
        "ubicacion": "La ubicación es obligatoria.",
        "responsable": "El responsable es obligatorio.",
    }
    datos = {}
    for campo, mensaje in campos_obligatorios.items():
        valor = form.get(campo, "").strip()
        if not valor:
            errores.append(mensaje)
        datos[campo] = valor

    ram = form.get("ram_gb", "").strip()
    if not ram:
        errores.append("La RAM (GB) es obligatoria.")
    else:
        try:
            ram = int(ram)
            if not (1 <= ram <= 1024):
                errores.append("La RAM debe estar entre 1 y 1024 GB.")
        except ValueError:
            errores.append("La RAM debe ser un número entero (GB).")
    datos["ram_gb"] = ram

    datos["almacenamiento"] = form.get("almacenamiento", "").strip()
    datos["sistema_operativo"] = form.get("sistema_operativo", "").strip()
    datos["estado"] = form.get("estado", "Nuevo").strip() or "Nuevo"
    datos["observaciones"] = form.get("observaciones", "").strip() or None

    return errores, datos


@app.route("/crear", methods=["GET", "POST"])
@permiso_requerido("equipos.crear")
def crear():
    """Muestra el formulario y crea un equipo (CREATE)."""
    if request.method == "POST":
        errores, datos = validar_formulario(request.form)

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("form.html", equipo=request.form, modo="crear")

        try:
            new_id = db_execute(
                """
                INSERT INTO equipos
                    (nombre_equipo, marca, modelo, numero_serie, tipo,
                     procesador, ram_gb, almacenamiento, sistema_operativo,
                     estado, ubicacion, responsable, observaciones, created_by, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    datos["nombre_equipo"], datos["marca"], datos["modelo"],
                    datos["numero_serie"], datos["tipo"], datos["procesador"],
                    datos["ram_gb"], datos["almacenamiento"],
                    datos["sistema_operativo"], datos["estado"],
                    datos["ubicacion"], datos["responsable"],
                    datos["observaciones"],
                    current_user.username, current_user.username,
                ),
            )
        except pymysql.err.IntegrityError:
            flash("El número de serie ya existe en la base de datos.", "error")
            return render_template("form.html", equipo=request.form, modo="crear")

        registrar_bitacora(
            "crear_equipo", f"Registró el equipo '{datos['nombre_equipo']}' (id {new_id})"
        )
        flash("Equipo registrado correctamente.", "exito")
        return redirect(url_for("index"))

    return render_template("form.html", equipo={}, modo="crear")


@app.route("/editar/<int:equipo_id>", methods=["GET", "POST"])
@permiso_requerido("equipos.editar")
def editar(equipo_id):
    """Muestra el formulario y actualiza un equipo (UPDATE)."""
    equipo = db_query("SELECT * FROM equipos WHERE id = %s", (equipo_id,), one=True)
    if equipo is None:
        flash("El equipo solicitado no existe.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        errores, datos = validar_formulario(request.form)

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template(
                "form.html", equipo=request.form, modo="editar", equipo_id=equipo_id
            )

        try:
            db_execute(
                """
                UPDATE equipos SET
                    nombre_equipo = %s, marca = %s, modelo = %s,
                    numero_serie = %s, tipo = %s, procesador = %s,
                    ram_gb = %s, almacenamiento = %s, sistema_operativo = %s,
                    estado = %s, ubicacion = %s, responsable = %s,
                    observaciones = %s, updated_by = %s
                WHERE id = %s
                """,
                (
                    datos["nombre_equipo"], datos["marca"], datos["modelo"],
                    datos["numero_serie"], datos["tipo"], datos["procesador"],
                    datos["ram_gb"], datos["almacenamiento"],
                    datos["sistema_operativo"], datos["estado"],
                    datos["ubicacion"], datos["responsable"],
                    datos["observaciones"], current_user.username, equipo_id,
                ),
            )
        except pymysql.err.IntegrityError:
            flash("El número de serie ya pertenece a otro equipo.", "error")
            return render_template(
                "form.html", equipo=request.form, modo="editar", equipo_id=equipo_id
            )

        registrar_bitacora(
            "editar_equipo", f"Editó el equipo '{datos['nombre_equipo']}' (id {equipo_id})"
        )
        flash("Equipo actualizado correctamente.", "exito")
        return redirect(url_for("index"))

    return render_template(
        "form.html", equipo=equipo, modo="editar", equipo_id=equipo_id
    )


@app.route("/eliminar/<int:equipo_id>", methods=["POST"])
@permiso_requerido("equipos.eliminar")
def eliminar(equipo_id):
    """Elimina un equipo (DELETE)."""
    equipo = db_query(
        "SELECT nombre_equipo FROM equipos WHERE id = %s", (equipo_id,), one=True
    )
    db_execute("DELETE FROM equipos WHERE id = %s", (equipo_id,))
    registrar_bitacora(
        "eliminar_equipo",
        f"Eliminó el equipo '{equipo['nombre_equipo']}' (id {equipo_id})"
        if equipo else f"Eliminó el equipo id {equipo_id}",
    )
    flash("Equipo eliminado correctamente.", "exito")
    return redirect(url_for("index"))


@app.route("/exportar")
@permiso_requerido("reportes.exportar")
def exportar():
    """Exporta el inventario completo a CSV (descarga)."""
    equipos = db_query("SELECT * FROM equipos ORDER BY id")
    salida = io.StringIO()
    writer = csv.writer(salida)

    writer.writerow([
        "ID", "Nombre", "Marca", "Modelo", "No. Serie", "Tipo", "Procesador",
        "RAM (GB)", "Almacenamiento", "Sistema Operativo", "Estado",
        "Ubicación", "Responsable", "Observaciones", "Creado por",
        "Actualizado por", "Fecha creación", "Última actualización",
    ])
    for e in equipos:
        writer.writerow([
            e["id"], e["nombre_equipo"], e["marca"], e["modelo"],
            e["numero_serie"], e["tipo"], e["procesador"], e["ram_gb"],
            e["almacenamiento"], e["sistema_operativo"], e["estado"],
            e["ubicacion"], e["responsable"], e["observaciones"] or "",
            e["created_by"] or "", e["updated_by"] or "",
            e["created_at"], e["updated_at"],
        ])

    salida.seek(0)
    data = io.BytesIO(salida.getvalue().encode("utf-8-sig"))  # BOM para Excel
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    registrar_bitacora("exportar_csv", "Exportó el inventario a CSV")
    return send_file(
        data,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"inventario_equipos_{fecha}.csv",
    )


# ==========================================================
# GESTIÓN DE USUARIOS (solo admin)
# ==========================================================
@app.route("/usuarios")
@permiso_requerido("usuarios.gestionar")
def usuarios_lista():
    usuarios = db_query(
        """
        SELECT u.id, u.nombre, u.username, u.email, u.activo, u.ultimo_acceso,
               r.nombre AS rol_nombre
        FROM usuarios u JOIN roles r ON r.id = u.rol_id
        ORDER BY u.id
        """
    )
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/crear", methods=["GET", "POST"])
@permiso_requerido("usuarios.gestionar")
def usuarios_crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip() or None
        password = request.form.get("password", "")
        rol_id = request.form.get("rol_id", "")

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not username or not username.replace("_", "").replace(".", "").isalnum():
            errores.append("Username inválido (letras, números, punto y guion bajo).")
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres.")
        if not rol_id.isdigit():
            errores.append("Selecciona un rol válido.")
        if errores:
            for e in errores:
                flash(e, "error")
        else:
            try:
                db_execute(
                    """
                    INSERT INTO usuarios (nombre, username, email, password_hash, rol_id, activo)
                    VALUES (%s, %s, %s, %s, %s, 1)
                    """,
                    (nombre, username, email, generate_password_hash(password), int(rol_id)),
                )
            except pymysql.err.IntegrityError:
                flash("Ese username ya existe.", "error")
            else:
                registrar_bitacora(
                    "crear_usuario", f"Creó el usuario '{username}' (rol id {rol_id})"
                )
                flash(f"Usuario '{username}' creado correctamente.", "exito")
                return redirect(url_for("usuarios_lista"))

    roles = db_query("SELECT * FROM roles ORDER BY id")
    return render_template("usuario_form.html", usuario={}, modo="crear", roles=roles)


@app.route("/usuarios/editar/<int:usuario_id>", methods=["GET", "POST"])
@permiso_requerido("usuarios.gestionar")
def usuarios_editar(usuario_id):
    usuario = db_query("SELECT * FROM usuarios WHERE id = %s", (usuario_id,), one=True)
    if usuario is None:
        flash("El usuario no existe.", "error")
        return redirect(url_for("usuarios_lista"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip() or None
        rol_id = request.form.get("rol_id", "")
        activo = 1 if request.form.get("activo") == "on" else 0
        nueva_password = request.form.get("password", "")

        # Protección: no desactivarse ni quitarse el rol a sí mismo
        if str(usuario_id) == current_user.id and (not activo or int(rol_id) != current_user.rol_id):
            flash("No puedes desactivarte ni cambiarte el rol a ti mismo.", "error")
            return redirect(url_for("usuarios_editar", usuario_id=usuario_id))

        if not nombre or not rol_id.isdigit():
            flash("Nombre y rol son obligatorios.", "error")
            return redirect(url_for("usuarios_editar", usuario_id=usuario_id))

        db_execute(
            """
            UPDATE usuarios
            SET nombre = %s, email = %s, rol_id = %s, activo = %s
            WHERE id = %s
            """,
            (nombre, email, int(rol_id), activo, usuario_id),
        )
        if nueva_password:
            if len(nueva_password) < 8:
                flash(
                    "La contraseña no se cambió: debe tener al menos 8 caracteres.",
                    "error",
                )
            else:
                db_execute(
                    "UPDATE usuarios SET password_hash = %s WHERE id = %s",
                    (generate_password_hash(nueva_password), usuario_id),
                )

        registrar_bitacora(
            "editar_usuario", f"Editó el usuario '{usuario['username']}' (id {usuario_id})"
        )
        flash("Usuario actualizado correctamente.", "exito")
        return redirect(url_for("usuarios_lista"))

    roles = db_query("SELECT * FROM roles ORDER BY id")
    return render_template(
        "usuario_form.html", usuario=usuario, modo="editar", roles=roles
    )


# ==========================================================
# BITÁCORA (admin y gerente)
# ==========================================================
@app.route("/bitacora")
@permiso_requerido("bitacora.ver")
def bitacora():
    registros = db_query(
        "SELECT * FROM bitacora ORDER BY fecha DESC, id DESC LIMIT 200"
    )
    return render_template("bitacora.html", registros=registros)


# ----------------------------------------------------------
if __name__ == "__main__":
    # Pon FLASK_DEBUG=0 en .env cuando lo despliegues en producción
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
