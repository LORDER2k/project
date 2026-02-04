"""
config.py - Configurações do sistema Contabilidade Automata
Versão simplificada
"""

import os
from datetime import datetime

class Config:
    """Configurações principais do sistema"""
    
    # Diretórios
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
    LOGS_DIR = os.path.join(DATA_DIR, 'logs')
    RELATORIOS_DIR = os.path.join(DATA_DIR, 'relatorios')
    TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')
    
    # Caminhos de arquivos
    DATABASE_PATH = os.path.join(DATA_DIR, 'database.json')
    CONFIG_PATH = os.path.join(DATA_DIR, 'config.json')
    
    # Configurações de negócio
    MOEDA_PADRAO = "BRL"
    IDIOMA_PADRAO = "pt-BR"
    FORMATO_DATA = "%d/%m/%Y"
    FORMATO_DATA_ISO = "%Y-%m-%d"
    FORMATO_HORA = "%H:%M:%S"
    CASAS_DECIMAIS = 2
    
    # Configurações de cálculo
    LIMITE_IMPOSTOS_PERCENTUAL = 100.0
    MARGEM_LUCRO_MINIMA_ALERTA = 5.0
    LIQUIDEZ_MINIMA_RECOMENDADA = 1.5
    
    # Configurações de sistema
    BACKUP_AUTOMATICO = True
    INTERVALO_BACKUP_HORAS = 24
    MANTER_LOGS_DIAS = 30
    LIMITE_REGISTROS_POR_EMPRESA = 1000
    
    @classmethod
    def criar_estrutura_diretorios(cls):
        """Cria a estrutura completa de diretórios"""
        diretorios = [
            cls.DATA_DIR,
            cls.BACKUP_DIR,
            cls.LOGS_DIR,
            cls.RELATORIOS_DIR,
            os.path.join(cls.RELATORIOS_DIR, 'mensais'),
            os.path.join(cls.RELATORIOS_DIR, 'anuais'),
            os.path.join(cls.RELATORIOS_DIR, 'customizados'),
            cls.TEMPLATES_DIR,
            os.path.join(cls.DATA_DIR, 'empresas')
        ]
        
        for diretorio in diretorios:
            os.makedirs(diretorio, exist_ok=True)
            print(f"✅ Diretório criado/verificado: {diretorio}")

def inicializar_sistema():
    """Inicializa o sistema com configurações padrão"""
    
    print("=" * 60)
    print("📊 INICIALIZANDO SISTEMA CONTABILIDADE AUTOMATA")
    print("=" * 60)
    
    # Cria estrutura de diretórios
    Config.criar_estrutura_diretorios()
    
    print("✅ Sistema inicializado com sucesso!")
    print("=" * 60)

# Teste se executado diretamente
if __name__ == "__main__":
    inicializar_sistema()