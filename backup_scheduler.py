import os
import schedule
import time
from datetime import datetime

def backup_database():
    """Faz backup automático do banco"""
    if DB_TYPE == 'sqlite':
        import shutil
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/backup_{timestamp}.db'
        
        shutil.copy2('database/contasmart.db', backup_file)
        print(f"✅ Backup criado: {backup_file}")