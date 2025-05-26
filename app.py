from flask import Flask, render_template, request, redirect, send_file
import os, sqlite3
from werkzeug.utils import secure_filename
from fpdf import FPDF

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_NAME = 'agendamentos.db'
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT, horario TEXT, cliente TEXT, telefone TEXT,
            endereco TEXT, bairro TEXT, servico TEXT, produto TEXT,
            status TEXT, forma_pg TEXT, quem_fez TEXT, valor TEXT,
            observacao TEXT, foto_antes TEXT, foto_depois TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, documento TEXT, celular TEXT, endereco TEXT,
            bairro TEXT, email TEXT, observacao TEXT)''')
init_db()

@app.route('/')
def index():
    return "Sistema Resolve online!"

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    if request.method == 'POST':
        d = request.form
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO clientes (nome, documento, celular, endereco, bairro, email, observacao)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (d['nome'], d['documento'], d['celular'], d['endereco'], d['bairro'], d['email'], d['observacao']))
        return redirect('/')
    return render_template('cliente.html')

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        d = request.form
        f1 = request.files['foto_antes']
        f2 = request.files['foto_depois']
        f1_path = os.path.join(app.config['UPLOAD_FOLDER'], f1.filename)
        f2_path = os.path.join(app.config['UPLOAD_FOLDER'], f2.filename)
        f1.save(f1_path)
        f2.save(f2_path)
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO chamados (data, horario, cliente, telefone, endereco, bairro, servico, produto, 
                status, forma_pg, quem_fez, valor, observacao, foto_antes, foto_depois)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (d['data'], d['horario'], d['cliente'], d['telefone'], d['endereco'], d['bairro'], d['servico'],
                 d['produto'], d['status'], d['forma_pg'], d['quem_fez'], d['valor'], d['observacao'],
                 f1.filename, f2.filename))
        return redirect('/')
    return render_template('novo.html')

if __name__ == '__main__':
    app.run(debug=True)
