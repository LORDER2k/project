#!/usr/bin/env python3
"""
Script para corrigir problemas no banco de dados
"""
import sqlite3
import os

def fix_database():
    print("🔧 Corrigindo banco de dados...")
    
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = sqlite3.connect('database/contasmart.db')
    cursor = conn.cursor()
    
    # Verificar tabelas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    print(f"📋 Tabelas encontradas: {tables}")
    
    # Criar tabelas faltantes
    tables_to_create = {
        'users': '''
            CREATE TABLE IF NOT EXISTS users (
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
        ''',
        'categories': '''
            CREATE TABLE IF NOT EXISTS categories (
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
        ''',
        'transactions': '''
            CREATE TABLE IF NOT EXISTS transactions (
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
        ''',
        'goals': '''
            CREATE TABLE IF NOT EXISTS goals (
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
        '''
    }
    
    for table_name, create_sql in tables_to_create.items():
        if table_name not in tables:
            print(f"📝 Criando tabela: {table_name}")
            cursor.execute(create_sql)
    
    # Verificar usuário admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        print("👤 Criando usuário admin...")
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash('admin2026')
        cursor.execute(
            "INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@contasmart.com', hashed_password, 'Administrador')
        )
    
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados corrigido com sucesso!")
    print("🚀 Execute: python app.py")
    print("🌐 Acesse: http://localhost:5000")
    print("👤 Usuário: admin")
    print("🔑 Senha: admin2026")

if __name__ == "__main__":
    fix_database()