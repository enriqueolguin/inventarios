-- ============================================================
-- Base de datos: registro_equipos
-- CRUD de registro de equipos de cómputo (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS registro_equipos
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE registro_equipos;

CREATE TABLE IF NOT EXISTS equipos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombre_equipo   VARCHAR(100)  NOT NULL,
  marca           VARCHAR(60)   NOT NULL,
  modelo          VARCHAR(60)   NOT NULL,
  numero_serie    VARCHAR(60)   NOT NULL UNIQUE,
  tipo            ENUM('Laptop','Desktop','Servidor','All-in-One','Tablet') NOT NULL,
  procesador      VARCHAR(80)   NOT NULL,
  ram_gb          INT           NOT NULL,
  almacenamiento  VARCHAR(80)   NOT NULL,
  sistema_operativo VARCHAR(60) NOT NULL,
  estado          ENUM('Nuevo','Bueno','Regular','En reparación','Dado de baja') NOT NULL DEFAULT 'Nuevo',
  ubicacion       VARCHAR(100)  NOT NULL,
  responsable     VARCHAR(100)  NOT NULL,
  observaciones   TEXT          NULL,
  created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Datos de ejemplo (opcional, coméntalos si no los quieres)
INSERT INTO equipos
  (nombre_equipo, marca, modelo, numero_serie, tipo, procesador, ram_gb,
   almacenamiento, sistema_operativo, estado, ubicacion, responsable, observaciones)
VALUES
  ('PC-Oficina-01', 'Dell',    'OptiPlex 7090', 'DL7090X001', 'Desktop',  'Intel Core i5-10500',  8,  'SSD 256GB', 'Windows 11 Pro',  'Bueno',         'Oficina A - Piso 1', 'Ana López',    NULL),
  ('Lap-Gerencia',  'HP',      'EliteBook 840', 'HP840G8221', 'Laptop',   'Intel Core i7-1165G7', 16, 'SSD 512GB', 'Windows 11 Pro',  'Nuevo',         'Oficina B - Piso 2', 'Carlos Ruiz',  'Equipo asignado a gerencia'),
  ('Srv-Archivos',  'Lenovo',  'ThinkSystem',   'LNST550099', 'Servidor', 'Xeon Silver 4210',     32, 'RAID 4TB',  'Windows Server',  'Bueno',         'Cuarto de servidores','Soporte TI',   'Backup automático diario'),
  ('AIO-Recepcion', 'Apple',   'iMac 24"',      'APIM24X887', 'All-in-One','Apple M1',             8,  'SSD 256GB', 'macOS Sonoma',    'Regular',       'Recepción',          'María Torres', 'Detalle menor en bisagra'),
  ('Tab-Inventario','Samsung', 'Galaxy Tab A8', 'SMTAB8842',  'Tablet',   'Unisoc T618',          4,  '64GB',      'Android 13',      'En reparación', 'Almacén TI',         'Jorge Méndez', 'Pantalla dañada, en garantía');
