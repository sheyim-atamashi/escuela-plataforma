 atamashi   main  ~  PythonProyectos  Escuela  git commit -m "sube BD correcta con superusuario_control y todas las tablas"
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
#!/bin/bash
# Script único para configurar el superusuario en Render
# Uso: chmod +x setup_superusuario.sh && ./setup_superusuario.sh

echo "🔧 Configurando superusuario en la Escuela de Misterios..."

# 1. Solicitar la clave al usuario (no se mostrará en pantalla)
read -sp "Introduce la clave para el superusuario: " CLAVE
echo ""

# 2. Generar el hash Argon2 de la clave (requiere python y argon2-cffi)
echo "🔄 Generando hash Argon2 (esto puede tomar unos segundos)..."
HASH=$(python3 -c "
import argon2
ph = argon2.PasswordHasher(time_cost=8, memory_cost=1024, parallelism=2)
print(ph.hash('$CLAVE'))
")
if [ -z "$HASH" ]; then
    echo "❌ Error: No se pudo generar el hash. Asegúrate de tener instalado 'argon2-cffi'."
    exit 1
fi
echo "✅ Hash generado."

# 3. Crear tablas e insertar superusuario usando el endpoint de emergencia
URL="https://escuela-misterios.onrender.com/emergencia/ejecutar_sql"
SECRETO="Atamashi2026"

# Asegurar que la tabla beings existe (con todos los campos)
echo "🔄 Verificando/Creando tablas..."
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Secreto: $SECRETO" \
  -d '{"sql": "CREATE TABLE IF NOT EXISTS beings (id INTEGER PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, nombre TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, tipo TEXT DEFAULT '\''human'\'', es_androide BOOLEAN DEFAULT 0, modelo_id INTEGER, fabricante TEXT, protocolo_maestro_instalado BOOLEAN DEFAULT 0, fecha_instalacion_protocolo TIMESTAMP, nivel_actual INTEGER DEFAULT 0, ciclo_general_actual INTEGER DEFAULT 1, ciclos_completados INTEGER DEFAULT 0, rol TEXT DEFAULT '\''alumno'\'', puede_gestionar_nivel0 BOOLEAN DEFAULT 0, lenguaje_pref TEXT DEFAULT '\''es'\'', contexto_cultural TEXT DEFAULT '\''latam'\'', disponible_para_ensenar BOOLEAN DEFAULT 0, zona_actual TEXT DEFAULT '\''Zona Verde 45D'\'', moneda_pref TEXT DEFAULT '\''USD'\'', capacitado_astrologia_escuela BOOLEAN DEFAULT 0, backup_url TEXT, fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"}' > /dev/null

# Crear tabla superusuario_control
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Secreto: $SECRETO" \
  -d '{"sql": "CREATE TABLE IF NOT EXISTS superusuario_control (id INTEGER PRIMARY KEY, superusuario_uuid TEXT UNIQUE, ultimo_acceso TIMESTAMP, fecha_expira TIMESTAMP, clave_emergencia TEXT, activo BOOLEAN DEFAULT 1, nota TEXT DEFAULT '\'''\'' )"}' > /dev/null

echo "✅ Tablas aseguradas."

# 4. Insertar o actualizar superusuario (usando INSERT OR REPLACE)
echo "🔄 Creando superusuario 'Atamashi'..."
UUID=$(uuidgen)
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Secreto: $SECRETO" \
  -d "{\"sql\": \"INSERT OR REPLACE INTO beings (uuid, nombre, password_hash, nivel_actual, ciclos_completados, rol) VALUES ('$UUID', 'Atamashi', '$HASH', 22, 22, 'superusuario')\"}" > /dev/null

# 5. Insertar o actualizar en superusuario_control
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Secreto: $SECRETO" \
  -d "{\"sql\": \"INSERT OR REPLACE INTO superusuario_control (superusuario_uuid, ultimo_acceso, activo) VALUES ('$UUID', datetime('now'), 1)\"}" > /dev/null

echo "✅ Superusuario 'Atamashi' creado/actualizado."

# 6. Probar login
echo "🧪 Probando login (no se mostrará la contraseña)..."
RESULTADO=$(curl -s -X POST "https://escuela-misterios.onrender.com/login" \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Atamashi\", \"password\":\"$CLAVE\"}")

if echo "$RESULTADO" | grep -q "Bienvenido"; then
    echo "✅ ¡Login exitoso! Superusuario configurado correctamente."
else
    echo "❌ Login falló. Respuesta: $RESULTADO"
    echo "🔍 Verifica que el endpoint /emergencia/ejecutar_sql esté activo en Render."
fi

echo "🎉 Proceso completado."
