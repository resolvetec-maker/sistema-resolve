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
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            nome TEXT,
            documento TEXT,
            celular TEXT,
            contato TEXT,
            cep TEXT,
            endereco TEXT,
            bairro TEXT,
            email TEXT,
            observacao TEXT,
            numero TEXT,
            complemento TEXT
        )''')
init_db()

# As demais rotas seguem abaixo...
