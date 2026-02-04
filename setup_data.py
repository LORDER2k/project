"""
setup_data.py - Script para criar estrutura inicial da pasta data
Execute: python setup_data.py
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

def criar_estrutura_data():
    """Cria estrutura completa da pasta data"""
    
    print("=" * 70)
    print("📊 CRIANDO ESTRUTURA DA PASTA DATA")
    print("=" * 70)
    
    # Diretório base
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Lista de diretórios a criar
    DIRETORIOS = [
        DATA_DIR,
        os.path.join(DATA_DIR, 'empresas'),
        os.path.join(DATA_DIR, 'empresas', 'empresa_ABC'),
        os.path.join(DATA_DIR, 'empresas', 'empresa_XYZ'),
        os.path.join(DATA_DIR, 'backups'),
        os.path.join(DATA_DIR, 'logs'),
        os.path.join(DATA_DIR, 'relatorios'),
        os.path.join(DATA_DIR, 'relatorios', 'mensais'),
        os.path.join(DATA_DIR, 'relatorios', 'anuais'),
        os.path.join(DATA_DIR, 'relatorios', 'customizados'),
        os.path.join(DATA_DIR, 'templates')
    ]
    
    # Cria todos os diretórios
    for diretorio in DIRETORIOS:
        os.makedirs(diretorio, exist_ok=True)
        print(f"✅ Diretório criado/verificado: {diretorio}")
    
    # 1. Cria database.json
    criar_database_json(DATA_DIR)
    
    # 2. Cria config.py
    criar_config_py(DATA_DIR)
    
    # 3. Cria empresas exemplo
    criar_empresas_exemplo(DATA_DIR)
    
    # 4. Cria templates
    criar_templates(DATA_DIR)
    
    # 5. Cria __init__.py
    criar_init_py(DATA_DIR)
    
    print("\n" + "=" * 70)
    print("✅ ESTRUTURA DATA CRIADA COM SUCESSO!")
    print("=" * 70)
    
    # Mostra estrutura
    print("\n📁 Estrutura criada:")
    mostrar_estrutura(DATA_DIR)

def criar_database_json(data_dir):
    """Cria arquivo database.json"""
    
    database_path = os.path.join(data_dir, 'database.json')
    
    if os.path.exists(database_path):
        print(f"📁 database.json já existe")
        return
    
    database = {
        "meta": {
            "versao_banco": "1.0.0",
            "data_criacao": datetime.now().isoformat(),
            "ultima_atualizacao": datetime.now().isoformat(),
            "total_registros": 0,
            "empresas_cadastradas": 0
        },
        "configuracoes": {
            "moeda_padrao": "BRL",
            "idioma": "pt-BR",
            "formato_data": "DD/MM/YYYY",
            "casas_decimais": 2,
            "backup_automatico": True,
            "intervalo_backup_horas": 24
        },
        "empresas": [],
        "usuarios": [
            {
                "id": "USR001",
                "nome": "Administrador",
                "email": "admin@contabilidade.com",
                "perfil": "admin",
                "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
                "ultimo_acesso": datetime.now().isoformat()
            }
        ],
        "registros_dre": [],
        "registros_balanco": [],
        "registros_fluxo_caixa": [],
        "analises_salvas": [],
        "relatorios_gerados": [],
        "log_alteracoes": []
    }
    
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"✅ database.json criado")

def criar_config_py(data_dir):
    """Cria arquivo config.py"""
    
    config_path = os.path.join(data_dir, 'config.py')
    
    if os.path.exists(config_path):
        print(f"📁 config.py já existe")
        return
    
    config_content = '''
"""
config.py - Configurações do sistema Contabilidade Automata
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
            print(f"✅ Diretório criado/verificado: {{diretorio}}")

def inicializar_sistema():
    """Inicializa o sistema com configurações padrão"""
    
    print("=" * 60)
    print("📊 INICIALIZANDO SISTEMA CONTABILIDADE AUTOMATA")
    print("=" * 60)
    
    # Cria estrutura de diretórios
    Config.criar_estrutura_diretorios()
    
    print("✅ Sistema inicializado com sucesso!")
    print("=" * 60)
