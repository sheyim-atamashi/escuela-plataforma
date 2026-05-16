-- =====================================================
-- AGREGAR COLUMNAS FALTANTES A TABLAS EXISTENTES
-- =====================================================
ALTER TABLE respuestas_estandar ADD COLUMN es_canonico BOOLEAN DEFAULT 0;
ALTER TABLE respuestas_estandar ADD COLUMN tradicion TEXT;

ALTER TABLE citas_celebres ADD COLUMN es_canonico BOOLEAN DEFAULT 0;
ALTER TABLE citas_celebres ADD COLUMN tradicion TEXT;

ALTER TABLE parabolas_hermes ADD COLUMN es_canonico BOOLEAN DEFAULT 0;
ALTER TABLE parabolas_hermes ADD COLUMN tradicion TEXT;

ALTER TABLE ensenanza_dialectica ADD COLUMN contexto_cultural TEXT;
ALTER TABLE ensenanza_dialectica ADD COLUMN creado_por_uuid TEXT;
ALTER TABLE ensenanza_dialectica ADD COLUMN aprobado BOOLEAN DEFAULT 1;
ALTER TABLE ensenanza_dialectica ADD COLUMN nivel_asociado INTEGER DEFAULT 0;

-- =====================================================
-- INSERCIONES DE CONTENIDO (con OR IGNORE)
-- =====================================================
INSERT OR IGNORE INTO respuestas_estandar (palabras_clave, respuesta, tradicion, es_canonico) VALUES
('yo,identidad,personalidad', 'Ouspensky: "El hombre no tiene un Yo único, sino muchos ''yoes'' que cambian constantemente." Observa cuántos ''tú'' aparecen en un día. ¿Puedes recordarte a ti mismo ahora?', 'ouspensky', 1),
('evolución,evolucionar,cambiar', 'La evolución posible no es automática. Ouspensky enseñó que requiere un centro magnético y trabajo consciente. ¿Has empezado a construir el tuyo con pequeños hechos?', 'ouspensky', 1),
('escuela,enseñanza,maestro', 'Una escuela real no da respuestas, muestra cómo buscarlas. Fragmentos de una enseñanza desconocida son eso: fragmentos. ¿Quieres juntar los tuyos?', 'ouspensky', 1),
('sueño,dormido,inconsciente', 'El hombre no nace despierto. La mayoría vive en sueño. El primer paso es darse cuenta de que se duerme. ¿Notas ahora que estabas sonámbulo?', 'ouspensky', 1),
('voluntad,control,decisión', 'La voluntad no se ordena, se construye con pequeñas victorias sobre la mecánica. ¿Has hecho algo hoy que no te apeteciera, solo porque tú quisiste?', 'ouspensky', 1),
('registro,inscripción,primer paso', 'Registrarse es el primer acto de voluntad: reconocer que no puedes solo y que necesitas una escuela. ¿Te atreves a dar ese paso?', 'general', 1),
('ciclo,dominación,elementos,nutrición,agotamiento', 'Esa enseñanza pertenece a niveles intermedios de la Escuela, después de haber completado los primeros cinco niveles. Si te registras y avanzas, llegarás a ella. ¿Quieres dar el primer paso?', 'gurdjieff-china', 1);

INSERT OR IGNORE INTO citas_celebres (autor, cita, palabras_clave, tradicion, es_canonico) VALUES
('P.D. Ouspensky', 'La única manera de cambiar es darse cuenta de que no se puede cambiar por sí mismo; se necesita una escuela.', 'cambio,escuela,solo', 'ouspensky', 1),
('G.I. Gurdjieff', 'El hombre es una máquina. Todas sus acciones son automáticas. Para salir de la máquina, debe crear un alma.', 'máquina,alma,automático', 'gurdjieff', 1),
('P.D. Ouspensky', 'El centro magnético no se hace, se forma solo cuando se acumulan suficientes fragmentos de verdad.', 'magnetismo,verdad,búsqueda', 'ouspensky', 1),
('G.I. Gurdjieff', 'Recuerda que no recuerdas. Ese es el primer recordatorio.', 'recuerdo,autobservación', 'gurdjieff', 1);

INSERT OR IGNORE INTO parabolas_hermes (palabras_clave, parabola, tradicion, es_canonico) VALUES
('carruaje,caballo,cochero,amo', 'El carruaje es el cuerpo, el caballo las emociones, el cochero la mente y el amo el verdadero Yo. La mayoría vive sin amo, con el caballo desbocado y el cochero dormido. Ouspensky enseñó a despertar al cochero. ¿Has oído hablar del amo dentro de ti?', 'ouspensky', 1),
('fraccionamiento,múltiple', 'Imagina un hombre que se llama Pedro por la mañana, Juan al mediodía y Nadie por la noche. Eres muchos, no uno. La enseñanza desconocida muestra cómo unificar. ¿Quieres empezar a verte como fragmento?', 'ouspensky', 1);

