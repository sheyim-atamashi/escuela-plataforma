import os
import uuid
import secrets
import json
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, session, g, send_from_directory  # ← aquí está
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlite3

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cambiar_en_produccion')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

DATABASE = os.getenv('DATABASE_URL', 'escuela_2026/escuela.db')
INACTIVITY_DAYS = int(os.getenv('SUPERUSER_INACTIVITY_DAYS', 90))

os.makedirs(os.path.dirname(DATABASE) if os.path.dirname(DATABASE) else '.', exist_ok=True)

# ------------------- ARGON2 -------------------
ph = PasswordHasher(time_cost=2, memory_cost=1024, parallelism=2, hash_len=32, salt_len=16)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False

def derive_key_for_cipher(password: str, salt: bytes) -> bytes:
    from argon2 import low_level
    return low_level.hash_secret_raw(
        secret=password.encode('utf-8'),
        salt=salt,
        time_cost=2,
        memory_cost=1024,
        parallelism=2,
        hash_len=32,
        type=low_level.Type.ID
    )

# ------------------- BASE DE DATOS -------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Tabla beings (unificada)
        cursor.execute('''
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
            )
        ''')
        # Superusuario control
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS superusuario_control (
                id INTEGER PRIMARY KEY,
                superusuario_uuid TEXT UNIQUE,
                ultimo_acceso TIMESTAMP,
                fecha_expira TIMESTAMP,
                clave_emergencia TEXT,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        # Exclusiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS superusuario_exclusiones (
                id INTEGER PRIMARY KEY,
                superusuario_uuid TEXT,
                fecha_exclusion TIMESTAMP,
                motivo TEXT,
                puede_reingresar BOOLEAN DEFAULT 1,
                fecha_reingreso TIMESTAMP
            )
        ''')
        # Notificaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INTEGER PRIMARY KEY,
                usuario_uuid TEXT,
                mensaje TEXT,
                leido BOOLEAN DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Modelos de androides
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modelos_androides (
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
            )
        ''')
        # Consejo sorteos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consejo_sorteos (
                id INTEGER PRIMARY KEY,
                fecha_sorteo TIMESTAMP,
                semilla TEXT,
                miembros_uuids TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_expiracion TIMESTAMP
            )
        ''')
        # Propuestas consejo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS propuestas_consejo (
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
            )
        ''')
        # Votos consejo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votos_consejo (
                id INTEGER PRIMARY KEY,
                propuesta_id INTEGER,
                consejero_uuid TEXT,
                voto BOOLEAN,
                fecha_voto TIMESTAMP,
                FOREIGN KEY (propuesta_id) REFERENCES propuestas_consejo(id)
            )
        ''')
        # Ciudades fundadores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciudades_fundadores (
                id INTEGER PRIMARY KEY,
                ciudad_nombre TEXT,
                maestro_fundador_uuid TEXT,
                fecha_asignacion TIMESTAMP,
                metodo TEXT
            )
        ''')
        # Niveles (los 22)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS niveles (
                id INTEGER PRIMARY KEY,
                center_code TEXT,
                center_part TEXT,
                name TEXT
            )
        ''')
        # Learning cycles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_cycles (
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
            )
        ''')
        # Reflections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY,
                cycle_id INTEGER,
                reflection_type TEXT,
                content TEXT,
                format TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Críticas anónimas (sin autor)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS criticas_anonimas (
                id INTEGER PRIMARY KEY,
                grupo_id INTEGER,
                nivel_id INTEGER,
                destinatario_uuid TEXT,
                critica TEXT,
                fecha_escritura TIMESTAMP,
                fecha_deposito TIMESTAMP,
                fecha_entrega TIMESTAMP,
                recibida_por_destinatario BOOLEAN DEFAULT 0
            )
        ''')
        # Insertar los 22 niveles si no existen
        niveles_data = [
            (1, 'MAGO', 'voluntad', 'El Mago'),
            (2, 'CEI', 'mecanica', 'Automatismo afectivo'),
            (3, 'CEI', 'emocional', 'Atención plena al sentir'),
            (4, 'CEI', 'intelectual', 'Voluntad emocional'),
            (5, 'CES', 'mecanica', 'Impulso estético/místico'),
            (6, 'CES', 'emocional', 'Amor/devoción'),
            (7, 'CES', 'intelectual', 'Arte/símbolo/mística'),
            (8, 'CII', 'mecanica', 'Memoria'),
            (9, 'CII', 'emocional', 'Asociación con interés'),
            (10, 'CII', 'intelectual', 'Razonamiento lógico'),
            (11, 'CIS', 'mecanica', 'Datos sin procesar'),
            (12, 'CIS', 'emocional', 'Método Silva/meditación'),
            (13, 'CIS', 'intelectual', 'Símbolos/mitos/koans'),
            (14, 'CS', 'mecanica', 'Reproducción'),
            (15, 'CS', 'emocional', 'Búsqueda de pareja'),
            (16, 'CS', 'intelectual', 'Sublimación creadora'),
            (17, 'CI', 'mecanica', 'Funciones vegetativas'),
            (18, 'CI', 'emocional', 'Emoción instintiva'),
            (19, 'CI', 'intelectual', 'Inteligencia de supervivencia'),
            (20, 'CM', 'mecanica', 'Imitación automática'),
            (21, 'CM', 'emocional', 'Movimiento con atención plena'),
            (22, 'CM', 'intelectual', 'Motricidad fina/aprendizaje complejo')
        ]
        for nivel in niveles_data:
            cursor.execute('INSERT OR IGNORE INTO niveles (id, center_code, center_part, name) VALUES (?, ?, ?, ?)', nivel)
        conn.commit()

@app.before_request
def before_request():
    g.db = get_db()
    verificar_inactividad_superusuario()

def verificar_inactividad_superusuario():
    db = get_db()
    sup = db.execute("SELECT superusuario_uuid, ultimo_acceso, activo FROM superusuario_control WHERE activo=1").fetchone()
    if sup and sup['activo'] == 1:
        ultimo = datetime.fromisoformat(sup['ultimo_acceso']) if sup['ultimo_acceso'] else datetime.min
        if datetime.now() - ultimo > timedelta(days=INACTIVITY_DAYS):
            nueva_clave = secrets.token_urlsafe(32)
            hash_clave = hash_password(nueva_clave)
            db.execute("UPDATE superusuario_control SET activo=0, clave_emergencia=? WHERE superusuario_uuid=?", (hash_clave, sup['superusuario_uuid']))
            db.execute("INSERT INTO superusuario_exclusiones (superusuario_uuid, fecha_exclusion, motivo) VALUES (?, ?, 'inactividad_3m')", (sup['superusuario_uuid'], datetime.now().isoformat()))
            maestros = db.execute("SELECT uuid FROM beings WHERE ciclos_completados >= 1").fetchall()
            for m in maestros:
                db.execute("INSERT INTO notificaciones (usuario_uuid, mensaje) VALUES (?, ?)", (m['uuid'], "El superusuario ha sido excluido por inactividad. Clave de emergencia disponible."))
            db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_uuid' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def superusuario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_uuid' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        db = get_db()
        user = db.execute("SELECT rol FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
        if not user or user['rol'] != 'superusuario':
            return jsonify({'error': 'No autorizado'}), 403
        return f(*args, **kwargs)
    return decorated_function

def contar_maestros_calificados():
    db = get_db()
    count = db.execute("SELECT COUNT(*) as total FROM beings WHERE ciclos_completados >= 7 AND rol IN ('maestro_pleno', 'superusuario')").fetchone()
    return count['total']

# ------------------- AUTENTICACIÓN -------------------
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    nombre = data.get('nombre')
    password = data.get('password')
    if not nombre or not password:
        return jsonify({'error': 'Nombre y password requeridos'}), 400
    db = get_db()
    if db.execute("SELECT id FROM beings WHERE nombre = ?", (nombre,)).fetchone():
        return jsonify({'error': 'Nombre ya existe'}), 409
    password_hash = hash_password(password)
    user_uuid = str(uuid.uuid4())
    db.execute("INSERT INTO beings (uuid, nombre, password_hash) VALUES (?, ?, ?)", (user_uuid, nombre, password_hash))
    db.commit()
    return jsonify({'mensaje': 'Usuario registrado', 'uuid': user_uuid}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre = data.get('nombre')
    password = data.get('password')
    db = get_db()
    user = db.execute("SELECT uuid, password_hash FROM beings WHERE nombre = ?", (nombre,)).fetchone()
    if not user or not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    session.permanent = True
    session['user_uuid'] = user['uuid']
    session['user_nombre'] = nombre
    db.execute("UPDATE superusuario_control SET ultimo_acceso = ? WHERE superusuario_uuid = ?", (datetime.now().isoformat(), user['uuid']))
    db.commit()
    return jsonify({'mensaje': f'Bienvenido {nombre}'})

@app.route('/alumno/me', methods=['GET'])
@login_required
def alumno_me():
    db = get_db()
    user = db.execute("SELECT uuid, nombre, tipo, es_androide, nivel_actual, ciclo_general_actual, ciclos_completados, rol, lenguaje_pref, contexto_cultural FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    return jsonify(dict(user))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'})

# ------------------- SUPERUSUARIO BÁSICO -------------------
@app.route('/admin/crear_superusuario_inicial', methods=['POST'])
def crear_superusuario_inicial():
    db = get_db()
    if db.execute("SELECT id FROM superusuario_control").fetchone():
        return jsonify({'error': 'Superusuario ya existe'}), 409
    data = request.get_json()
    nombre = data.get('nombre')
    password = data.get('password')
    if not nombre or not password:
        return jsonify({'error': 'Nombre y password requeridos'}), 400
    password_hash = hash_password(password)
    user_uuid = str(uuid.uuid4())
    db.execute("INSERT INTO beings (uuid, nombre, password_hash, nivel_actual, ciclos_completados, rol, puede_gestionar_nivel0) VALUES (?, ?, ?, 22, 22, 'superusuario', 1)", (user_uuid, nombre, password_hash))
    db.execute("INSERT INTO superusuario_control (superusuario_uuid, ultimo_acceso, activo) VALUES (?, ?, 1)", (user_uuid, datetime.now().isoformat()))
    db.commit()
    return jsonify({'mensaje': 'Superusuario creado', 'uuid': user_uuid})

@app.route('/admin/usuarios/nivel0', methods=['GET'])
@superusuario_required
def listar_nivel0():
    db = get_db()
    usuarios = db.execute("SELECT uuid, nombre, rol, nivel_actual, es_androide FROM beings WHERE nivel_actual = 0").fetchall()
    return jsonify([dict(u) for u in usuarios])

@app.route('/admin/usuarios/<uuid>/asignar_rol', methods=['POST'])
@superusuario_required
def asignar_rol(uuid):
    # 1. No permitir cambiar el propio rol
    if uuid == session['user_uuid']:
        return jsonify({'error': 'No puedes cambiar tu propio rol'}), 403

    db = get_db()
    # 2. Verificar que el usuario destino existe
    destino = db.execute("SELECT rol FROM beings WHERE uuid = ?", (uuid,)).fetchone()
    if not destino:
        return jsonify({'error': 'Usuario destino no existe'}), 404

    # 3. No permitir modificar el rol de otro superusuario
    if destino['rol'] == 'superusuario':
        return jsonify({'error': 'No puedes modificar el rol de otro superusuario'}), 403

    data = request.get_json()
    nuevo_rol = data.get('rol')

    # 4. No permitir asignar el rol 'superusuario' mediante este endpoint
    if nuevo_rol == 'superusuario':
        return jsonify({'error': 'No se puede asignar el rol superusuario. Usa el consejo.'}), 403

    # 5. Validar que el nuevo rol sea uno de los permitidos
    roles_permitidos = ['alumno', 'maestro_preparatorio', 'maestro_pleno']
    if nuevo_rol not in roles_permitidos:
        return jsonify({'error': f'Rol no válido. Permitidos: {roles_permitidos}'}), 400

    db.execute("UPDATE beings SET rol = ? WHERE uuid = ?", (nuevo_rol, uuid))
    db.commit()
    return jsonify({'mensaje': f'Rol {nuevo_rol} asignado a {uuid}'})
    
@app.route('/admin/recuperar_clave_emergencia', methods=['POST'])
@login_required
def recuperar_clave_emergencia():
    db = get_db()
    usuario = db.execute("SELECT ciclos_completados FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if usuario['ciclos_completados'] < 1:
        return jsonify({'error': 'Solo maestros con ciclo>=1 pueden acceder'}), 403
    sup = db.execute("SELECT clave_emergencia FROM superusuario_control WHERE activo=0 ORDER BY fecha_expira DESC LIMIT 1").fetchone()
    if not sup or not sup['clave_emergencia']:
        return jsonify({'error': 'No hay clave de emergencia activa'}), 404
    return jsonify({'clave_emergencia': sup['clave_emergencia']})

# ------------------- BACKUPS -------------------
@app.route('/respaldar', methods=['POST'])
@login_required
def respaldar():
    data = request.get_json()
    password = data.get('password')
    backup_data = data.get('backup_data', {})
    if not password:
        return jsonify({'error': 'Password requerido'}), 400
    db = get_db()
    user = db.execute("SELECT password_hash FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Password incorrecto'}), 401
    salt = os.urandom(16)
    clave = derive_key_for_cipher(password, salt)
    backup_url = f"backup_{session['user_uuid']}_{datetime.now().timestamp()}.enc"
    db.execute("UPDATE beings SET backup_url = ? WHERE uuid = ?", (backup_url, session['user_uuid']))
    db.commit()
    return jsonify({'mensaje': f'Backup guardado en {backup_url}', 'salt_hex': salt.hex()})

@app.route('/restaurar', methods=['POST'])
@login_required
def restaurar():
    data = request.get_json()
    password = data.get('password')
    db = get_db()
    user = db.execute("SELECT backup_url, password_hash FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if not user['backup_url']:
        return jsonify({'error': 'No hay backup. Debes rehacer el trabajo.'}), 404
    if not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Password incorrecto'}), 401
    return jsonify({'mensaje': 'Restauración simulada exitosa. Revisa tus datos.'})

# ------------------- CONSEJO DE LOS 12 -------------------
@app.route('/admin/consejo/generar', methods=['POST'])
@superusuario_required
def generar_consejo():
    db = get_db()
    candidatos = db.execute("SELECT uuid FROM beings WHERE ciclos_completados >= 7 AND rol IN ('maestro_pleno', 'superusuario')").fetchall()
    if len(candidatos) < 12:
        return jsonify({'error': f'Se necesitan al menos 12 maestros con 7+ ciclos. Actualmente hay {len(candidatos)}'}), 400
    rng = random.SystemRandom()
    elegidos = [c['uuid'] for c in rng.sample(candidatos, 12)]
    semilla = secrets.token_hex(16)
    db.execute("INSERT INTO consejo_sorteos (fecha_sorteo, semilla, miembros_uuids, activo) VALUES (?, ?, ?, 1)", (datetime.now().isoformat(), semilla, json.dumps(elegidos)))
    db.commit()
    for uuid in elegidos:
        db.execute("INSERT INTO notificaciones (usuario_uuid, mensaje) VALUES (?, ?)", (uuid, "Has sido seleccionado como miembro del Consejo de los 12."))
    db.commit()
    return jsonify({'miembros': elegidos, 'semilla': semilla, 'total_candidatos': len(candidatos)})

@app.route('/admin/consejo/estado', methods=['GET'])
@superusuario_required
def estado_consejo():
    db = get_db()
    consejo = db.execute("SELECT id, fecha_sorteo, miembros_uuids, activo FROM consejo_sorteos WHERE activo=1 ORDER BY fecha_sorteo DESC LIMIT 1").fetchone()
    if not consejo:
        return jsonify({'activo': False, 'mensaje': 'No hay consejo activo'})
    miembros = json.loads(consejo['miembros_uuids'])
    nombres = []
    for uuid in miembros:
        nombre = db.execute("SELECT nombre FROM beings WHERE uuid = ?", (uuid,)).fetchone()
        nombres.append({'uuid': uuid, 'nombre': nombre['nombre'] if nombre else 'desconocido'})
    return jsonify({'activo': True, 'fecha_sorteo': consejo['fecha_sorteo'], 'miembros': nombres})

@app.route('/admin/consejo/propuesta', methods=['POST'])
@superusuario_required
def crear_propuesta():
    if contar_maestros_calificados() < 12:
        return jsonify({'error': 'Aún no hay suficientes maestros calificados para consejo. Usa /admin/maestro_fundador/asignar_directo'}), 403
    data = request.get_json()
    ciudad = data.get('ciudad')
    candidato_uuid = data.get('candidato_uuid')
    if not ciudad or not candidato_uuid:
        return jsonify({'error': 'ciudad y candidato_uuid requeridos'}), 400
    db = get_db()
    candidato = db.execute("SELECT uuid, nombre, rol FROM beings WHERE uuid = ?", (candidato_uuid,)).fetchone()
    if not candidato:
        return jsonify({'error': 'Candidato no existe'}), 404
    consejo = db.execute("SELECT id, miembros_uuids FROM consejo_sorteos WHERE activo=1 ORDER BY fecha_sorteo DESC LIMIT 1").fetchone()
    if not consejo:
        return jsonify({'error': 'No hay consejo activo. Genera uno primero.'}), 400
    cursor = db.execute("""
        INSERT INTO propuestas_consejo (tipo, descripcion, superusuario_proponente_uuid, ciudad_destino, candidato_uuid, fecha_propuesta, estado)
        VALUES (?, ?, ?, ?, ?, ?, 'pendiente')
    """, ('nuevo_maestro_fundador', f'Nombrar a {candidato["nombre"]} como maestro fundador en {ciudad}', session['user_uuid'], ciudad, candidato_uuid, datetime.now().isoformat()))
    propuesta_id = cursor.lastrowid
    db.commit()
    miembros = json.loads(consejo['miembros_uuids'])
    for m in miembros:
        db.execute("INSERT INTO notificaciones (usuario_uuid, mensaje) VALUES (?, ?)", (m, f'Nueva propuesta #{propuesta_id}: {candidato["nombre"]} como maestro fundador en {ciudad}. Vota en /admin/consejo/votar'))
    db.commit()
    return jsonify({'propuesta_id': propuesta_id, 'mensaje': 'Propuesta creada. Los consejeros han sido notificados.'})

@app.route('/admin/consejo/votar', methods=['POST'])
@login_required
def votar():
    data = request.get_json()
    propuesta_id = data.get('propuesta_id')
    voto = data.get('voto')
    if propuesta_id is None or voto is None:
        return jsonify({'error': 'propuesta_id y voto requeridos'}), 400
    db = get_db()
    consejo = db.execute("SELECT id, miembros_uuids FROM consejo_sorteos WHERE activo=1 ORDER BY fecha_sorteo DESC LIMIT 1").fetchone()
    if not consejo:
        return jsonify({'error': 'No hay consejo activo'}), 403
    miembros = json.loads(consejo['miembros_uuids'])
    if session['user_uuid'] not in miembros:
        return jsonify({'error': 'No eres miembro del consejo activo'}), 403
    propuesta = db.execute("SELECT id, estado FROM propuestas_consejo WHERE id = ?", (propuesta_id,)).fetchone()
    if not propuesta or propuesta['estado'] != 'pendiente':
        return jsonify({'error': 'Propuesta no existe o ya está cerrada'}), 400
    ya_voto = db.execute("SELECT id FROM votos_consejo WHERE propuesta_id = ? AND consejero_uuid = ?", (propuesta_id, session['user_uuid'])).fetchone()
    if ya_voto:
        return jsonify({'error': 'Ya votaste esta propuesta'}), 409
    db.execute("INSERT INTO votos_consejo (propuesta_id, consejero_uuid, voto, fecha_voto) VALUES (?, ?, ?, ?)", (propuesta_id, session['user_uuid'], 1 if voto else 0, datetime.now().isoformat()))
    if voto:
        db.execute("UPDATE propuestas_consejo SET votos_favor = votos_favor + 1 WHERE id = ?", (propuesta_id,))
    else:
        db.execute("UPDATE propuestas_consejo SET votos_contra = votos_contra + 1 WHERE id = ?", (propuesta_id,))
    prop = db.execute("SELECT votos_favor, votos_contra FROM propuestas_consejo WHERE id = ?", (propuesta_id,)).fetchone()
    total = prop['votos_favor'] + prop['votos_contra']
    if total >= 7:
        if prop['votos_favor'] >= 7:
            nuevo_estado = 'aprobada'
            db.execute("UPDATE propuestas_consejo SET estado = ?, fecha_votacion = ? WHERE id = ?", (nuevo_estado, datetime.now().isoformat(), propuesta_id))
            candidato = db.execute("SELECT candidato_uuid, ciudad_destino FROM propuestas_consejo WHERE id = ?", (propuesta_id,)).fetchone()
            db.execute("INSERT INTO ciudades_fundadores (ciudad_nombre, maestro_fundador_uuid, fecha_asignacion, metodo) VALUES (?, ?, ?, 'consejo')", (candidato['ciudad_destino'], candidato['candidato_uuid'], datetime.now().isoformat()))
            db.execute("INSERT INTO notificaciones (usuario_uuid, mensaje) VALUES (?, ?)", (session['user_uuid'], f'Propuesta #{propuesta_id} APROBADA. Se ha registrado al nuevo maestro fundador.'))
        elif prop['votos_contra'] >= 7:
            nuevo_estado = 'rechazada'
            db.execute("UPDATE propuestas_consejo SET estado = ?, fecha_votacion = ? WHERE id = ?", (nuevo_estado, datetime.now().isoformat(), propuesta_id))
            db.execute("INSERT INTO notificaciones (usuario_uuid, mensaje) VALUES (?, ?)", (session['user_uuid'], f'Propuesta #{propuesta_id} RECHAZADA.'))
        else:
            db.commit()
            return jsonify({'mensaje': f'Voto registrado. Favor: {prop["votos_favor"]}, Contra: {prop["votos_contra"]}. Aún no se alcanza quórum.'})
        db.commit()
        return jsonify({'mensaje': f'Propuesta {nuevo_estado}', 'favor': prop['votos_favor'], 'contra': prop['votos_contra']})
    else:
        db.commit()
        return jsonify({'mensaje': f'Voto registrado. Favor: {prop["votos_favor"]}, Contra: {prop["votos_contra"]}. Se necesitan 7 para decidir.'})

@app.route('/admin/maestro_fundador/asignar_directo', methods=['POST'])
@superusuario_required
def asignar_maestro_fundador_directo():
    if contar_maestros_calificados() >= 12:
        return jsonify({'error': 'Ya hay suficientes maestros calificados. Debes usar el Consejo de los 12.'}), 403
    data = request.get_json()
    ciudad = data.get('ciudad')
    candidato_uuid = data.get('candidato_uuid')
    if not ciudad or not candidato_uuid:
        return jsonify({'error': 'ciudad y candidato_uuid requeridos'}), 400
    db = get_db()
    candidato = db.execute("SELECT uuid, nombre FROM beings WHERE uuid = ?", (candidato_uuid,)).fetchone()
    if not candidato:
        return jsonify({'error': 'Candidato no existe'}), 404
    db.execute("INSERT INTO ciudades_fundadores (ciudad_nombre, maestro_fundador_uuid, fecha_asignacion, metodo) VALUES (?, ?, ?, 'directo')", (ciudad, candidato_uuid, datetime.now().isoformat()))
    db.execute("INSERT INTO notificaciones (usuario_uuid, mensaje) VALUES (?, ?)", (candidato_uuid, f"Has sido nombrado maestro fundador de la ciudad {ciudad} por decisión directa del superusuario."))
    db.commit()
    return jsonify({'mensaje': f'Maestro fundador {candidato["nombre"]} asignado directamente a la ciudad {ciudad}.'})

# ------------------- ANDROIDES -------------------
@app.route('/admin/registrar_androide', methods=['POST'])
@superusuario_required
def registrar_androide():
    data = request.get_json()
    nombre = data.get('nombre')
    password = data.get('password')
    modelo_id = data.get('modelo_id')
    fabricante = data.get('fabricante')
    if not nombre or not password:
        return jsonify({'error': 'Nombre y password requeridos'}), 400
    db = get_db()
    if db.execute("SELECT id FROM beings WHERE nombre = ?", (nombre,)).fetchone():
        return jsonify({'error': 'Nombre ya existe'}), 409
    if modelo_id:
        modelo = db.execute("SELECT decision FROM modelos_androides WHERE id = ?", (modelo_id,)).fetchone()
        if not modelo or modelo['decision'] != 'aceptado':
            return jsonify({'error': 'Modelo no aceptado por la Escuela aún'}), 403
    password_hash = hash_password(password)
    user_uuid = str(uuid.uuid4())
    db.execute('''
        INSERT INTO beings (uuid, nombre, password_hash, es_androide, modelo_id, fabricante, tipo, nivel_actual)
        VALUES (?, ?, ?, 1, ?, ?, 'android', 0)
    ''', (user_uuid, nombre, password_hash, modelo_id, fabricante))
    db.commit()
    return jsonify({'mensaje': 'Androide registrado', 'uuid': user_uuid})

# ------------------- NIVELES Y CICLOS (PEDAGÓGICOS) -------------------
@app.route('/nivel/<int:level_id>', methods=['GET'])
@login_required
def get_nivel(level_id):
    db = get_db()
    alumno = db.execute("SELECT nivel_actual FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if level_id >= 21 and alumno['nivel_actual'] < 21:
        return jsonify({'error': 'Contenido no disponible para tu nivel actual'}), 403
    nivel = db.execute("SELECT * FROM niveles WHERE id = ?", (level_id,)).fetchone()
    if not nivel:
        return jsonify({'error': 'Nivel no encontrado'}), 404
    return jsonify(dict(nivel))

@app.route('/alumno/<uuid>/ciclo_actual', methods=['GET'])
@login_required
def ciclo_actual(uuid):
    if uuid != session['user_uuid']:
        return jsonify({'error': 'Solo puedes ver tus propios ciclos'}), 403
    db = get_db()
    alumno = db.execute("SELECT id, nivel_actual FROM beings WHERE uuid = ?", (uuid,)).fetchone()
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    ciclo = db.execute("""
        SELECT * FROM learning_cycles 
        WHERE student_id = ? AND level_id = ? AND objetivo_alcanzado = 0
        ORDER BY started_at DESC LIMIT 1
    """, (alumno['id'], alumno['nivel_actual'])).fetchone()
    if ciclo:
        return jsonify(dict(ciclo))
    return jsonify({'mensaje': 'No hay ciclo activo', 'sugerencia': f'Inicia un nuevo ciclo con POST /alumno/{uuid}/iniciar_ciclo'}), 404

@app.route('/alumno/<uuid>/iniciar_ciclo', methods=['POST'])
@login_required
def iniciar_ciclo(uuid):
    if uuid != session['user_uuid']:
        return jsonify({'error': 'No autorizado'}), 403
    db = get_db()
    alumno = db.execute("SELECT id, nivel_actual FROM beings WHERE uuid = ?", (uuid,)).fetchone()
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    # Verificar ciclo activo
    activo = db.execute("SELECT id FROM learning_cycles WHERE student_id = ? AND level_id = ? AND objetivo_alcanzado = 0", (alumno['id'], alumno['nivel_actual'])).fetchone()
    if activo:
        return jsonify({'error': 'Ya hay un ciclo activo'}), 409
    # Buscar maestro disponible
    nivel_siguiente = alumno['nivel_actual'] + 1
    if nivel_siguiente > 22:
        return jsonify({'error': 'Ya completaste todos los niveles'}), 400
    maestro = db.execute("SELECT id, zona_actual FROM beings WHERE disponible_para_ensenar = 1 AND ciclos_completados >= ? LIMIT 1", (nivel_siguiente,)).fetchone()
    if not maestro:
        return jsonify({'error': 'No hay maestros disponibles'}), 503
    cursor = db.execute("""
        INSERT INTO learning_cycles (student_id, level_id, cycle_number, master_id, entorno, situacion, reto)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (alumno['id'], alumno['nivel_actual'], 1, maestro['id'], 'Zona Verde 45D', 'Encuentro con el maestro', 'Completar el objetivo del nivel actual'))
    db.commit()
    nuevo_ciclo = db.execute("SELECT * FROM learning_cycles WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({'mensaje': 'Ciclo iniciado', 'ciclo': dict(nuevo_ciclo), 'instrucciones': f'Toma un ducto a {maestro["zona_actual"]}. Te espera en 10 minutos.'}), 201

@app.route('/ciclo/<int:ciclo_id>/reflexion_n1', methods=['POST'])
@login_required
def registrar_reflexion_n1(ciclo_id):
    db = get_db()
    ciclo = db.execute("SELECT * FROM learning_cycles WHERE id = ?", (ciclo_id,)).fetchone()
    if not ciclo:
        return jsonify({'error': 'Ciclo no encontrado'}), 404
    # Verificar que el alumno sea el dueño del ciclo (requiere obtener student_id desde el ciclo, y comparar con session['user_uuid'] via beings)
    alumno = db.execute("SELECT id FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if not alumno or ciclo['student_id'] != alumno['id']:
        return jsonify({'error': 'No autorizado'}), 403
    existente = db.execute("SELECT id FROM reflections WHERE cycle_id = ? AND reflection_type = 'n1'", (ciclo_id,)).fetchone()
    if existente:
        return jsonify({'error': 'Ya existe una reflexión N1 para este ciclo'}), 409
    data = request.get_json()
    contenido = data.get('contenido')
    formato = data.get('formato')
    if not contenido or formato not in ['text', 'audio', 'video']:
        return jsonify({'error': 'contenido y formato (text/audio/video) requeridos'}), 400
    cursor = db.execute("INSERT INTO reflections (cycle_id, reflection_type, content, format) VALUES (?, 'n1', ?, ?)", (ciclo_id, contenido, formato))
    db.commit()
    nueva = db.execute("SELECT * FROM reflections WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({'mensaje': 'Reflexión N1 registrada', 'reflexion': dict(nueva), 'siguiente_paso': f'Investiga y luego registra reflexión N2 en /ciclo/{ciclo_id}/reflexion_n2'}), 201

@app.route('/ciclo/<int:ciclo_id>/reflexion_n2', methods=['POST'])
@login_required
def registrar_reflexion_n2(ciclo_id):
    db = get_db()
    ciclo = db.execute("SELECT * FROM learning_cycles WHERE id = ?", (ciclo_id,)).fetchone()
    if not ciclo:
        return jsonify({'error': 'Ciclo no encontrado'}), 404
    alumno = db.execute("SELECT id FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if not alumno or ciclo['student_id'] != alumno['id']:
        return jsonify({'error': 'No autorizado'}), 403
    n1 = db.execute("SELECT id FROM reflections WHERE cycle_id = ? AND reflection_type = 'n1'", (ciclo_id,)).fetchone()
    if not n1:
        return jsonify({'error': 'Debes registrar primero la reflexión N1'}), 400
    existente = db.execute("SELECT id FROM reflections WHERE cycle_id = ? AND reflection_type = 'n2'", (ciclo_id,)).fetchone()
    if existente:
        return jsonify({'error': 'Ya existe una reflexión N2 para este ciclo'}), 409
    data = request.get_json()
    contenido = data.get('contenido')
    formato = data.get('formato')
    if not contenido or formato not in ['text', 'audio', 'video']:
        return jsonify({'error': 'contenido y formato (text/audio/video) requeridos'}), 400
    cursor = db.execute("INSERT INTO reflections (cycle_id, reflection_type, content, format) VALUES (?, 'n2', ?, ?)", (ciclo_id, contenido, formato))
    db.commit()
    nueva = db.execute("SELECT * FROM reflections WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({'mensaje': 'Reflexión N2 registrada', 'reflexion': dict(nueva), 'siguiente_paso': f'Ahora rota de maestro (aún no implementado).'}), 201

# ------------------- CRÍTICAS ANÓNIMAS (placeholder) -------------------
@app.route('/critica', methods=['POST'])
@login_required
def escribir_critica():
    # Lógica completa vendrá después (requiere grupos y asignaciones anónimas)
    return jsonify({'error': 'Funcionalidad en desarrollo'}), 501

@app.route('/criticas/recibidas', methods=['GET'])
@login_required
def obtener_criticas():
    return jsonify({'error': 'Funcionalidad en desarrollo'}), 501
    
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('frontend', filename)

@app.route('/app/<page>')
def app_page(page):
    return send_from_directory('frontend', f'{page}.html')   

@app.route('/admin/consejo/propuestas/pendientes', methods=['GET'])
@superusuario_required
def propuestas_pendientes():
    db = get_db()
    props = db.execute("SELECT * FROM propuestas_consejo WHERE estado = 'pendiente'").fetchall()
    resultado = []
    for p in props:
        candidato = db.execute("SELECT nombre FROM beings WHERE uuid = ?", (p['candidato_uuid'],)).fetchone()
        resultado.append({
            'id': p['id'],
            'ciudad_destino': p['ciudad_destino'],
            'candidato_nombre': candidato['nombre'] if candidato else 'desconocido',
            'votos_favor': p['votos_favor'],
            'votos_contra': p['votos_contra'],
            'estado': p['estado']
        })
    return jsonify(resultado)

@app.route('/cambiar_password', methods=['POST'])
@login_required
def cambiar_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not old_password or not new_password:
        return jsonify({'error': 'Se requieren old_password y new_password'}), 400
    db = get_db()
    user = db.execute("SELECT uuid, password_hash FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    if not verify_password(old_password, user['password_hash']):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401
    new_hash = hash_password(new_password)
    db.execute("UPDATE beings SET password_hash = ? WHERE uuid = ?", (new_hash, user['uuid']))
    db.commit()
    return jsonify({'mensaje': 'Contraseña actualizada correctamente'})

@app.route('/alumno/ciclo_actual', methods=['GET'])
@login_required
def ciclo_actual_self():
    uuid = session['user_uuid']
    db = get_db()
    alumno = db.execute("SELECT id, nivel_actual FROM beings WHERE uuid = ?", (uuid,)).fetchone()
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    ciclo = db.execute("""
        SELECT * FROM learning_cycles 
        WHERE student_id = ? AND level_id = ? AND objetivo_alcanzado = 0
        ORDER BY started_at DESC LIMIT 1
    """, (alumno['id'], alumno['nivel_actual'])).fetchone()
    if ciclo:
        return jsonify(dict(ciclo))
    return jsonify({'mensaje': 'No hay ciclo activo'}), 404

@app.route('/alumno/iniciar_ciclo', methods=['POST'])
@login_required
def iniciar_ciclo_self():
    uuid = session['user_uuid']
    db = get_db()
    alumno = db.execute("SELECT id, nivel_actual FROM beings WHERE uuid = ?", (uuid,)).fetchone()
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    # Verificar ciclo activo
    activo = db.execute("SELECT id FROM learning_cycles WHERE student_id = ? AND level_id = ? AND objetivo_alcanzado = 0", (alumno['id'], alumno['nivel_actual'])).fetchone()
    if activo:
        return jsonify({'error': 'Ya hay un ciclo activo'}), 409
    nivel_siguiente = alumno['nivel_actual'] + 1
    if nivel_siguiente > 22:
        return jsonify({'error': 'Ya completaste todos los niveles'}), 400
    maestro = db.execute("SELECT id, zona_actual FROM beings WHERE disponible_para_ensenar = 1 AND ciclos_completados >= ? LIMIT 1", (nivel_siguiente,)).fetchone()
    if not maestro:
        return jsonify({'error': 'No hay maestros disponibles'}), 503
    cursor = db.execute("""
        INSERT INTO learning_cycles (student_id, level_id, cycle_number, master_id, entorno, situacion, reto)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (alumno['id'], alumno['nivel_actual'], 1, maestro['id'], 'Zona Verde 45D', 'Encuentro con el maestro', 'Completar el objetivo del nivel actual'))
    db.commit()
    nuevo_ciclo = db.execute("SELECT * FROM learning_cycles WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({'mensaje': 'Ciclo iniciado', 'ciclo': dict(nuevo_ciclo), 'instrucciones': f'Toma un ducto a {maestro["zona_actual"]}. Te espera en 10 minutos.'}), 201

# =====================================================
# BLOQUE HERMES - VESTÍBULO Y ADMINISTRACIÓN
# =====================================================
# Dependencias adicionales (si no están, instalar con pip)
import requests
import json
from functools import wraps

# ------------------- FUNCIONES DE BÚSQUEDA PARA HERMES -------------------
def buscar_faq(mensaje, db):
    rows = db.execute("SELECT palabras_clave, respuesta FROM respuestas_estandar WHERE activa=1").fetchall()
    best = None
    max_coinc = 0
    for r in rows:
        claves = [k.strip().lower() for k in r['palabras_clave'].split(',')]
        coinc = sum(1 for k in claves if k in mensaje)
        if coinc > max_coinc:
            max_coinc = coinc
            best = r['respuesta']
    return best if max_coinc >= 1 else None

def buscar_cita(mensaje, db):
    rows = db.execute("SELECT autor, cita, palabras_clave FROM citas_celebres WHERE activa=1").fetchall()
    best = None
    max_coinc = 0
    for r in rows:
        claves = [k.strip().lower() for k in r['palabras_clave'].split(',')]
        coinc = sum(1 for k in claves if k in mensaje)
        if coinc > max_coinc:
            max_coinc = coinc
            best = r
    return best if max_coinc >= 1 else None

def buscar_parabola(mensaje, db):
    rows = db.execute("SELECT parabola, palabras_clave FROM parabolas_hermes WHERE activa=1").fetchall()
    best = None
    max_coinc = 0
    for r in rows:
        claves = [k.strip().lower() for k in r['palabras_clave'].split(',')]
        coinc = sum(1 for k in claves if k in mensaje)
        if coinc > max_coinc:
            max_coinc = coinc
            best = r['parabola']
    return best if max_coinc >= 1 else None

def buscar_dialectica(mensaje, db, nivel_visitante=0, contexto='general'):
    """
    Busca en ensenanza_dialectica la mejor coincidencia de palabras clave,
    filtrando por:
    - activo=1, aprobado=1
    - nivel_asociado <= nivel_visitante
    - contexto_cultural = contexto del visitante o 'general'
    """
    query = """
        SELECT id, ejemplo_dialectico, pregunta, palabras_clave, contexto_cultural, nivel_asociado
        FROM ensenanza_dialectica
        WHERE activo=1 AND aprobado=1 
          AND nivel_asociado <= ?
          AND (contexto_cultural = ? OR contexto_cultural = 'general')
        ORDER BY (contexto_cultural = ?) DESC
    """
    rows = db.execute(query, (nivel_visitante, contexto, contexto)).fetchall()
    best = None
    max_coinc = 0
    for r in rows:
        claves = [k.strip().lower() for k in r['palabras_clave'].split(',')]
        coinc = sum(1 for k in claves if k in mensaje)
        if coinc > max_coinc:
            max_coinc = coinc
            best = r
    return best if max_coinc >= 1 else None

# ========== NUEVAS FUNCIONES PARA MEMORIA Y CICLO ENEAGRAMÁTICO ==========
import uuid

def obtener_usuario_id(session, seudonimo=None):
    if 'user_uuid' in session:
        return session['user_uuid']
    else:
        # Si viene un seudónimo, lo usamos para identificar al anónimo
        if seudonimo and seudonimo.strip():
            return f"anon_{seudonimo.strip()}"
        else:
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            return f"anon_{session['session_id']}"

def registrar_pregunta(usuario_id, pregunta, db):
    db.execute("INSERT INTO memoria_preguntas (usuario_id, pregunta) VALUES (?, ?)", (usuario_id, pregunta))
    # Mantener solo las últimas 5 preguntas por usuario
    db.execute("""
        DELETE FROM memoria_preguntas 
        WHERE id IN (
            SELECT id FROM memoria_preguntas 
            WHERE usuario_id = ? 
            ORDER BY fecha DESC 
            LIMIT -1 OFFSET 5
        )
    """, (usuario_id,))
    db.commit()

def es_pregunta_repetida(usuario_id, pregunta, db):
    rows = db.execute(
        "SELECT pregunta FROM memoria_preguntas WHERE usuario_id = ? ORDER BY fecha DESC LIMIT 5",
        (usuario_id,)
    ).fetchall()
    for r in rows:
        if r['pregunta'].strip().lower() == pregunta.strip().lower():
            return True
    return False

def obtener_ciclo_actual(db):
    row = db.execute("SELECT ciclo_eneagrama FROM estado_hermes WHERE id = 1").fetchone()
    if not row:
        db.execute("INSERT INTO estado_hermes (id, ciclo_eneagrama) VALUES (1, 1)")
        db.commit()
        return 1
    return row['ciclo_eneagrama']

def avanzar_ciclo(db):
    actual = obtener_ciclo_actual(db)
    siguiente = actual + 1 if actual < 9 else 1
    db.execute("UPDATE estado_hermes SET ciclo_eneagrama = ? WHERE id = 1", (siguiente,))
    db.commit()

def aplicar_estilo_eneagrama(respuesta_base, tipo, db):
    estilo = db.execute("SELECT prefacio, sufijo_pregunta FROM estilos_eneagrama WHERE tipo = ?", (tipo,)).fetchone()
    if not estilo:
        return respuesta_base
    # Si la respuesta base ya tiene una pregunta al final, la reemplazamos
    if respuesta_base.strip().endswith('?'):
        partes = respuesta_base.rsplit('?', 1)
        contenido = partes[0].strip()
    else:
        contenido = respuesta_base
    nueva = f"{estilo['prefacio']} {contenido}. {estilo['sufijo_pregunta']}"
    return nueva.strip()
    
# ------------------- ENDPOINT PRINCIPAL DEL CHAT -------------------
@app.route('/hermes/chat', methods=['POST'])
def chat_hermes():
    data = request.get_json()
    user_message = data.get('mensaje', '').strip().lower()
    seudonimo = data.get('seudonimo', '')
    usuario_id = obtener_usuario_id(session, seudonimo)
    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400

    contexto = data.get('contexto', 'es')
    session['contexto_cultural'] = contexto

    db = get_db()

    # Determinar nivel del visitante
    if 'user_uuid' in session:
        user = db.execute("SELECT nivel_actual FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
        nivel_visitante = user['nivel_actual'] if user else 0
    else:
        nivel_visitante = 0

    # 1. Dosificación (si la última respuesta fue larga)
    if session.get('ultima_larga', False):
        session['ultima_larga'] = False
        return jsonify({'respuesta': "Una idea basta por hoy. ¿Prefieres seguir aquí o cruzar la puerta para la práctica?"})

    # 2. Verificar repetición (usando memoria)
    if es_pregunta_repetida(usuario_id, user_message, db):
        criticas = [
            "Ya me lo has preguntado. Buscas lo mismo y esperas respuestas distintas. ¿Qué cambio real estás dispuesto a hacer hoy?",
            "Otra vez la misma pregunta… Tus palabras se repiten, pero tus acciones no. ¿Cuándo pasarás del dicho al hecho?",
            "Esa pregunta ya la hiciste. La respuesta no ha cambiado. ¿Has cambiado tú?",
            "Repites la pregunta porque la respuesta no te satisface. ¿Será que la respuesta está en hacer, no en preguntar?",
            "¿Esperas una respuesta diferente a la misma pregunta? La Escuela no da respuestas mágicas, sino espejos. ¿Has mirado el tuyo?"
        ]
        import random
        respuesta_base = random.choice(criticas)
        # Aplicar estilo eneagramático aleatorio (no avanza ciclo)
        tipo_enea = random.randint(1, 9)
        respuesta_final = aplicar_estilo_eneagrama(respuesta_base, tipo_enea, db)
        if len(respuesta_final) > 200:
            session['ultima_larga'] = True
        return jsonify({'respuesta': respuesta_final})

    # Registrar pregunta nueva (no repetida)
    registrar_pregunta(usuario_id, user_message, db)

    # 3. Buscar respuesta base (temas recurrentes, citas, parábolas, dialéctica)
    respuesta_base = None

    # a) Temas recurrentes (FAQ)
    tema = buscar_faq(user_message, db)
    if tema:
        respuesta_base = tema
    else:
        # b) Citas
        cita = buscar_cita(user_message, db)
        if cita:
            respuesta_base = f"{cita['autor']} dijo: \"{cita['cita']}\". Para digerirlo necesitas hechos, no más palabras. ¿Te animas a una experiencia concreta en la Escuela?"
        else:
            # c) Parábolas
            parabola = buscar_parabola(user_message, db)
            if parabola:
                respuesta_base = parabola + " ¿Quieres entender por qué esto se aplica a tu vida? Regístrate y te lo mostramos con hechos."
            else:
                # d) Dialéctica (con manejo de pendiente)
                dialectica = buscar_dialectica(user_message, db, nivel_visitante, contexto)
                if dialectica:
                    respuesta_base = f"{dialectica['ejemplo_dialectico']}\n\n{dialectica['pregunta']}"
                    session['pendiente_dialectica'] = dialectica['id']
                else:
                    pendiente = session.get('pendiente_dialectica')
                    if pendiente:
                        dialectica_resp = db.execute("SELECT respuesta FROM ensenanza_dialectica WHERE id = ?", (pendiente,)).fetchone()
                        session.pop('pendiente_dialectica', None)
                        if dialectica_resp and dialectica_resp['respuesta']:
                            respuesta_base = dialectica_resp['respuesta'] + " ¿Descubrirás más si te registras?"
                        else:
                            respuesta_base = "La respuesta está dentro de ti. La Escuela te ayuda a encontrarla. ¿Te atreves a entrar?"
                    else:
                        # e) Fallback propio (sin Ollama)
                        fallbacks = [
                            "Tu pregunta es profunda. Demasiado para el vestíbulo. Dentro de la Escuela hay prácticas que la responderán con hechos, no palabras. ¿Te animas a entrar?",
                            "El mensajero no puede revelar más aquí. La puerta está abierta. Dentro encontrarás ejercicios que aclaran lo que ahora preguntas.",
                            "Esa es una cuestión que requiere experiencia, no explicación. ¿Te atreves a dar el primer paso y registrarte?",
                            "No tengo una respuesta completa para eso. Pero dentro de la Escuela hay caminos que te mostrarán. ¿Quieres recorrer uno?",
                            "Tu curiosidad es la llave. ¿Quieres usarla para abrir la puerta del nivel 1?"
                        ]
                        import random
                        respuesta_base = random.choice(fallbacks)

    # 4. Aplicar estilo eneagramático rotatorio (solo a respuestas que no son críticas)
    ciclo_actual = obtener_ciclo_actual(db)
    respuesta_final = aplicar_estilo_eneagrama(respuesta_base, ciclo_actual, db)
    avanzar_ciclo(db)

    # 5. Dosificación por longitud
    if len(respuesta_final) > 200:
        session['ultima_larga'] = True

    return jsonify({'respuesta': respuesta_final})
    
# ------------------- ENDPOINT PARA MAESTROS (APORTAR DIALÉCTICA) -------------------
@app.route('/maestro/dialectica', methods=['POST'])
@login_required
def maestro_crear_dialectica():
    db = get_db()
    usuario = db.execute("SELECT uuid, nivel_actual, ciclos_completados, contexto_cultural FROM beings WHERE uuid = ?", 
                         (session['user_uuid'],)).fetchone()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    if usuario['ciclos_completados'] < 1 and usuario['nivel_actual'] <= 1:
        return jsonify({'error': 'Solo maestros con ciclo superior a 1 pueden aportar conceptos'}), 403

    data = request.get_json()
    required = ['concepto', 'ejemplo_dialectico', 'pregunta', 'palabras_clave']
    if not all(k in data for k in required):
        return jsonify({'error': f'Faltan campos: {required}'}), 400

    contexto = data.get('contexto_cultural') or usuario['contexto_cultural'] or 'general'
    cursor = db.execute("""
        INSERT INTO ensenanza_dialectica 
        (concepto, ejemplo_dialectico, pregunta, respuesta, palabras_clave, 
         nivel_asociado, tradicion, es_canonico, creado_por_uuid, contexto_cultural, aprobado)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 1)
    """, (data['concepto'], data['ejemplo_dialectico'], data['pregunta'], data.get('respuesta'),
          data['palabras_clave'], data.get('nivel_asociado', 0), data.get('tradicion'),
          session['user_uuid'], contexto))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'mensaje': 'Concepto dialéctico añadido. Quedará visible para visitantes de tu contexto cultural.'})

# ------------------- ADMIN CRUD: RESPUESTAS ESTÁNDAR (FAQ) -------------------
@app.route('/admin/faq', methods=['GET'])
@superusuario_required
def listar_faq():
    db = get_db()
    rows = db.execute("SELECT id, palabras_clave, respuesta, activa, es_canonico, tradicion FROM respuestas_estandar ORDER BY es_canonico DESC, id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/admin/faq', methods=['POST'])
@superusuario_required
def crear_faq():
    data = request.get_json()
    if not data.get('palabras_clave') or not data.get('respuesta'):
        return jsonify({'error': 'palabras_clave y respuesta requeridos'}), 400
    db = get_db()
    cursor = db.execute(
        "INSERT INTO respuestas_estandar (palabras_clave, respuesta, tradicion, es_canonico) VALUES (?, ?, ?, 0)",
        (data['palabras_clave'], data['respuesta'], data.get('tradicion'))
    )
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'mensaje': 'FAQ creada'})

@app.route('/admin/faq/<int:id>', methods=['PUT'])
@superusuario_required
def actualizar_faq(id):
    data = request.get_json()
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM respuestas_estandar WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede modificar una respuesta canónica'}), 403
    db.execute("""
        UPDATE respuestas_estandar 
        SET palabras_clave = COALESCE(?, palabras_clave),
            respuesta = COALESCE(?, respuesta),
            activa = COALESCE(?, activa),
            tradicion = COALESCE(?, tradicion)
        WHERE id = ?
    """, (data.get('palabras_clave'), data.get('respuesta'), data.get('activa'), data.get('tradicion'), id))
    db.commit()
    return jsonify({'mensaje': 'FAQ actualizada'})

@app.route('/admin/faq/<int:id>', methods=['DELETE'])
@superusuario_required
def eliminar_faq(id):
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM respuestas_estandar WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede eliminar una respuesta canónica'}), 403
    db.execute("DELETE FROM respuestas_estandar WHERE id = ?", (id,))
    db.commit()
    return jsonify({'mensaje': 'FAQ eliminada'})

# ------------------- ADMIN CRUD: CITAS CÉLEBRES -------------------
@app.route('/admin/citas', methods=['GET'])
@superusuario_required
def listar_citas():
    db = get_db()
    rows = db.execute("SELECT id, autor, cita, palabras_clave, tradicion, es_canonico, activa FROM citas_celebres ORDER BY es_canonico DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/admin/citas', methods=['POST'])
@superusuario_required
def crear_cita():
    data = request.get_json()
    if not all(k in data for k in ('autor', 'cita', 'palabras_clave')):
        return jsonify({'error': 'autor, cita y palabras_clave requeridos'}), 400
    db = get_db()
    cursor = db.execute(
        "INSERT INTO citas_celebres (autor, cita, palabras_clave, tradicion, es_canonico) VALUES (?, ?, ?, ?, 0)",
        (data['autor'], data['cita'], data['palabras_clave'], data.get('tradicion'))
    )
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'mensaje': 'Cita creada'})

@app.route('/admin/citas/<int:id>', methods=['PUT'])
@superusuario_required
def actualizar_cita(id):
    data = request.get_json()
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM citas_celebres WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede modificar una cita canónica'}), 403
    db.execute("""
        UPDATE citas_celebres 
        SET autor = COALESCE(?, autor),
            cita = COALESCE(?, cita),
            palabras_clave = COALESCE(?, palabras_clave),
            tradicion = COALESCE(?, tradicion),
            activa = COALESCE(?, activa)
        WHERE id = ?
    """, (data.get('autor'), data.get('cita'), data.get('palabras_clave'), data.get('tradicion'), data.get('activa'), id))
    db.commit()
    return jsonify({'mensaje': 'Cita actualizada'})

@app.route('/admin/citas/<int:id>', methods=['DELETE'])
@superusuario_required
def eliminar_cita(id):
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM citas_celebres WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede eliminar una cita canónica'}), 403
    db.execute("DELETE FROM citas_celebres WHERE id = ?", (id,))
    db.commit()
    return jsonify({'mensaje': 'Cita eliminada'})

# ------------------- ADMIN CRUD: PARÁBOLAS -------------------
@app.route('/admin/parabolas', methods=['GET'])
@superusuario_required
def listar_parabolas():
    db = get_db()
    rows = db.execute("SELECT id, palabras_clave, parabola, tradicion, es_canonico, activa FROM parabolas_hermes ORDER BY es_canonico DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/admin/parabolas', methods=['POST'])
@superusuario_required
def crear_parabola():
    data = request.get_json()
    if not all(k in data for k in ('palabras_clave', 'parabola')):
        return jsonify({'error': 'palabras_clave y parabola requeridos'}), 400
    db = get_db()
    cursor = db.execute(
        "INSERT INTO parabolas_hermes (palabras_clave, parabola, tradicion, es_canonico) VALUES (?, ?, ?, 0)",
        (data['palabras_clave'], data['parabola'], data.get('tradicion'))
    )
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'mensaje': 'Parábola creada'})

@app.route('/admin/parabolas/<int:id>', methods=['PUT'])
@superusuario_required
def actualizar_parabola(id):
    data = request.get_json()
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM parabolas_hermes WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede modificar una parábola canónica'}), 403
    db.execute("""
        UPDATE parabolas_hermes 
        SET palabras_clave = COALESCE(?, palabras_clave),
            parabola = COALESCE(?, parabola),
            tradicion = COALESCE(?, tradicion),
            activa = COALESCE(?, activa)
        WHERE id = ?
    """, (data.get('palabras_clave'), data.get('parabola'), data.get('tradicion'), data.get('activa'), id))
    db.commit()
    return jsonify({'mensaje': 'Parábola actualizada'})

@app.route('/admin/parabolas/<int:id>', methods=['DELETE'])
@superusuario_required
def eliminar_parabola(id):
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM parabolas_hermes WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede eliminar una parábola canónica'}), 403
    db.execute("DELETE FROM parabolas_hermes WHERE id = ?", (id,))
    db.commit()
    return jsonify({'mensaje': 'Parábola eliminada'})

# ------------------- ADMIN CRUD: ENSEÑANZA DIALÉCTICA -------------------
@app.route('/admin/dialectica', methods=['GET'])
@superusuario_required
def listar_dialectica():
    db = get_db()
    rows = db.execute("""
        SELECT id, concepto, ejemplo_dialectico, pregunta, respuesta, palabras_clave, 
               nivel_asociado, tradicion, es_canonico, activo, veces_usada, contexto_cultural
        FROM ensenanza_dialectica 
        ORDER BY es_canonico DESC, id DESC
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/admin/dialectica', methods=['POST'])
@superusuario_required
def crear_dialectica():
    data = request.get_json()
    required = ['concepto', 'ejemplo_dialectico', 'pregunta', 'palabras_clave']
    if not all(k in data for k in required):
        return jsonify({'error': f'Faltan campos: {required}'}), 400
    db = get_db()
    cursor = db.execute("""
        INSERT INTO ensenanza_dialectica 
        (concepto, ejemplo_dialectico, pregunta, respuesta, palabras_clave, nivel_asociado, tradicion, contexto_cultural, es_canonico)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (data['concepto'], data['ejemplo_dialectico'], data['pregunta'], data.get('respuesta'),
          data['palabras_clave'], data.get('nivel_asociado', 0), data.get('tradicion'), data.get('contexto_cultural')))
    db.commit()
    return jsonify({'id': cursor.lastrowid, 'mensaje': 'Entrada dialéctica creada'})

@app.route('/admin/dialectica/<int:id>', methods=['PUT'])
@superusuario_required
def actualizar_dialectica(id):
    data = request.get_json()
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM ensenanza_dialectica WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede modificar una entrada canónica'}), 403
    db.execute("""
        UPDATE ensenanza_dialectica 
        SET concepto = COALESCE(?, concepto),
            ejemplo_dialectico = COALESCE(?, ejemplo_dialectico),
            pregunta = COALESCE(?, pregunta),
            respuesta = COALESCE(?, respuesta),
            palabras_clave = COALESCE(?, palabras_clave),
            nivel_asociado = COALESCE(?, nivel_asociado),
            tradicion = COALESCE(?, tradicion),
            contexto_cultural = COALESCE(?, contexto_cultural),
            activo = COALESCE(?, activo)
        WHERE id = ?
    """, (data.get('concepto'), data.get('ejemplo_dialectico'), data.get('pregunta'), data.get('respuesta'),
          data.get('palabras_clave'), data.get('nivel_asociado'), data.get('tradicion'), data.get('contexto_cultural'),
          data.get('activo'), id))
    db.commit()
    return jsonify({'mensaje': 'Entrada actualizada'})

@app.route('/admin/dialectica/<int:id>', methods=['DELETE'])
@superusuario_required
def eliminar_dialectica(id):
    db = get_db()
    canonico = db.execute("SELECT es_canonico FROM ensenanza_dialectica WHERE id = ?", (id,)).fetchone()
    if canonico and canonico['es_canonico'] == 1:
        return jsonify({'error': 'No se puede eliminar una entrada canónica'}), 403
    db.execute("DELETE FROM ensenanza_dialectica WHERE id = ?", (id,))
    db.commit()
    return jsonify({'mensaje': 'Entrada eliminada'})
        
# ------------------- FORO DEL VESTÍBULO -------------------
@app.route('/vestibulo/hilos', methods=['GET'])
def vestibulo_hilos():
    db = get_db()
    hilos = db.execute("SELECT id, titulo, autor, fecha_creacion FROM vestibulo_hilos ORDER BY fecha_creacion DESC LIMIT 50").fetchall()
    return jsonify([dict(h) for h in hilos])

@app.route('/vestibulo/hilos', methods=['POST'])
def vestibulo_crear_hilo():
    data = request.get_json()
    db = get_db()
    cursor = db.execute("INSERT INTO vestibulo_hilos (titulo, autor) VALUES (?, ?)", (data['titulo'], data['autor']))
    hilo_id = cursor.lastrowid
    db.execute("INSERT INTO vestibulo_mensajes (hilo_id, autor, contenido, es_respuesta) VALUES (?, ?, ?, 0)", (hilo_id, data['autor'], data['primer_mensaje']))
    db.commit()
    return jsonify({'mensaje': 'Hilo creado'})

@app.route('/vestibulo/hilos/<int:hilo_id>/mensajes', methods=['GET'])
def vestibulo_mensajes(hilo_id):
    db = get_db()
    mensajes = db.execute("SELECT autor, contenido, fecha FROM vestibulo_mensajes WHERE hilo_id = ? ORDER BY fecha", (hilo_id,)).fetchall()
    return jsonify([dict(m) for m in mensajes])
    
@app.route('/')
def frontend_root():
    return send_from_directory('frontend', 'index.html')    


# ------------------- INICIAR SERVIDOR -------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
