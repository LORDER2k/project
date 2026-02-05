"""
CONTASMART PRO EXECUTIVO - Sistema Financeiro
Configurado para deploy no Render.com
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from datetime import datetime, timedelta
from functools import wraps
import math
import traceback

# ===== CONFIGURAÇÃO PARA RENDER =====
app = Flask(__name__)

# Configuração da secret key (Render injetará via variável de ambiente)
app.secret_key = os.environ.get('SECRET_KEY', 'contasmart-executivo-2026-secret-dev')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuração de banco para Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    DATABASE = DATABASE_URL
    print(f"🔗 Usando PostgreSQL: {DATABASE[:50]}...")
else:
    DATABASE = 'database/contasmart.db'
    print("📁 Usando SQLite local")

# ===== FUNÇÕES AUXILIARES =====

def get_db_connection():
    """Conectar ao banco de dados"""
    if DATABASE.startswith('postgresql://'):
        # PostgreSQL no Render
        import psycopg2
        from psycopg2.extras import DictCursor
        
        conn = psycopg2.connect(DATABASE, sslmode='require')
        conn.cursor_factory = DictCursor
        return conn
    else:
        # SQLite local
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Inicializar banco de dados"""
    print("🔄 Inicializando banco de dados executivo...")
    
    # Criar diretório database se for SQLite
    if DATABASE == 'database/contasmart.db':
        os.makedirs('database', exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabela de usuários
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name VARCHAR(255),
                    avatar VARCHAR(255) DEFAULT 'default.png',
                    theme VARCHAR(50) DEFAULT 'executive',
                    currency VARCHAR(10) DEFAULT 'BRL',
                    language VARCHAR(10) DEFAULT 'pt_BR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT,
                    avatar TEXT DEFAULT 'default.png',
                    theme TEXT DEFAULT 'executive',
                    currency TEXT DEFAULT 'BRL',
                    language TEXT DEFAULT 'pt_BR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Tabela de categorias
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    type VARCHAR(10) CHECK(type IN ('income', 'expense')) NOT NULL,
                    color VARCHAR(20) DEFAULT '#0066ff',
                    icon VARCHAR(50) DEFAULT 'fas fa-tag',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                    color TEXT DEFAULT '#0066ff',
                    icon TEXT DEFAULT 'fas fa-tag',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Tabela de transações
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    type VARCHAR(10) CHECK(type IN ('income', 'expense')) NOT NULL,
                    category_id INTEGER,
                    amount DECIMAL(10, 2) NOT NULL,
                    description TEXT,
                    transaction_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                    category_id INTEGER,
                    amount DECIMAL(10, 2) NOT NULL,
                    description TEXT,
                    transaction_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
        
        # Tabela de metas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    target_amount DECIMAL(10, 2) NOT NULL,
                    current_amount DECIMAL(10, 2) DEFAULT 0,
                    deadline DATE,
                    priority VARCHAR(10) CHECK(priority IN ('low', 'medium', 'high')),
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    target_amount DECIMAL(10, 2) NOT NULL,
                    current_amount DECIMAL(10, 2) DEFAULT 0,
                    deadline DATE,
                    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
                    is_completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Tabela de alertas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    icon VARCHAR(50) DEFAULT 'fas fa-bell',
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    icon TEXT DEFAULT 'fas fa-bell',
                    is_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        conn.commit()
        
        # Verificar usuário admin
        cursor.execute('SELECT * FROM users WHERE username = %s', ('admin',))
        admin = cursor.fetchone()
        
        if not admin:
            hashed_password = generate_password_hash('admin2026')
            
            if DATABASE.startswith('postgresql://'):
                cursor.execute('''
                    INSERT INTO users (username, email, password, full_name, theme)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', ('admin', 'admin@contasmart.com', hashed_password, 'Administrador', 'executive'))
                user_id = cursor.fetchone()['id']
            else:
                cursor.execute('''
                    INSERT INTO users (username, email, password, full_name, theme)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('admin', 'admin@contasmart.com', hashed_password, 'Administrador', 'executive'))
                user_id = cursor.lastrowid
            
            # Categorias padrão
            default_categories = [
                ('Salário', 'income', '#00ff88', 'fas fa-money-check-alt'),
                ('Freelance', 'income', '#00ffff', 'fas fa-laptop-code'),
                ('Investimentos', 'income', '#9d00ff', 'fas fa-chart-line'),
                ('Dividendos', 'income', '#0066ff', 'fas fa-coins'),
                ('Alimentação', 'expense', '#ff3366', 'fas fa-utensils'),
                ('Transporte', 'expense', '#ff9900', 'fas fa-car'),
                ('Moradia', 'expense', '#ff0066', 'fas fa-home'),
                ('Lazer', 'expense', '#00ccff', 'fas fa-gamepad'),
                ('Educação', 'expense', '#9966ff', 'fas fa-graduation-cap'),
                ('Saúde', 'expense', '#ff66cc', 'fas fa-heartbeat'),
                ('Compras', 'expense', '#ffcc00', 'fas fa-shopping-bag'),
                ('Serviços', 'expense', '#33ccff', 'fas fa-tools')
            ]
            
            for name, type, color, icon in default_categories:
                cursor.execute('''
                    INSERT INTO categories (user_id, name, type, color, icon)
                    VALUES (%s, %s, %s, %s, %s)
                ''' if DATABASE.startswith('postgresql://') else '''
                    INSERT INTO categories (user_id, name, type, color, icon)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, name, type, color, icon))
            
            # Transações de exemplo
            import random
            cursor.execute('SELECT id, type FROM categories WHERE user_id = %s', (user_id,))
            categories = cursor.fetchall()
            income_cats = [cat['id'] for cat in categories if cat['type'] == 'income']
            expense_cats = [cat['id'] for cat in categories if cat['type'] == 'expense']
            
            for i in range(20):
                if i < 8:  # 8 receitas
                    trans_type = 'income'
                    category_id = random.choice(income_cats) if income_cats else None
                    amount = round(random.uniform(100, 5000), 2)
                    description = f'Receita {i+1}'
                else:  # 12 despesas
                    trans_type = 'expense'
                    category_id = random.choice(expense_cats) if expense_cats else None
                    amount = round(random.uniform(50, 2000), 2)
                    description = f'Despesa {i-7}'
                
                days_ago = random.randint(0, 90)
                date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                cursor.execute('''
                    INSERT INTO transactions (user_id, type, category_id, amount, description, transaction_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''' if DATABASE.startswith('postgresql://') else '''
                    INSERT INTO transactions (user_id, type, category_id, amount, description, transaction_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, trans_type, category_id, amount, description, date))
            
            # Metas de exemplo
            example_goals = [
                ('Reserva de Emergência', 'Economizar para imprevistos', 10000, 4500, '2024-12-31', 'high'),
                ('Viagem Internacional', 'Conhecer a Europa', 20000, 8000, '2024-10-15', 'medium'),
                ('Novo Notebook', 'Para trabalho e estudos', 6000, 3200, '2024-08-30', 'medium'),
                ('Investimentos', 'Aumentar patrimônio', 50000, 18500, '2025-12-31', 'high'),
                ('Curso Especialização', 'Pós-graduação em finanças', 12000, 6000, '2024-11-20', 'low')
            ]
            
            for title, desc, target, current, deadline, priority in example_goals:
                cursor.execute('''
                    INSERT INTO goals (user_id, title, description, target_amount, current_amount, deadline, priority)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''' if DATABASE.startswith('postgresql://') else '''
                    INSERT INTO goals (user_id, title, description, target_amount, current_amount, deadline, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, title, desc, target, current, deadline, priority))
            
            conn.commit()
        
        print("✅ Banco de dados executivo inicializado!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def login_required(f):
    """Decorator para exigir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acesso restrito. Faça login para continuar.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(value):
    """Formatar valor como moeda"""
    if value is None:
        value = 0
    try:
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return f"R$ {float(value or 0):.2f}"

def calculate_percentage(part, total):
    """Calcular porcentagem"""
    try:
        return (part / total * 100) if total > 0 else 0
    except:
        return 0

# ===== ROTAS ESTÁTICAS =====

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
def index():
    """Página inicial"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index_executivo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Preencha todos os campos.', 'danger')
            return render_template('login_executivo.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', 
                          (username, username))
        else:
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                          (username, username))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name'] or user['username']
            session['theme'] = user['theme']
            session.permanent = True
            
            flash(f'Bem-vindo ao sistema executivo, {session["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    
    return render_template('login_executivo.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip() or username
        
        if not username or not email or not password:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('register_executivo.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register_executivo.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register_executivo.html')
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if DATABASE.startswith('postgresql://'):
                cursor.execute('''
                    INSERT INTO users (username, email, password, full_name, theme)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (username, email, hashed_password, full_name, 'executive'))
                new_user_id = cursor.fetchone()['id']
            else:
                cursor.execute('''
                    INSERT INTO users (username, email, password, full_name, theme)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, hashed_password, full_name, 'executive'))
                new_user_id = cursor.lastrowid
            
            conn.commit()
            
            # Copiar categorias padrão do admin (ID 1)
            cursor.execute('SELECT * FROM categories WHERE user_id = 1')
            default_categories = cursor.fetchall()
            
            for cat in default_categories:
                cursor.execute('''
                    INSERT INTO categories (user_id, name, type, color, icon)
                    VALUES (%s, %s, %s, %s, %s)
                ''' if DATABASE.startswith('postgresql://') else '''
                    INSERT INTO categories (user_id, name, type, color, icon)
                    VALUES (?, ?, ?, ?, ?)
                ''', (new_user_id, cat['name'], cat['type'], cat['color'], cat['icon']))
            
            conn.commit()
            
            flash('Conta criada com sucesso! Faça login para acessar o sistema.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            if 'unique' in str(e).lower():
                flash('Usuário ou email já cadastrados.', 'danger')
            else:
                flash(f'Erro ao criar conta: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('register_executivo.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Estatísticas principais
        stats = get_dashboard_stats(user_id, conn)
        
        # Transações recentes
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT t.*, c.name as category_name, c.color as category_color, c.icon as category_icon
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s
                ORDER BY t.transaction_date DESC, t.created_at DESC
                LIMIT 10
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT t.*, c.name as category_name, c.color as category_color, c.icon as category_icon
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                ORDER BY t.transaction_date DESC, t.created_at DESC
                LIMIT 10
            ''', (user_id,))
        
        recent_transactions = cursor.fetchall()
        
        # Converter para dicionário para serialização
        recent_transactions_list = []
        for trans in recent_transactions:
            recent_transactions_list.append(dict(trans))
        
        # Metas em destaque
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT * FROM goals 
                WHERE user_id = %s AND is_completed = FALSE
                ORDER BY 
                    CASE priority 
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END,
                    deadline ASC
                LIMIT 5
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM goals 
                WHERE user_id = ? AND is_completed = 0
                ORDER BY 
                    CASE priority 
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END,
                    deadline ASC
                LIMIT 5
            ''', (user_id,))
        
        featured_goals = cursor.fetchall()
        goals_list = [dict(goal) for goal in featured_goals]
        
        # Gráfico de tendências (últimos 6 meses)
        trend_data = get_trend_data(user_id, conn)
        
        # Alertas do sistema
        alerts = get_system_alerts(user_id, conn)
        
        conn.close()
        
        return render_template('dashboard_executivo.html',
                             stats=stats,
                             recent_transactions=recent_transactions_list,
                             goals=goals_list,
                             trend_data=trend_data,
                             alerts=alerts,
                             now=datetime.now())
    except Exception as e:
        print(f"ERROR in dashboard: {str(e)}")
        print(traceback.format_exc())
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return render_template('dashboard_executivo.html',
                             stats={},
                             recent_transactions=[],
                             goals=[],
                             trend_data=[],
                             alerts=[],
                             now=datetime.now())

def get_dashboard_stats(user_id, conn):
    """Obter estatísticas do dashboard"""
    try:
        cursor = conn.cursor()
        
        # Totais gerais
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'income'
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'income'
            ''', (user_id,))
        
        total_income_result = cursor.fetchone()
        total_income = float(total_income_result['total']) if total_income_result else 0
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'expense'
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'expense'
            ''', (user_id,))
        
        total_expense_result = cursor.fetchone()
        total_expense = float(total_expense_result['total']) if total_expense_result else 0
        
        balance = total_income - total_expense
        
        # Este mês
        current_month = datetime.now().strftime('%Y-%m')
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'income' 
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'income' 
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, current_month))
        
        month_income_result = cursor.fetchone()
        month_income = float(month_income_result['total']) if month_income_result else 0
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'expense'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'expense'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, current_month))
        
        month_expense_result = cursor.fetchone()
        month_expense = float(month_expense_result['total']) if month_expense_result else 0
        
        month_balance = month_income - month_expense
        
        # Progresso de metas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN current_amount >= target_amount THEN 1 ELSE 0 END) as completed,
                    AVG(CASE 
                        WHEN target_amount > 0 THEN (current_amount * 100.0) / target_amount 
                        ELSE 0 
                    END) as avg_progress
                FROM goals 
                WHERE user_id = %s AND is_completed = FALSE
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN current_amount >= target_amount THEN 1 ELSE 0 END) as completed,
                    AVG(CASE 
                        WHEN target_amount > 0 THEN (current_amount * 100.0) / target_amount 
                        ELSE 0 
                    END) as avg_progress
                FROM goals 
                WHERE user_id = ? AND is_completed = 0
            ''', (user_id,))
        
        goals_progress = cursor.fetchone()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'month_income': month_income,
            'month_expense': month_expense,
            'month_balance': month_balance,
            'total_goals': goals_progress['total'] or 0 if goals_progress else 0,
            'completed_goals': goals_progress['completed'] or 0 if goals_progress else 0,
            'avg_progress': float(goals_progress['avg_progress'] or 0) if goals_progress else 0
        }
    except Exception as e:
        print(f"ERROR in get_dashboard_stats: {str(e)}")
        return {
            'total_income': 0,
            'total_expense': 0,
            'balance': 0,
            'month_income': 0,
            'month_expense': 0,
            'month_balance': 0,
            'total_goals': 0,
            'completed_goals': 0,
            'avg_progress': 0
        }

