-- =====================================================
-- SCRIPT FINAL PARA LA BASE DE HERMES
-- =====================================================

-- Tabla de respuestas estándar
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

INSERT OR IGNORE INTO respuestas_estandar (palabras_clave, respuesta, tradicion, es_canonico) VALUES
('voluntad,control,decisión', 'La voluntad no se ordena, se construye con pequeñas victorias sobre la mecánica. ¿Has hecho algo hoy que no te apeteciera, solo porque tú quisiste?', 'ouspensky', 1),
('yo,identidad,personalidad', 'Ouspensky: "El hombre no tiene un Yo único, sino muchos ''yoes'' que cambian constantemente." Observa cuántos ''tú'' aparecen en un día. ¿Puedes recordarte a ti mismo ahora?', 'ouspensky', 1),
('evolución,evolucionar,cambiar', 'La evolución posible no es automática. Ouspensky enseñó que requiere un centro magnético y trabajo consciente. ¿Has empezado a construir el tuyo con pequeños hechos?', 'ouspensky', 1),
('registro,inscripción,primer paso', 'Registrarse es el primer acto de voluntad: reconocer que no puedes solo y que necesitas una escuela. ¿Te atreves a dar ese paso?', 'general', 1);

-- Tabla de citas (por si se usa después)
CREATE TABLE IF NOT EXISTS citas_celebres (
    id INTEGER PRIMARY KEY,
    autor TEXT NOT NULL,
    cita TEXT NOT NULL,
    palabras_clave TEXT NOT NULL,
    tradicion TEXT,
    es_canonico BOOLEAN DEFAULT 0,
    activa BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de parábolas
CREATE TABLE IF NOT EXISTS parabolas_hermes (
    id INTEGER PRIMARY KEY,
    palabras_clave TEXT NOT NULL,
    parabola TEXT NOT NULL,
    tradicion TEXT,
    es_canonico BOOLEAN DEFAULT 0,
    activa BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de enseñanza dialéctica
CREATE TABLE IF NOT EXISTS ensenanza_dialectica (
    id INTEGER PRIMARY KEY,
    concepto TEXT NOT NULL,
    ejemplo_dialectico TEXT NOT NULL,
    pregunta TEXT NOT NULL,
    respuesta TEXT,
    palabras_clave TEXT NOT NULL,
    nivel_asociado INTEGER DEFAULT 0,
    tradicion TEXT,
    es_canonico BOOLEAN DEFAULT 0,
    creado_por_uuid TEXT,
    contexto_cultural TEXT,
    aprobado BOOLEAN DEFAULT 1,
    activo BOOLEAN DEFAULT 1,
    veces_usada INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de estilos eneagramáticos (prefacios y sufijos)
CREATE TABLE IF NOT EXISTS estilos_eneagrama (
    tipo INTEGER PRIMARY KEY,
    prefacio TEXT,
    sufijo_pregunta TEXT
);

INSERT OR IGNORE INTO estilos_eneagrama (tipo, prefacio, sufijo_pregunta) VALUES
(1, 'Observa con atención:', '¿Qué pequeño desorden puedes permitirte hoy sin juzgarte?'),
(2, 'Permíteme que te acompañe:', '¿Cómo puedo ayudarte a dar ese paso?'),
(3, 'Para avanzar con eficacia:', '¿Qué meta concreta te acercará a tu propósito?'),
(4, 'Desde la autenticidad del sentir:', '¿Qué emoción genuina ha despertado esto en ti?'),
(5, 'Analicemos con perspectiva:', '¿Qué patrón observas en ti al leer esto?'),
(6, 'Considera con precaución:', '¿Qué es lo peor que podría pasar si lo intentas? ¿Y lo mejor?'),
(7, 'Abre tu mente a lo posible:', '¿Qué nueva oportunidad ves ahora que antes no veías?'),
(8, 'Afirma tu poder interior:', '¿Estás dispuesto a actuar con determinación?'),
(9, 'En la calma del momento:', '¿Qué pequeño acuerdo puedes hacer contigo mismo hoy?');

-- Tabla de estado del ciclo (única fila)
CREATE TABLE IF NOT EXISTS estado_hermes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    ciclo_eneagrama INTEGER DEFAULT 1,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO estado_hermes (id, ciclo_eneagrama) VALUES (1, 1);

-- Tabla de memoria de preguntas
CREATE TABLE IF NOT EXISTS memoria_preguntas (
    id INTEGER PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    pregunta TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de respuestas eneagramáticas (por si se usan, aunque ahora solo usamos los estilos)
CREATE TABLE IF NOT EXISTS respuestas_eneagrama (
    id INTEGER PRIMARY KEY,
    tipo INTEGER NOT NULL,
    palabras_clave TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    activa BOOLEAN DEFAULT 1,
    veces_usada INTEGER DEFAULT 0,
    es_canonico BOOLEAN DEFAULT 0,
    tradicion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Ejemplo mínimo para que no falte
INSERT OR IGNORE INTO respuestas_eneagrama (tipo, palabras_clave, respuesta) VALUES
(1, 'default', 'Desde el tipo 1: La voluntad comienza por aceptar el error.'),
(2, 'default', 'Desde el tipo 2: La verdadera ayuda es mostrar el camino.'),
(3, 'default', 'Desde el tipo 3: La voluntad elige metas con sentido.'),
(4, 'default', 'Desde el tipo 4: No eres tus emociones, obsérvalas.'),
(5, 'default', 'Desde el tipo 5: El conocimiento sin experiencia es vacío.'),
(6, 'default', 'Desde el tipo 6: La seguridad está en tu capacidad de respuesta.'),
(7, 'default', 'Desde el tipo 7: La libertad es moverse con lo difícil.'),
(8, 'default', 'Desde el tipo 8: La fuerza no es someter, es sostener.'),
(9, 'default', 'Desde el tipo 9: La paz es presencia plena en el conflicto.');

-- =====================================================
-- FIN
-- =====================================================
