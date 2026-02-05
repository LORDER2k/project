#!/bin/bash
# Script de inicialização para Render

echo "Iniciando aplicação Flask..."

# Ativa modo de produção
export FLASK_ENV=production

# Configura PostgreSQL
if [ -n "$DATABASE_URL" ]; then
    echo "Configurando PostgreSQL..."
    export DATABASE_URL=${DATABASE_URL/postgres:\/\//postgresql:\/\/}
fi

# Executa migrações se necessário
# flask db upgrade

# Inicia a aplicação com Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT wsgi:app --workers 2 --threads 4 --timeout 120