def get_trend_data(user_id, conn):
    """Obter dados para gráfico de tendências"""
    trend_data = []
    
    try:
        cursor = conn.cursor()
        
        for i in range(5, -1, -1):  # Últimos 6 meses
            date = datetime.now() - timedelta(days=30*i)
            month_year = date.strftime('%Y-%m')
            month_name = date.strftime('%b')
            
            if DATABASE.startswith('postgresql://'):
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = %s AND type = 'income'
                    AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                ''', (user_id, month_year))
            else:
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = ? AND type = 'income'
                    AND strftime('%Y-%m', transaction_date) = ?
                ''', (user_id, month_year))
            
            income_result = cursor.fetchone()
            income = float(income_result['total']) if income_result else 0
            
            if DATABASE.startswith('postgresql://'):
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = %s AND type = 'expense'
                    AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                ''', (user_id, month_year))
            else:
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = ? AND type = 'expense'
                    AND strftime('%Y-%m', transaction_date) = ?
                ''', (user_id, month_year))
            
            expense_result = cursor.fetchone()
            expense = float(expense_result['total']) if expense_result else 0
            
            trend_data.append({
                'month': month_name,
                'income': income,
                'expense': expense,
                'balance': income - expense
            })
    except Exception as e:
        print(f"ERROR in get_trend_data: {str(e)}")
        # Dados de exemplo em caso de erro
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
        for month in months:
            trend_data.append({
                'month': month,
                'income': 0,
                'expense': 0,
                'balance': 0
            })
    
    return trend_data

