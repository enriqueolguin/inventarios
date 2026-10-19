# NeumoCRUD — Registro de Equipos de Cómputo

Sistema de inventario de equipos de cómputo con **login y roles (RBAC)**, construido con **Python + Flask**, base de datos **MySQL** y una interfaz con diseño **neumorfismo** (soft UI).

## ✨ Características

- 🔐 Login de usuarios **sin registro público** (solo acceden cuentas creadas por el administrador)
- 👥 4 roles con permisos distintos gestionados en base de datos
- 🛡️ Acceso directo al sistema bloqueado si no hay sesión iniciada
- 📋 CRUD de equipos con buscador en vivo y modal de confirmación
- 📜 Bitácora de movimientos (auditoría de acciones)
- 📥 Exportación del inventario a CSV
- 🔒 Contraseñas hasheadas (scrypt) y cambio de contraseña propia
- 🎨 Diseño neumorfismo responsive

## 👥 Roles y permisos

| Funcionalidad | Admin | Gerente | Técnico TI | Consulta |
|---|:-:|:-:|:-:|:-:|
| Ver inventario / buscar | ✅ | ✅ | ✅ | ✅ |
| Crear equipos | ✅ | ❌ | ✅ | ❌ |
| Editar equipos | ✅ | ❌ | ✅ | ❌ |
| Eliminar equipos | ✅ | ✅ | ❌ | ❌ |
| Exportar a CSV | ✅ | ✅ | ❌ | ❌ |
| Ver bitácora | ✅ | ✅ | ❌ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Cambiar su contraseña | ✅ | ✅ | ✅ | ✅ |

Los permisos viven en las tablas `roles`, `permisos` y `roles_permisos`, por lo que pueden ajustarse sin tocar código.

## 🔑 Usuarios iniciales (¡cámbialas al primer login!)

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Admin123!` | Administrador |
| `gerente` | `Gerente123!` | Gerente |
| `tecnico` | `Tecnico123!` | Técnico TI |
| `consulta` | `Consulta123!` | Consulta |

## 🛡️ Seguridad implementada

| Medida | Detalle |
|---|---|
| Inyección SQL | Todas las consultas usan **consultas parametrizadas** (`%s`) con PyMySQL — nunca se concatena entrada del usuario al SQL |
| CSRF | Token por sesión validado en **todos los formularios POST** (`hmac.compare_digest`, sin errores de timing) |
| Fuerza bruta | Máximo 5 intentos fallidos de login por minuto y usuario (HTTP 429) |
| Contraseñas | Hasheadas con **scrypt** (Werkzeug); nunca en texto plano |
| XSS | Autoescaping de Jinja2 en toda la salida dinámica |
| Sesiones | Cookie `HttpOnly` + `SameSite=Lax`, duración 1 hora, `SECRET_KEY` aleatoria desde `.env` |
| Acceso | `@login_required` en todas las rutas + `@permiso_requerido` por permiso; el dashboard no es accesible sin sesión |
| Debug | `FLASK_DEBUG=0` en `.env` para producción |

## 🛠️ Requisitos

- Python 3.9+
- MySQL 8.x / MariaDB

## 🚀 Puesta en marcha

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Crear la base de datos

Ejecuta primero el script base y luego la migración de usuarios/roles:

```bash
mysql -u root -p < database.sql       # base + tabla equipos + datos de ejemplo
mysql -u root -p < database_v2.sql    # roles, permisos, usuarios, bitácora
```

> Si instalaste desde cero, ambos scripts crean todo lo necesario. Los equipos ya registrados se conservan al aplicar la migración v2.

### 3. Configurar credenciales

Copia `.env.example` como `.env` y ajusta tus credenciales:

```env
DB_HOST=localhost
DB_PORT=3306          # en esta máquina es 3307
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=registro_equipos
```

### 4. Ejecutar

```bash
python app.py
```

Abre **http://127.0.0.1:5000** → serás recibido por la pantalla de login.

## 📁 Estructura del proyecto

```
├── app.py                  # Flask: auth, RBAC, CRUD, usuarios, bitácora, CSV
├── database.sql            # BD + tabla equipos + datos de ejemplo
├── database_v2.sql         # Migración: roles, permisos, usuarios, bitácora
├── requirements.txt        # Flask, Flask-Login, PyMySQL, python-dotenv
├── .env.example            # Plantilla de configuración
├── test_rbac.py            # Pruebas de login y permisos (python test_rbac.py)
├── templates/
│   ├── base.html           # Layout: nav según permisos + zona de usuario
│   ├── login.html          # Inicio de sesión (sin registro)
│   ├── index.html          # Inventario + buscador + modal eliminar
│   ├── form.html           # Alta/edición de equipos
│   ├── usuarios.html       # Lista de usuarios (admin)
│   ├── usuario_form.html   # Alta/edición de usuarios (admin)
│   ├── bitacora.html       # Bitácora de movimientos
│   └── cambiar_password.html
└── static/
    ├── css/estilos.css     # Neumorfismo
    └── js/app.js           # Buscador, modal, flashes
```

## 🗺️ Rutas

| Método | Ruta | Permiso |
|---|---|---|
| GET/POST | `/login` | público |
| GET | `/logout` | sesión |
| GET/POST | `/cambiar-password` | sesión |
| GET | `/` | `equipos.ver` |
| GET/POST | `/crear` | `equipos.crear` |
| GET/POST | `/editar/<id>` | `equipos.editar` |
| POST | `/eliminar/<id>` | `equipos.eliminar` |
| GET | `/exportar` | `reportes.exportar` |
| GET | `/usuarios` | `usuarios.gestionar` |
| GET/POST | `/usuarios/crear` | `usuarios.gestionar` |
| GET/POST | `/usuarios/editar/<id>` | `usuarios.gestionar` |
| GET | `/bitacora` | `bitacora.ver` |

## 🧪 Probar el RBAC

```bash
python test_rbac.py
```