'''
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ config.py criado")

def criar_empresas_exemplo(data_dir):
    """Cria empresas de exemplo"""
    
    empresas_dir = os.path.join(data_dir, 'empresas')
    
    # Empresa ABC
    empresa_abc_dir = os.path.join(empresas_dir, 'empresa_ABC')
    
    # Configuração da empresa ABC
    config_abc = {
        "empresa": {
            "id": "EMP001",
            "cnpj": "12.345.678/0001-90",
            "razao_social": "EMPRESA ABC LTDA",
            "nome_fantasia": "ABC SOLUÇÕES",
            "data_fundacao": "2010-05-15",
            "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
            "status": "ativa",
            "contato": {
                "email": "contato@empresaabc.com",
                "telefone": "(11) 99999-9999"
            }
        },
        "configuracoes_contabeis": {
            "setor": "tecnologia",
            "regime_tributario": "lucro_real",
            "contador_responsavel": "Carlos Silva"
        }
    }
    
    config_path = os.path.join(empresa_abc_dir, 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_abc, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Empresa criada: empresa_ABC/config.json")
    
    # Empresa XYZ
    empresa_xyz_dir = os.path.join(empresas_dir, 'empresa_XYZ')
    
    config_xyz = {
        "empresa": {
            "id": "EMP002",
            "cnpj": "98.765.432/0001-10",
            "razao_social": "EMPRESA XYZ S/A",
            "nome_fantasia": "XYZ COMÉRCIO",
            "data_fundacao": "2015-08-20",
            "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
            "status": "ativa"
        }
    }
    
    config_path = os.path.join(empresa_xyz_dir, 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_xyz, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Empresa criada: empresa_XYZ/config.json")

def criar_templates(data_dir):
    """Cria templates padrão"""
    
    templates_dir = os.path.join(data_dir, 'templates')
    
    # Template DRE
    dre_template = {
        "template_id": "TMP_DRE_001",
        "nome": "Template DRE Padrão",
        "descricao": "Modelo padrão para Demonstração do Resultado do Exercício",
        "estrutura": {
            "receitas": ["receita_bruta", "deducoes", "receita_liquida"],
            "custos": ["custo_vendas", "lucro_bruto"],
            "despesas": ["operacionais", "financeiras"],
            "resultado": ["lucro_liquido", "margem_liquida"]
        }
    }
    
    dre_path = os.path.join(templates_dir, 'dre_template.json')
    with open(dre_path, 'w', encoding='utf-8') as f:
        json.dump(dre_template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Template criado: templates/dre_template.json")
    
    # Template Balanço
    balanco_template = {
        "template_id": "TMP_BALANCO_001",
        "nome": "Template Balanço Patrimonial",
        "descricao": "Modelo para Balanço Patrimonial",
        "estrutura": {
            "ativo": ["circulante", "nao_circulante"],
            "passivo": ["circulante", "nao_circulante"],
            "patrimonio_liquido": ["capital", "reservas", "lucros"]
        }
    }
    
    balanco_path = os.path.join(templates_dir, 'balanco_template.json')
    with open(balanco_path, 'w', encoding='utf-8') as f:
        json.dump(balanco_template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Template criado: templates/balanco_template.json")

def criar_init_py(data_dir):
    """Cria __init__.py para tornar data um pacote Python"""
    
    init_path = os.path.join(data_dir, '__init__.py')
    
    init_content = '''
"""
data - Pacote de dados do Contabilidade Automata
"""

from .config import Config, inicializar_sistema

__version__ = "1.0.0"
__author__ = "Contabilidade Automata"
'''
    
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(init_content)
    
    print(f"✅ __init__.py criado")

def mostrar_estrutura(data_dir):
    """Mostra estrutura de diretórios"""
    
    for root, dirs, files in os.walk(data_dir):
        nivel = root.replace(data_dir, '').count(os.sep)
        indent = ' ' * 2 * nivel
        print(f'{indent}📁 {os.path.basename(root) or "data"}/')
        
        subindent = ' ' * 2 * (nivel + 1)
        
        # Mostra arquivos
        for file in files:
            if file.endswith('.json') or file.endswith('.py'):
                print(f'{subindent}📄 {file}')

if __name__ == "__main__":
    criar_estrutura_data()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Execute o servidor: python app.py")
    print("2. Acesse: http://localhost:5000")
    print("3. Teste API: http://localhost:5000/api/health")
    print("4. Teste dados: http://localhost:5000/api/data/status")