def get_system_alerts(user_id, conn):
    """Obter alertas do sistema"""
    alerts = []
    
    try:
        cursor = conn.cursor()
        
        # Verificar saldo negativo
        stats = get_dashboard_stats(user_id, conn)
        if stats['balance'] < 0:
            alerts.append({
                'type': 'danger',
                'icon': 'exclamation-triangle',
                'title': 'Saldo Negativo',
                'message': f'Seu saldo atual é {format_currency(stats["balance"])}',
                'action': 'Recomendamos revisar suas despesas'
            })
        
        # Verificar metas próximas do prazo
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COUNT(*) as count FROM goals 
                WHERE user_id = %s AND is_completed = FALSE 
                AND deadline <= CURRENT_DATE + INTERVAL '7 days'
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT COUNT(*) as count FROM goals 
                WHERE user_id = ? AND is_completed = 0 
                AND deadline <= date("now", "+7 days")
            ''', (user_id,))
        
        due_goals = cursor.fetchone()
        
        if due_goals and due_goals['count'] > 0:
            alerts.append({
                'type': 'warning',
                'icon': 'calendar-exclamation',
                'title': 'Metas Próximas',
                'message': f'{due_goals["count"]} meta(s) próximo(s) do prazo',
                'action': 'Verifique o progresso'
            })
        
        # Verificar despesas altas este mês
        if stats['month_income'] > 0:
            expense_ratio = (stats['month_expense'] / stats['month_income']) * 100
            if expense_ratio > 80:  # >80% da receita
                alerts.append({
                    'type': 'info',
                    'icon': 'chart-line',
                    'title': 'Despesas Elevadas',
                    'message': f'Despesas consomem {expense_ratio:.1f}% da receita',
                    'action': 'Considere revisar orçamento'
                })
        
        # Se não houver alertas, mostrar mensagem positiva
        if not alerts:
            alerts.append({
                'type': 'success',
                'icon': 'check-circle',
                'title': 'Tudo em Ordem',
                'message': 'Suas finanças estão sob controle',
                'action': 'Continue monitorando'
            })
    except Exception as e:
        print(f"ERROR in get_system_alerts: {str(e)}")
        alerts.append({
            'type': 'info',
            'icon': 'info-circle',
            'title': 'Sistema Online',
            'message': 'Dashboard carregado com sucesso',
            'action': 'Bem-vindo ao sistema'
        })
    
    return alerts

@app.route('/transactions')
@login_required
def transactions():
    """Página de transações"""
    try:
        user_id = session['user_id']
        
        # Parâmetros de filtro com valores padrão seguros
        filter_type = request.args.get('type', 'all')
        filter_category = request.args.get('category', 'all')
        filter_date = request.args.get('date', 'all')
        filter_search = request.args.get('search', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query base
        if DATABASE.startswith('postgresql://'):
            query = '''
                SELECT 
                    t.id, t.user_id, t.type, t.category_id, 
                    t.amount, t.description, t.transaction_date, t.created_at,
                    c.name as category_name, 
                    c.color as category_color, 
                    c.icon as category_icon
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s
            '''
        else:
            query = '''
                SELECT 
                    t.id, t.user_id, t.type, t.category_id, 
                    t.amount, t.description, t.transaction_date, t.created_at,
                    c.name as category_name, 
                    c.color as category_color, 
                    c.icon as category_icon
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
            '''
        
        params = [user_id]
        
        # Aplicar filtros
        if filter_type != 'all':
            query += ' AND t.type = '
            query += '%s' if DATABASE.startswith('postgresql://') else '?'
            params.append(filter_type)
        
        if filter_category != 'all' and filter_category.isdigit():
            query += ' AND t.category_id = '
            query += '%s' if DATABASE.startswith('postgresql://') else '?'
            params.append(int(filter_category))
        
        if filter_date != 'all':
            if filter_date == 'today':
                if DATABASE.startswith('postgresql://'):
                    query += " AND t.transaction_date = CURRENT_DATE"
                else:
                    query += ' AND date(t.transaction_date) = date("now")'
            elif filter_date == 'week':
                if DATABASE.startswith('postgresql://'):
                    query += " AND t.transaction_date >= CURRENT_DATE - INTERVAL '7 days'"
                else:
                    query += ' AND t.transaction_date >= date("now", "-7 days")'
            elif filter_date == 'month':
                if DATABASE.startswith('postgresql://'):
                    query += " AND TO_CHAR(t.transaction_date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')"
                else:
                    query += ' AND strftime("%Y-%m", t.transaction_date) = strftime("%Y-%m", "now")'
        
        if filter_search and filter_search.strip():
            query += ' AND (t.description LIKE '
            query += '%s' if DATABASE.startswith('postgresql://') else '?'
            query += ' OR c.name LIKE '
            query += '%s' if DATABASE.startswith('postgresql://') else '?'
            query += ')'
            search_term = f'%{filter_search.strip()}%'
            params.extend([search_term, search_term])
        
        query += ' ORDER BY t.transaction_date DESC, t.created_at DESC'
        
        print(f"DEBUG: Query: {query}")
        print(f"DEBUG: Params: {params}")
        
        # Executar query
        cursor.execute(query, params)
        transactions_list = cursor.fetchall()
        
        # Converter para lista de dicionários
        transactions_dict = []
        for trans in transactions_list:
            trans_dict = dict(trans)
            # Garantir que valores numéricos sejam float
            trans_dict['amount'] = float(trans_dict['amount']) if trans_dict['amount'] else 0.0
            transactions_dict.append(trans_dict)
        
        # Totais filtrados
        if DATABASE.startswith('postgresql://'):
            income_query = "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = %s AND type = 'income'"
            expense_query = "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = %s AND type = 'expense'"
        else:
            income_query = 'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "income"'
            expense_query = 'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense"'
        
        cursor.execute(income_query, (user_id,))
        income_total_result = cursor.fetchone()
        cursor.execute(expense_query, (user_id,))
        expense_total_result = cursor.fetchone()
        
        income_total = float(income_total_result['total']) if income_total_result and income_total_result['total'] else 0.0
        expense_total = float(expense_total_result['total']) if expense_total_result and expense_total_result['total'] else 0.0
        
        # Categorias para filtro
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT * FROM categories 
                WHERE user_id = %s 
                ORDER BY 
                    CASE type 
                        WHEN 'income' THEN 1 
                        WHEN 'expense' THEN 2 
                        ELSE 3 
                    END, 
                    name
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM categories 
                WHERE user_id = ? 
                ORDER BY 
                    CASE type 
                        WHEN 'income' THEN 1 
                        WHEN 'expense' THEN 2 
                        ELSE 3 
                    END, 
                    name
            ''', (user_id,))
        
        categories = cursor.fetchall()
        categories_dict = [dict(cat) for cat in categories]
        
        conn.close()
        
        print(f"DEBUG: Found {len(transactions_dict)} transactions")
        print(f"DEBUG: Found {len(categories_dict)} categories")
        print(f"DEBUG: Income total: {income_total}, Expense total: {expense_total}")
        
        return render_template('transacoes_executivo.html',
                             transactions=transactions_dict,
                             categories=categories_dict,
                             income_total=income_total,
                             expense_total=expense_total,
                             filter_type=filter_type,
                             filter_category=filter_category,
                             filter_date=filter_date,
                             filter_search=filter_search,
                             now=datetime.now())
        
    except Exception as e:
        print(f"ERROR in transactions: {str(e)}")
        print(traceback.format_exc())
        flash(f'Erro ao carregar transações: {str(e)}', 'danger')
        return render_template('transacoes_executivo.html',
                             transactions=[],
                             categories=[],
                             income_total=0.0,
                             expense_total=0.0,
                             filter_type='all',
                             filter_category='all',
                             filter_date='all',
                             filter_search='',
                             now=datetime.now())

