from flask import Flask, render_template, request, redirect, send_file
import os, sqlite3, csv
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
            tipo TEXT, nome TEXT, documento TEXT, celular TEXT, contato TEXT,
            cep TEXT, endereco TEXT, bairro TEXT, email TEXT,
            observacao TEXT, numero TEXT, complemento TEXT)''')
init_db()

@app.route('/')
def index():
    return "Sistema Resolve online!"

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    if request.method == 'POST':
        d = request.form

        nome_formatado = '🔐 ' + ' '.join([
            palavra.capitalize() if len(palavra) > 2 else palavra.lower()
            for palavra in d['nome'].split()
        ])

        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO clientes (
                    tipo, nome, documento, celular, contato, cep,
                    endereco, bairro, email, observacao, numero, complemento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        d['tipo'],
                        nome_formatado,
                        d['documento'],
                        d['celular'],
                        d.get('contato', ''),
                        d['cep'],
                        d['endereco'],
                        d['bairro'],
                        d['email'],
                        d['observacao'],
                        d.get('numero', ''),
                        d.get('complemento', '')
                    )
                )

            # Salvar também em CSV
            with open('clientes.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    d['tipo'],
                    nome_formatado,
                    d['documento'],
                    d['celular'],
                    d.get('contato', ''),
                    d['cep'],
                    d['endereco'],
                    d['bairro'],
                    d['email'].lower(),
                    d['observacao'],
                    d.get('numero', ''),
                    d.get('complemento', '')
                ])

            return redirect('/')
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {e}")
            return "Erro interno ao cadastrar cliente", 500
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
            c.execute('''INSERT INTO chamados (
                data, horario, cliente, telefone, endereco, bairro, servico,
                produto, status, forma_pg, quem_fez, valor, observacao, foto_antes, foto_depois)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    d['data'], d['horario'], d['cliente'], d['telefone'], d['endereco'],
                    d['bairro'], d['servico'], d['produto'], d['status'], d['forma_pg'],
                    d['quem_fez'], d['valor'], d['observacao'], f1.filename, f2.filename
                )
            )
        return redirect('/')
    return render_template('novo.html')

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/exportar_clientes')
def exportar_clientes():
    caminho = 'clientes.csv'
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    return "Arquivo clientes.csv não encontrado", 404
