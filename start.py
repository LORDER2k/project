#!/usr/bin/env python3
"""
ContaSmart Pro Executive - Sistema de Gestão Financeira
Inicializador do Sistema Executivo

Comandos disponíveis:
  python start.py               # Inicia o servidor
  python start.py --init        # Inicializa banco de dados
  python start.py --reset       # Reseta banco de dados
  python start.py --demo        # Carrega dados de demonstração
  python start.py --test        # Executa testes
  python start.py --backup      # Cria backup do banco
  python start.py --restore     # Restaura backup
  python start.py --update      # Atualiza sistema
  python start.py --help        # Mostra ajuda
"""

import os
import sys
import sqlite3
import shutil
import argparse
from datetime import datetime
import subprocess
import webbrowser
import json

def print_banner():
    """Exibir banner do sistema"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║   ██████╗ ██████╗ ███╗   ██╗████████╗ █████╗ ███████╗               ║
    ║  ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝               ║
    ║  ██║     ██║   ██║██╔██╗ ██║   ██║   ███████║███████╗               ║
    ║  ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██║╚════██║               ║
    ║  ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║███████║               ║
    ║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝               ║
    ║                                                                      ║
    ║                🚀 EXECUTIVE EDITION 2026                             ║
    ║                Sistema de Gestão Financeira                          ║
    ║                                                                      ║
    ║                Desenvolvido por: Deyvid Santos Luz                   ║
    ║                Email: suportdeyvid@gmail.com                         ║
    ║                deyv's company © 2026                                 ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print("\033[96m" + banner + "\033[0m")
    
def check_dependencies():
    """Verificar dependências do sistema"""
    print("🔍 Verificando dependências...")
    
    dependencies = {
        'Flask': 'flask',
        'Flask-SQLAlchemy': 'flask_sqlalchemy',
        'Werkzeug': 'werkzeug'
    }
    
    missing = []
    
    for package, import_name in dependencies.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Dependências faltando: {', '.join(missing)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Todas dependências verificadas!")
    return True

def init_database():
    """Inicializar banco de dados"""
    print("\n🔄 Inicializando banco de dados...")
    
    try:
        from app import init_db
        init_db()
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def reset_database():
    """Resetar banco de dados"""
    print("\n⚠️  RESETAR BANCO DE DADOS")
    print("=" * 50)
    print("ATENÇÃO: Esta ação irá:")
    print("  1. Apagar TODOS os dados existentes")
    print("  2. Criar um novo banco de dados")
    print("  3. Carregar dados de demonstração")
    print("=" * 50)
    
    confirm = input("\n⚠️  Tem certeza que deseja continuar? (s/n): ")
    if confirm.lower() != 's':
        print("Operação cancelada.")
        return False
    
    # Fazer backup antes de resetar
    backup_database()
    
    # Remover banco existente
    if os.path.exists('database/contasmart.db'):
        os.remove('database/contasmart.db')
        print("✅ Banco de dados antigo removido.")
    
    # Criar novo banco
    return init_database()

def load_demo_data():
    """Carregar dados de demonstração"""
    print("\n🎮 Carregando dados de demonstração...")
    
    try:
        conn = sqlite3.connect('database/contasmart.db')
        cursor = conn.cursor()
        
        # Verificar se já existem dados
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 1:  # Já tem admin + outros usuários
            print("⚠️  Banco já contém dados. Use --reset para recriar.")
            conn.close()
            return False
        
        # Adicionar mais dados de demonstração
        demo_users = [
            ('ceo', 'ceo@empresa.com', 'Carlos Silva', 'CEO Corporativo'),
            ('financeiro', 'finance@empresa.com', 'Ana Santos', 'Diretora Financeira'),
            ('analista', 'analyst@empresa.com', 'Roberto Lima', 'Analista Sênior')
        ]
        
        for username, email, name, role in demo_users:
            # Verificar se usuário já existe
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (username, email, full_name, password, theme)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, name, 'demo2026', 'executive'))
                
                user_id = cursor.lastrowid
                
                # Criar transações de demonstração
                import random
                from datetime import datetime, timedelta
                
                for i in range(15):
                    trans_type = 'income' if random.random() > 0.6 else 'expense'
                    amount = random.uniform(100, 5000) if trans_type == 'income' else random.uniform(50, 2000)
                    days_ago = random.randint(0, 90)
                    date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                    
                    cursor.execute('''
                        INSERT INTO transactions (user_id, type, amount, description, transaction_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, trans_type, amount, f'Transação demo {i+1}', date))
                
                print(f"  ✅ Usuário demo: {name} ({role})")
        
        conn.commit()
        conn.close()
        
        print("✅ Dados de demonstração carregados com sucesso!")
        print("\n👥 Usuários de demonstração disponíveis:")
        print("   👑 admin / admin2026 (Administrador)")
        print("   👔 ceo / demo2026 (CEO Corporativo)")
        print("   💼 financeiro / demo2026 (Diretora Financeira)")
        print("   📊 analista / demo2026 (Analista Sênior)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados demo: {e}")
        return False

def backup_database():
    """Criar backup do banco de dados"""
    print("\n💾 Criando backup do banco de dados...")
    
    if not os.path.exists('database/contasmart.db'):
        print("⚠️  Banco de dados não encontrado.")
        return False
    
    # Criar diretório de backups se não existir
    os.makedirs('backups', exist_ok=True)
    
    # Gerar nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/contasmart_backup_{timestamp}.db'
    
    try:
        shutil.copy2('database/contasmart.db', backup_file)
        
        # Manter apenas os últimos 5 backups
        backups = sorted([f for f in os.listdir('backups') if f.endswith('.db')])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(f'backups/{old_backup}')
        
        print(f"✅ Backup criado: {backup_file}")
        print(f"📁 Backups disponíveis: {len(backups)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def restore_backup():
    """Restaurar backup do banco de dados"""
    print("\n🔄 Restaurando backup...")
    
    backups = sorted([f for f in os.listdir('backups') if f.endswith('.db')])
    
    if not backups:
        print("⚠️  Nenhum backup encontrado.")
        return False
    
    print("📁 Backups disponíveis:")
    for i, backup in enumerate(backups, 1):
        # CORREÇÃO DA LINHA 231: Adicionar fecha aspas
        size = os.path.getsize(f'backups/{backup}') / 1024  # ✅ CORRIGIDO
        print(f"  {i}. {backup} ({size:.1f} KB)")
    
    try:
        choice = int(input("\nEscolha o backup para restaurar (número): "))
        if 1 <= choice <= len(backups):
            backup_file = f'backups/{backups[choice-1]}'
            
            # Fazer backup do banco atual
            current_backup = f'backups/contasmart_current_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            if os.path.exists('database/contasmart.db'):
                shutil.copy2('database/contasmart.db', current_backup)
            
            # Restaurar backup
            shutil.copy2(backup_file, 'database/contasmart.db')
            
            print(f"✅ Backup restaurado: {backup_file}")
            print(f"📋 Backup atual salvo como: {current_backup}")
            return True
        else:
            print("❌ Escolha inválida.")
            return False
            
    except (ValueError, IndexError) as e:
        print(f"❌ Erro: {e}")
        return False

def run_tests():
    """Executar testes do sistema"""
    print("\n🧪 Executando testes...")
    
    tests = [
        ('Teste de conexão com banco', test_database_connection),
        ('Teste de rotas principais', test_routes),
        ('Teste de templates', test_templates),
        ('Teste de APIs', test_apis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"  🔄 {test_name}...")
            success, message = test_func()
            if success:
                print(f"    ✅ {message}")
                results.append(True)
            else:
                print(f"    ❌ {message}")
                results.append(False)
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resultado dos testes: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print("⚠️  Alguns testes falharam.")
        return False

def test_database_connection():
    """Testar conexão com banco de dados"""
    try:
        conn = sqlite3.connect('database/contasmart.db')
        cursor = conn.cursor()
        
        # Testar tabelas
        tables = ['users', 'transactions', 'categories', 'goals']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                return False, f"Tabela {table} não encontrada"
        
        # Testar dados básicos
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        conn.close()
        
        return True, f"Conexão OK ({user_count} usuários)"
        
    except Exception as e:
        return False, f"Erro de conexão: {e}"

def test_routes():
    """Testar rotas principais"""
    # CORREÇÃO DA LINHA 233: Adicionar bloco try-except completo
    try:
        import app
        from flask import Flask
        
        test_app = Flask(__name__)
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Testar rota principal
            response = client.get('/')
            if response.status_code != 200:
                return False, "Rota principal falhou"
            
            # Testar login
            response = client.get('/login')
            if response.status_code != 200:
                return False, "Rota de login falhou"
            
            return True, "Rotas OK"
            
    except Exception as e:
        return False, f"Erro nas rotas: {e}"

def test_templates():
    """Testar templates"""
    try:
        templates = [
            'index_executivo.html',
            'login_executivo.html',
            'dashboard_executivo.html',
            'base_executivo.html'
        ]
        
        for template in templates:
            if not os.path.exists(f'templates/{template}'):
                return False, f"Template {template} não encontrado"
        
        return True, "Templates OK"
        
    except Exception as e:
        return False, f"Erro nos templates: {e}"

def test_apis():
    """Testar APIs"""
    try:
        import json
        
        # Verificar se as APIs estão definidas no app.py
        with open('app.py', 'r') as f:
            content = f.read()
            
        apis = [
            '@app.route(\'/api/add_transaction\'',
            '@app.route(\'/api/delete_transaction\'',
            '@app.route(\'/api/add_goal\'',
            '@app.route(\'/api/dashboard_data\''
        ]
        
        for api in apis:
            if api not in content:
                return False, f"API {api} não encontrada"
        
        return True, "APIs OK"
        
    except Exception as e:
        return False, f"Erro nas APIs: {e}"

def update_system():
    """Atualizar sistema"""
    print("\n🔄 Atualizando sistema...")
    
    print("1. Verificando atualizações...")
    
    # Verificar se há atualizações no requirements.txt
    if os.path.exists('requirements.txt'):
        print("2. Atualizando dependências...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', 'requirements.txt'], 
                          check=True)
            print("✅ Dependências atualizadas!")
        except subprocess.CalledProcessError:
            print("⚠️  Erro ao atualizar dependências")
    
    print("3. Verificando estrutura de diretórios...")
    
    # Criar diretórios necessários
    directories = [
        'templates',
        'static/css',
        'static/js',
        'static/img',
        'database',
        'backups',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("4. Verificando arquivos de configuração...")
    
    # Verificar se todos os templates necessários existem
    required_templates = [
        'base_executivo.html',
        'index_executivo.html',
        'dashboard_executivo.html',
        'transacoes_executivo.html',
        'analytics_executivo.html',
        'metas_executivo.html',
        'ia_executivo.html',
        'perfil_executivo.html',
        'login_executivo.html',
        'register_executivo.html',
        'sobre_executivo.html'
    ]
    
    for template in required_templates:
        if not os.path.exists(f'templates/{template}'):
            print(f"  ⚠️  Template {template} não encontrado")
    
    print("5. Limpando cache...")
    
    # Limpar cache do Flask
    cache_dirs = ['__pycache__', 'static/.cache']
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"  ✅ {cache_dir} removido")
    
    print("\n✅ Sistema atualizado com sucesso!")
    return True

def check_system_health():
    """Verificar saúde do sistema"""
    print("\n🏥 Verificando saúde do sistema...")
    
    checks = [
        ('Banco de dados', check_database_health),
        ('Arquivos do sistema', check_files_health),
        ('Configuração', check_config_health),
        ('Permissões', check_permissions_health)
    ]
    
    all_healthy = True
    
    for check_name, check_func in checks:
        try:
            healthy, message = check_func()
            if healthy:
                print(f"  ✅ {check_name}: {message}")
            else:
                print(f"  ❌ {check_name}: {message}")
                all_healthy = False
        except Exception as e:
            print(f"  ⚠️  {check_name}: Erro - {e}")
            all_healthy = False
    
    if all_healthy:
        print("\n🎉 Sistema saudável e pronto para uso!")
    else:
        print("\n⚠️  Alguns problemas foram detectados.")
        print("   Execute 'python start.py --update' para tentar corrigir.")
    
    return all_healthy

def check_database_health():
    """Verificar saúde do banco de dados"""
    try:
        if not os.path.exists('database/contasmart.db'):
            return False, "Arquivo do banco não encontrado"
        
        conn = sqlite3.connect('database/contasmart.db')
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if len(tables) < 4:
            return False, f"Apenas {len(tables)} tabelas encontradas"
        
        # Verificar usuário admin
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            return False, "Usuário admin não encontrado"
        
        conn.close()
        return True, f"{len(tables)} tabelas, banco OK"
        
    except Exception as e:
        return False, f"Erro: {e}"

def check_files_health():
    """Verificar saúde dos arquivos"""
    required_files = [
        'app.py',
        'start.py',
        'requirements.txt',
        'templates/base_executivo.html',
        'static/css/executive-style.css'
    ]
    
    missing = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        return False, f"{len(missing)} arquivos faltando"
    
    return True, "Todos arquivos presentes"

def check_config_health():
    """Verificar configuração"""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Verificar configurações importantes
        checks = [
            ('SECRET_KEY configurada', 'app.secret_key ='),
            ('Database configurado', 'DATABASE ='),
            ('Debug configurado', 'app.run(debug='),
        ]
        
        for check_name, check_string in checks:
            if check_string not in content:
                return False, f"{check_name} não encontrada"
        
        return True, "Configuração OK"
        
    except Exception as e:
        return False, f"Erro: {e}"

def check_permissions_health():
    """Verificar permissões"""
    try:
        # Verificar se podemos escrever nos diretórios necessários
        directories = ['database', 'backups', 'logs']
        
        for directory in directories:
            if os.path.exists(directory):
                test_file = os.path.join(directory, '.test_write')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except Exception:
                    return False, f"Sem permissão de escrita em {directory}"
        
        return True, "Permissões OK"
        
    except Exception as e:
        return False, f"Erro: {e}"

def start_server(port=5000, host='0.0.0.0'):
    """Iniciar servidor Flask"""
    print(f"\n🚀 Iniciando servidor executivo na porta {port}...")
    
    # Verificar se o sistema está saudável
    if not check_system_health():
        print("\n⚠️  Corrija os problemas antes de iniciar o servidor.")
        return False
    
    # Iniciar servidor
    try:
        # Abrir navegador automaticamente
        url = f"http://localhost:{port}"
        print(f"\n🌐 Acesse: {url}")
        print("👤 Login: admin")
        print("🔑 Senha: admin2026")
        print("\n⚡ Servidor executivo iniciando...\n")
        
        # Tentar abrir no navegador
        try:
            webbrowser.open(url)
        except:
            pass
        
        # Importar e executar app
        from app import app
        app.run(debug=True, host=host, port=port)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def show_help():
    """Mostrar ajuda"""
    print_banner()
    print(__doc__)
    
    print("\n📋 Exemplos de uso:")
    print("  python start.py                    # Inicia o servidor")
    print("  python start.py --init --demo      # Inicia com dados demo")
    print("  python start.py --test --health    # Testa e verifica saúde")
    print("  python start.py --backup --update  # Backup e atualiza")
    
    print("\n🔧 Opções avançadas:")
    print("  --port PORT      # Especificar porta (padrão: 5000)")
    print("  --host HOST      # Especificar host (padrão: 0.0.0.0)")
    print("  --no-browser     # Não abrir navegador automaticamente")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='ContaSmart Pro Executive - Sistema de Gestão Financeira')
    
    # Opções principais
    parser.add_argument('--init', action='store_true', help='Inicializar banco de dados')
    parser.add_argument('--reset', action='store_true', help='Resetar banco de dados (PERIGO!)')
    parser.add_argument('--demo', action='store_true', help='Carregar dados de demonstração')
    parser.add_argument('--test', action='store_true', help='Executar testes do sistema')
    parser.add_argument('--backup', action='store_true', help='Criar backup do banco')
    parser.add_argument('--restore', action='store_true', help='Restaurar backup do banco')
    parser.add_argument('--update', action='store_true', help='Atualizar sistema')
    parser.add_argument('--health', action='store_true', help='Verificar saúde do sistema')
    parser.add_argument('--help', action='store_true', help='Mostrar esta mensagem de ajuda')
    
    # Opções do servidor
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor (padrão: 5000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host do servidor (padrão: 0.0.0.0)')
    parser.add_argument('--no-browser', action='store_true', help='Não abrir navegador automaticamente')
    
    args = parser.parse_args()
    
    # Mostrar banner
    print_banner()
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Dependências faltando. Instale com:")
        print("   pip install -r requirements.txt")
        return
    
    # Processar comandos
    if args.help:
        show_help()
        return
    
    if args.reset:
        reset_database()
    
    if args.init and not args.reset:  # Se não for reset, só inicializar
        init_database()
    
    if args.demo:
        load_demo_data()
    
    if args.backup:
        backup_database()
    
    if args.restore:
        restore_backup()
    
    if args.update:
        update_system()
    
    if args.test:
        run_tests()
    
    if args.health:
        check_system_health()
    
    # CORREÇÃO DA LINHA 701: Quebrar linha longa
    if not any([
        args.init, args.reset, args.demo, args.test,
        args.backup, args.restore, args.update, args.health
    ]):
        start_server(port=args.port, host=args.host)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)