@app.route('/api/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    """API para adicionar transação"""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        
        trans_type = data.get('type')
        amount = float(data.get('amount', 0))
        description = data.get('description', '').strip()
        category_id = data.get('category_id')
        transaction_date = data.get('transaction_date', datetime.now().strftime('%Y-%m-%d'))
        
        if not trans_type or amount <= 0:
            return jsonify({'success': False, 'error': 'Dados inválidos'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                INSERT INTO transactions (user_id, type, category_id, amount, description, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, trans_type, category_id, amount, description, transaction_date))
        else:
            cursor.execute('''
                INSERT INTO transactions (user_id, type, category_id, amount, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, trans_type, category_id, amount, description, transaction_date))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Transação adicionada!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_transaction/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """API para excluir transação"""
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('DELETE FROM transactions WHERE id = %s AND user_id = %s', 
                          (transaction_id, user_id))
        else:
            cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', 
                          (transaction_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Transação excluída!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analytics')
@login_required
def analytics():
    """Página de análises"""
    try:
        user_id = session['user_id']
        
        # Parâmetros
        period = request.args.get('period', 'month')
        year = request.args.get('year', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Análise por categoria
        category_analysis = get_category_analysis(user_id, period, conn)
        
        # Tendências
        trends = get_financial_trends(user_id, period, conn)
        
        # Comparativos
        comparisons = get_comparative_analysis(user_id, period, conn)
        
        # Insights
        insights = generate_financial_insights(user_id, conn)
        
        conn.close()
        
        return render_template('analytics_executivo.html',
                             category_analysis=category_analysis,
                             trends=trends,
                             comparisons=comparisons,
                             insights=insights,
                             period=period,
                             year=year,
                             month=month)
    except Exception as e:
        print(f"ERROR in analytics: {str(e)}")
        flash(f'Erro ao carregar análises: {str(e)}', 'danger')
        return render_template('analytics_executivo.html',
                             category_analysis={'expenses': [], 'incomes': []},
                             trends=[],
                             comparisons=[],
                             insights=[],
                             period='month',
                             year=datetime.now().year,
                             month=datetime.now().month)

def get_category_analysis(user_id, period, conn):
    """Análise por categoria"""
    try:
        cursor = conn.cursor()
        
        # Despesas por categoria
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT c.name, c.color, c.icon, SUM(t.amount) as total,
                       COUNT(t.id) as count, AVG(t.amount) as average
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = 'expense'
                GROUP BY c.id, c.name, c.color, c.icon
                ORDER BY total DESC
                LIMIT 8
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT c.name, c.color, c.icon, SUM(t.amount) as total,
                       COUNT(t.id) as count, AVG(t.amount) as average
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                GROUP BY c.id
                ORDER BY total DESC
                LIMIT 8
            ''', (user_id,))
        
        expense_categories = cursor.fetchall()
        
        # Receitas por categoria
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT c.name, c.color, c.icon, SUM(t.amount) as total,
                       COUNT(t.id) as count
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = 'income'
                GROUP BY c.id, c.name, c.color, c.icon
                ORDER BY total DESC
                LIMIT 8
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT c.name, c.color, c.icon, SUM(t.amount) as total,
                       COUNT(t.id) as count
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'income'
                GROUP BY c.id
                ORDER BY total DESC
                LIMIT 8
            ''', (user_id,))
        
        income_categories = cursor.fetchall()
        
        return {
            'expenses': [dict(cat) for cat in expense_categories],
            'incomes': [dict(cat) for cat in income_categories]
        }
    except Exception as e:
        print(f"ERROR in get_category_analysis: {str(e)}")
        return {
            'expenses': [],
            'incomes': []
        }

def get_financial_trends(user_id, period, conn):
    """Obter tendências financeiras"""
    trends = []
    
    try:
        cursor = conn.cursor()
        
        if period == 'year':
            # Últimos 12 meses
            for i in range(11, -1, -1):
                date = datetime.now() - timedelta(days=30*i)
                month_year = date.strftime('%Y-%m')
                month_name = date.strftime('%b/%y')
                
                if DATABASE.startswith('postgresql://'):
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = %s AND type = 'income'
                        AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                    ''', (user_id, month_year))
                else:
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = ? AND type = 'income'
                        AND strftime('%Y-%m', transaction_date) = ?
                    ''', (user_id, month_year))
                
                income_result = cursor.fetchone()
                income = float(income_result['total']) if income_result else 0
                
                if DATABASE.startswith('postgresql://'):
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = %s AND type = 'expense'
                        AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                    ''', (user_id, month_year))
                else:
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = ? AND type = 'expense'
                        AND strftime('%Y-%m', transaction_date) = ?
                    ''', (user_id, month_year))
                
                expense_result = cursor.fetchone()
                expense = float(expense_result['total']) if expense_result else 0
                
                trends.append({
                    'period': month_name,
                    'income': income,
                    'expense': expense,
                    'balance': income - expense
                })
        else:
            # Últimos 6 meses para outros períodos
            for i in range(5, -1, -1):
                date = datetime.now() - timedelta(days=30*i)
                month_year = date.strftime('%Y-%m')
                month_name = date.strftime('%b')
                
                if DATABASE.startswith('postgresql://'):
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = %s AND type = 'income'
                        AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                    ''', (user_id, month_year))
                else:
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = ? AND type = 'income'
                        AND strftime('%Y-%m', transaction_date) = ?
                    ''', (user_id, month_year))
                
                income_result = cursor.fetchone()
                income = float(income_result['total']) if income_result else 0
                
                if DATABASE.startswith('postgresql://'):
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = %s AND type = 'expense'
                        AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                    ''', (user_id, month_year))
                else:
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE user_id = ? AND type = 'expense'
                        AND strftime('%Y-%m', transaction_date) = ?
                    ''', (user_id, month_year))
                
                expense_result = cursor.fetchone()
                expense = float(expense_result['total']) if expense_result else 0
                
                trends.append({
                    'period': month_name,
                    'income': income,
                    'expense': expense,
                    'balance': income - expense
                })
    except Exception as e:
        print(f"ERROR in get_financial_trends: {str(e)}")
    
    return trends

def get_comparative_analysis(user_id, period, conn):
    """Análise comparativa"""
    comparisons = []
    
    try:
        cursor = conn.cursor()
        
        # Comparativo mês atual vs anterior
        current_month = datetime.now().strftime('%Y-%m')
        prev_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
        
        # Receitas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'income'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'income'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, current_month))
        
        current_income_result = cursor.fetchone()
        current_income = float(current_income_result['total']) if current_income_result else 0
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'income'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, prev_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'income'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, prev_month))
        
        prev_income_result = cursor.fetchone()
        prev_income = float(prev_income_result['total']) if prev_income_result else 0
        
        income_change = calculate_percentage_change(current_income, prev_income)
        
        # Despesas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'expense'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'expense'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, current_month))
        
        current_expense_result = cursor.fetchone()
        current_expense = float(current_expense_result['total']) if current_expense_result else 0
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'expense'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, prev_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'expense'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, prev_month))
        
        prev_expense_result = cursor.fetchone()
        prev_expense = float(prev_expense_result['total']) if prev_expense_result else 0
        
        expense_change = calculate_percentage_change(current_expense, prev_expense)
        
        comparisons.append({
            'metric': 'Receitas',
            'current': current_income,
            'previous': prev_income,
            'change': income_change,
            'trend': 'up' if income_change > 0 else 'down'
        })
        
        comparisons.append({
            'metric': 'Despesas',
            'current': current_expense,
            'previous': prev_expense,
            'change': expense_change,
            'trend': 'down' if expense_change < 0 else 'up'
        })
    except Exception as e:
        print(f"ERROR in get_comparative_analysis: {str(e)}")
    
    return comparisons

def calculate_percentage_change(current, previous):
    """Calcular mudança percentual"""
    try:
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    except:
        return 0

def generate_financial_insights(user_id, conn):
    """Gerar insights financeiros"""
    insights = []
    
    try:
        cursor = conn.cursor()
        
        # Obter dados do mês
        current_month = datetime.now().strftime('%Y-%m')
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'income'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'income'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, current_month))
        
        month_income_result = cursor.fetchone()
        month_income = float(month_income_result['total']) if month_income_result else 0
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'expense'
                AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'expense'
                AND strftime('%Y-%m', transaction_date) = ?
            ''', (user_id, current_month))
        
        month_expense_result = cursor.fetchone()
        month_expense = float(month_expense_result['total']) if month_expense_result else 0
        
        # Insight 1: Taxa de poupança
        if month_income > 0:
            savings_rate = ((month_income - month_expense) / month_income) * 100
            if savings_rate > 20:
                insights.append({
                    'type': 'success',
                    'icon': 'piggy-bank',
                    'title': 'Excelente Poupança',
                    'message': f'Você está poupando {savings_rate:.1f}% da sua renda!'
                })
            elif savings_rate < 0:
                insights.append({
                    'type': 'danger',
                    'icon': 'exclamation-triangle',
                    'title': 'Atenção',
                    'message': 'Suas despesas superam suas receitas este mês'
                })
        
        # Insight 2: Maior despesa
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT c.name, SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = 'expense'
                AND TO_CHAR(t.transaction_date, 'YYYY-MM') = %s
                GROUP BY c.id, c.name
                ORDER BY total DESC
                LIMIT 1
            ''', (user_id, current_month))
        else:
            cursor.execute('''
                SELECT c.name, SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                AND strftime('%Y-%m', t.transaction_date) = ?
                GROUP BY c.id
                ORDER BY total DESC
                LIMIT 1
            ''', (user_id, current_month))
        
        top_expense = cursor.fetchone()
        
        if top_expense and month_expense > 0:
            expense_percentage = (top_expense['total'] / month_expense) * 100
            if expense_percentage > 40:
                insights.append({
                    'type': 'warning',
                    'icon': 'chart-pie',
                    'title': 'Categoria Dominante',
                    'message': f'{top_expense["name"]} representa {expense_percentage:.1f}% das despesas'
                })
        
        # Insight 3: Metas próximas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT title, target_amount, current_amount, deadline
                FROM goals 
                WHERE user_id = %s AND is_completed = FALSE 
                AND deadline <= CURRENT_DATE + INTERVAL '30 days'
                ORDER BY deadline
                LIMIT 2
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT title, target_amount, current_amount, deadline
                FROM goals 
                WHERE user_id = ? AND is_completed = 0 
                AND deadline <= date("now", "+30 days")
                ORDER BY deadline
                LIMIT 2
            ''', (user_id,))
        
        near_goals = cursor.fetchall()
        
        for goal in near_goals:
            progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            days_left = (datetime.strptime(goal['deadline'], '%Y-%m-%d') - datetime.now()).days
            
            if progress < 80 and days_left < 15:
                insights.append({
                    'type': 'info',
                    'icon': 'bullseye',
                    'title': 'Meta Requer Atenção',
                    'message': f'{goal["title"]} está {progress:.1f}% concluída com {days_left} dias restantes'
                })
    except Exception as e:
        print(f"ERROR in generate_financial_insights: {str(e)}")
    
    return insights

