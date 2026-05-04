import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-desarrollo-no-usar-en-produccion")

# Configuración de Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Usuarios de ejemplo (solo para pruebas. Luego, base de datos)
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role  # 'aprendiz', 'ejecutor', 'maestro', 'admin'

users = {
    "atamashi": User(1, "atamashi", "admin123", "admin"),
    "maestro1": User(2, "maestro1", "maestro123", "maestro")
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if str(user.id) == user_id:
            return user
    return None

# Rutas públicas
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username and u.password == password), None)
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

# Rutas protegidas (requieren login)
@app.route('/dashboard')
@login_required
def dashboard():
    # Según el rol, mostrará cosas diferentes
    return render_template('dashboard.html', user=current_user)

@app.route('/nivel/<int:nivel_id>')
@login_required
def nivel(nivel_id):
    if nivel_id < 1 or nivel_id > 22:
        return "Nivel inválido", 404
    # Aquí luego cargarás el contenido real del nivel desde tus archivos o BD
    return render_template('nivel.html', nivel=nivel_id, user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
