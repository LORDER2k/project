#!/usr/bin/env python3
"""
Script para resetar completamente o banco de dados
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

def reset_database():
    print("🔄 Resetando banco de dados completo...")
    
    # Remover banco existente
    if os.path.exists('database/contasmart.db'):
        os.remove('database/contasmart.db')
        print("🗑️  Banco antigo removido")
    
    # Criar diretório se não existir
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Conectar e criar banco
    conn = sqlite3.connect('database/contasmart.db')
    cursor = conn.cursor()
    
    print("📋 Criando tabelas...")
    
    # 1. Tabela users
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
    print("✅ Tabela 'users' criada")
    
    # 2. Tabela categories
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
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ Tabela 'categories' criada")
    
    # 3. Tabela transactions
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            category_id INTEGER,
            amount DECIMAL(10, 2) NOT NULL,
            description TEXT,
            transaction_date DATE NOT NULL,
            due_date DATE,
            is_paid BOOLEAN DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    print("✅ Tabela 'transactions' criada")
    
    # 4. Tabela goals (A TABELA FALTANTE!)
    cursor.execute('''
        CREATE TABLE goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target_amount DECIMAL(10, 2) NOT NULL,
            current_amount DECIMAL(10, 2) DEFAULT 0,
            deadline DATE,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
            is_completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ Tabela 'goals' criada")
    
    # Criar usuário admin
    hashed_password = generate_password_hash('admin2026')
    cursor.execute(
        'INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
        ('admin', 'admin@contasmart.com', hashed_password, 'Administrador')
    )
    print("✅ Usuário 'admin' criado")
    
    # Obter ID do admin
    admin_id = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()[0]
    
    # Criar categorias padrão para o admin
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
            'INSERT INTO categories (user_id, name, type, color, icon) VALUES (?, ?, ?, ?, ?)',
            (admin_id, cat[0], cat[1], cat[2], cat[3])
        )
    
    print("✅ Categorias padrão criadas")
    
    # Adicionar algumas transações de exemplo
    import random
    from datetime import datetime, timedelta
    
    for i in range(15):
        category_type = 'income' if i % 3 == 0 else 'expense'
        amount = random.uniform(50, 2000) if category_type == 'income' else random.uniform(10, 500)
        date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Obter uma categoria do tipo correto
        cat = cursor.execute(
            'SELECT id FROM categories WHERE user_id = ? AND type = ? ORDER BY RANDOM() LIMIT 1',
            (admin_id, category_type)
        ).fetchone()
        
        if cat:
            cursor.execute('''
                INSERT INTO transactions (user_id, type, category_id, amount, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, category_type, cat[0], amount, f'Transação exemplo {i+1}', date.strftime('%Y-%m-%d')))
    
    print("✅ Transações de exemplo criadas")
    
    # Adicionar metas de exemplo
    metas_exemplo = [
        ('Viagem às Maldivas', 'Economizar para viagem dos sonhos', 15000, 3000, '2024-12-31', 'high'),
        ('Notebook novo', 'Comprar notebook para trabalho', 5000, 1200, '2024-06-30', 'medium'),
        ('Reserva de emergência', 'Criar reserva para 6 meses', 18000, 5000, '2024-12-31', 'high'),
        ('Curso de inglês', 'Investir em educação', 2000, 800, '2024-04-30', 'low'),
    ]
    
    for meta in metas_exemplo:
        cursor.execute('''
            INSERT INTO goals (user_id, title, description, target_amount, current_amount, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, meta[0], meta[1], meta[2], meta[3], meta[4], meta[5]))
    
    print("✅ Metas de exemplo criadas")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 BANCO DE DADOS RESETADO COM SUCESSO!")
    print("="*60)
    print("📊 Todas as tabelas foram criadas:")
    print("   👤 users        📂 categories")
    print("   💰 transactions 🎯 goals")
    print("\n👤 Usuário: admin")
    print("🔑 Senha: admin2026")
    print("\n🚀 Execute: python app.py")
    print("🌐 Acesse: http://localhost:5000")
    print("="*60)

if __name__ == "__main__":
    reset_database()