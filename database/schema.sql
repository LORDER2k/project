-- Tabela de usuários atualizada
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
);

-- Tabela de transações com impostos
CREATE TABLE IF NOT EXISTS transactions (
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
);

-- Tabela de categorias hierárquicas
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
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- Tabela de metas financeiras
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    target_amount DECIMAL(10, 2) NOT NULL,
    current_amount DECIMAL(10, 2) DEFAULT 0,
    deadline DATE,
    category TEXT,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    is_completed BOOLEAN DEFAULT 0,
    auto_deduct BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de impostos e taxas
CREATE TABLE IF NOT EXISTS taxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    tax_type TEXT CHECK(tax_type IN ('income_tax', 'sales_tax', 'property_tax', 'service_tax', 'other')),
    rate DECIMAL(5, 2) NOT NULL,
    calculation_method TEXT CHECK(calculation_method IN ('percentage', 'fixed', 'graduated')),
    applies_to TEXT,
    due_date DATE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de orçamentos
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    period TEXT CHECK(period IN ('daily', 'weekly', 'monthly', 'yearly')),
    start_date DATE,
    end_date DATE,
    notifications BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Tabela de investimentos
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('stocks', 'bonds', 'crypto', 'real_estate', 'other')),
    initial_amount DECIMAL(10, 2) NOT NULL,
    current_value DECIMAL(10, 2),
    purchase_date DATE,
    return_rate DECIMAL(5, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de lembretes
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    reminder_date DATE NOT NULL,
    reminder_time TIME,
    is_recurring BOOLEAN DEFAULT 0,
    frequency TEXT,
    is_completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Inserir categorias padrão
INSERT OR IGNORE INTO categories (name, type, color, icon, is_default) VALUES
-- Receitas
('Salário', 'income', '#2ecc71', 'fas fa-money-check-alt', 1),
('Freelance', 'income', '#27ae60', 'fas fa-laptop-code', 1),
('Investimentos', 'income', '#16a085', 'fas fa-chart-line', 1),
('Aluguel', 'income', '#1abc9c', 'fas fa-home', 1),
('Outros', 'income', '#3498db', 'fas fa-plus-circle', 1),

-- Despesas
('Alimentação', 'expense', '#e74c3c', 'fas fa-utensils', 1),
('Transporte', 'expense', '#e67e22', 'fas fa-car', 1),
('Moradia', 'expense', '#d35400', 'fas fa-house-user', 1),
('Educação', 'expense', '#9b59b6', 'fas fa-graduation-cap', 1),
('Saúde', 'expense', '#e84393', 'fas fa-heartbeat', 1),
('Lazer', 'expense', '#00cec9', 'fas fa-gamepad', 1),
('Compras', 'expense', '#6c5ce7', 'fas fa-shopping-bag', 1),
('Serviços', 'expense', '#fd79a8', 'fas fa-concierge-bell', 1),
('Impostos', 'expense', '#34495e', 'fas fa-file-invoice-dollar', 1),
('Outros', 'expense', '#636e72', 'fas fa-ellipsis-h', 1);