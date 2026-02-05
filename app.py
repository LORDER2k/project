"""
CONTASMART PRO EXECUTIVO - Sistema Financeiro
Versão otimizada para Render.com
Desenvolvedor: Deyvid Santos Luz
Empresa: deyv's company
Email: suportdeyvid@gmail.com
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from datetime import datetime, timedelta
from functools import wraps
import traceback

# ===== CONFIGURAÇÃO PARA RENDER =====
app = Flask(__name__)

# Configuração da secret key
app.secret_key = os.environ.get('SECRET_KEY', 'contasmart-executivo-2026-secret-dev')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuração de banco para Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    DATABASE = DATABASE_URL
    DB_TYPE = 'postgresql'
    print(f"🔗 Usando PostgreSQL no Render")
else:
    DATABASE = 'database/contasmart.db'
    DB_TYPE = 'sqlite'
    print("📁 Usando SQLite local")

# ===== SISTEMA PERSONALIZADO =====

def get_system_info():
    """Retorna informações do sistema personalizadas"""
    return {
        'company': "deyv's company",
        'developer': "Deyvid Santos Luz",
        'email': "suportdeyvid@gmail.com",
        'version': "2.0.1 Executive",
        'year': 2026
    }

def get_developer_info():
    """Retorna informações do desenvolvedor"""
    return {
        'name': "Deyvid Santos Luz",
        'role': "CEO & Desenvolvedor Principal",
        'company': "deyv's company",
        'email': "suportdeyvid@gmail.com",
        'expertise': ["Python", "Flask", "Sistemas Financeiros", "SQL", "JavaScript"],
        'bio': "Desenvolvedor full-stack especializado em sistemas financeiros e aplicações web empresariais."
    }

# ===== FUNÇÕES AUXILIARES =====

def get_db_connection():
    """Conectar ao banco de dados"""
    if DB_TYPE == 'postgresql':
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

def sql_placeholder():
    """Retorna placeholder correto para o banco"""
    return '%s' if DB_TYPE == 'postgresql' else '?'

def execute_sql(cursor, sql, params=None):
    """Executa SQL com placeholders corretos"""
    if params is None:
        params = []
    cursor.execute(sql, params)

def init_db():
    """Inicializar banco de dados"""
    print("🔄 Inicializando banco de dados...")
    
    # Criar diretório database se for SQLite
    if DB_TYPE == 'sqlite':
        os.makedirs('database', exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabela de usuários
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                id {'SERIAL PRIMARY KEY' if DB_TYPE == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
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
        
        # Tabela de categorias
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS categories (
                id {'SERIAL PRIMARY KEY' if DB_TYPE == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
                user_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(10) CHECK(type IN ('income', 'expense')) NOT NULL,
                color VARCHAR(20) DEFAULT '#0066ff',
                icon VARCHAR(50) DEFAULT 'fas fa-tag',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de transações
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS transactions (
                id {'SERIAL PRIMARY KEY' if DB_TYPE == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
                user_id INTEGER NOT NULL,
                type VARCHAR(10) CHECK(type IN ('income', 'expense')) NOT NULL,
                category_id INTEGER,
                amount DECIMAL(10, 2) NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de metas
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS goals (
                id {'SERIAL PRIMARY KEY' if DB_TYPE == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
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
        
        # Tabela de notificações
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS notifications (
                id {'SERIAL PRIMARY KEY' if DB_TYPE == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT,
                type VARCHAR(20) DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        
        # Verificar usuário admin
        placeholder = sql_placeholder()
        execute_sql(cursor, f'SELECT * FROM users WHERE username = {placeholder}', ('admin',))
        admin = cursor.fetchone()
        
        if not admin:
            hashed_password = generate_password_hash('admin2026')
            
            execute_sql(cursor, f'''
                INSERT INTO users (username, email, password, full_name, theme)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                {'RETURNING id' if DB_TYPE == 'postgresql' else ''}
            ''', ('admin', 'admin@contasmart.com', hashed_password, 'Administrador', 'executive'))
            
            if DB_TYPE == 'postgresql':
                user_id = cursor.fetchone()['id']
            else:
                user_id = cursor.lastrowid
            
            # Categorias padrão
            default_categories = [
                ('Salário', 'income', '#00ff88', 'fas fa-money-check-alt'),
                ('Freelance', 'income', '#00ffff', 'fas fa-laptop-code'),
                ('Investimentos', 'income', '#9d00ff', 'fas fa-chart-line'),
                ('Alimentação', 'expense', '#ff3366', 'fas fa-utensils'),
                ('Transporte', 'expense', '#ff9900', 'fas fa-car'),
                ('Moradia', 'expense', '#ff0066', 'fas fa-home'),
                ('Lazer', 'expense', '#00ccff', 'fas fa-gamepad')
            ]
            
            for name, type, color, icon in default_categories:
                execute_sql(cursor, f'''
                    INSERT INTO categories (user_id, name, type, color, icon)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                ''', (user_id, name, type, color, icon))
            
            conn.commit()
            print("✅ Banco de dados inicializado com sucesso!")
        
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

def create_notification(user_id, title, message, type='info'):
    """Criar nova notificação"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = sql_placeholder()
    
    execute_sql(cursor, f'''
        INSERT INTO notifications (user_id, title, message, type)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
    ''', (user_id, title, message, type))
    
    conn.commit()
    conn.close()

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
def index():
    """Página inicial"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    system_info = get_system_info()
    developer_info = get_developer_info()
    return render_template('index_executivo.html', 
                         system_info=system_info,
                         developer_info=developer_info,
                         now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    system_info = get_system_info()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Preencha todos os campos.', 'danger')
            return render_template('login_executivo.html', system_info=system_info)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        placeholder = sql_placeholder()
        execute_sql(cursor, 
                   f'SELECT * FROM users WHERE username = {placeholder} OR email = {placeholder}', 
                   (username, username))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name'] or user['username']
            session['theme'] = user['theme']
            session.permanent = True
            
            # Criar notificação de login
            create_notification(user['id'], 'Login realizado', f'Bem-vindo de volta, {user["username"]}!', 'success')
            
            flash(f'Bem-vindo, {session["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    
    return render_template('login_executivo.html', system_info=system_info)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    system_info = get_system_info()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip() or username
        
        if not username or not email or not password:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('register_executivo.html', system_info=system_info)
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register_executivo.html', system_info=system_info)
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register_executivo.html', system_info=system_info)
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            placeholder = sql_placeholder()
            execute_sql(cursor, f'''
                INSERT INTO users (username, email, password, full_name, theme)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                {'RETURNING id' if DB_TYPE == 'postgresql' else ''}
            ''', (username, email, hashed_password, full_name, 'executive'))
            
            if DB_TYPE == 'postgresql':
                new_user_id = cursor.fetchone()['id']
            else:
                new_user_id = cursor.lastrowid
            
            # Copiar categorias padrão do admin (ID 1)
            execute_sql(cursor, 'SELECT * FROM categories WHERE user_id = 1')
            default_categories = cursor.fetchall()
            
            for cat in default_categories:
                execute_sql(cursor, f'''
                    INSERT INTO categories (user_id, name, type, color, icon)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                ''', (new_user_id, cat['name'], cat['type'], cat['color'], cat['icon']))
            
            conn.commit()
            
            flash('Conta criada com sucesso! Faça login para acessar o sistema.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            conn.rollback()
            if 'unique' in str(e).lower():
                flash('Usuário ou email já cadastrados.', 'danger')
            else:
                flash(f'Erro ao criar conta: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('register_executivo.html', system_info=system_info)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        user_id = session['user_id']
        system_info = get_system_info()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Estatísticas
        placeholder = sql_placeholder()
        
        # Total receitas
        execute_sql(cursor, 
                   f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income'", 
                   (user_id,))
        total_income = float(cursor.fetchone()['total'])
        
        # Total despesas
        execute_sql(cursor, 
                   f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense'", 
                   (user_id,))
        total_expense = float(cursor.fetchone()['total'])
        
        balance = total_income - total_expense
        
        # Este mês
        current_month = datetime.now().strftime('%Y-%m')
        
        if DB_TYPE == 'postgresql':
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income' AND TO_CHAR(transaction_date, 'YYYY-MM') = {placeholder}", 
                       (user_id, current_month))
        else:
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income' AND strftime('%Y-%m', transaction_date) = {placeholder}", 
                       (user_id, current_month))
        month_income = float(cursor.fetchone()['total'])
        
        if DB_TYPE == 'postgresql':
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense' AND TO_CHAR(transaction_date, 'YYYY-MM') = {placeholder}", 
                       (user_id, current_month))
        else:
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense' AND strftime('%Y-%m', transaction_date) = {placeholder}", 
                       (user_id, current_month))
        month_expense = float(cursor.fetchone()['total'])
        
        month_balance = month_income - month_expense
        
        # Transações recentes
        execute_sql(cursor, f'''
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = {placeholder}
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        recent_transactions = cursor.fetchall()
        recent_transactions_list = [dict(trans) for trans in recent_transactions]
        
        # Metas ativas
        execute_sql(cursor, f'''
            SELECT * FROM goals 
            WHERE user_id = {placeholder} AND is_completed = FALSE
            ORDER BY deadline ASC
            LIMIT 5
        ''', (user_id,))
        
        goals = cursor.fetchall()
        goals_list = [dict(goal) for goal in goals]
        
        # Notificações não lidas
        execute_sql(cursor, f'''
            SELECT COUNT(*) as count FROM notifications 
            WHERE user_id = {placeholder} AND is_read = FALSE
        ''', (user_id,))
        
        unread_notifications = cursor.fetchone()['count']
        
        conn.close()
        
        return render_template('dashboard_executivo.html',
                             total_income=total_income,
                             total_expense=total_expense,
                             balance=balance,
                             month_income=month_income,
                             month_expense=month_expense,
                             month_balance=month_balance,
                             recent_transactions=recent_transactions_list,
                             goals=goals_list,
                             unread_notifications=unread_notifications,
                             format_currency=format_currency,
                             system_info=system_info,
                             now=datetime.now())
        
    except Exception as e:
        print(f"ERROR in dashboard: {str(e)}")
        print(traceback.format_exc())
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return render_template('dashboard_executivo.html',
                             total_income=0,
                             total_expense=0,
                             balance=0,
                             month_income=0,
                             month_expense=0,
                             month_balance=0,
                             recent_transactions=[],
                             goals=[],
                             unread_notifications=0,
                             format_currency=format_currency,
                             system_info=get_system_info(),
                             now=datetime.now())

@app.route('/transactions')
@login_required
def transactions():
    """Página de transações"""
    try:
        user_id = session['user_id']
        system_info = get_system_info()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        # Todas as transações do usuário
        execute_sql(cursor, f'''
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = {placeholder}
            ORDER BY t.transaction_date DESC
        ''', (user_id,))
        
        transactions_list = cursor.fetchall()
        transactions_dict = [dict(trans) for trans in transactions_list]
        
        # Categorias para filtro
        execute_sql(cursor, f'''
            SELECT * FROM categories 
            WHERE user_id = {placeholder} 
            ORDER BY type, name
        ''', (user_id,))
        
        categories = cursor.fetchall()
        categories_dict = [dict(cat) for cat in categories]
        
        conn.close()
        
        return render_template('transacoes_executivo.html',
                             transactions=transactions_dict,
                             categories=categories_dict,
                             format_currency=format_currency,
                             system_info=system_info,
                             now=datetime.now())
        
    except Exception as e:
        print(f"ERROR in transactions: {str(e)}")
        flash(f'Erro ao carregar transações: {str(e)}', 'danger')
        return render_template('transacoes_executivo.html',
                             transactions=[],
                             categories=[],
                             format_currency=format_currency,
                             system_info=get_system_info(),
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
        placeholder = sql_placeholder()
        
        execute_sql(cursor, f'''
            INSERT INTO transactions (user_id, type, category_id, amount, description, transaction_date)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (user_id, trans_type, category_id, amount, description, transaction_date))
        
        conn.commit()
        conn.close()
        
        # Criar notificação
        tipo = "Receita" if trans_type == 'income' else "Despesa"
        create_notification(user_id, f'Nova {tipo} adicionada', 
                          f'{tipo} de R$ {amount:.2f} registrada: {description}', 'info')
        
        return jsonify({'success': True, 'message': 'Transação adicionada!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/goals')
@login_required
def goals():
    """Página de metas"""
    try:
        user_id = session['user_id']
        system_info = get_system_info()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        execute_sql(cursor, f'''
            SELECT * FROM goals 
            WHERE user_id = {placeholder}
            ORDER BY deadline ASC
        ''', (user_id,))
        
        goals_list = cursor.fetchall()
        goals_dict = [dict(goal) for goal in goals_list]
        
        conn.close()
        
        return render_template('metas_executivo.html',
                             goals=goals_dict,
                             format_currency=format_currency,
                             system_info=system_info,
                             now=datetime.now())
        
    except Exception as e:
        print(f"ERROR in goals: {str(e)}")
        flash(f'Erro ao carregar metas: {str(e)}', 'danger')
        return render_template('metas_executivo.html',
                             goals=[],
                             format_currency=format_currency,
                             system_info=get_system_info(),
                             now=datetime.now())

@app.route('/profile')
@login_required
def profile():
    """Página de perfil"""
    try:
        user_id = session['user_id']
        system_info = get_system_info()
        developer_info = get_developer_info()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        execute_sql(cursor, f'SELECT * FROM users WHERE id = {placeholder}', (user_id,))
        user = cursor.fetchone()
        user_dict = dict(user) if user else {}
        
        # Estatísticas do usuário
        execute_sql(cursor, f'''
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
            FROM transactions 
            WHERE user_id = {placeholder}
        ''', (user_id,))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return render_template('perfil_executivo.html',
                             user=user_dict,
                             stats=dict(stats) if stats else {},
                             format_currency=format_currency,
                             system_info=system_info,
                             developer_info=developer_info,
                             now=datetime.now())
        
    except Exception as e:
        print(f"ERROR in profile: {str(e)}")
        flash(f'Erro ao carregar perfil: {str(e)}', 'danger')
        return render_template('perfil_executivo.html',
                             user={},
                             stats={},
                             format_currency=format_currency,
                             system_info=get_system_info(),
                             developer_info=get_developer_info(),
                             now=datetime.now())
    
@app.route('/api/monthly_data')
@login_required
def api_monthly_data():
    """API para dados mensais dos gráficos"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        # Dados dos últimos 6 meses
        months = []
        income_data = []
        expense_data = []
        
        for i in range(5, -1, -1):
            date = datetime.now() - timedelta(days=30*i)
            month_year = date.strftime('%Y-%m')
            month_name = date.strftime('%b')
            months.append(month_name)
            
            if DB_TYPE == 'postgresql':
                execute_sql(cursor, 
                           f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income' AND TO_CHAR(transaction_date, 'YYYY-MM') = {placeholder}", 
                           (user_id, month_year))
            else:
                execute_sql(cursor, 
                           f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income' AND strftime('%Y-%m', transaction_date) = {placeholder}", 
                           (user_id, month_year))
            income = float(cursor.fetchone()['total'])
            income_data.append(income)
            
            if DB_TYPE == 'postgresql':
                execute_sql(cursor, 
                           f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense' AND TO_CHAR(transaction_date, 'YYYY-MM') = {placeholder}", 
                           (user_id, month_year))
            else:
                execute_sql(cursor, 
                           f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense' AND strftime('%Y-%m', transaction_date) = {placeholder}", 
                           (user_id, month_year))
            expense = float(cursor.fetchone()['total'])
            expense_data.append(expense)
        
        # Dados por categoria (este mês)
        current_month = datetime.now().strftime('%Y-%m')
        categories_data = []
        
        if DB_TYPE == 'postgresql':
            execute_sql(cursor, f'''
                SELECT c.name, c.color, COALESCE(SUM(t.amount), 0) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = {placeholder} AND t.type = 'expense'
                AND TO_CHAR(t.transaction_date, 'YYYY-MM') = {placeholder}
                GROUP BY c.id, c.name, c.color
                ORDER BY total DESC
                LIMIT 5
            ''', (user_id, current_month))
        else:
            execute_sql(cursor, f'''
                SELECT c.name, c.color, COALESCE(SUM(t.amount), 0) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = {placeholder} AND t.type = 'expense'
                AND strftime('%Y-%m', t.transaction_date) = {placeholder}
                GROUP BY c.id
                ORDER BY total DESC
                LIMIT 5
            ''', (user_id, current_month))
        
        categories = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'months': months,
            'income': income_data,
            'expense': expense_data,
            'categories': {
                'labels': [cat['name'] for cat in categories],
                'colors': [cat['color'] for cat in categories],
                'data': [float(cat['total']) for cat in categories]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})    

