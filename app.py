import os
import uuid
import secrets
import json
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, session, g, send_from_directory
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlite3
import requests   # ← esta es la librería para peticiones HTTP

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
        time_cost=8,
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
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        return send_from_directory('frontend', 'registro.html')
    
    # Si es POST, procesa el registro
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return send_from_directory('frontend', 'login.html')
    
    data = request.get_json()
    nombre = data.get('nombre')
    password = data.get('password')
    db = get_db()
    user = db.execute("SELECT uuid, password_hash, rol FROM beings WHERE nombre = ?", (nombre,)).fetchone()
    if not user or not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    session.permanent = True
    session['user_uuid'] = user['uuid']
    session['user_nombre'] = nombre
    
    # Bombón para superusuario
    if user['rol'] == 'superusuario':
        # Verificar si existe en superusuario_control; si no, crearlo con valores inocuos
        existe = db.execute("SELECT id FROM superusuario_control WHERE superusuario_uuid = ?", (user['uuid'],)).fetchone()
        if not existe:
            db.execute("INSERT INTO superusuario_control (superusuario_uuid, ultimo_acceso, activo) VALUES (?, ?, 0)", 
                       (user['uuid'], datetime.now().isoformat()))
        # Actualizar el último acceso (tanto si existía como si se creó ahora)
        db.execute("UPDATE superusuario_control SET ultimo_acceso = ? WHERE superusuario_uuid = ?", 
                   (datetime.now().isoformat(), user['uuid']))
    
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

    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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
    data = requests.get_json()
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

@app.route('/hermes/chat', methods=['POST'])
# =====================================================
# FUNCIONES AUXILIARES PARA HERMES
# =====================================================

def buscar_faq(mensaje, db):
    mensaje = mensaje.lower()
    rows = db.execute("SELECT palabras_clave, respuesta FROM respuestas_estandar WHERE activa=1").fetchall()
    best = None
    max_coinc = 0
    for r in rows:
        claves = [k.strip().lower() for k in r['palabras_clave'].split(',')]
        coinc = 0
        for k in claves:
            if k in mensaje:
                coinc += 1
  #      print(f"DEBUG FAQ: claves={claves}, coinc={coinc}, respuesta={r['respuesta'][:50]}")
        if coinc > max_coinc:
            max_coinc = coinc
            best = r['respuesta']
 #   print(f"DEBUG FAQ RESULT: max_coinc={max_coinc}, best={best[:50] if best else None}")
    # Si no hay coincidencia, devolver None
    if max_coinc == 0:
        return None
    return best
    
