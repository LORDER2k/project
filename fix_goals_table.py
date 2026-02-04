#!/usr/bin/env python3
"""
Script para criar a tabela goals faltante
"""
import sqlite3
import os

def create_goals_table():
    print("🔧 Corrigindo erro: Criando tabela 'goals'...")
    
    # Verificar se o diretório existe
    if not os.path.exists('database'):
        os.makedirs('database')
        print("✅ Diretório 'database' criado")
    
    # Conectar ao banco
    conn = sqlite3.connect('database/contasmart.db')
    cursor = conn.cursor()
    
    # Verificar se a tabela já existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goals'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ Tabela 'goals' já existe")
    else:
        print("📝 Criando tabela 'goals'...")
        
        # Criar tabela goals
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
        
        print("✅ Tabela 'goals' criada com sucesso!")
        
        # Verificar outras tabelas importantes
        tables_to_check = ['users', 'categories', 'transactions']
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"⚠️  Tabela '{table}' não existe!")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Banco de dados corrigido!")
    print("🚀 Execute: python app.py")
    print("🌐 Acesse: http://localhost:5000")

if __name__ == "__main__":
    create_goals_table()