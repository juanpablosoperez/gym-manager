-- Script para arreglar la tabla rutinas
-- Cambia la columna documento_rutina a LONGBLOB para soportar archivos más grandes

-- Verificar la estructura actual de la tabla
DESCRIBE rutinas;

-- Cambiar la columna documento_rutina a LONGBLOB (soporta hasta 4GB)
ALTER TABLE rutinas MODIFY COLUMN documento_rutina LONGBLOB;

-- Verificar que el cambio se aplicó correctamente
DESCRIBE rutinas;

-- Opcional: Verificar que no hay datos que se puedan perder
SELECT COUNT(*) as total_rutinas FROM rutinas; 