@app.route('/goals')
@login_required
def goals():
    """Página de metas"""
    try:
        user_id = session['user_id']
        
        # Parâmetros de filtro
        filter_status = request.args.get('status', 'active')
        filter_priority = request.args.get('priority', 'all')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query
        if DATABASE.startswith('postgresql://'):
            query = 'SELECT * FROM goals WHERE user_id = %s'
        else:
            query = 'SELECT * FROM goals WHERE user_id = ?'
        
        params = [user_id]
        
        if filter_status == 'active':
            query += ' AND is_completed = FALSE' if DATABASE.startswith('postgresql://') else ' AND is_completed = 0'
        elif filter_status == 'completed':
            query += ' AND is_completed = TRUE' if DATABASE.startswith('postgresql://') else ' AND is_completed = 1'
        
        if filter_priority != 'all':
            query += ' AND priority = '
            query += '%s' if DATABASE.startswith('postgresql://') else '?'
            params.append(filter_priority)
        
        query += ' ORDER BY priority = "high" DESC, deadline ASC'
        
        cursor.execute(query, params)
        goals_list = cursor.fetchall()
        goals_dict = [dict(goal) for goal in goals_list]
        
        # Estatísticas
        total_goals = len(goals_dict)
        active_goals = sum(1 for g in goals_dict if not g.get('is_completed', False))
        completed_goals = total_goals - active_goals
        
        # Progresso total
        total_progress = 0
        active_with_target = 0
        
        for goal in goals_dict:
            if goal.get('target_amount', 0) > 0 and not goal.get('is_completed', False):
                total_progress += (goal.get('current_amount', 0) / goal['target_amount']) * 100
                active_with_target += 1
        
        avg_progress = total_progress / active_with_target if active_with_target > 0 else 0
        
        conn.close()
        
        return render_template('metas_executivo.html',
                             goals=goals_dict,
                             total_goals=total_goals,
                             active_goals=active_goals,
                             completed_goals=completed_goals,
                             avg_progress=avg_progress,
                             filter_status=filter_status,
                             filter_priority=filter_priority)
    except Exception as e:
        print(f"ERROR in goals: {str(e)}")
        flash(f'Erro ao carregar metas: {str(e)}', 'danger')
        return render_template('metas_executivo.html',
                             goals=[],
                             total_goals=0,
                             active_goals=0,
                             completed_goals=0,
                             avg_progress=0,
                             filter_status='active',
                             filter_priority='all')

