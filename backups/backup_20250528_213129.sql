-- Backup generado por Gym Manager
SET FOREIGN_KEY_CHECKS=0;

-- Estructura de la tabla comprobantes_pago
CREATE TABLE IF NOT EXISTS `comprobantes_pago` (
  `id_comprobante` int NOT NULL AUTO_INCREMENT,
  `contenido` blob NOT NULL,
  `fecha_emision` datetime NOT NULL,
  `id_pago` int NOT NULL,
  PRIMARY KEY (`id_comprobante`),
  UNIQUE KEY `id_pago` (`id_pago`),
  CONSTRAINT `comprobantes_pago_ibfk_1` FOREIGN KEY (`id_pago`) REFERENCES `pagos` (`id_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla metodos_pago
CREATE TABLE IF NOT EXISTS `metodos_pago` (
  `id_metodo_pago` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_metodo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estructura de la tabla miembros
CREATE TABLE IF NOT EXISTS `miembros` (
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
CREATE TABLE IF NOT EXISTS `pagos` (
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
CREATE TABLE IF NOT EXISTS `rutinas` (
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
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `contraseña` varchar(100) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de la tabla usuarios
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (31, 'admin', 'sdfsf', 'admin', '$2b$12$aqV8s4NQwLNaE/VooUkpi.K8tgIdyHstPsF1HuUYzxNCZtfN3k06u', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (32, 'admin1', 'dggs', 'admin', '$2b$12$5HbBvSzDQE9C9Q5kjQkAiOPYF2LKSum0CROaQEMNvLe.5elT7laqi', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (35, 'yoel', 'junges', 'admin', '$2b$12$9aoJOAhF5yrqPWsrx4/0hep0vt4YNMN0a22ZNTSIXuvwbiaWuwsIi', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (36, 'facu', 'asasd', 'admin', '$2b$12$1a.0JIwakzP6HJDeMcPmjuwkNlx5G49JsIMidLvYxi4DL6K6XeMvm', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (37, 'assdasd', 'afsaf', 'admin', '$2b$12$/.QuDBxBMb94k0KPpzuz2.esgnM/tJMndt/qMHeuX3J7i5DrJb08.', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (38, 'asfsafssf', 'asfasfasf', 'admin', '$2b$12$nmaj7YDwzKmKxwE3zKdecOdOZ9pH3v3E.qhHUezOdZqlwZgg9FWFS', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (39, 'dsgdsgds', 'sgdgsdgsd', 'admin', '$2b$12$djmxcNR7OIIFUW3WlbwL3Or7Htnx9eRygexF/4S8OyW2AF03VwlBq', 1);
INSERT INTO usuarios (id_usuario, nombre, apellido, rol, contraseña, estado) VALUES (40, 'sdgdsgsdgsdg', 'sdgdsgdsg', 'admin', '$2b$12$TGeJABZcI1toCLsMBMkMOeSqbPrlQOlyikQdT63go5gFN9qZB4kOG', 1);

