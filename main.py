from flask import Flask, jsonify, render_template, request, redirect, flash, url_for, session
import sqlite3
import os
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pipopo'
bcrypt = Bcrypt(app)  # Inicializando Bcrypt com o aplicativo Flask

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

#inicializar o banco de dados
def init_db():
    with app.app_context():
        db = get_db()
        basedir = os.path.abspath(os.path.dirname(__file__))
        try:
            if not os.path.exists(os.path.join(basedir, 'banco/banco.sql')):
                print("Arquivo SQL não encontrado!")
                return "Arquivo SQL não encontrado!"
            with app.open_resource(os.path.join(basedir, 'banco/banco.sql'), mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            print("Banco de dados inicializado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
            return f"Erro ao inicializar o banco de dados: {e}"
        finally:
            db.close()

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/initdb')
def initialize_database():
    result = init_db()
    if result:
        return result
    return 'Banco de dados inicializado!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('email')
        password = request.form.get('password')

        # Conectar ao banco de dados e buscar o usuário
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE login = ?", (login,))
        user = cursor.fetchone()
        conn.close()

        # Verificar o user
        if user:
            #Verificar a senha
            if bcrypt.check_password_hash(user['password'], password):
                if user['status'] == 'bloqueado':
                    flash('Usuário bloqueado!', 'danger')
                    return redirect(url_for('login'))

                # Armazenar informações
                session['user_id'] = user['id']
                session['user_name'] = user['nome']
                flash(f'Bem-vindo(a) {user["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Login ou senha inválidos', 'danger')
        else:
            flash('Usuário não encontrado', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Conectar ao banco e verificar se o login já existe
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE login = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('O e-mail já está cadastrado. Tente outro.', 'danger')
            return redirect(url_for('register'))

        # Gerar o hash da senha
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Inserir o novo usuário no banco de dados
        cursor.execute("""
            INSERT INTO users (nome, login, password, created, modified, status)
            VALUES (?, ?, ?, datetime('now'), datetime('now'), 'ativo')
        """, (name, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastrar.html')

# Verificar se o usuário está logado antes de acessar o dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar o painel.', 'danger')
        return redirect(url_for('login'))

    return render_template('dashboard.html', user_name=session['user_name'])

@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Atualizar as informações do usuário
        cursor.execute("""
            UPDATE users
            SET nome = ?, login = ?, modified = datetime('now')
            WHERE id = ?
        """, (name, email, user_id))
        conn.commit()
        conn.close()

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Carregar os dados do usuário para edição
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('editar.html', user=user)

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Você foi desconectado!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
