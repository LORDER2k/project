#!/usr/bin/env python3
"""
Script para resetar completamente o banco de dados
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Remover banco existente
if os.path.exists('database/contasmart.db'):
    os.remove('database/contasmart.db')
    print("🗑️  Banco de dados antigo removido")

# Criar diretório se não existir
if not os.path.exists('database'):
    os.makedirs('database')

# Conectar e criar banco
conn = sqlite3.connect('database/contasmart.db')
cursor = conn.cursor()

# Criar tabelas
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        avatar TEXT DEFAULT 'default.png',
        theme TEXT DEFAULT 'light',
        currency TEXT DEFAULT 'BRL',
        language TEXT DEFAULT 'pt_BR',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
        color TEXT DEFAULT '#3498db',
        icon TEXT DEFAULT 'fas fa-tag',
        parent_id INTEGER DEFAULT NULL,
        budget_limit DECIMAL(10, 2) DEFAULT 0,
        is_default BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (parent_id) REFERENCES categories(id)
    )
''')

cursor.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('income', 'expense', 'transfer', 'investment')) NOT NULL,
        category_id INTEGER,
        amount DECIMAL(10, 2) NOT NULL,
        tax_amount DECIMAL(10, 2) DEFAULT 0,
        net_amount DECIMAL(10, 2) DEFAULT 0,
        description TEXT,
        transaction_date DATE NOT NULL,
        due_date DATE,
        payment_method TEXT,
        is_recurring BOOLEAN DEFAULT 0,
        recurring_frequency TEXT,
        is_paid BOOLEAN DEFAULT 1,
        tags TEXT,
        attachment TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
''')

# Criar usuário admin com senha correta
hashed_password = generate_password_hash('admin2026')
cursor.execute(
    'INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
    ('admin', 'admin@contasmart.com', hashed_password, 'Administrador')
)

print("✅ Usuário admin criado com sucesso!")
print("👤 Username: admin")
print("🔑 Password: admin2026")
print("📧 Email: admin@contasmart.com")

# Criar categorias padrão
default_categories = [
    # Receitas
    ('Salário', 'income', '#2ecc71', 'fas fa-money-check-alt'),
    ('Freelance', 'income', '#27ae60', 'fas fa-laptop-code'),
    ('Investimentos', 'income', '#16a085', 'fas fa-chart-line'),
    ('Aluguel', 'income', '#1abc9c', 'fas fa-home'),
    ('Outros', 'income', '#3498db', 'fas fa-plus-circle'),
    # Despesas
    ('Alimentação', 'expense', '#e74c3c', 'fas fa-utensils'),
    ('Transporte', 'expense', '#e67e22', 'fas fa-car'),
    ('Moradia', 'expense', '#d35400', 'fas fa-house-user'),
    ('Educação', 'expense', '#9b59b6', 'fas fa-graduation-cap'),
    ('Saúde', 'expense', '#e84393', 'fas fa-heartbeat'),
    ('Lazer', 'expense', '#00cec9', 'fas fa-gamepad'),
    ('Compras', 'expense', '#6c5ce7', 'fas fa-shopping-bag'),
    ('Serviços', 'expense', '#fd79a8', 'fas fa-concierge-bell'),
    ('Impostos', 'expense', '#34495e', 'fas fa-file-invoice-dollar'),
    ('Outros', 'expense', '#636e72', 'fas fa-ellipsis-h'),
]

for cat in default_categories:
    cursor.execute(
        'INSERT INTO categories (name, type, color, icon, is_default) VALUES (?, ?, ?, ?, 1)',
        cat
    )

conn.commit()
conn.close()

print("✅ Banco de dados resetado com sucesso!")
print("📁 Arquivo: database/contasmart.db")
print("\n🚀 Execute: python app.py")
print("🌐 Acesse: http://localhost:5000")