-- Tabla de estado del ciclo
CREATE TABLE IF NOT EXISTS estado_hermes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    ciclo_eneagrama INTEGER DEFAULT 1,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO estado_hermes (id, ciclo_eneagrama) VALUES (1, 1);

-- Tabla de estilos eneagramáticos (prefacio y sufijo)
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

-- Tabla de memoria de preguntas (por usuario)
CREATE TABLE IF NOT EXISTS memoria_preguntas (
    id INTEGER PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    pregunta TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