INSERT OR IGNORE INTO ensenanza_dialectica (concepto, ejemplo_dialectico, pregunta, respuesta, palabras_clave, nivel_asociado, tradicion, es_canonico, contexto_cultural) VALUES
('Continuidad de propósito', 'Un hombre decide hacer dieta. Por la mañana lo tiene claro; al mediodía come lo primero que ve; por la noche se olvida de su propósito. Cree que quiere adelgazar, pero en realidad le sucede comer.', '¿Cuántas veces has cambiado de decisión hoy sin darte cuenta?', 'La continuidad de propósito no es un deseo, es un acto. Solo se cultiva con pequeñas victorias sobre la mecánica. ¿Qué pequeña acción incómoda harás ahora solo porque tú quieres?', 'propósito,continuidad,decisión,voluntad,cambio', 1, 'atamashi', 1, 'general'),
('Los muchos yoes', 'Pedro por la mañana es amable; al mediodía, irritado; por la noche, generoso. Cada uno cree ser el verdadero Pedro, pero ninguno lo es.', '¿Quién eres realmente cuando ninguno de esos personajes dura más de unas horas?', 'No hay un yo fijo, sino una galería de personajes que cambian según las circunstancias. El trabajo consiste en observar sin identificarte con ninguno.', 'yo,personalidad,identidad,múltiple', 1, 'ouspensky', 1, 'general'),
('El carruaje, el caballo y el cochero', 'Un carruaje tirado por un caballo desbocado, con un cochero dormido y un amo invisible en el interior. El carruaje es el cuerpo, el caballo las emociones, el cochero la mente, y el amo el verdadero Yo.', '¿Quién conduce tu vida: el caballo, el cochero dormido o nadie?', 'El primer paso es despertar al cochero. La Escuela enseña a recordarse a sí mismo para que el amo pueda tomar las riendas.', 'carruaje,caballo,cochero,amo,voluntad', 2, 'gurdjieff', 1, 'general'),
('Centro emocional y fuego', 'En medicina china, el fuego corresponde al corazón y al centro emocional superior. Pero el hombre común vive en el fuego del plexo solar: emociones reactivas, pasiones descontroladas.', '¿Tu "fuego" te quema o te ilumina?', 'La Escuela enseña a transmutar el fuego inferior en llama superior mediante ejercicios de auto-recordación.', 'fuego,corazón,emocional,centro', 3, 'gurdjieff-china', 1, 'general'),
('Las dos tierras del intelecto', 'El centro intelectual inferior (estrella 2, ceniza volcánica) es la mente lógica dual. El superior (estrella 8, sal marina) es la intuición sintética.', '¿Usas tu mente como ceniza que entierra o como sal que da sabor?', 'La Escuela enseña a cultivar la sal marina: el intelecto que no separa, sino que une.', 'tierra,intelecto,mente,dualidad', 5, 'gurdjieff-china', 1, 'general'),
('El umbral que no se ve', 'Un viajero llega a una puerta enorme. La empuja, pero no cede. Un guardián le dice: "No la empujes, gírate y da un paso atrás". El viajero se gira, da un paso y la puerta se abre sola.', '¿Qué "puerta" llevas tiempo empujando sin darte cuenta de que el primer paso es hacia atrás?', 'Registrarse en la Escuela es ese paso atrás. Parece retroceder, pero es la única manera de que la puerta se abra.', 'registro,puerta,primer paso,inscripción', 0, 'atamashi', 0, 'es'),
('El miedo al ridículo', 'Un hombre quería volar, pero nunca saltaba porque le daba vergüenza caer. Un sabio le dijo: "Todos los que vuelan han caído antes. La diferencia es que se levantaron y rieron de sí mismos".', '¿Qué estarías haciendo ahora si no te importara hacer el ridículo?', 'El miedo a caer es el mayor enemigo del crecimiento. La Escuela es un campo de pruebas donde está permitido fallar.', 'miedo,ridículo,caer,volar,fracaso', 0, 'latam', 0, 'es'),
('Centros y elementos: una pista', 'En la medicina china antigua, las emociones y funciones del cuerpo se agrupan en cinco elementos. Gurdjieff descubrió que esos elementos corresponden a sus centros psicológicos.', '¿Quieres saber qué elemento rige tu forma de pensar o sentir? Eso se enseña dentro de la Escuela, no en el vestíbulo.', 'Hay una llave que conecta el fuego con el corazón emocional, la tierra con el intelecto, el metal con el instinto, el agua con la sexualidad y la madera con el movimiento. Para usarla, necesitas prácticas guiadas. ¿Te animas a registrarte?', 'elementos,centros,medicina china', 0, 'gurdjieff-china', 1, 'zh'),
('El fuego del corazón en la vida diaria', 'En la medicina china, el corazón alberga el shen (espíritu). Cuando el fuego está equilibrado, la persona es alegre y serena; cuando está desequilibrado, aparece insomnio o risa nerviosa.', '¿Tu corazón está en calma o en llamas?', 'La Escuela enseña ejercicios sencillos para regular el fuego emocional sin suprimir la emoción. ¿Quieres aprender uno ahora? Regístrate y te lo mostramos.', 'corazón,fuego,emoción,shen', 0, 'medicina china', 0, 'zh'),
('La tierra del intelecto en la práctica', 'El bazo (tierra) rige la reflexión y la memorización. Una tierra sana digiere ideas; una tierra débil genera rumiación o preocupación excesiva.', '¿Tu mente digiere bien lo que aprendes o regurgita siempre lo mismo?', 'Hay prácticas para fortalecer la tierra intelectual. No son estudios teóricos, sino ejercicios de atención. Dentro de la Escuela los encontrarás. ¿Te atreves a probar?', 'intelecto,tierra,mente,preocupación', 0, 'medicina china', 0, 'zh');
