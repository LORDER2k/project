"""
Configuração do banco de dados para Render
"""

from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    # Configuração para Render PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    db.init_app(app)
    
    with app.app_context():
        # Cria tabelas se não existirem
        db.create_all()
    
    return db