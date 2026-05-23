-- 1. Asegurar que la tabla superusuario_control existe
CREATE TABLE IF NOT EXISTS superusuario_control (
    id INTEGER PRIMARY KEY,
    superusuario_uuid TEXT UNIQUE,
    ultimo_acceso TIMESTAMP,
    fecha_expira TIMESTAMP,
    clave_emergencia TEXT,
    activo BOOLEAN DEFAULT 1,
    nota TEXT DEFAULT ''
);

-- 2. Actualizar o insertar superusuario en beings (usando nombre único)
INSERT OR REPLACE INTO beings (uuid, nombre, password_hash, nivel_actual, ciclos_completados, rol)
VALUES (
    'admin-unico-uuid',
    'Atamashi',
    'AQUI_VA_EL_HASH_GENERADO_CON_ARGON2',
    22, 22, 'superusuario'
);

-- 3. Actualizar o insertar en superusuario_control
INSERT OR REPLACE INTO superusuario_control (superusuario_uuid, ultimo_acceso, activo)
VALUES (
    'admin-unico-uuid',
    datetime('now'),
    1
);
