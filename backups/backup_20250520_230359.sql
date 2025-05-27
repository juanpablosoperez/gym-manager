-- Backup generado por Gym Manager
SET FOREIGN_KEY_CHECKS=0;

-- Estructura de la tabla backups
DROP TABLE IF EXISTS backups;
CREATE TABLE `backups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `size_mb` float NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `error_message` text,
  `description` text,
  `created_by` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `check_backup_status` CHECK ((`status` in (_utf8mb4'completed',_utf8mb4'failed',_utf8mb4'in_progress')))
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla backups
INSERT INTO backups (id, name, file_path, size_mb, status, created_at, error_message, description, created_by) VALUES (25, 'backup_20250520_230145.sql', 'C:\Users\yoel_\OneDrive\Desktop\Mis_proyectos\gym-manager\backups\backup_20250520_230145.sql', 0.00499249, 'completed', '2025-05-20 23:01:46', NULL, 'Backup manual', 'admin');
INSERT INTO backups (id, name, file_path, size_mb, status, created_at, error_message, description, created_by) VALUES (26, 'backup_20250520_230359.sql', 'C:\Users\yoel_\OneDrive\Desktop\Mis_proyectos\gym-manager\backups\backup_20250520_230359.sql', 0.0, 'in_progress', '2025-05-20 23:04:00', NULL, 'Backup manual', 'admin');

-- Estructura de la tabla comprobantes_pago
DROP TABLE IF EXISTS comprobantes_pago;
CREATE TABLE `comprobantes_pago` (
  `id_comprobante` int NOT NULL AUTO_INCREMENT,
  `contenido` blob NOT NULL,
  `fecha_emision` datetime NOT NULL,
  `id_pago` int NOT NULL,
  PRIMARY KEY (`id_comprobante`),
  UNIQUE KEY `id_pago` (`id_pago`),
  CONSTRAINT `comprobantes_pago_ibfk_1` FOREIGN KEY (`id_pago`) REFERENCES `pagos` (`id_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla metodos_pago
DROP TABLE IF EXISTS metodos_pago;
CREATE TABLE `metodos_pago` (
  `id_metodo_pago` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla miembros
DROP TABLE IF EXISTS miembros;
CREATE TABLE `miembros` (
  `id_miembro` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `documento` varchar(20) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` varchar(10) NOT NULL,
  `correo_electronico` varchar(100) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `tipo_membresia` varchar(20) NOT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL,
  `informacion_medica` text,
  PRIMARY KEY (`id_miembro`),
  UNIQUE KEY `documento` (`documento`),
  UNIQUE KEY `correo_electronico` (`correo_electronico`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla pagos
DROP TABLE IF EXISTS pagos;
CREATE TABLE `pagos` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `fecha_pago` datetime NOT NULL,
  `monto` float NOT NULL,
  `referencia` varchar(50) DEFAULT NULL,
  `estado` tinyint(1) NOT NULL,
  `id_miembro` int NOT NULL,
  `id_metodo_pago` int NOT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `id_miembro` (`id_miembro`),
  KEY `id_metodo_pago` (`id_metodo_pago`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`),
  CONSTRAINT `pagos_ibfk_2` FOREIGN KEY (`id_metodo_pago`) REFERENCES `metodos_pago` (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla rutinas
DROP TABLE IF EXISTS rutinas;
CREATE TABLE `rutinas` (
  `id_rutina` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `documento_rutina` blob,
  `nivel_dificultad` varchar(20) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  `fecha_horario` datetime NOT NULL,
  `id_miembro` int NOT NULL,
  PRIMARY KEY (`id_rutina`),
  KEY `id_miembro` (`id_miembro`),
  CONSTRAINT `rutinas_ibfk_1` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla usuarios
DROP TABLE IF EXISTS usuarios;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `contraseña` varchar(100) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla usuarios
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (3, 'yoel', 'junges', 'admin', '$2b$12$pR4Ykf2./7kdulRJHgTLV.aBQ06t51LKpQKZ6mvWVUB3VxzsRq6Sy', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (4, 'facu', 'abba', 'admin', '$2b$12$jDdkufti8RZPNJcgf7Xeieb7wgsnAV8ugDJhAUMVLTs7ZXPQCZ/PK', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (5, 'franco', 'cristhen', 'admin', '$2b$12$zq/iQwXyZazJaVSaYeT/H.hHyB4lC4byrASn6fS4cogECF5GLd8S.', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (6, 'juan pablo', 'soperez', 'admin', '$2b$12$3UF4tCMkfsb5Zo8DsIB/Ze9H2.K87Rkj51k973ElZLx/K1MQ7Xh.i', 1);

