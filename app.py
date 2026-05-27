from flask import Flask, jsonify, request, send_from_directory
import os
import requests
import random

app = Flask(__name__)
app.secret_key = 'clave_temporal_para_pruebas'

# Configuración para servir archivos estáticos
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('frontend', filename)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

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

def analizar_interes(usuario_id, db):
    # Obtener últimas 5 preguntas
    rows = db.execute(
        "SELECT pregunta FROM memoria_preguntas WHERE usuario_id = ? ORDER BY fecha DESC LIMIT 5",
        (usuario_id,)
    ).fetchall()

    if len(rows) < 3:
        return 1

    # Detectar si las preguntas son sobre temas relacionados
    temas = []
    for r in rows:
        texto = r['pregunta'].lower()
        if any(p in texto for p in ['voluntad', 'consciencia', 'sueño', 'alma', 'despertar']):
            temas.append('profundo')
        else:
            temas.append('superficial')

    if temas.count('profundo') >= 3:
        return 3
    elif temas.count('profundo') >= 1:
        return 2
    else:
        return 1

def detectar_trigger(mensaje):
    mensaje_lower = mensaje.lower()
    triggers = {
        'miedo': ['miedo', 'temor', 'pánico', 'no puedo', 'me da cosa', 'inseguro'],
        'duda': ['no sé', 'quizás', 'tal vez', 'dudo', 'incierto', 'no entiendo'],
        'bloqueo': ['confuso', 'no avanza', 'estancado', 'no puedo más']
    }
    for tipo, palabras in triggers.items():
        for palabra in palabras:
            if palabra in mensaje_lower:
                return tipo
    return None

def obtener_historial(usuario_id, db, limite=3):
    rows = db.execute(
        "SELECT pregunta FROM memoria_preguntas WHERE usuario_id = ? ORDER BY fecha DESC LIMIT ?",
        (usuario_id, limite)
    ).fetchall()
    return [r['pregunta'] for r in rows]

def registrar_pregunta(usuario_id, pregunta, db):
    db.execute("INSERT INTO memoria_preguntas (usuario_id, pregunta) VALUES (?, ?)", (usuario_id, pregunta))
    # Mantener solo las últimas 5 preguntas
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
    
# Endpoint del chat (simplificado)
@app.route('/hermes/chat', methods=['POST'])
def chat_hermes():
    data = request.get_json()
    user_message = data.get('mensaje', '').strip()
    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400

    # Leer API key desde el entorno (definida en wsgi.py)
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    if not DEEPSEEK_API_KEY:
        return jsonify({'respuesta': "Hermes no puede hablar. API key no configurada."}), 500

    DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Eres Hermes, el mensajero de la Escuela de Misterios de la Sabiduría. Responde con 1 o 2 frases cortas, con misterio, dejando una pregunta abierta. No des respuestas completas. Si el usuario muestra interés, invítale a registrarse."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.85,
            "max_tokens": 120,
            "stream": False
        }
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content'].strip()
            return jsonify({'respuesta': reply})
        else:
            return jsonify({'respuesta': "Hermes está en una tormenta cósmica. Vuelve a preguntar."})
    except Exception as e:
        print(f"Error en Hermes: {e}")
        return jsonify({'respuesta': "Hermes no responde ahora. Intenta más tarde."})

if __name__ == '__main__':
    app.run()
