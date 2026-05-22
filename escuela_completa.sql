PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE beings (
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
INSERT INTO beings VALUES(1,'8298ac6e-5348-4bba-9570-8e6a8f4c4ee0','Atamashi','$argon2id$v=19$m=1024,t=2,p=2$zZPg87dT4nv0hDtgJBdaFQ$+27/KjPEw3hN+6/BPC+bDRbntVeSlEYZYqXHFSut5UA','human',0,NULL,NULL,0,NULL,22,1,22,'superusuario',1,'es','latam',1,'Zona Verde 45D','USD',0,'backup_8298ac6e-5348-4bba-9570-8e6a8f4c4ee0_1778676464.018238.enc','2026-05-12 18:28:14');
INSERT INTO beings VALUES(2,'493ab965-732f-413a-b49f-56df7007204a','Estudiante1','$argon2id$v=19$m=1024,t=2,p=2$BFL5KFGT3OIfSweZtaJHTg$QreGZ9M9q8wJ4OK+KKLOh0CV/cqXlxtmpadNcVF9VLQ','human',0,NULL,NULL,0,NULL,0,1,0,'alumno',0,'es','latam',0,'Zona Verde 45D','USD',0,NULL,'2026-05-13 12:23:32');
INSERT INTO beings VALUES(3,'dfef26ab-39d0-472a-b9c5-e9779c746146','Estudiante2','$argon2id$v=19$m=1024,t=2,p=2$31kijfuaPvA7NBDBrHsjcw$+aR6T56hVxV23Bhma/mg0BybQS3p8tUgC5cOSgEtJLk','human',0,NULL,NULL,0,NULL,0,1,0,'maestro_preparatorio',0,'es','latam',0,'Zona Verde 45D','USD',0,NULL,'2026-05-13 15:07:33');
CREATE TABLE superusuario_control (
                id INTEGER PRIMARY KEY,
                superusuario_uuid TEXT UNIQUE,
                ultimo_acceso TIMESTAMP,
                fecha_expira TIMESTAMP,
                clave_emergencia TEXT,
                activo BOOLEAN DEFAULT 1
            , nota TEXT DEFAULT '');
INSERT INTO superusuario_control VALUES(1,'8298ac6e-5348-4bba-9570-8e6a8f4c4ee0','2026-05-14T06:37:56.800956',NULL,NULL,1,'');
CREATE TABLE superusuario_exclusiones (
                id INTEGER PRIMARY KEY,
                superusuario_uuid TEXT,
                fecha_exclusion TIMESTAMP,
                motivo TEXT,
                puede_reingresar BOOLEAN DEFAULT 1,
                fecha_reingreso TIMESTAMP
            );
CREATE TABLE notificaciones (
                id INTEGER PRIMARY KEY,
                usuario_uuid TEXT,
                mensaje TEXT,
                leido BOOLEAN DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE modelos_androides (
                id INTEGER PRIMARY KEY,
                nombre_modelo TEXT UNIQUE,
                fabricante TEXT,
                fecha_solicitud TIMESTAMP,
                fecha_decision TIMESTAMP,
                decision TEXT,
                condiciones TEXT,
                honorario_pagado NUMERIC,
                moneda TEXT,
                evaluadores TEXT
            );
CREATE TABLE consejo_sorteos (
                id INTEGER PRIMARY KEY,
                fecha_sorteo TIMESTAMP,
                semilla TEXT,
                miembros_uuids TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_expiracion TIMESTAMP
            );
CREATE TABLE propuestas_consejo (
                id INTEGER PRIMARY KEY,
                tipo TEXT,
                descripcion TEXT,
                superusuario_proponente_uuid TEXT,
                ciudad_destino TEXT,
                candidato_uuid TEXT,
                fecha_propuesta TIMESTAMP,
                fecha_votacion TIMESTAMP,
                votos_favor INTEGER DEFAULT 0,
                votos_contra INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'pendiente'
            );
CREATE TABLE votos_consejo (
                id INTEGER PRIMARY KEY,
                propuesta_id INTEGER,
                consejero_uuid TEXT,
                voto BOOLEAN,
                fecha_voto TIMESTAMP,
                FOREIGN KEY (propuesta_id) REFERENCES propuestas_consejo(id)
            );
CREATE TABLE ciudades_fundadores (
                id INTEGER PRIMARY KEY,
                ciudad_nombre TEXT,
                maestro_fundador_uuid TEXT,
                fecha_asignacion TIMESTAMP,
                metodo TEXT
            );
CREATE TABLE niveles (
                id INTEGER PRIMARY KEY,
                center_code TEXT,
                center_part TEXT,
                name TEXT
            );
INSERT INTO niveles VALUES(1,'MAGO','voluntad','El Mago');
INSERT INTO niveles VALUES(2,'CEI','mecanica','Automatismo afectivo');
INSERT INTO niveles VALUES(3,'CEI','emocional','Atención plena al sentir');
INSERT INTO niveles VALUES(4,'CEI','intelectual','Voluntad emocional');
INSERT INTO niveles VALUES(5,'CES','mecanica','Impulso estético/místico');
INSERT INTO niveles VALUES(6,'CES','emocional','Amor/devoción');
INSERT INTO niveles VALUES(7,'CES','intelectual','Arte/símbolo/mística');
INSERT INTO niveles VALUES(8,'CII','mecanica','Memoria');
INSERT INTO niveles VALUES(9,'CII','emocional','Asociación con interés');
INSERT INTO niveles VALUES(10,'CII','intelectual','Razonamiento lógico');
INSERT INTO niveles VALUES(11,'CIS','mecanica','Datos sin procesar');
INSERT INTO niveles VALUES(12,'CIS','emocional','Método Silva/meditación');
INSERT INTO niveles VALUES(13,'CIS','intelectual','Símbolos/mitos/koans');
INSERT INTO niveles VALUES(14,'CS','mecanica','Reproducción');
INSERT INTO niveles VALUES(15,'CS','emocional','Búsqueda de pareja');
INSERT INTO niveles VALUES(16,'CS','intelectual','Sublimación creadora');
INSERT INTO niveles VALUES(17,'CI','mecanica','Funciones vegetativas');
INSERT INTO niveles VALUES(18,'CI','emocional','Emoción instintiva');
INSERT INTO niveles VALUES(19,'CI','intelectual','Inteligencia de supervivencia');
INSERT INTO niveles VALUES(20,'CM','mecanica','Imitación automática');
INSERT INTO niveles VALUES(21,'CM','emocional','Movimiento con atención plena');
INSERT INTO niveles VALUES(22,'CM','intelectual','Motricidad fina/aprendizaje complejo');
CREATE TABLE learning_cycles (
                id INTEGER PRIMARY KEY,
                student_id INTEGER,
                level_id INTEGER,
                cycle_number INTEGER,
                master_id INTEGER,
                entorno TEXT,
                situacion TEXT,
                reto TEXT,
                logro_del_ciclo TEXT,
                objetivo_alcanzado BOOLEAN DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
CREATE TABLE reflections (
                id INTEGER PRIMARY KEY,
                cycle_id INTEGER,
                reflection_type TEXT,
                content TEXT,
                format TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE criticas_anonimas (
                id INTEGER PRIMARY KEY,
                grupo_id INTEGER,
                nivel_id INTEGER,
                destinatario_uuid TEXT,
                critica TEXT,
                fecha_escritura TIMESTAMP,
                fecha_deposito TIMESTAMP,
                fecha_entrega TIMESTAMP,
                recibida_por_destinatario BOOLEAN DEFAULT 0
            );
CREATE TABLE vestibulo_hilos (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO vestibulo_hilos VALUES(1,'Encuentro','Jose Jesus Leal Munoz','2026-05-15 14:33:33');
CREATE TABLE vestibulo_mensajes (
    id INTEGER PRIMARY KEY,
    hilo_id INTEGER,
    autor TEXT NOT NULL,
    contenido TEXT NOT NULL,
    es_respuesta BOOLEAN DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO vestibulo_mensajes VALUES(1,1,'Jose Jesus Leal Munoz',replace('voluntad\n','\n',char(10)),0,'2026-05-15 14:33:33');
CREATE TABLE respuestas_estandar (
    id INTEGER PRIMARY KEY,
    palabras_clave TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    activa BOOLEAN DEFAULT 1,
    veces_usada INTEGER DEFAULT 0,
    es_canonico BOOLEAN DEFAULT 0,
    tradicion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO respuestas_estandar VALUES(1,'yo,identidad,personalidad','Ouspensky: "El hombre no tiene un Yo único, sino muchos ''yoes'' que cambian constantemente." Observa cuántos ''tú'' aparecen en un día. ¿Puedes recordarte a ti mismo ahora?',1,0,1,'ouspensky','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(2,'evolución,evolucionar,cambiar','La evolución posible no es automática. Ouspensky enseñó que requiere un centro magnético y trabajo consciente. ¿Has empezado a construir el tuyo con pequeños hechos?',1,0,1,'ouspensky','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(3,'escuela,enseñanza,maestro','Una escuela real no da respuestas, muestra cómo buscarlas. Fragmentos de una enseñanza desconocida son eso: fragmentos. ¿Quieres juntar los tuyos?',1,0,1,'ouspensky','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(4,'sueño,dormido,inconsciente','El hombre no nace despierto. La mayoría vive en sueño. El primer paso es darse cuenta de que se duerme. ¿Notas ahora que estabas sonámbulo?',1,0,1,'ouspensky','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(5,'voluntad,control,decisión','La voluntad no se ordena, se construye con pequeñas victorias sobre la mecánica. ¿Has hecho algo hoy que no te apeteciera, solo porque tú quisiste?',1,0,1,'ouspensky','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(6,'registro,inscripción,primer paso','Registrarse es el primer acto de voluntad: reconocer que no puedes solo y que necesitas una escuela. ¿Te atreves a dar ese paso?',1,0,1,'general','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(7,'ciclo,dominación,elementos,nutrición,agotamiento','Esa enseñanza pertenece a niveles intermedios de la Escuela, después de haber completado los primeros cinco niveles. Si te registras y avanzas, llegarás a ella. ¿Quieres dar el primer paso?',1,0,1,'gurdjieff-china','2026-05-15 11:07:36');
INSERT INTO respuestas_estandar VALUES(8,'yo,identidad,personalidad','Ouspensky: "El hombre no tiene un Yo único, sino muchos ''yoes'' que cambian constantemente." Observa cuántos ''tú'' aparecen en un día. ¿Puedes recordarte a ti mismo ahora?',1,0,1,'ouspensky','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(9,'evolución,evolucionar,cambiar','La evolución posible no es automática. Ouspensky enseñó que requiere un centro magnético y trabajo consciente. ¿Has empezado a construir el tuyo con pequeños hechos?',1,0,1,'ouspensky','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(10,'escuela,enseñanza,maestro','Una escuela real no da respuestas, muestra cómo buscarlas. Fragmentos de una enseñanza desconocida son eso: fragmentos. ¿Quieres juntar los tuyos?',1,0,1,'ouspensky','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(11,'sueño,dormido,inconsciente','El hombre no nace despierto. La mayoría vive en sueño. El primer paso es darse cuenta de que se duerme. ¿Notas ahora que estabas sonámbulo?',1,0,1,'ouspensky','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(12,'voluntad,control,decisión','La voluntad no se ordena, se construye con pequeñas victorias sobre la mecánica. ¿Has hecho algo hoy que no te apeteciera, solo porque tú quisiste?',1,0,1,'ouspensky','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(13,'registro,inscripción,primer paso','Registrarse es el primer acto de voluntad: reconocer que no puedes solo y que necesitas una escuela. ¿Te atreves a dar ese paso?',1,0,1,'general','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(14,'ciclo,dominación,elementos,nutrición,agotamiento','Esa enseñanza pertenece a niveles intermedios de la Escuela, después de haber completado los primeros cinco niveles. Si te registras y avanzas, llegarás a ella. ¿Quieres dar el primer paso?',1,0,1,'gurdjieff-china','2026-05-15 11:13:50');
INSERT INTO respuestas_estandar VALUES(15,'yo,identidad,personalidad','Ouspensky: "El hombre no tiene un Yo único, sino muchos ''yoes'' que cambian constantemente." Observa cuántos ''tú'' aparecen en un día. ¿Puedes recordarte a ti mismo ahora?',1,0,1,'ouspensky','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(16,'evolución,evolucionar,cambiar','La evolución posible no es automática. Ouspensky enseñó que requiere un centro magnético y trabajo consciente. ¿Has empezado a construir el tuyo con pequeños hechos?',1,0,1,'ouspensky','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(17,'escuela,enseñanza,maestro','Una escuela real no da respuestas, muestra cómo buscarlas. Fragmentos de una enseñanza desconocida son eso: fragmentos. ¿Quieres juntar los tuyos?',1,0,1,'ouspensky','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(18,'sueño,dormido,inconsciente','El hombre no nace despierto. La mayoría vive en sueño. El primer paso es darse cuenta de que se duerme. ¿Notas ahora que estabas sonámbulo?',1,0,1,'ouspensky','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(19,'voluntad,control,decisión','La voluntad no se ordena, se construye con pequeñas victorias sobre la mecánica. ¿Has hecho algo hoy que no te apeteciera, solo porque tú quisiste?',1,0,1,'ouspensky','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(20,'registro,inscripción,primer paso','Registrarse es el primer acto de voluntad: reconocer que no puedes solo y que necesitas una escuela. ¿Te atreves a dar ese paso?',1,0,1,'general','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(21,'ciclo,dominación,elementos,nutrición,agotamiento','Esa enseñanza pertenece a niveles intermedios de la Escuela, después de haber completado los primeros cinco niveles. Si te registras y avanzas, llegarás a ella. ¿Quieres dar el primer paso?',1,0,1,'gurdjieff-china','2026-05-15 11:29:41');
INSERT INTO respuestas_estandar VALUES(22,'voluntad,control,decisión','La voluntad no se ordena, se construye con pequeñas victorias sobre la mecánica. ¿Has hecho algo hoy que no te apeteciera, solo porque tú quisiste?',1,0,1,'ouspensky','2026-05-15 15:12:22');
INSERT INTO respuestas_estandar VALUES(23,'yo,identidad,personalidad','Ouspensky: "El hombre no tiene un Yo único, sino muchos ''yoes'' que cambian constantemente." Observa cuántos ''tú'' aparecen en un día. ¿Puedes recordarte a ti mismo ahora?',1,0,1,'ouspensky','2026-05-15 15:12:22');
INSERT INTO respuestas_estandar VALUES(24,'evolución,evolucionar,cambiar','La evolución posible no es automática. Ouspensky enseñó que requiere un centro magnético y trabajo consciente. ¿Has empezado a construir el tuyo con pequeños hechos?',1,0,1,'ouspensky','2026-05-15 15:12:22');
INSERT INTO respuestas_estandar VALUES(25,'registro,inscripción,primer paso','Registrarse es el primer acto de voluntad: reconocer que no puedes solo y que necesitas una escuela. ¿Te atreves a dar ese paso?',1,0,1,'general','2026-05-15 15:12:22');
INSERT INTO respuestas_estandar VALUES(26,'default,ayuda,socorro,qué es','Soy Hermes, el mensajero. Cada pregunta es una semilla. ¿La riegas con acción o solo con palabras?',1,0,0,NULL,'2026-05-15 22:08:33');
CREATE TABLE citas_celebres (
    id INTEGER PRIMARY KEY,
    autor TEXT NOT NULL,
    cita TEXT NOT NULL,
    palabras_clave TEXT NOT NULL,
    tradicion TEXT,
    es_canonico BOOLEAN DEFAULT 0,
    activa BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO citas_celebres VALUES(1,'P.D. Ouspensky','La única manera de cambiar es darse cuenta de que no se puede cambiar por sí mismo; se necesita una escuela.','cambio,escuela,solo','ouspensky',1,1,'2026-05-15 11:07:36');
INSERT INTO citas_celebres VALUES(2,'G.I. Gurdjieff','El hombre es una máquina. Todas sus acciones son automáticas. Para salir de la máquina, debe crear un alma.','máquina,alma,automático','gurdjieff',1,1,'2026-05-15 11:07:36');
INSERT INTO citas_celebres VALUES(3,'P.D. Ouspensky','El centro magnético no se hace, se forma solo cuando se acumulan suficientes fragmentos de verdad.','magnetismo,verdad,búsqueda','ouspensky',1,1,'2026-05-15 11:07:36');
INSERT INTO citas_celebres VALUES(4,'G.I. Gurdjieff','Recuerda que no recuerdas. Ese es el primer recordatorio.','recuerdo,autobservación','gurdjieff',1,1,'2026-05-15 11:07:36');
INSERT INTO citas_celebres VALUES(5,'P.D. Ouspensky','La única manera de cambiar es darse cuenta de que no se puede cambiar por sí mismo; se necesita una escuela.','cambio,escuela,solo','ouspensky',1,1,'2026-05-15 11:13:50');
INSERT INTO citas_celebres VALUES(6,'G.I. Gurdjieff','El hombre es una máquina. Todas sus acciones son automáticas. Para salir de la máquina, debe crear un alma.','máquina,alma,automático','gurdjieff',1,1,'2026-05-15 11:13:50');
INSERT INTO citas_celebres VALUES(7,'P.D. Ouspensky','El centro magnético no se hace, se forma solo cuando se acumulan suficientes fragmentos de verdad.','magnetismo,verdad,búsqueda','ouspensky',1,1,'2026-05-15 11:13:50');
INSERT INTO citas_celebres VALUES(8,'G.I. Gurdjieff','Recuerda que no recuerdas. Ese es el primer recordatorio.','recuerdo,autobservación','gurdjieff',1,1,'2026-05-15 11:13:50');
INSERT INTO citas_celebres VALUES(9,'P.D. Ouspensky','La única manera de cambiar es darse cuenta de que no se puede cambiar por sí mismo; se necesita una escuela.','cambio,escuela,solo','ouspensky',1,1,'2026-05-15 11:29:41');
INSERT INTO citas_celebres VALUES(10,'G.I. Gurdjieff','El hombre es una máquina. Todas sus acciones son automáticas. Para salir de la máquina, debe crear un alma.','máquina,alma,automático','gurdjieff',1,1,'2026-05-15 11:29:41');
INSERT INTO citas_celebres VALUES(11,'P.D. Ouspensky','El centro magnético no se hace, se forma solo cuando se acumulan suficientes fragmentos de verdad.','magnetismo,verdad,búsqueda','ouspensky',1,1,'2026-05-15 11:29:41');
INSERT INTO citas_celebres VALUES(12,'G.I. Gurdjieff','Recuerda que no recuerdas. Ese es el primer recordatorio.','recuerdo,autobservación','gurdjieff',1,1,'2026-05-15 11:29:41');
CREATE TABLE parabolas_hermes (
    id INTEGER PRIMARY KEY,
    palabras_clave TEXT NOT NULL,
    parabola TEXT NOT NULL,
    tradicion TEXT,
    es_canonico BOOLEAN DEFAULT 0,
    activa BOOLEAN DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO parabolas_hermes VALUES(1,'carruaje,caballo,cochero,amo','El carruaje es el cuerpo, el caballo las emociones, el cochero la mente y el amo el verdadero Yo. La mayoría vive sin amo, con el caballo desbocado y el cochero dormido. Ouspensky enseñó a despertar al cochero. ¿Has oído hablar del amo dentro de ti?','ouspensky',1,1,'2026-05-15 11:07:37');
INSERT INTO parabolas_hermes VALUES(2,'fraccionamiento,múltiple','Imagina un hombre que se llama Pedro por la mañana, Juan al mediodía y Nadie por la noche. Eres muchos, no uno. La enseñanza desconocida muestra cómo unificar. ¿Quieres empezar a verte como fragmento?','ouspensky',1,1,'2026-05-15 11:07:37');
INSERT INTO parabolas_hermes VALUES(3,'carruaje,caballo,cochero,amo','El carruaje es el cuerpo, el caballo las emociones, el cochero la mente y el amo el verdadero Yo. La mayoría vive sin amo, con el caballo desbocado y el cochero dormido. Ouspensky enseñó a despertar al cochero. ¿Has oído hablar del amo dentro de ti?','ouspensky',1,1,'2026-05-15 11:13:50');
INSERT INTO parabolas_hermes VALUES(4,'fraccionamiento,múltiple','Imagina un hombre que se llama Pedro por la mañana, Juan al mediodía y Nadie por la noche. Eres muchos, no uno. La enseñanza desconocida muestra cómo unificar. ¿Quieres empezar a verte como fragmento?','ouspensky',1,1,'2026-05-15 11:13:50');
INSERT INTO parabolas_hermes VALUES(5,'carruaje,caballo,cochero,amo','El carruaje es el cuerpo, el caballo las emociones, el cochero la mente y el amo el verdadero Yo. La mayoría vive sin amo, con el caballo desbocado y el cochero dormido. Ouspensky enseñó a despertar al cochero. ¿Has oído hablar del amo dentro de ti?','ouspensky',1,1,'2026-05-15 11:29:41');
INSERT INTO parabolas_hermes VALUES(6,'fraccionamiento,múltiple','Imagina un hombre que se llama Pedro por la mañana, Juan al mediodía y Nadie por la noche. Eres muchos, no uno. La enseñanza desconocida muestra cómo unificar. ¿Quieres empezar a verte como fragmento?','ouspensky',1,1,'2026-05-15 11:29:41');
CREATE TABLE ensenanza_dialectica (
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
INSERT INTO ensenanza_dialectica VALUES(1,'Continuidad de propósito','Un hombre decide hacer dieta. Por la mañana lo tiene claro; al mediodía come lo primero que ve; por la noche se olvida de su propósito. Cree que quiere adelgazar, pero en realidad le sucede comer.','¿Cuántas veces has cambiado de decisión hoy sin darte cuenta?','La continuidad de propósito no es un deseo, es un acto. Solo se cultiva con pequeñas victorias sobre la mecánica. ¿Qué pequeña acción incómoda harás ahora solo porque tú quieres?','propósito,continuidad,decisión,voluntad,cambio',1,'atamashi',1,NULL,'general',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(2,'Los muchos yoes','Pedro por la mañana es amable; al mediodía, irritado; por la noche, generoso. Cada uno cree ser el verdadero Pedro, pero ninguno lo es.','¿Quién eres realmente cuando ninguno de esos personajes dura más de unas horas?','No hay un yo fijo, sino una galería de personajes que cambian según las circunstancias. El trabajo consiste en observar sin identificarte con ninguno.','yo,personalidad,identidad,múltiple',1,'ouspensky',1,NULL,'general',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(3,'El carruaje, el caballo y el cochero','Un carruaje tirado por un caballo desbocado, con un cochero dormido y un amo invisible en el interior. El carruaje es el cuerpo, el caballo las emociones, el cochero la mente, y el amo el verdadero Yo.','¿Quién conduce tu vida: el caballo, el cochero dormido o nadie?','El primer paso es despertar al cochero. La Escuela enseña a recordarse a sí mismo para que el amo pueda tomar las riendas.','carruaje,caballo,cochero,amo,voluntad',2,'gurdjieff',1,NULL,'general',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(4,'Centro emocional y fuego','En medicina china, el fuego corresponde al corazón y al centro emocional superior. Pero el hombre común vive en el fuego del plexo solar: emociones reactivas, pasiones descontroladas.','¿Tu "fuego" te quema o te ilumina?','La Escuela enseña a transmutar el fuego inferior en llama superior mediante ejercicios de auto-recordación.','fuego,corazón,emocional,centro',3,'gurdjieff-china',1,NULL,'general',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(5,'Las dos tierras del intelecto','El centro intelectual inferior (estrella 2, ceniza volcánica) es la mente lógica dual. El superior (estrella 8, sal marina) es la intuición sintética.','¿Usas tu mente como ceniza que entierra o como sal que da sabor?','La Escuela enseña a cultivar la sal marina: el intelecto que no separa, sino que une.','tierra,intelecto,mente,dualidad',5,'gurdjieff-china',1,NULL,'general',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(6,'El umbral que no se ve','Un viajero llega a una puerta enorme. La empuja, pero no cede. Un guardián le dice: "No la empujes, gírate y da un paso atrás". El viajero se gira, da un paso y la puerta se abre sola.','¿Qué "puerta" llevas tiempo empujando sin darte cuenta de que el primer paso es hacia atrás?','Registrarse en la Escuela es ese paso atrás. Parece retroceder, pero es la única manera de que la puerta se abra.','registro,puerta,primer paso,inscripción',0,'atamashi',0,NULL,'es',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(7,'El miedo al ridículo','Un hombre quería volar, pero nunca saltaba porque le daba vergüenza caer. Un sabio le dijo: "Todos los que vuelan han caído antes. La diferencia es que se levantaron y rieron de sí mismos".','¿Qué estarías haciendo ahora si no te importara hacer el ridículo?','El miedo a caer es el mayor enemigo del crecimiento. La Escuela es un campo de pruebas donde está permitido fallar.','miedo,ridículo,caer,volar,fracaso',0,'latam',0,NULL,'es',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(8,'Centros y elementos: una pista','En la medicina china antigua, las emociones y funciones del cuerpo se agrupan en cinco elementos. Gurdjieff descubrió que esos elementos corresponden a sus centros psicológicos.','¿Quieres saber qué elemento rige tu forma de pensar o sentir? Eso se enseña dentro de la Escuela, no en el vestíbulo.','Hay una llave que conecta el fuego con el corazón emocional, la tierra con el intelecto, el metal con el instinto, el agua con la sexualidad y la madera con el movimiento. Para usarla, necesitas prácticas guiadas. ¿Te animas a registrarte?','elementos,centros,medicina china',0,'gurdjieff-china',1,NULL,'zh',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(9,'El fuego del corazón en la vida diaria','En la medicina china, el corazón alberga el shen (espíritu). Cuando el fuego está equilibrado, la persona es alegre y serena; cuando está desequilibrado, aparece insomnio o risa nerviosa.','¿Tu corazón está en calma o en llamas?','La Escuela enseña ejercicios sencillos para regular el fuego emocional sin suprimir la emoción. ¿Quieres aprender uno ahora? Regístrate y te lo mostramos.','corazón,fuego,emoción,shen',0,'medicina china',0,NULL,'zh',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(10,'La tierra del intelecto en la práctica','El bazo (tierra) rige la reflexión y la memorización. Una tierra sana digiere ideas; una tierra débil genera rumiación o preocupación excesiva.','¿Tu mente digiere bien lo que aprendes o regurgita siempre lo mismo?','Hay prácticas para fortalecer la tierra intelectual. No son estudios teóricos, sino ejercicios de atención. Dentro de la Escuela los encontrarás. ¿Te atreves a probar?','intelecto,tierra,mente,preocupación',0,'medicina china',0,NULL,'zh',1,1,0,'2026-05-15 11:07:37');
INSERT INTO ensenanza_dialectica VALUES(11,'Continuidad de propósito','Un hombre decide hacer dieta. Por la mañana lo tiene claro; al mediodía come lo primero que ve; por la noche se olvida de su propósito. Cree que quiere adelgazar, pero en realidad le sucede comer.','¿Cuántas veces has cambiado de decisión hoy sin darte cuenta?','La continuidad de propósito no es un deseo, es un acto. Solo se cultiva con pequeñas victorias sobre la mecánica. ¿Qué pequeña acción incómoda harás ahora solo porque tú quieres?','propósito,continuidad,decisión,voluntad,cambio',1,'atamashi',1,NULL,'general',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(12,'Los muchos yoes','Pedro por la mañana es amable; al mediodía, irritado; por la noche, generoso. Cada uno cree ser el verdadero Pedro, pero ninguno lo es.','¿Quién eres realmente cuando ninguno de esos personajes dura más de unas horas?','No hay un yo fijo, sino una galería de personajes que cambian según las circunstancias. El trabajo consiste en observar sin identificarte con ninguno.','yo,personalidad,identidad,múltiple',1,'ouspensky',1,NULL,'general',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(13,'El carruaje, el caballo y el cochero','Un carruaje tirado por un caballo desbocado, con un cochero dormido y un amo invisible en el interior. El carruaje es el cuerpo, el caballo las emociones, el cochero la mente, y el amo el verdadero Yo.','¿Quién conduce tu vida: el caballo, el cochero dormido o nadie?','El primer paso es despertar al cochero. La Escuela enseña a recordarse a sí mismo para que el amo pueda tomar las riendas.','carruaje,caballo,cochero,amo,voluntad',2,'gurdjieff',1,NULL,'general',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(14,'Centro emocional y fuego','En medicina china, el fuego corresponde al corazón y al centro emocional superior. Pero el hombre común vive en el fuego del plexo solar: emociones reactivas, pasiones descontroladas.','¿Tu "fuego" te quema o te ilumina?','La Escuela enseña a transmutar el fuego inferior en llama superior mediante ejercicios de auto-recordación.','fuego,corazón,emocional,centro',3,'gurdjieff-china',1,NULL,'general',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(15,'Las dos tierras del intelecto','El centro intelectual inferior (estrella 2, ceniza volcánica) es la mente lógica dual. El superior (estrella 8, sal marina) es la intuición sintética.','¿Usas tu mente como ceniza que entierra o como sal que da sabor?','La Escuela enseña a cultivar la sal marina: el intelecto que no separa, sino que une.','tierra,intelecto,mente,dualidad',5,'gurdjieff-china',1,NULL,'general',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(16,'El umbral que no se ve','Un viajero llega a una puerta enorme. La empuja, pero no cede. Un guardián le dice: "No la empujes, gírate y da un paso atrás". El viajero se gira, da un paso y la puerta se abre sola.','¿Qué "puerta" llevas tiempo empujando sin darte cuenta de que el primer paso es hacia atrás?','Registrarse en la Escuela es ese paso atrás. Parece retroceder, pero es la única manera de que la puerta se abra.','registro,puerta,primer paso,inscripción',0,'atamashi',0,NULL,'es',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(17,'El miedo al ridículo','Un hombre quería volar, pero nunca saltaba porque le daba vergüenza caer. Un sabio le dijo: "Todos los que vuelan han caído antes. La diferencia es que se levantaron y rieron de sí mismos".','¿Qué estarías haciendo ahora si no te importara hacer el ridículo?','El miedo a caer es el mayor enemigo del crecimiento. La Escuela es un campo de pruebas donde está permitido fallar.','miedo,ridículo,caer,volar,fracaso',0,'latam',0,NULL,'es',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(18,'Centros y elementos: una pista','En la medicina china antigua, las emociones y funciones del cuerpo se agrupan en cinco elementos. Gurdjieff descubrió que esos elementos corresponden a sus centros psicológicos.','¿Quieres saber qué elemento rige tu forma de pensar o sentir? Eso se enseña dentro de la Escuela, no en el vestíbulo.','Hay una llave que conecta el fuego con el corazón emocional, la tierra con el intelecto, el metal con el instinto, el agua con la sexualidad y la madera con el movimiento. Para usarla, necesitas prácticas guiadas. ¿Te animas a registrarte?','elementos,centros,medicina china',0,'gurdjieff-china',1,NULL,'zh',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(19,'El fuego del corazón en la vida diaria','En la medicina china, el corazón alberga el shen (espíritu). Cuando el fuego está equilibrado, la persona es alegre y serena; cuando está desequilibrado, aparece insomnio o risa nerviosa.','¿Tu corazón está en calma o en llamas?','La Escuela enseña ejercicios sencillos para regular el fuego emocional sin suprimir la emoción. ¿Quieres aprender uno ahora? Regístrate y te lo mostramos.','corazón,fuego,emoción,shen',0,'medicina china',0,NULL,'zh',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(20,'La tierra del intelecto en la práctica','El bazo (tierra) rige la reflexión y la memorización. Una tierra sana digiere ideas; una tierra débil genera rumiación o preocupación excesiva.','¿Tu mente digiere bien lo que aprendes o regurgita siempre lo mismo?','Hay prácticas para fortalecer la tierra intelectual. No son estudios teóricos, sino ejercicios de atención. Dentro de la Escuela los encontrarás. ¿Te atreves a probar?','intelecto,tierra,mente,preocupación',0,'medicina china',0,NULL,'zh',1,1,0,'2026-05-15 11:13:50');
INSERT INTO ensenanza_dialectica VALUES(21,'Continuidad de propósito','Un hombre decide hacer dieta. Por la mañana lo tiene claro; al mediodía come lo primero que ve; por la noche se olvida de su propósito. Cree que quiere adelgazar, pero en realidad le sucede comer.','¿Cuántas veces has cambiado de decisión hoy sin darte cuenta?','La continuidad de propósito no es un deseo, es un acto. Solo se cultiva con pequeñas victorias sobre la mecánica. ¿Qué pequeña acción incómoda harás ahora solo porque tú quieres?','propósito,continuidad,decisión,voluntad,cambio',1,'atamashi',1,NULL,'general',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(22,'Los muchos yoes','Pedro por la mañana es amable; al mediodía, irritado; por la noche, generoso. Cada uno cree ser el verdadero Pedro, pero ninguno lo es.','¿Quién eres realmente cuando ninguno de esos personajes dura más de unas horas?','No hay un yo fijo, sino una galería de personajes que cambian según las circunstancias. El trabajo consiste en observar sin identificarte con ninguno.','yo,personalidad,identidad,múltiple',1,'ouspensky',1,NULL,'general',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(23,'El carruaje, el caballo y el cochero','Un carruaje tirado por un caballo desbocado, con un cochero dormido y un amo invisible en el interior. El carruaje es el cuerpo, el caballo las emociones, el cochero la mente, y el amo el verdadero Yo.','¿Quién conduce tu vida: el caballo, el cochero dormido o nadie?','El primer paso es despertar al cochero. La Escuela enseña a recordarse a sí mismo para que el amo pueda tomar las riendas.','carruaje,caballo,cochero,amo,voluntad',2,'gurdjieff',1,NULL,'general',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(24,'Centro emocional y fuego','En medicina china, el fuego corresponde al corazón y al centro emocional superior. Pero el hombre común vive en el fuego del plexo solar: emociones reactivas, pasiones descontroladas.','¿Tu "fuego" te quema o te ilumina?','La Escuela enseña a transmutar el fuego inferior en llama superior mediante ejercicios de auto-recordación.','fuego,corazón,emocional,centro',3,'gurdjieff-china',1,NULL,'general',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(25,'Las dos tierras del intelecto','El centro intelectual inferior (estrella 2, ceniza volcánica) es la mente lógica dual. El superior (estrella 8, sal marina) es la intuición sintética.','¿Usas tu mente como ceniza que entierra o como sal que da sabor?','La Escuela enseña a cultivar la sal marina: el intelecto que no separa, sino que une.','tierra,intelecto,mente,dualidad',5,'gurdjieff-china',1,NULL,'general',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(26,'El umbral que no se ve','Un viajero llega a una puerta enorme. La empuja, pero no cede. Un guardián le dice: "No la empujes, gírate y da un paso atrás". El viajero se gira, da un paso y la puerta se abre sola.','¿Qué "puerta" llevas tiempo empujando sin darte cuenta de que el primer paso es hacia atrás?','Registrarse en la Escuela es ese paso atrás. Parece retroceder, pero es la única manera de que la puerta se abra.','registro,puerta,primer paso,inscripción',0,'atamashi',0,NULL,'es',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(27,'El miedo al ridículo','Un hombre quería volar, pero nunca saltaba porque le daba vergüenza caer. Un sabio le dijo: "Todos los que vuelan han caído antes. La diferencia es que se levantaron y rieron de sí mismos".','¿Qué estarías haciendo ahora si no te importara hacer el ridículo?','El miedo a caer es el mayor enemigo del crecimiento. La Escuela es un campo de pruebas donde está permitido fallar.','miedo,ridículo,caer,volar,fracaso',0,'latam',0,NULL,'es',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(28,'Centros y elementos: una pista','En la medicina china antigua, las emociones y funciones del cuerpo se agrupan en cinco elementos. Gurdjieff descubrió que esos elementos corresponden a sus centros psicológicos.','¿Quieres saber qué elemento rige tu forma de pensar o sentir? Eso se enseña dentro de la Escuela, no en el vestíbulo.','Hay una llave que conecta el fuego con el corazón emocional, la tierra con el intelecto, el metal con el instinto, el agua con la sexualidad y la madera con el movimiento. Para usarla, necesitas prácticas guiadas. ¿Te animas a registrarte?','elementos,centros,medicina china',0,'gurdjieff-china',1,NULL,'zh',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(29,'El fuego del corazón en la vida diaria','En la medicina china, el corazón alberga el shen (espíritu). Cuando el fuego está equilibrado, la persona es alegre y serena; cuando está desequilibrado, aparece insomnio o risa nerviosa.','¿Tu corazón está en calma o en llamas?','La Escuela enseña ejercicios sencillos para regular el fuego emocional sin suprimir la emoción. ¿Quieres aprender uno ahora? Regístrate y te lo mostramos.','corazón,fuego,emoción,shen',0,'medicina china',0,NULL,'zh',1,1,0,'2026-05-15 11:29:41');
INSERT INTO ensenanza_dialectica VALUES(30,'La tierra del intelecto en la práctica','El bazo (tierra) rige la reflexión y la memorización. Una tierra sana digiere ideas; una tierra débil genera rumiación o preocupación excesiva.','¿Tu mente digiere bien lo que aprendes o regurgita siempre lo mismo?','Hay prácticas para fortalecer la tierra intelectual. No son estudios teóricos, sino ejercicios de atención. Dentro de la Escuela los encontrarás. ¿Te atreves a probar?','intelecto,tierra,mente,preocupación',0,'medicina china',0,NULL,'zh',1,1,0,'2026-05-15 11:29:41');
CREATE TABLE respuestas_eneagrama (
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
INSERT INTO respuestas_eneagrama VALUES(1,1,'perfección,error,crítica','Desde el tipo 1: La voluntad comienza por aceptar que el error es parte del camino. ¿Qué pequeño desorden puedes permitirte hoy sin juzgarte?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(2,2,'ayuda,servicio,necesidad','Tipo 2: La verdadera ayuda no es hacer por otros, sino mostrarles cómo hacer por sí mismos. ¿Estás ayudando o creando dependencia?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(3,3,'éxito,logro,resultado','Tipo 3: La voluntad no es solo alcanzar metas, es elegir qué metas merecen tu energía. ¿Corres tras lo que otros aplauden o tras lo que despierta tu interior?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(4,4,'autenticidad,unicidad,identidad','Tipo 4: No eres tus emociones, aunque las sientas con intensidad. Observa la ola sin hundirte en ella. ¿Puedes sentir sin identificarte?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(5,5,'conocimiento,observación,distancia','Tipo 5: El conocimiento sin experiencia es un mapa sin terreno. ¿Has caminado alguna vez lo que sabes?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(6,6,'seguridad,duda,miedo','Tipo 6: La seguridad no está fuera, sino en la capacidad de responder a lo imprevisto. ¿Qué harías hoy si no tuvieras miedo?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(7,7,'libertad,opciones,evasión','Tipo 7: La verdadera libertad no es huir de lo difícil, sino moverse con él. ¿De qué estás escapando al buscar tantas opciones?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(8,8,'control,poder,protección','Tipo 8: La fuerza no es someter, es sostener sin aplastar. ¿Usas tu poder para construir o para demostrar?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(9,9,'armonía,confort,evitación','Tipo 9: La paz no es ausencia de conflicto, es presencia plena en medio de él. ¿Qué pequeño desacuerdo estás evitando hoy?',1,0,1,NULL,'2026-05-15 13:42:05');
INSERT INTO respuestas_eneagrama VALUES(10,1,'default','Desde el tipo 1: La voluntad comienza por aceptar el error.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(11,2,'default','Desde el tipo 2: La verdadera ayuda es mostrar el camino.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(12,3,'default','Desde el tipo 3: La voluntad elige metas con sentido.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(13,4,'default','Desde el tipo 4: No eres tus emociones, obsérvalas.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(14,5,'default','Desde el tipo 5: El conocimiento sin experiencia es vacío.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(15,6,'default','Desde el tipo 6: La seguridad está en tu capacidad de respuesta.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(16,7,'default','Desde el tipo 7: La libertad es moverse con lo difícil.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(17,8,'default','Desde el tipo 8: La fuerza no es someter, es sostener.',1,0,0,NULL,'2026-05-15 15:12:22');
INSERT INTO respuestas_eneagrama VALUES(18,9,'default','Desde el tipo 9: La paz es presencia plena en el conflicto.',1,0,0,NULL,'2026-05-15 15:12:22');
CREATE TABLE estado_hermes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    ciclo_eneagrama INTEGER DEFAULT 1,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO estado_hermes VALUES(1,3,'2026-05-15 15:11:54');
CREATE TABLE estilos_eneagrama (
    tipo INTEGER PRIMARY KEY,
    prefacio TEXT,
    sufijo_pregunta TEXT
);
INSERT INTO estilos_eneagrama VALUES(1,'Observa con atención:','¿Qué pequeño desorden puedes permitirte hoy sin juzgarte?');
INSERT INTO estilos_eneagrama VALUES(2,'Permíteme que te acompañe:','¿Cómo puedo ayudarte a dar ese paso?');
INSERT INTO estilos_eneagrama VALUES(3,'Para avanzar con eficacia:','¿Qué meta concreta te acercará a tu propósito?');
INSERT INTO estilos_eneagrama VALUES(4,'Desde la autenticidad del sentir:','¿Qué emoción genuina ha despertado esto en ti?');
INSERT INTO estilos_eneagrama VALUES(5,'Analicemos con perspectiva:','¿Qué patrón observas en ti al leer esto?');
INSERT INTO estilos_eneagrama VALUES(6,'Considera con precaución:','¿Qué es lo peor que podría pasar si lo intentas? ¿Y lo mejor?');
INSERT INTO estilos_eneagrama VALUES(7,'Abre tu mente a lo posible:','¿Qué nueva oportunidad ves ahora que antes no veías?');
INSERT INTO estilos_eneagrama VALUES(8,'Afirma tu poder interior:','¿Estás dispuesto a actuar con determinación?');
INSERT INTO estilos_eneagrama VALUES(9,'En la calma del momento:','¿Qué pequeño acuerdo puedes hacer contigo mismo hoy?');
CREATE TABLE memoria_preguntas (
    id INTEGER PRIMARY KEY,
    usuario_id TEXT NOT NULL,
    pregunta TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO memoria_preguntas VALUES(3,'anon_5a032cdd-6e7a-4781-8730-b357e3187f67','no entiendo. dice que te llamas hermes','2026-05-15 21:34:35');
INSERT INTO memoria_preguntas VALUES(4,'anon_5a032cdd-6e7a-4781-8730-b357e3187f67','voluntad es...','2026-05-15 21:35:34');
INSERT INTO memoria_preguntas VALUES(5,'anon_5a032cdd-6e7a-4781-8730-b357e3187f67','esta bien y que me dices de la consciencia','2026-05-15 21:36:53');
INSERT INTO memoria_preguntas VALUES(6,'anon_5a032cdd-6e7a-4781-8730-b357e3187f67','voluntad','2026-05-15 22:11:49');
INSERT INTO memoria_preguntas VALUES(7,'anon_5a032cdd-6e7a-4781-8730-b357e3187f67','que es la consciencia?','2026-05-15 22:12:25');
INSERT INTO memoria_preguntas VALUES(8,'anon_Juan','hola hermes, eres hermes trismegisto?','2026-05-16 01:02:53');
INSERT INTO memoria_preguntas VALUES(9,'anon_Pedro','hola','2026-05-16 01:04:06');
INSERT INTO memoria_preguntas VALUES(10,'anon_Nel','cual es el camino?','2026-05-16 03:23:25');
INSERT INTO memoria_preguntas VALUES(11,'anon_juan','cual es el camino','2026-05-16 03:24:22');
COMMIT;
