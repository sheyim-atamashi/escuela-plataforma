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

INSERT OR IGNORE INTO respuestas_eneagrama (tipo, palabras_clave, respuesta, es_canonico) VALUES
(1, 'perfección,error,crítica', 'Desde el tipo 1: La voluntad comienza por aceptar que el error es parte del camino. ¿Qué pequeño desorden puedes permitirte hoy sin juzgarte?', 1),
(2, 'ayuda,servicio,necesidad', 'Tipo 2: La verdadera ayuda no es hacer por otros, sino mostrarles cómo hacer por sí mismos. ¿Estás ayudando o creando dependencia?', 1),
(3, 'éxito,logro,resultado', 'Tipo 3: La voluntad no es solo alcanzar metas, es elegir qué metas merecen tu energía. ¿Corres tras lo que otros aplauden o tras lo que despierta tu interior?', 1),
(4, 'autenticidad,unicidad,identidad', 'Tipo 4: No eres tus emociones, aunque las sientas con intensidad. Observa la ola sin hundirte en ella. ¿Puedes sentir sin identificarte?', 1),
(5, 'conocimiento,observación,distancia', 'Tipo 5: El conocimiento sin experiencia es un mapa sin terreno. ¿Has caminado alguna vez lo que sabes?', 1),
(6, 'seguridad,duda,miedo', 'Tipo 6: La seguridad no está fuera, sino en la capacidad de responder a lo imprevisto. ¿Qué harías hoy si no tuvieras miedo?', 1),
(7, 'libertad,opciones,evasión', 'Tipo 7: La verdadera libertad no es huir de lo difícil, sino moverse con él. ¿De qué estás escapando al buscar tantas opciones?', 1),
(8, 'control,poder,protección', 'Tipo 8: La fuerza no es someter, es sostener sin aplastar. ¿Usas tu poder para construir o para demostrar?', 1),
(9, 'armonía,confort,evitación', 'Tipo 9: La paz no es ausencia de conflicto, es presencia plena en medio de él. ¿Qué pequeño desacuerdo estás evitando hoy?', 1);
