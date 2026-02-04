"""
logger.py - Sistema de logging para Contabilidade Automata
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import Config

class ContabilidadeLogger:
    """Logger personalizado para o sistema"""
    
    def __init__(self):
        self.logs_dir = Config.LOGS_DIR
        self.setup_logging()
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        
        # Cria diretório de logs se não existir
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Configura formato dos logs
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Logger principal
        self.logger = logging.getLogger('ContabilidadeAutomata')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes
        self.logger.handlers.clear()
        
        # Handler para arquivo (rotação diária)
        log_file = os.path.join(self.logs_dir, 'contabilidade.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        
        # Handler para erros (arquivo separado)
        error_file = os.path.join(self.logs_dir, 'erros.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=30,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(log_format)
        
        # Handler para auditoria
        audit_file = os.path.join(self.logs_dir, 'auditoria.log')
        audit_handler = RotatingFileHandler(
            audit_file,
            maxBytes=5*1024*1024,
            backupCount=30,
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s - %(user)s - %(action)s - %(detalhes)s'
        )
        audit_handler.setFormatter(audit_formatter)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        self.audit_handler = audit_handler
    
    def log_info(self, message: str, **kwargs):
        """Log de informação"""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, exc_info=None, **kwargs):
        """Log de erro"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log de warning"""
        self.logger.warning(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log de debug"""
        self.logger.debug(message, extra=kwargs)
    
    def log_auditoria(self, user: str, action: str, detalhes: str = ""):
        """Log de auditoria"""
        log_record = logging.LogRecord(
            name='Auditoria',
            level=logging.INFO,
            pathname=__file__,
            lineno=0,
            msg='',
            args=(),
            exc_info=None
        )
        log_record.user = user
        log_record.action = action
        log_record.detalhes = detalhes
        
        self.audit_handler.emit(log_record)
    
    def log_calculo(self, tipo: str, dados: dict, resultado: dict, user: str = "Sistema"):
        """Log específico para cálculos"""
        self.log_info(
            f"Cálculo {tipo} realizado",
            tipo_calculo=tipo,
            user=user
        )
        
        self.log_auditoria(
            user=user,
            action=f"calculo_{tipo}",
            detalhes=f"Dados: {dados} | Resultado: {resultado}"
        )
    
    def log_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Log de requisições API"""
        self.log_info(
            f"API Request: {method} {endpoint} - Status: {status} - Duration: {duration:.2f}ms",
            endpoint=endpoint,
            method=method,
            status=status,
            duration=duration
        )
    
    def log_empresa_operation(self, empresa_id: str, operation: str, user: str, details: dict):
        """Log de operações em empresas"""
        self.log_info(
            f"Operação em empresa {empresa_id}: {operation}",
            empresa_id=empresa_id,
            operation=operation,
            user=user
        )
        
        self.log_auditoria(
            user=user,
            action=f"empresa_{operation}",
            detalhes=f"Empresa: {empresa_id} | Detalhes: {details}"
        )
    
    def get_logs(self, nivel: str = "INFO", limite: int = 100):
        """Recupera logs recentes"""
        log_file = os.path.join(self.logs_dir, 'contabilidade.log')
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if nivel in line:
                    logs.append(line.strip())
        
        return logs[-limite:]
    
    def clear_old_logs(self, dias: int = 30):
        """Limpa logs antigos"""
        import glob
        from datetime import datetime, timedelta
        
        limite_data = datetime.now() - timedelta(days=dias)
        
        for log_file in glob.glob(os.path.join(self.logs_dir, "*.log*")):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < limite_data:
                    os.remove(log_file)
                    self.log_info(f"Arquivo de log antigo removido: {log_file}")
            except Exception as e:
                self.log_error(f"Erro ao remover log antigo: {e}")

# Instância global do logger
logger = ContabilidadeLogger()

# Funções de conveniência
def log_info(msg, **kwargs):
    logger.log_info(msg, **kwargs)

def log_error(msg, exc_info=None, **kwargs):
    logger.log_error(msg, exc_info=exc_info, **kwargs)

def log_warning(msg, **kwargs):
    logger.log_warning(msg, **kwargs)

def log_auditoria(user, action, detalhes):
    logger.log_auditoria(user, action, detalhes)

def log_calculo(tipo, dados, resultado, user="Sistema"):
    logger.log_calculo(tipo, dados, resultado, user)

def log_api_request(endpoint, method, status, duration):
    logger.log_api_request(endpoint, method, status, duration)

if __name__ == "__main__":
    # Teste do logger
    log_info("Logger inicializado com sucesso")
    log_auditoria("admin", "login", "Login realizado no sistema")
    log_calculo("DRE", {"receita": 100000}, {"lucro": 15000}, "joao")
    log_api_request("/api/calcular/dre", "POST", 200, 125.5)
    
    print("✅ Logger testado com sucesso!")