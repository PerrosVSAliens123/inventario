-- ============================================================
--  Script de inicialización de la base de datos "inventario"
--  MySQL lo ejecuta automáticamente SOLO la primera vez,
--  cuando el volumen datos_mysql está vacío.
-- ============================================================

SET NAMES utf8mb4;
USE inventario;

CREATE TABLE IF NOT EXISTS equipos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    tipo            ENUM('Computadora de escritorio','Laptop','Proyector','Impresora','Tableta','Switch de red','Access point') NOT NULL,
    marca           VARCHAR(50)  NOT NULL,
    numero_serie    VARCHAR(50)  NOT NULL UNIQUE,
    ubicacion       VARCHAR(100) NOT NULL,
    estado          ENUM('Disponible','En uso','En mantenimiento','Fuera de servicio') NOT NULL DEFAULT 'Disponible',
    fecha_registro  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Registros de ejemplo (datos ficticios)
INSERT INTO equipos (nombre, tipo, marca, numero_serie, ubicacion, estado) VALUES
('PC laboratorio 1',         'Computadora de escritorio', 'Dell',     'COB-001', 'Laboratorio de cómputo', 'En uso'),
('PC laboratorio 2',         'Computadora de escritorio', 'Dell',     'COB-002', 'Laboratorio de cómputo', 'En mantenimiento'),
('Laptop dirección',         'Laptop',                    'HP',       'COB-003', 'Dirección',              'En uso'),
('Laptop sala de maestros',  'Laptop',                    'Lenovo',   'COB-004', 'Sala de maestros',       'Disponible'),
('Proyector aula 3',         'Proyector',                 'Epson',    'COB-005', 'Aula 3',                 'En uso'),
('Impresora administración', 'Impresora',                 'HP',       'COB-006', 'Administración',         'Fuera de servicio'),
('Tableta biblioteca',       'Tableta',                   'Samsung',  'COB-007', 'Biblioteca',             'Disponible'),
('Switch cuarto de red',     'Switch de red',             'Cisco',    'COB-008', 'Cuarto de red',          'En uso'),
('Access point planta alta', 'Access point',              'Ubiquiti', 'COB-009', 'Pasillo planta alta',    'En uso');