@app.route('/api/add_goal', methods=['POST'])
@login_required
def add_goal():
    """API para adicionar meta"""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        target_amount = float(data.get('target_amount', 0))
        deadline = data.get('deadline')
        priority = data.get('priority', 'medium')
        
        if not title or target_amount <= 0:
            return jsonify({'success': False, 'error': 'Dados inválidos'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                INSERT INTO goals (user_id, title, description, target_amount, deadline, priority)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, title, description, target_amount, deadline, priority))
        else:
            cursor.execute('''
                INSERT INTO goals (user_id, title, description, target_amount, deadline, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, target_amount, deadline, priority))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Meta criada com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update_goal_progress/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    """API para atualizar progresso da meta"""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Valor inválido'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se a meta existe e pertence ao usuário
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT * FROM goals WHERE id = %s AND user_id = %s', (goal_id, user_id))
        else:
            cursor.execute('SELECT * FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
        
        goal = cursor.fetchone()
        
        if not goal:
            return jsonify({'success': False, 'error': 'Meta não encontrada'})
        
        # Atualizar progresso
        new_amount = goal['current_amount'] + amount
        
        # Verificar se a meta foi concluída
        is_completed = True if new_amount >= goal['target_amount'] else False
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                UPDATE goals 
                SET current_amount = %s, is_completed = %s
                WHERE id = %s AND user_id = %s
            ''', (new_amount, is_completed, goal_id, user_id))
        else:
            cursor.execute('''
                UPDATE goals 
                SET current_amount = ?, is_completed = ?
                WHERE id = ? AND user_id = ?
            ''', (new_amount, 1 if is_completed else 0, goal_id, user_id))
        
        conn.commit()
        conn.close()
        
        message = 'Progresso atualizado!'
        if is_completed:
            message = 'Parabéns! Meta concluída!'
        
        return jsonify({'success': True, 'message': message, 'completed': is_completed})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_goal/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    """API para excluir meta"""
    user_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('DELETE FROM goals WHERE id = %s AND user_id = %s', (goal_id, user_id))
        else:
            cursor.execute('DELETE FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Meta excluída!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ai_financeira')
