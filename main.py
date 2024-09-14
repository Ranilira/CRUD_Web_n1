from flask import Flask, jsonify, render_template
import sqlite3
import os
 
app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db
 
# Função para inicializar o banco de dados
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
 
if __name__ == '__main__':
    app.run(debug=True)