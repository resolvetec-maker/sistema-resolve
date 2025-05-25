from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from fpdf import FPDF

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializa o banco de dados
DB_NAME = 'agendamentos.db'
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            horario TEXT,
            cliente TEXT,
            telefone TEXT,
            endereco TEXT,
            bairro TEXT,
            servico TEXT,
            produto TEXT,
            status TEXT,
            forma_pg TEXT,
            quem_fez TEXT,
            valor TEXT,
            observacao TEXT,
            foto_antes TEXT,
            foto_depois TEXT
        )''')
init_db()

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chamados ORDER BY data DESC, horario DESC")
        chamados = cursor.fetchall()
    return render_template('index.html', chamados=chamados)

@app.route('/novo', methods=['GET', 'POST'])
def novo_chamado():
    if request.method == 'POST':
        try:
            dados = request.form
            foto_antes = request.files['foto_antes']
            foto_depois = request.files['foto_depois']

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            filename_antes = secure_filename(foto_antes.filename)
            filepath_antes = os.path.join(app.config['UPLOAD_FOLDER'], filename_antes)
            foto_antes.save(filepath_antes)

            filename_depois = secure_filename(foto_depois.filename)
            filepath_depois = os.path.join(app.config['UPLOAD_FOLDER'], filename_depois)
            foto_depois.save(filepath_depois)

            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO chamados
                    (data, horario, cliente, telefone, endereco, bairro, servico, produto,
                     status, forma_pg, quem_fez, valor, observacao, foto_antes, foto_depois)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (dados['data'], dados['horario'], dados['cliente'], dados['telefone'],
                     dados['endereco'], dados['bairro'], dados['servico'], dados['produto'],
                     dados['status'], dados['forma_pg'], dados['quem_fez'], dados['valor'],
                     dados['observacao'], filename_antes, filename_depois))
            return redirect('/')
        except Exception as e:
            print(f"Erro ao cadastrar chamado: {e}")
            return "Erro interno no servidor", 500
    return render_template('novo.html')

@app.route('/os/<int:chamado_id>')
def gerar_os(chamado_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chamados WHERE id = ?", (chamado_id,))
        chamado = cursor.fetchone()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    campos = ["ID", "Data", "Horário", "Cliente", "Telefone", "Endereço", "Bairro",
              "Serviço", "Produto", "Status", "Forma de PG", "Quem Fez", "Valor",
              "Observação"]

    for i, campo in enumerate(campos):
        pdf.cell(0, 10, f"{campo}: {chamado[i]}", ln=True)

    # Inserir imagens se existirem
    foto_antes = os.path.join(app.config['UPLOAD_FOLDER'], chamado[14])
    foto_depois = os.path.join(app.config['UPLOAD_FOLDER'], chamado[15])

    if os.path.exists(foto_antes):
        pdf.cell(0, 10, "Foto Antes:", ln=True)
        pdf.image(foto_antes, w=100)

    if os.path.exists(foto_depois):
        pdf.cell(0, 10, "Foto Depois:", ln=True)
        pdf.image(foto_depois, w=100)

    os_path = f"ordens/os_{chamado_id}.pdf"
    os.makedirs("ordens", exist_ok=True)
    pdf.output(os_path)
    return send_file(os_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
