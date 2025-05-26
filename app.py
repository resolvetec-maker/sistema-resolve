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
        c.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT, nome TEXT, documento TEXT, celular TEXT, contato TEXT,
            cep TEXT, endereco TEXT, numero TEXT, complemento TEXT, bairro TEXT,
            email TEXT, observacao TEXT
        )''')
init_db()

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)
    return len(cnpj) == 14 and cnpj.isdigit()

@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    if request.method == 'POST':
        d = request.form
        tipo = d['tipo']
        doc = re.sub(r'\D', '', d['documento'])

        if tipo == 'pf' and not validar_cpf(doc):
            return "CPF inválido", 400
        if tipo == 'pj' and not validar_cnpj(doc):
            return "CNPJ inválido", 400

        nome = '🔐 ' + ' '.join([
            palavra.capitalize() if len(palavra) > 2 else palavra.lower()
            for palavra in d['nome'].split()
        ])

        endereco_completo = f"{d['endereco']} {d.get('numero', '')} {d.get('complemento', '')}".strip()

        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO clientes (
                    tipo, nome, documento, celular, contato, cep, endereco, numero, complemento,
                    bairro, email, observacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    tipo,
                    nome,
                    doc,
                    d['celular'],
                    d.get('contato', ''),
                    d['cep'],
                    d['endereco'],
                    d.get('numero', ''),
                    d.get('complemento', ''),
                    d['bairro'],
                    d['email'].lower(),
                    d['observacao']
                ))

            # salvar csv
            csv_path = "clientes.csv"
            file_existe = os.path.exists(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_existe:
                    writer.writerow([
                        "Name", "Notes", "Tipo", "Celular", "CEP",
                        "Endereço", "Bairro", "Email", "Contato", "Observação"
                    ])
                writer.writerow([
                    nome,
                    f"CPF: {doc}" if tipo == 'pf' else f"CNPJ: {doc}",
                    "Pessoa Física" if tipo == 'pf' else "Pessoa Jurídica",
                    d['celular'],
                    d['cep'],
                    endereco_completo,
                    d['bairro'],
                    d['email'].lower(),
                    d.get('contato', ''),
                    d['observacao']
                ])
            return "<h3>Chamado enviado com sucesso! ✅</h3><a href='/cliente'>Voltar</a>"
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {e}")
            return "Erro interno ao cadastrar cliente", 500

    return render_template('cliente.html')

@app.route('/exportar_clientes')
def exportar_clientes():
    caminho = 'clientes.csv'
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    return "Arquivo clientes.csv não encontrado", 404

@app.route('/')
def index():
    return redirect('/cliente')

if __name__ == '__main__':
    app.run(debug=True)
