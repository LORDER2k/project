"""
backup_manager.py - Sistema de backup automático
"""

import os
import json
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from config import Config
from data.logs.logger import log_info, log_error, log_warning

class BackupManager:
    """Gerenciador de backups do sistema"""
    
    def __init__(self):
        self.backup_dir = Config.BACKUP_DIR
        self.data_dir = Config.DATA_DIR
        self.intervalo_horas = Config.INTERVALO_BACKUP_HORAS
        
        # Cria diretório de backups se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def criar_backup_completo(self, motivo: str = "rotina"):
        """Cria um backup completo do sistema"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_nome = f"backup_completo_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_nome)
        
        try:
            # Cria diretório do backup
            os.makedirs(backup_path, exist_ok=True)
            
            # 1. Copia arquivos principais
            arquivos_principais = ['database.json', 'config.json']
            for arquivo in arquivos_principais:
                origem = os.path.join(self.data_dir, arquivo)
                if os.path.exists(origem):
                    shutil.copy2(origem, os.path.join(backup_path, arquivo))
            
            # 2. Copia pasta de empresas
            empresas_dir = os.path.join(self.data_dir, 'empresas')
            if os.path.exists(empresas_dir):
                backup_empresas = os.path.join(backup_path, 'empresas')
                shutil.copytree(empresas_dir, backup_empresas)
            
            # 3. Copia logs importantes
            logs_dir = Config.LOGS_DIR
            if os.path.exists(logs_dir):
                backup_logs = os.path.join(backup_path, 'logs')
                os.makedirs(backup_logs, exist_ok=True)
                
                for log_file in ['contabilidade.log', 'erros.log', 'auditoria.log']:
                    origem_log = os.path.join(logs_dir, log_file)
                    if os.path.exists(origem_log):
                        shutil.copy2(origem_log, os.path.join(backup_logs, log_file))
            
            # 4. Cria arquivo de metadados do backup
            metadados = {
                'nome_backup': backup_nome,
                'data_criacao': datetime.now().isoformat(),
                'motivo': motivo,
                'tipo': 'completo',
                'tamanho_total': self.calcular_tamanho_backup(backup_path),
                'hash_verificacao': self.calcular_hash_backup(backup_path),
                'arquivos_incluidos': self.listar_arquivos_backup(backup_path)
            }
            
            metadados_path = os.path.join(backup_path, 'metadados.json')
            with open(metadados_path, 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=2, ensure_ascii=False)
            
            # 5. Compacta o backup
            backup_zip = f"{backup_path}.zip"
            self.comprimir_backup(backup_path, backup_zip)
            
            # 6. Remove diretório temporário
            shutil.rmtree(backup_path)
            
            # Log do backup
            log_info(
                f"Backup completo criado: {backup_nome}.zip",
                tamanho=os.path.getsize(backup_zip),
                motivo=motivo
            )
            
            log_auditoria(
                user="Sistema",
                action="backup_criado",
                detalhes=f"Backup: {backup_nome} | Motivo: {motivo}"
            )
            
            # 7. Limpa backups antigos
            self.limpar_backups_antigos()
            
            return {
                'sucesso': True,
                'backup_nome': backup_nome,
                'arquivo': backup_zip,
                'tamanho': os.path.getsize(backup_zip),
                'metadados': metadados
            }
            
        except Exception as e:
            log_error(f"Erro ao criar backup: {str(e)}", exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def criar_backup_incremental(self, motivo: str = "incremental"):
        """Cria backup incremental (apenas alterações)"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_nome = f"backup_incremental_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_nome)
        
        try:
            # Obtém último backup para comparar
            ultimo_backup = self.obter_ultimo_backup()
            
            # Cria diretório do backup
            os.makedirs(backup_path, exist_ok=True)
            
            # Lista arquivos modificados desde o último backup
            arquivos_modificados = self.obter_arquivos_modificados(ultimo_backup)
            
            if not arquivos_modificados:
                log_info("Nenhum arquivo modificado desde o último backup")
                shutil.rmtree(backup_path)
                return {
                    'sucesso': True,
                    'mensagem': 'Nenhuma alteração desde o último backup'
                }
            
            # Copia apenas arquivos modificados
            for arquivo in arquivos_modificados:
                origem = os.path.join(self.data_dir, arquivo)
                destino = os.path.join(backup_path, arquivo)
                
                # Cria diretório de destino se necessário
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.copy2(origem, destino)
            
            # Metadados do backup incremental
            metadados = {
                'nome_backup': backup_nome,
                'data_criacao': datetime.now().isoformat(),
                'motivo': motivo,
                'tipo': 'incremental',
                'backup_base': ultimo_backup['nome'] if ultimo_backup else None,
                'arquivos_modificados': arquivos_modificados,
                'hash_verificacao': self.calcular_hash_backup(backup_path)
            }
            
            metadados_path = os.path.join(backup_path, 'metadados.json')
            with open(metadados_path, 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=2, ensure_ascii=False)
            
            # Compacta
            backup_zip = f"{backup_path}.zip"
            self.comprimir_backup(backup_path, backup_zip)
            shutil.rmtree(backup_path)
            
            log_info(
                f"Backup incremental criado: {backup_nome}.zip",
                arquivos_modificados=len(arquivos_modificados)
            )
            
            return {
                'sucesso': True,
                'backup_nome': backup_nome,
                'arquivos_modificados': len(arquivos_modificados)
            }
            
        except Exception as e:
            log_error(f"Erro ao criar backup incremental: {str(e)}")
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def restaurar_backup(self, backup_nome: str, destino: str = None):
        """Restaura um backup"""
        
        try:
            if not destino:
                destino = self.data_dir
            
            backup_path = os.path.join(self.backup_dir, f"{backup_nome}.zip")
            
            if not os.path.exists(backup_path):
                return {
                    'sucesso': False,
                    'erro': f"Backup não encontrado: {backup_nome}"
                }
            
            # Cria diretório temporário para extração
            temp_dir = os.path.join(self.backup_dir, 'temp_restore')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extrai backup
            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Verifica integridade
            metadados_path = os.path.join(temp_dir, 'metadados.json')
            if not os.path.exists(metadados_path):
                shutil.rmtree(temp_dir)
                return {
                    'sucesso': False,
                    'erro': 'Metadados do backup não encontrados'
                }
            
            with open(metadados_path, 'r', encoding='utf-8') as f:
                metadados = json.load(f)
            
            # Verifica hash
            hash_atual = self.calcular_hash_backup(temp_dir)
            if hash_atual != metadados.get('hash_verificacao'):
                log_warning(f"Hash do backup não confere: {backup_nome}")
                # Continua mesmo assim, mas loga o warning
            
            # Cria backup atual antes de restaurar
            self.criar_backup_completo("pre_restauracao")
            
            # Copia arquivos para o destino
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == 'metadados.json':
                        continue
                    
                    origem = os.path.join(root, file)
                    rel_path = os.path.relpath(origem, temp_dir)
                    destino_final = os.path.join(destino, rel_path)
                    
                    # Cria diretório de destino se necessário
                    os.makedirs(os.path.dirname(destino_final), exist_ok=True)
                    shutil.copy2(origem, destino_final)
            
            # Limpa diretório temporário
            shutil.rmtree(temp_dir)
            
            log_info(f"Backup restaurado: {backup_nome}")
            log_auditoria(
                user="Sistema",
                action="backup_restaurado",
                detalhes=f"Backup: {backup_nome} | Destino: {destino}"
            )
            
            return {
                'sucesso': True,
                'backup_restaurado': backup_nome,
                'data_backup': metadados.get('data_criacao'),
                'metadados': metadados
            }
            
        except Exception as e:
            log_error(f"Erro ao restaurar backup: {str(e)}", exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        
        backups = []
        
        for arquivo in os.listdir(self.backup_dir):
            if arquivo.endswith('.zip'):
                backup_path = os.path.join(self.backup_dir, arquivo)
                
                try:
                    # Tenta extrair metadados
                    with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                        if 'metadados.json' in zip_ref.namelist():
                            with zip_ref.open('metadados.json') as f:
                                metadados = json.load(f)
                            
                            backups.append({
                                'nome': arquivo.replace('.zip', ''),
                                'caminho': backup_path,
                                'tamanho': os.path.getsize(backup_path),
                                'data_criacao': metadados.get('data_criacao'),
                                'tipo': metadados.get('tipo', 'desconhecido'),
                                'motivo': metadados.get('motivo', ''),
                                'metadados': metadados
                            })
                except:
                    # Backup sem metadados
                    backups.append({
                        'nome': arquivo.replace('.zip', ''),
                        'caminho': backup_path,
                        'tamanho': os.path.getsize(backup_path),
                        'data_criacao': datetime.fromtimestamp(
                            os.path.getmtime(backup_path)
                        ).isoformat(),
                        'tipo': 'desconhecido',
                        'motivo': 'Backup antigo'
                    })
        
        # Ordena por data (mais recente primeiro)
        backups.sort(
            key=lambda x: x['data_criacao'],
            reverse=True
        )
        
        return backups
    
    def limpar_backups_antigos(self, dias_manter: int = 30):
        """Remove backups mais antigos que o período especificado"""
        
        limite_data = datetime.now() - timedelta(days=dias_manter)
        backups_removidos = []
        
        for backup_info in self.listar_backups():
            try:
                data_backup = datetime.fromisoformat(
                    backup_info['data_criacao'].replace('Z', '+00:00')
                )
                
                if data_backup < limite_data:
                    os.remove(backup_info['caminho'])
                    backups_removidos.append(backup_info['nome'])
                    
                    log_info(f"Backup antigo removido: {backup_info['nome']}")
            except Exception as e:
                log_error(f"Erro ao remover backup antigo: {e}")
        
        if backups_removidos:
            log_auditoria(
                user="Sistema",
                action="backups_limpos",
                detalhes=f"Backups removidos: {', '.join(backups_removidos)}"
            )
        
        return backups_removidos
    
    def verificar_integridade_backup(self, backup_nome: str):
        """Verifica integridade de um backup"""
        
        backup_path = os.path.join(self.backup_dir, f"{backup_nome}.zip")
        
        if not os.path.exists(backup_path):
            return {
                'sucesso': False,
                'erro': 'Backup não encontrado'
            }
        
        try:
            # Verifica se é um arquivo zip válido
            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                # Testa integridade
                test_result = zip_ref.testzip()
                
                if test_result is not None:
                    return {
                        'sucesso': False,
                        'erro': f'Arquivo corrompido: {test_result}'
                    }
            
            return {
                'sucesso': True,
                'mensagem': 'Backup íntegro'
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro na verificação: {str(e)}'
            }
    
    # Métodos auxiliares
    def calcular_tamanho_backup(self, backup_path: str) -> int:
        """Calcula tamanho total do backup em bytes"""
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(backup_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        return total_size
    
    def calcular_hash_backup(self, backup_path: str) -> str:
        """Calcula hash SHA-256 do backup"""
        hasher = hashlib.sha256()
        
        arquivos = []
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                if file != 'metadados.json':  # Exclui metadados do hash
                    arquivos.append(os.path.join(root, file))
        
        # Ordena para garantir consistência
        arquivos.sort()
        
        for arquivo in arquivos:
            with open(arquivo, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def listar_arquivos_backup(self, backup_path: str) -> list:
        """Lista todos os arquivos do backup"""
        arquivos = []
        
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), backup_path)
                arquivos.append(rel_path)
        
        return sorted(arquivos)
    
    def comprimir_backup(self, origem: str, destino_zip: str):
        """Comprime diretório em arquivo ZIP"""
        
        with zipfile.ZipFile(destino_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(origem):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, origem)
                    zipf.write(file_path, arcname)
    
    def obter_ultimo_backup(self):
        """Obtém informações do último backup"""
        
        backups = self.listar_backups()
        if backups:
            return backups[0]
        return None
    
    def obter_arquivos_modificados(self, ultimo_backup: dict) -> list:
        """Identifica arquivos modificados desde o último backup"""
        
        if not ultimo_backup:
            # Sem backup anterior, todos os arquivos são "modificados"
            arquivos_modificados = []
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), self.data_dir)
                    arquivos_modificados.append(rel_path)
            return arquivos_modificados
        
        # Extrai último backup para comparação
        temp_dir = os.path.join(self.backup_dir, 'temp_comparacao')
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(ultimo_backup['caminho'], 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Compara arquivos
            arquivos_modificados = []
            
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    origem = os.path.join(root, file)
                    rel_path = os.path.relpath(origem, self.data_dir)
                    destino = os.path.join(temp_dir, rel_path)
                    
                    if not os.path.exists(destino):
                        # Arquivo novo
                        arquivos_modificados.append(rel_path)
                    else:
                        # Verifica se foi modificado
                        origem_mtime = os.path.getmtime(origem)
                        destino_mtime = os.path.getmtime(destino)
                        
                        if origem_mtime > destino_mtime:
                            arquivos_modificados.append(rel_path)
            
            # Remove diretório temporário
            shutil.rmtree(temp_dir)
            
            return arquivos_modificados
            
        except Exception as e:
            log_error(f"Erro ao comparar backups: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return []
    
    def executar_backup_automatico(self):
        """Executa backup automático baseado no intervalo configurado"""
        
        ultimo_backup = self.obter_ultimo_backup()
        
        if ultimo_backup:
            # Verifica se passou tempo suficiente desde o último backup
            try:
                ultima_data = datetime.fromisoformat(
                    ultimo_backup['data_criacao'].replace('Z', '+00:00')
                )
                tempo_decorrido = datetime.now() - ultima_data
                horas_decorridas = tempo_decorrido.total_seconds() / 3600
                
                if horas_decorridas < self.intervalo_horas:
                    return {
                        'executado': False,
                        'motivo': f'Ainda não passaram {self.intervalo_horas} horas desde o último backup'
                    }
            except:
                pass
        
        # Executa backup
        resultado = self.criar_backup_completo("automatico")
        resultado['executado'] = True
        
        return resultado

# Instância global do gerenciador de backups
backup_manager = BackupManager()

# Funções de conveniência
def criar_backup_completo(motivo="rotina"):
    return backup_manager.criar_backup_completo(motivo)

def criar_backup_incremental(motivo="incremental"):
    return backup_manager.criar_backup_incremental(motivo)

def restaurar_backup(backup_nome, destino=None):
    return backup_manager.restaurar_backup(backup_nome, destino)

def listar_backups():
    return backup_manager.listar_backups()

def executar_backup_automatico():
    return backup_manager.executar_backup_automatico()

if __name__ == "__main__":
    # Teste do sistema de backup
    print("🧪 Testando sistema de backup...")
    
    # Lista backups existentes
    backups = listar_backups()
    print(f"📁 Backups existentes: {len(backups)}")
    
    # Cria backup de teste
    print("🔄 Criando backup completo...")
    resultado = criar_backup_completo("teste")
    
    if resultado['sucesso']:
        print(f"✅ Backup criado: {resultado['backup_nome']}")
        
        # Lista backups novamente
        backups = listar_backups()
        print(f"📁 Total de backups: {len(backups)}")
        
        # Verifica integridade
        print("🔍 Verificando integridade...")
        integridade = backup_manager.verificar_integridade_backup(resultado['backup_nome'])
        print(f"Integridade: {integridade}")
        
    else:
        print(f"❌ Erro: {resultado['erro']}")
    
    print("✅ Teste de backup concluído!")