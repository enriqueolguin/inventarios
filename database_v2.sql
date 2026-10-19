-- ============================================================
-- NeumoCRUD v2 — Migración: usuarios, roles y permisos (RBAC)
-- Se ejecuta sobre la base existente "registro_equipos".
-- Los equipos ya registrados se conservan.
-- ============================================================

USE registro_equipos;

-- ------------------------------------------------------------
-- 1) Tabla de roles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(150) NOT NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2) Tabla de usuarios
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL,
  username      VARCHAR(50)  NOT NULL UNIQUE,
  email         VARCHAR(120) NULL,
  password_hash VARCHAR(255) NOT NULL,
  rol_id        INT          NOT NULL,
  activo        TINYINT(1)   NOT NULL DEFAULT 1,
  ultimo_acceso DATETIME     NULL,
  created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id)
    REFERENCES roles (id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3) Tabla de permisos y su relación con roles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS permisos (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  clave       VARCHAR(60) NOT NULL UNIQUE,
  descripcion VARCHAR(150) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS roles_permisos (
  rol_id     INT NOT NULL,
  permiso_id INT NOT NULL,
  PRIMARY KEY (rol_id, permiso_id),
  CONSTRAINT fk_rp_rol     FOREIGN KEY (rol_id)     REFERENCES roles (id),
  CONSTRAINT fk_rp_permiso FOREIGN KEY (permiso_id) REFERENCES permisos (id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4) Bitácora de movimientos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bitacora (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT          NULL,
  username   VARCHAR(50)  NOT NULL,
  accion     VARCHAR(60)  NOT NULL,
  detalle    VARCHAR(255) NULL,
  fecha      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_bitacora_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5) Auditoría en equipos: quién creó / actualizó
-- ------------------------------------------------------------
ALTER TABLE equipos
  ADD COLUMN created_by VARCHAR(50) NULL AFTER observaciones,
  ADD COLUMN updated_by VARCHAR(50) NULL AFTER created_by;

-- ------------------------------------------------------------
-- 6) Catálogo de roles
-- ------------------------------------------------------------
INSERT INTO roles (id, nombre, descripcion) VALUES
  (1, 'Administrador', 'Control total: usuarios, roles, equipos y bitácora'),
  (2, 'Gerente',       'Supervisa inventario, elimina equipos y consulta bitácora'),
  (3, 'Técnico TI',    'Registra y actualiza equipos del día a día'),
  (4, 'Consulta',      'Solo lectura del inventario')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- ------------------------------------------------------------
-- 7) Catálogo de permisos
-- ------------------------------------------------------------
INSERT INTO permisos (clave, descripcion) VALUES
  ('equipos.ver',        'Ver el inventario y buscar equipos'),
  ('equipos.crear',      'Registrar nuevos equipos'),
  ('equipos.editar',     'Editar equipos existentes'),
  ('equipos.eliminar',   'Eliminar equipos'),
  ('reportes.exportar',  'Exportar el inventario a CSV'),
  ('bitacora.ver',       'Consultar la bitácora de movimientos'),
  ('usuarios.gestionar', 'Crear, editar y activar/desactivar usuarios')
ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion);

-- ------------------------------------------------------------
-- 8) Asignación de permisos por rol
--    Administrador: todos
-- ------------------------------------------------------------
INSERT IGNORE INTO roles_permisos (rol_id, permiso_id)
SELECT 1, id FROM permisos;

-- Gerente: ver, eliminar, exportar, bitácora
INSERT IGNORE INTO roles_permisos (rol_id, permiso_id)
SELECT 2, id FROM permisos WHERE clave IN
  ('equipos.ver', 'equipos.eliminar', 'reportes.exportar', 'bitacora.ver');

-- Técnico: ver, crear, editar
INSERT IGNORE INTO roles_permisos (rol_id, permiso_id)
SELECT 3, id FROM permisos WHERE clave IN
  ('equipos.ver', 'equipos.crear', 'equipos.editar');

-- Consulta: solo ver
INSERT IGNORE INTO roles_permisos (rol_id, permiso_id)
SELECT 4, id FROM permisos WHERE clave = 'equipos.ver';

-- ------------------------------------------------------------
-- 9) Usuarios iniciales
--    (contraseñas hasheadas con Werkzeug/scrypt)
--    admin/Admin123! · gerente/Gerente123!
--    tecnico/Tecnico123! · consulta/Consulta123!
--    ¡Cámbialas al primer inicio de sesión!
-- ------------------------------------------------------------
INSERT INTO usuarios (nombre, username, email, password_hash, rol_id, activo) VALUES
  ('Administrador del sistema', 'admin',     'admin@empresa.local',     'scrypt:32768:8:1$1i6OBYOtPN5AXfC6$d8ab8b0c983ae314f97ab808b94fa40edeac6f1969143f7de77193230a2b82429f0ab272c2fe857f605682e69c43696596aa955663f5fc8d501e54e4fbfa49cf', 1, 1),
  ('Gerente de área',           'gerente',   'gerente@empresa.local',   'scrypt:32768:8:1$mhOVSu5x4FM3hlok$72aebd0f992535d91159cba54ed47893352b709ef256e1627f2d0119a5693d41a3e145ca6b4985cf39f50a5992486a3c636b4703a710fd4672f571c945a7b53d', 2, 1),
  ('Técnico de soporte',        'tecnico',   'tecnico@empresa.local',   'scrypt:32768:8:1$yYb2li204CY1jJ6h$83f27c019641d0c0aa081a3c4ac9d3699f5b01351017db710222c60259aaadb368a6863657f201713e747968cd84e16a1bd853103cef7ccc491a1da5940c5e61', 3, 1),
  ('Empleado consulta',         'consulta',  'consulta@empresa.local',  'scrypt:32768:8:1$7OPTHUXwng3vG2Tg$42955980e8b4e4bfbe2d9a01b3095b51c577a8a06131d8c03518340dd109c858a9d63495782c896b86f642992505697bde58c5f3af860cf66de9967936835921', 4, 1);

-- ------------------------------------------------------------
-- 10) Bitácora inicial
-- ------------------------------------------------------------
INSERT INTO bitacora (usuario_id, username, accion, detalle)
VALUES (1, 'admin', 'sistema', 'Migración v2 aplicada: usuarios, roles y permisos creados');