@app.route('/analytics')
@login_required
def analytics():
    """Página de análises (placeholder)"""
    system_info = get_system_info()
    flash('Página de análises em desenvolvimento!', 'info')
    return render_template('base_executivo.html', 
                         system_info=system_info,
                         page_title='Análises',
                         page_subtitle='Em desenvolvimento')

@app.route('/ai_financeira')
@login_required
def ai_financeira():
    """Página de IA Financeira (placeholder)"""
    system_info = get_system_info()
    flash('IA Financeira em desenvolvimento!', 'info')
    return render_template('base_executivo.html', 
                         system_info=system_info,
                         page_title='IA Financeira',
                         page_subtitle='Em desenvolvimento')

@app.route('/about')
def about():
    """Página sobre"""
    system_info = get_system_info()
    developer_info = get_developer_info()
    return render_template('sobre_executivo.html', 
                         system_info=system_info,
                         developer_info=developer_info,
                         now=datetime.now())

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('index'))

# ===== APIs para dashboard =====

@app.route('/api/health')
def health():
    """API de saúde do sistema"""
    system_info = get_system_info()
    return jsonify({
        'status': 'online',
        'app': 'ContaSmart Pro Executive 2026',
        'developer': system_info['developer'],
        'company': system_info['company'],
        'version': system_info['version'],
        'timestamp': datetime.now().isoformat(),
        'database': DB_TYPE
    })