@login_required
def ai_financeira():
    """IA Financeira"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Dados para análise da IA
        monthly_data = []
        for i in range(3, -1, -1):
            date = datetime.now() - timedelta(days=30*i)
            month_year = date.strftime('%Y-%m')
            month_name = date.strftime('%b')
            
            if DATABASE.startswith('postgresql://'):
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = %s AND type = 'income'
                    AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                ''', (user_id, month_year))
            else:
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = ? AND type = 'income'
                    AND strftime('%Y-%m', transaction_date) = ?
                ''', (user_id, month_year))
            
            income_result = cursor.fetchone()
            income = float(income_result['total']) if income_result else 0
            
            if DATABASE.startswith('postgresql://'):
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = %s AND type = 'expense'
                    AND TO_CHAR(transaction_date, 'YYYY-MM') = %s
                ''', (user_id, month_year))
            else:
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                    WHERE user_id = ? AND type = 'expense'
                    AND strftime('%Y-%m', transaction_date) = ?
                ''', (user_id, month_year))
            
            expense_result = cursor.fetchone()
            expense = float(expense_result['total']) if expense_result else 0
            
            monthly_data.append({
                'month': month_name,
                'income': income,
                'expense': expense
            })
        
        # Recomendações baseadas nos dados
        recommendations = generate_ai_recommendations(user_id, conn, monthly_data)
        
        # FAQs financeiros
        faqs = [
            {
                'question': 'Como melhorar minha taxa de poupança?',
                'answer': 'Acompanhe suas despesas regularmente, estabeleça metas realistas e automatize transferências para poupança.'
            },
            {
                'question': 'Qual é o primeiro passo para investir?',
                'answer': 'Crie uma reserva de emergência de 3-6 meses de despesas antes de começar a investir.'
            },
            {
                'question': 'Como reduzir despesas desnecessárias?',
                'answer': 'Faça um diagnóstico de 30 dias identificando todos os gastos e categorize por necessidade.'
            },
            {
                'question': 'O que fazer com dívidas de alto juro?',
                'answer': 'Priorize o pagamento das dívidas com maiores taxas de juros usando métodos como avalanche ou bola de neve.'
            }
        ]
        
        conn.close()
        
        return render_template('ia_executivo.html',
                             monthly_data=monthly_data,
                             recommendations=recommendations,
                             faqs=faqs)
    except Exception as e:
        print(f"ERROR in ai_financeira: {str(e)}")
        flash(f'Erro ao carregar IA Financeira: {str(e)}', 'danger')
        return render_template('ia_executivo.html',
                             monthly_data=[],
                             recommendations=[],
                             faqs=[])

def generate_ai_recommendations(user_id, conn, monthly_data):
    """Gerar recomendações da IA"""
    recommendations = []
    
    try:
        cursor = conn.cursor()
        
        # Análise básica
        if len(monthly_data) >= 2:
            latest = monthly_data[-1]
            previous = monthly_data[-2]
            
            # Análise de tendência de despesas
            if latest['expense'] > previous['expense'] * 1.2:  # Aumento de 20%
                recommendations.append({
                    'type': 'warning',
                    'icon': 'chart-line',
                    'title': 'Atenção às Despesas',
                    'description': 'Suas despesas aumentaram significativamente este mês.',
                    'action': 'Revise suas categorias de gastos principais'
                })
            
            # Análise de poupança
            if latest['income'] > 0:
                savings_rate = ((latest['income'] - latest['expense']) / latest['income']) * 100
                if savings_rate < 10:
                    recommendations.append({
                        'type': 'info',
                        'icon': 'piggy-bank',
                        'title': 'Oportunidade de Poupança',
                        'description': f'Sua taxa de poupança atual é de {savings_rate:.1f}%.',
                        'action': 'Tente aumentar para pelo menos 15% no próximo mês'
                    })
        
        # Análise de categorias de despesa
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT c.name, SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = 'expense'
                AND TO_CHAR(t.transaction_date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
                GROUP BY c.id, c.name
                ORDER BY total DESC
                LIMIT 3
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT c.name, SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                AND strftime('%Y-%m', t.transaction_date) = strftime('%Y-%m', 'now')
                GROUP BY c.id
                ORDER BY total DESC
                LIMIT 3
            ''', (user_id,))
        
        expense_categories = cursor.fetchall()
        
        if expense_categories:
            top_category = expense_categories[0]
            total_expense = sum(cat['total'] for cat in expense_categories)
            
            if total_expense > 0:
                percentage = (top_category['total'] / total_expense) * 100
                if percentage > 40:
                    recommendations.append({
                        'type': 'info',
                        'icon': 'chart-pie',
                        'title': 'Categoria Dominante',
                        'description': f'{top_category["name"]} representa {percentage:.1f}% de suas despesas.',
                        'action': 'Considere diversificar ou reduzir gastos nesta categoria'
                    })
        
        # Verificação de metas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT title, target_amount, current_amount, deadline
                FROM goals 
                WHERE user_id = %s AND is_completed = FALSE
                AND deadline <= CURRENT_DATE + INTERVAL '30 days'
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT title, target_amount, current_amount, deadline
                FROM goals 
                WHERE user_id = ? AND is_completed = 0
                AND deadline <= date('now', '+30 days')
            ''', (user_id,))
        
        goals = cursor.fetchall()
        
        for goal in goals:
            progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            days_left = (datetime.strptime(goal['deadline'], '%Y-%m-%d') - datetime.now()).days
            
            if progress < 50 and days_left < 15:
                recommendations.append({
                    'type': 'warning',
                    'icon': 'bullseye',
                    'title': 'Meta em Risco',
                    'description': f'A meta "{goal["title"]}" está apenas {progress:.1f}% concluída.',
                    'action': f'Ajuste o prazo ou aumente o ritmo de contribuição'
                })
    except Exception as e:
        print(f"ERROR in generate_ai_recommendations: {str(e)}")
    
    return recommendations

@app.route('/profile')
@login_required
def profile():
    """Página de perfil"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        else:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        
        user = cursor.fetchone()
        user_dict = dict(user) if user else {}
        
        # Estatísticas do usuário
        stats = get_user_statistics(user_id, conn)
        
        # Histórico de atividades (simulado)
        activities = [
            {'date': 'Hoje', 'action': 'Acesso ao dashboard', 'icon': 'tachometer-alt'},
            {'date': 'Ontem', 'action': 'Adicionou nova transação', 'icon': 'plus-circle'},
            {'date': '2 dias atrás', 'action': 'Atualizou progresso de meta', 'icon': 'bullseye'},
            {'date': '1 semana atrás', 'action': 'Exportou relatório', 'icon': 'file-export'},
            {'date': '2 semanas atrás', 'action': 'Configurou novas categorias', 'icon': 'cog'}
        ]
        
        conn.close()
        
        return render_template('perfil_executivo.html',
                             user=user_dict,
                             stats=stats,
                             activities=activities,
                             now=datetime.now())
    except Exception as e:
        print(f"ERROR in profile: {str(e)}")
        flash(f'Erro ao carregar perfil: {str(e)}', 'danger')
        return render_template('perfil_executivo.html',
                             user={},
                             stats={},
                             activities=[],
                             now=datetime.now())