#faq = buscar_faq(user_message, db)
#print(f"FAQ devuelto: {faq}")

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
    query = """
        SELECT id, ejemplo_dialectico, pregunta, palabras_clave
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

def buscar_eneagrama(mensaje, db):
    # Mapeo simple de palabras a tipos
    map_tipo = {
        'error': 1, 'crítica': 1, 'crítico': 1, 'perfecto': 1, 'fallo': 1,
        'ayudar': 2, 'servicio': 2, 'necesito': 2, 'necesidad': 2,
        'éxito': 3, 'logro': 3, 'resultado': 3, 'meta': 3, 'competir': 3,
        'auténtico': 4, 'identidad': 4, 'sentir': 4, 'único': 4, 'emociones': 4,
        'saber': 5, 'conocimiento': 5, 'observar': 5, 'analizar': 5, 'teoría': 5,
        'miedo': 6, 'seguridad': 6, 'duda': 6, 'riesgo': 6, 'precaución': 6,
        'libertad': 7, 'opciones': 7, 'escapar': 7, 'aburrido': 7, 'aventura': 7,
        'control': 8, 'poder': 8, 'fuerza': 8, 'proteger': 8, 'dominar': 8,
        'paz': 9, 'armonía': 9, 'evitar': 9, 'confort': 9, 'tranquilo': 9
    }
    mensaje_lower = mensaje.lower()
    tipo = None
    for palabra, t in map_tipo.items():
        if palabra in mensaje_lower:
            tipo = t
            break
    if tipo is None:
        import random
        tipo = random.randint(1, 9)
    respuesta = db.execute(
        "SELECT respuesta FROM respuestas_eneagrama WHERE tipo = ? AND activa = 1 ORDER BY RANDOM() LIMIT 1",
        (tipo,)
    ).fetchone()
    return respuesta['respuesta'] if respuesta else None

def generar_con_modelo(mensaje):
   #  Si no quieres usar Ollama aún, comenta esta función y usa un fallback
    # Por ahora, devolvemos un mensaje genérico
    return "Soy Hermes. Si quieres respuestas más profundas, cruza la puerta y regístrate en la Escuela."

# =====================================================
# ENDPOINT DEL CHAT
# =====================================================

@app.route('/hermes/chat', methods=['POST'])
def chat_hermes():
    data = request.get_json()
    user_message = data.get('mensaje', '').strip().lower()
    contexto = data.get('contexto', 'es')
    session['contexto_cultural'] = contexto

    print(f"📩 Mensaje: {user_message} | Contexto: {contexto}")

    db = get_db()
    nivel_visitante = 0
    if 'user_uuid' in session:
        user = db.execute("SELECT nivel_actual FROM beings WHERE uuid = ?", (session['user_uuid'],)).fetchone()
        nivel_visitante = user['nivel_actual'] if user else 0

    # Dosificación
    if session.get('ultima_larga', False):
        session['ultima_larga'] = False
        return jsonify({'respuesta': "Una idea basta por hoy. ¿Cruzas la puerta para la práctica?"})

    # 1. FAQ
    faq = buscar_faq(user_message, db)
    if faq:
        if len(faq) > 250 or faq.count('.') > 2:
            session['ultima_larga'] = True
        return jsonify({'respuesta': faq})

    # 2. Eneagrama
    enea = buscar_eneagrama(user_message, db)
    if enea:
        return jsonify({'respuesta': enea})

    # 3. Citas
    cita = buscar_cita(user_message, db)
    if cita:
        respuesta = f"{cita['autor']} dijo: \"{cita['cita']}\". ¿Te animas a una experiencia concreta en la Escuela?"
        session['ultima_larga'] = True
        return jsonify({'respuesta': respuesta})

    # 4. Parábolas
    parabola = buscar_parabola(user_message, db)
    if parabola:
        respuesta = parabola + " ¿Quieres entender por qué esto se aplica a tu vida? Regístrate."
        if len(respuesta) > 200:
            session['ultima_larga'] = True
        return jsonify({'respuesta': respuesta})

    # 5. Dialéctica (con respuesta pendiente)
    dialectica = buscar_dialectica(user_message, db, nivel_visitante, contexto)
    if dialectica:
        respuesta = f"{dialectica['ejemplo_dialectico']}\n\n{dialectica['pregunta']}"
        session['pendiente_dialectica'] = dialectica['id']
        session['ultima_larga'] = True
        return jsonify({'respuesta': respuesta})

    pendiente = session.get('pendiente_dialectica')
    if pendiente:
        dialectica_resp = db.execute("SELECT respuesta FROM ensenanza_dialectica WHERE id = ?", (pendiente,)).fetchone()
        session.pop('pendiente_dialectica', None)
        if dialectica_resp and dialectica_resp['respuesta']:
            return jsonify({'respuesta': dialectica_resp['respuesta'] + " ¿Descubrirás más si te registras?"})
        else:
            return jsonify({'respuesta': "La respuesta está dentro de ti. ¿Te atreves a entrar?"})

    # 6. Generación con modelo (fallback)
    respuesta_generada = generar_con_modelo(user_message)
    if len(respuesta_generada) > 200:
        session['ultima_larga'] = True
    return jsonify({'respuesta': respuesta_generada})
    
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

@app.route('/admin/panel')
@login_required
def admin_panel():
    return send_from_directory('frontend', 'admin_panel.html')
# Crear tablas si no existen (al iniciar la app)
with app.app_context():
    init_db() 

# ------------------- INICIAR SERVIDOR -------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