@app.route('/api/quick_stats')
@login_required
def quick_stats():
    """API para estatísticas rápidas"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        # Receitas do mês
        current_month = datetime.now().strftime('%Y-%m')
        
        if DB_TYPE == 'postgresql':
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income' AND TO_CHAR(transaction_date, 'YYYY-MM') = {placeholder}", 
                       (user_id, current_month))
        else:
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'income' AND strftime('%Y-%m', transaction_date) = {placeholder}", 
                       (user_id, current_month))
        month_income = float(cursor.fetchone()['total'])
        
        # Despesas do mês
        if DB_TYPE == 'postgresql':
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense' AND TO_CHAR(transaction_date, 'YYYY-MM') = {placeholder}", 
                       (user_id, current_month))
        else:
            execute_sql(cursor, 
                       f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = {placeholder} AND type = 'expense' AND strftime('%Y-%m', transaction_date) = {placeholder}", 
                       (user_id, current_month))
        month_expense = float(cursor.fetchone()['total'])
        
        # Metas ativas
        execute_sql(cursor, f'''
            SELECT COUNT(*) as count FROM goals 
            WHERE user_id = {placeholder} AND is_completed = FALSE
        ''', (user_id,))
        active_goals = cursor.fetchone()['count']
        
        # Notificações não lidas
        execute_sql(cursor, f'''
            SELECT COUNT(*) as count FROM notifications 
            WHERE user_id = {placeholder} AND is_read = FALSE
        ''', (user_id,))
        unread_notifications = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'month_income': month_income,
            'month_expense': month_expense,
            'month_balance': month_income - month_expense,
            'active_goals': active_goals,
            'unread_notifications': unread_notifications,
            'formatted': {
                'month_income': format_currency(month_income),
                'month_expense': format_currency(month_expense),
                'month_balance': format_currency(month_income - month_expense)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications')
@login_required
def api_notifications():
    """API para notificações"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        execute_sql(cursor, f'''
            SELECT * FROM notifications 
            WHERE user_id = {placeholder}
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        notifications = cursor.fetchall()
        notifications_list = [dict(n) for n in notifications]
        
        # Marcar como lidas
        execute_sql(cursor, f'''
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE user_id = {placeholder} AND is_read = FALSE
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(notifications_list),
            'notifications': notifications_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system_report')
@login_required
def api_system_report():
    """API para relatório do sistema"""
    try:
        user_id = session['user_id']
        system_info = get_system_info()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholder = sql_placeholder()
        
        # Estatísticas do usuário
        execute_sql(cursor, 
                   f"SELECT COUNT(*) as total FROM transactions WHERE user_id = {placeholder}", 
                   (user_id,))
        
        user_stats = cursor.fetchone()
        conn.close()
        
        report = {
            'system': system_info,
            'user_stats': {
                'total_transactions': user_stats['total'] if user_stats else 0
            },
            'generated_at': datetime.now().isoformat(),
            'report_id': f"CS-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
        
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
    
    system_info = get_system_info()
    
    print("\n" + "="*60)
    print("🚀 CONTASMART PRO EXECUTIVO - SISTEMA FINANCEIRO")
    print("="*60)
    print(f"👨‍💻 Desenvolvedor: {system_info['developer']}")
    print(f"🏢 Empresa: {system_info['company']}")
    print(f"📧 Contato: {system_info['email']}")
    print(f"🌐 Versão: {system_info['version']}")
    print("="*60)
    print(f"🌐 Acesse: http://localhost:{port}")
    print(f"📊 Banco de dados: {DB_TYPE}")
    print("👤 Login: admin")
    print("🔑 Senha: admin2026")
    print("\n⚡ Servidor iniciando...\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)