def get_user_statistics(user_id, conn):
    """Obter estatísticas do usuário"""
    try:
        cursor = conn.cursor()
        
        # Total de transações
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT COUNT(*) as count FROM transactions WHERE user_id = %s', (user_id,))
        else:
            cursor.execute('SELECT COUNT(*) as count FROM transactions WHERE user_id = ?', (user_id,))
        
        total_transactions_result = cursor.fetchone()
        total_transactions = total_transactions_result['count'] if total_transactions_result else 0
        
        # Total de metas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT COUNT(*) as count FROM goals WHERE user_id = %s', (user_id,))
        else:
            cursor.execute('SELECT COUNT(*) as count FROM goals WHERE user_id = ?', (user_id,))
        
        total_goals_result = cursor.fetchone()
        total_goals = total_goals_result['count'] if total_goals_result else 0
        
        # Dias usando o sistema
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT created_at FROM users WHERE id = %s', (user_id,))
        else:
            cursor.execute('SELECT created_at FROM users WHERE id = ?', (user_id,))
        
        user_data = cursor.fetchone()
        days_active = 1
        if user_data and user_data['created_at']:
            try:
                if isinstance(user_data['created_at'], str):
                    join_date = datetime.strptime(user_data['created_at'], '%Y-%m-%d %H:%M:%S')
                else:
                    join_date = user_data['created_at']
                days_active = (datetime.now() - join_date).days + 1
            except:
                days_active = 1
        
        # Categorias mais usadas
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT c.name, COUNT(t.id) as count
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s
                GROUP BY c.id, c.name
                ORDER BY count DESC
                LIMIT 3
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT c.name, COUNT(t.id) as count
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                GROUP BY c.id
                ORDER BY count DESC
                LIMIT 3
            ''', (user_id,))
        
        top_categories = cursor.fetchall()
        top_categories_list = [dict(cat) for cat in top_categories]
        
        return {
            'total_transactions': total_transactions,
            'total_goals': total_goals,
            'days_active': days_active,
            'top_categories': top_categories_list
        }
    except Exception as e:
        print(f"ERROR in get_user_statistics: {str(e)}")
        return {
            'total_transactions': 0,
            'total_goals': 0,
            'days_active': 1,
            'top_categories': []
        }

@app.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    """API para atualizar perfil"""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        theme = data.get('theme', 'executive')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email é obrigatório'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se email já existe (exceto para o próprio usuário)
        if DATABASE.startswith('postgresql://'):
            cursor.execute('SELECT id FROM users WHERE email = %s AND id != %s', (email, user_id))
        else:
            cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id))
        
        existing = cursor.fetchone()
        
        if existing:
            return jsonify({'success': False, 'error': 'Email já está em uso'})
        
        # Atualizar perfil
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                UPDATE users 
                SET full_name = %s, email = %s, theme = %s
                WHERE id = %s
            ''', (full_name, email, theme, user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, email = ?, theme = ?
                WHERE id = ?
            ''', (full_name, email, theme, user_id))
        
        conn.commit()
        conn.close()
        
        # Atualizar sessão
        session['full_name'] = full_name
        session['theme'] = theme
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/about')
def about():
    """Página sobre"""
    return render_template('sobre_executivo.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('index'))

# ===== APIs para dashboard =====

@app.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    """API para dados do dashboard"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Dados em tempo real
        today = datetime.now().strftime('%Y-%m-%d')
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'income' AND transaction_date = %s
            ''', (user_id, today))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'income' AND date(transaction_date) = ?
            ''', (user_id, today))
        
        today_income_result = cursor.fetchone()
        today_income = float(today_income_result['total']) if today_income_result else 0
        
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = %s AND type = 'expense' AND transaction_date = %s
            ''', (user_id, today))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                WHERE user_id = ? AND type = 'expense' AND date(transaction_date) = ?
            ''', (user_id, today))
        
        today_expense_result = cursor.fetchone()
        today_expense = float(today_expense_result['total']) if today_expense_result else 0
        
        # Alertas urgentes
        urgent_alerts = []
        
        # Saldo negativo
        stats = get_dashboard_stats(user_id, conn)
        if stats['balance'] < 0:
            urgent_alerts.append({
                'type': 'danger',
                'message': f'Saldo negativo: {format_currency(stats["balance"])}'
            })
        
        # Metas vencendo hoje
        if DATABASE.startswith('postgresql://'):
            cursor.execute('''
                SELECT COUNT(*) as count FROM goals 
                WHERE user_id = %s AND is_completed = FALSE 
                AND deadline = CURRENT_DATE
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT COUNT(*) as count FROM goals 
                WHERE user_id = ? AND is_completed = 0 
                AND deadline = date('now')
            ''', (user_id,))
        
        today_goals = cursor.fetchone()
        
        if today_goals and today_goals['count'] > 0:
            urgent_alerts.append({
                'type': 'warning',
                'message': f'{today_goals["count"]} meta(s) vence(m) hoje'
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'today_income': today_income,
            'today_expense': today_expense,
            'today_balance': today_income - today_expense,
            'alerts': urgent_alerts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"ERROR in api_dashboard_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'today_income': 0,
            'today_expense': 0,
            'today_balance': 0,
            'alerts': [],
            'timestamp': datetime.now().isoformat()
        })

@app.before_request
def before_request():
    """Executar antes de cada requisição"""
    # Garantir que a sessão tenha valores padrão
    if 'user_id' not in session:
        session.setdefault('theme', 'executive')
        session.setdefault('currency', 'BRL')
        session.setdefault('language', 'pt_BR')
    session.permanent = True

# ===== INICIALIZAÇÃO =====

if __name__ == '__main__':
    # Garantir diretórios
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    # Inicializar banco
    init_db()
    
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("🚀 CONTASMART PRO EXECUTIVO - SISTEMA FINANCEIRO")
    print("="*60)
    print(f"🌐 Acesse: http://localhost:{port}")
    print("👤 Login: admin")
    print("🔑 Senha: admin2026")
    print("\n⚡ Servidor executivo iniciando...\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)