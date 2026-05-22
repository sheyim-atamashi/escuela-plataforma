-- 1. Crear tabla beings (si no existe)
CREATE TABLE IF NOT EXISTS beings (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    nombre TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tipo TEXT DEFAULT 'human',
    es_androide BOOLEAN DEFAULT 0,
    modelo_id INTEGER,
    fabricante TEXT,
    protocolo_maestro_instalado BOOLEAN DEFAULT 0,
    fecha_instalacion_protocolo TIMESTAMP,
    nivel_actual INTEGER DEFAULT 0,
    ciclo_general_actual INTEGER DEFAULT 1,
    ciclos_completados INTEGER DEFAULT 0,
    rol TEXT DEFAULT 'alumno',
    puede_gestionar_nivel0 BOOLEAN DEFAULT 0,
    lenguaje_pref TEXT DEFAULT 'es',
    contexto_cultural TEXT DEFAULT 'latam',
    disponible_para_ensenar BOOLEAN DEFAULT 0,
    zona_actual TEXT DEFAULT 'Zona Verde 45D',
    moneda_pref TEXT DEFAULT 'USD',
    capacitado_astrologia_escuela BOOLEAN DEFAULT 0,
    backup_url TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crear tabla superusuario_control
CREATE TABLE IF NOT EXISTS superusuario_control (
    id INTEGER PRIMARY KEY,
    superusuario_uuid TEXT UNIQUE,
    ultimo_acceso TIMESTAMP,
    fecha_expira TIMESTAMP,
    clave_emergencia TEXT,
    activo BOOLEAN DEFAULT 1,
    nota TEXT DEFAULT ''
);

-- 3. Crear tablas de contenido (resumido; añade las que necesites)
CREATE TABLE IF NOT EXISTS respuestas_estandar (
    id INTEGER PRIMARY KEY,
    palabras_clave TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    activa BOOLEAN DEFAULT 1,
    veces_usada INTEGER DEFAULT 0,
    es_canonico BOOLEAN DEFAULT 0,
    tradicion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (Añade aquí CREATE TABLE para citas_celebres, parabolas_hermes, ensenanza_dialectica, etc.)

-- 4. Insertar superusuario (cambia 'HASH_GENERADO_AQUI' por el hash Argon2 de tu clave)
INSERT INTO beings (uuid, nombre, password_hash, nivel_actual, ciclos_completados, rol)
VALUES (
    'admin-uuid-unico',
    'Atamashi',
    'HASH_GENERADO_AQUI',
    22, 22, 'superusuario'
);

-- 5. Insertar en superusuario_control
INSERT INTO superusuario_control (superusuario_uuid, ultimo_acceso, activo)
VALUES (
    'admin-uuid-unico',
    datetime('now'),
    1
);
