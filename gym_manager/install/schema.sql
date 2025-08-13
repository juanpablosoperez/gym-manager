-- Codificación y BD
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS `gym_manager`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE `gym_manager`;

-- Tabla usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL,
  `apellido` VARCHAR(50) NOT NULL,
  `rol` VARCHAR(20) NOT NULL,
  `contraseña` VARCHAR(100) NOT NULL,
  `estado` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla rutinas
CREATE TABLE IF NOT EXISTS `rutinas` (
  `id_rutina` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `descripcion` TEXT,
  `documento_rutina` LONGBLOB,
  `nivel_dificultad` VARCHAR(20) NOT NULL,
  `fecha_creacion` DATETIME,
  `fecha_horario` DATETIME,
  PRIMARY KEY (`id_rutina`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla miembros
CREATE TABLE IF NOT EXISTS `miembros` (
  `id_miembro` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL,
  `apellido` VARCHAR(50) NOT NULL,
  `documento` VARCHAR(20) NOT NULL,
  `fecha_nacimiento` DATE NOT NULL,
  `genero` VARCHAR(10) NOT NULL,
  `correo_electronico` VARCHAR(100) NOT NULL,
  `estado` TINYINT(1) NOT NULL DEFAULT 1,
  `tipo_membresia` VARCHAR(20) NOT NULL,
  `direccion` VARCHAR(200),
  `telefono` VARCHAR(20),
  `fecha_registro` DATETIME NOT NULL,
  `informacion_medica` TEXT,
  `id_rutina` INT,
  PRIMARY KEY (`id_miembro`),
  UNIQUE KEY `uk_miembros_documento` (`documento`),
  UNIQUE KEY `uk_miembros_correo` (`correo_electronico`),
  KEY `fk_miembro_rutina` (`id_rutina`),
  CONSTRAINT `fk_miembro_rutina` FOREIGN KEY (`id_rutina`) REFERENCES `rutinas` (`id_rutina`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla metodos_pago
CREATE TABLE IF NOT EXISTS `metodos_pago` (
  `id_metodo_pago` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(50) NOT NULL,
  `estado` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla pagos
CREATE TABLE IF NOT EXISTS `pagos` (
  `id_pago` INT NOT NULL AUTO_INCREMENT,
  `fecha_pago` DATETIME NOT NULL,
  `monto` FLOAT NOT NULL,
  `referencia` VARCHAR(50),
  `estado` TINYINT(1) NOT NULL DEFAULT 1,
  `id_miembro` INT NOT NULL,
  `id_metodo_pago` INT NOT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `idx_pagos_miembro` (`id_miembro`),
  KEY `idx_pagos_metodo` (`id_metodo_pago`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`),
  CONSTRAINT `pagos_ibfk_2` FOREIGN KEY (`id_metodo_pago`) REFERENCES `metodos_pago` (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla comprobantes_pago
CREATE TABLE IF NOT EXISTS `comprobantes_pago` (
  `id_comprobante` INT NOT NULL AUTO_INCREMENT,
  `contenido` BLOB NOT NULL,
  `fecha_emision` DATETIME NOT NULL,
  `id_pago` INT NOT NULL,
  PRIMARY KEY (`id_comprobante`),
  UNIQUE KEY `uk_comprobantes_pago_id_pago` (`id_pago`),
  CONSTRAINT `comprobantes_pago_ibfk_1` FOREIGN KEY (`id_pago`) REFERENCES `pagos` (`id_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla cuota_mensual
CREATE TABLE IF NOT EXISTS `cuota_mensual` (
  `id_cuota` INT NOT NULL AUTO_INCREMENT,
  `monto` FLOAT NOT NULL,
  `fecha_actualizacion` DATETIME NOT NULL,
  `activo` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_cuota`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla miembro_rutina (relación N:N)
CREATE TABLE IF NOT EXISTS `miembro_rutina` (
  `id_miembro` INT NOT NULL,
  `id_rutina` INT NOT NULL,
  PRIMARY KEY (`id_miembro`, `id_rutina`),
  KEY `idx_miembro_rutina_rutina` (`id_rutina`),
  CONSTRAINT `miembro_rutina_ibfk_1` FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`),
  CONSTRAINT `miembro_rutina_ibfk_2` FOREIGN KEY (`id_rutina`) REFERENCES `rutinas` (`id_rutina`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Semillas idempotentes: métodos de pago
INSERT INTO `metodos_pago` (`descripcion`, `estado`)
SELECT 'Efectivo', 1 FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `metodos_pago` WHERE `descripcion` = 'Efectivo');

INSERT INTO `metodos_pago` (`descripcion`, `estado`)
SELECT 'Transferencia', 1 FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `metodos_pago` WHERE `descripcion` = 'Transferencia');

INSERT INTO `metodos_pago` (`descripcion`, `estado`)
SELECT 'Tarjeta', 1 FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `metodos_pago` WHERE `descripcion` = 'Tarjeta');

-- Admin inicial
INSERT INTO `usuarios` (`nombre`,`apellido`,`rol`,`contraseña`,`estado`)
SELECT 'admin','admin','admin','$2b$12$rqmh93QG/JuNX/0nZh6wZ.hDaeaQLJA43fzIHX5mN4giQE7tm59lC',1
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `usuarios` WHERE nombre='admin' AND apellido='admin'
);