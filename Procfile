# ============================================
# CONTABILIDADE AUTOMATA - PROCFILE
# ============================================
# Release Phase (executa antes do deploy)
release: 
  python -c "from data.config import inicializar_sistema; inicializar_sistema()"

# Web Process (aplicação principal)
web: gunicorn app:app --workers=4 --threads=2 --worker-class=gthread --timeout 120 --bind=0.0.0.0:$PORT --access-logfile - --error-logfile -

# Worker Process (tarefas em background - opcional)
# worker: python worker.py

# Scheduler (tarefas agendadas - opcional)
# scheduler: python scheduler.py