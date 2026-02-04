# arquivo: create_admin.py
import sqlite3
from werkzeug.security import generate_password_hash

# Conectar ao banco
conn = sqlite3.connect('database/contasmart.db')
cursor = conn.cursor()

# Verificar se o usuário admin já existe
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
user = cursor.fetchone()

if not user:
    # Criar usuário admin
    hashed_password = generate_password_hash('admin2026')
    cursor.execute(
        "INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@contasmart.com', hashed_password, 'Administrador')
    )
    conn.commit()
    print("✅ Usuário admin criado com sucesso!")
    print("👤 Usuário: admin")
    print("🔑 Senha: admin2026")
else:
    # Resetar senha do admin existente
    hashed_password = generate_password_hash('admin2026')
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = 'admin'",
        (hashed_password,)
    )
    conn.commit()
    print("✅ Senha do usuário admin resetada!")
    print("👤 Usuário: admin")
    print("🔑 Senha: admin2026")

conn.close()