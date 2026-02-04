"""
Módulo para exportação de dados
Autor: Sistema de Contabilidade
"""

import csv
import json
import os
from datetime import datetime


class ExportadorCSV:
    """Classe para exportar dados para CSV"""
    
    @staticmethod
    def exportar_calculos(lista_calculos, nome_arquivo="calculos_exportados.csv"):
        """
        Exporta lista de cálculos para CSV
        
        Args:
            lista_calculos: Lista de dicionários com cálculos
            nome_arquivo: Nome do arquivo CSV de saída
        
        Returns:
            Caminho do arquivo criado ou None em caso de erro
        """
        if not lista_calculos:
            return None
        
        try:
            # Define o caminho completo
            caminho_completo = os.path.join("web", "data", nome_arquivo)
            
            # Garante que a pasta existe
            os.makedirs(os.path.dirname(caminho_completo), exist_ok=True)
            
            # Extrai cabeçalhos do primeiro dicionário
            cabecalhos = lista_calculos[0].keys()
            
            with open(caminho_completo, 'w', newline='', encoding='utf-8') as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
                writer.writeheader()
                writer.writerows(lista_calculos)
            
            print(f"✅ CSV exportado com sucesso: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao exportar CSV: {e}")
            return None
    
    @staticmethod
    def exportar_despesas(despesas, nome_arquivo="despesas_exportadas.csv"):
        """
        Exporta lista de despesas para CSV
        
        Args:
            despesas: Lista de dicionários com despesas
            nome_arquivo: Nome do arquivo CSV de saída
        
        Returns:
            Caminho do arquivo criado
        """
        if not despesas:
            return None
        
        try:
            # Formata os dados para CSV
            dados_formatados = []
            for despesa in despesas:
                dados_formatados.append({
                    'Data': despesa.get('data', datetime.now().strftime('%Y-%m-%d')),
                    'Descrição': despesa.get('descricao', despesa.get('nome', 'Despesa')),
                    'Valor (R$)': f"{despesa.get('valor', 0):,.2f}",
                    'Categoria': despesa.get('categoria', 'Outros'),
                    'Forma de Pagamento': despesa.get('forma_pagamento', 'Não informado'),
                    'Centro de Custo': despesa.get('centro_custo', 'Geral')
                })
            
            caminho_completo = os.path.join("web", "data", nome_arquivo)
            os.makedirs(os.path.dirname(caminho_completo), exist_ok=True)
            
            cabecalhos = ['Data', 'Descrição', 'Valor (R$)', 'Categoria', 
                         'Forma de Pagamento', 'Centro de Custo']
            
            with open(caminho_completo, 'w', newline='', encoding='utf-8') as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
                writer.writeheader()
                writer.writerows(dados_formatados)
            
            print(f"✅ Despesas exportadas: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao exportar despesas: {e}")
            return None
    
    @staticmethod
    def exportar_impostos(resultado_impostos, nome_arquivo="impostos_calculados.csv"):
        """
        Exporta resultado de cálculos de impostos para CSV
        
        Args:
            resultado_impostos: Dicionário com resultado dos impostos
            nome_arquivo: Nome do arquivo CSV de saída
        
        Returns:
            Caminho do arquivo criado
        """
        try:
            # Prepara dados para exportação
            dados = []
            
            if 'faturamento' in resultado_impostos:
                # É um cálculo de Simples Nacional
                dados.append({
                    'Tipo': 'Simples Nacional',
                    'Faturamento (R$)': f"{resultado_impostos.get('faturamento', 0):,.2f}",
                    'Faixa': resultado_impostos.get('faixa', 'N/A'),
                    'Alíquota (%)': f"{resultado_impostos.get('aliquota', 0)*100:.2f}",
                    'Imposto (R$)': f"{resultado_impostos.get('imposto', 0):,.2f}",
                    'Líquido (R$)': f"{resultado_impostos.get('liquido', 0):,.2f}",
                    'Data Cálculo': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            elif 'salario_bruto' in resultado_impostos:
                # É um cálculo de INSS
                dados.append({
                    'Tipo': 'INSS',
                    'Salário Bruto (R$)': f"{resultado_impostos.get('salario_bruto', 0):,.2f}",
                    'Alíquota (%)': f"{resultado_impostos.get('aliquota', 0)*100:.2f}",
                    'INSS (R$)': f"{resultado_impostos.get('inss', 0):,.2f}",
                    'Salário Líquido (R$)': f"{resultado_impostos.get('salario_liquido', 0):,.2f}",
                    'Data Cálculo': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            if not dados:
                return None
            
            caminho_completo = os.path.join("web", "data", nome_arquivo)
            os.makedirs(os.path.dirname(caminho_completo), exist_ok=True)
            
            cabecalhos = dados[0].keys()
            
            with open(caminho_completo, 'w', newline='', encoding='utf-8') as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
                writer.writeheader()
                writer.writerows(dados)
            
            print(f"✅ Impostos exportados: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao exportar impostos: {e}")
            return None
    
    @staticmethod
    def gerar_csv_lucro(resultado_lucro, nome_arquivo="analise_lucro.csv"):
        """
        Gera CSV com análise completa de lucro
        
        Args:
            resultado_lucro: Dicionário com resultado do cálculo de lucro
            nome_arquivo: Nome do arquivo CSV de saída
        
        Returns:
            Caminho do arquivo criado
        """
        try:
            dados = []
            
            # Dados principais
            dados.append({
                'Item': 'Receita Total',
                'Valor (R$)': f"{resultado_lucro.get('receita', 0):,.2f}",
                'Percentual': '100%'
            })
            
            dados.append({
                'Item': 'Total Despesas',
                'Valor (R$)': f"{resultado_lucro.get('despesas', 0):,.2f}",
                'Percentual': f"{resultado_lucro.get('despesas', 0)/resultado_lucro.get('receita', 1)*100:.1f}%"
            })
            
            dados.append({
                'Item': 'Lucro Bruto',
                'Valor (R$)': f"{resultado_lucro.get('lucro_bruto', 0):,.2f}",
                'Percentual': f"{resultado_lucro.get('margens', {}).get('bruta', 0):.1f}%"
            })
            
            # Impostos
            impostos = resultado_lucro.get('impostos', {})
            if impostos:
                dados.append({
                    'Item': 'IRPJ (15%)',
                    'Valor (R$)': f"{impostos.get('irpj', 0):,.2f}",
                    'Percentual': ''
                })
                
                dados.append({
                    'Item': 'CSLL (9%)',
                    'Valor (R$)': f"{impostos.get('csll', 0):,.2f}",
                    'Percentual': ''
                })
            
            dados.append({
                'Item': 'Lucro Líquido',
                'Valor (R$)': f"{resultado_lucro.get('lucro_liquido', 0):,.2f}",
                'Percentual': f"{resultado_lucro.get('margens', {}).get('liquida', 0):.1f}%"
            })
            
            caminho_completo = os.path.join("web", "data", nome_arquivo)
            os.makedirs(os.path.dirname(caminho_completo), exist_ok=True)
            
            cabecalhos = ['Item', 'Valor (R$)', 'Percentual']
            
            with open(caminho_completo, 'w', newline='', encoding='utf-8') as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=cabecalhos)
                writer.writeheader()
                writer.writerows(dados)
            
            print(f"✅ Análise de lucro exportada: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao gerar CSV de lucro: {e}")
            return None


class GerenciadorDownloads:
    """Gerencia download de arquivos exportados"""
    
    @staticmethod
    def listar_arquivos_disponiveis():
        """Lista todos os arquivos disponíveis para download"""
        try:
            pasta_dados = os.path.join("web", "data")
            if not os.path.exists(pasta_dados):
                return []
            
            arquivos = []
            for arquivo in os.listdir(pasta_dados):
                if arquivo.endswith('.csv'):
                    caminho = os.path.join(pasta_dados, arquivo)
                    tamanho = os.path.getsize(caminho)
                    data_modificacao = datetime.fromtimestamp(
                        os.path.getmtime(caminho)
                    ).strftime('%d/%m/%Y %H:%M')
                    
                    arquivos.append({
                        'nome': arquivo,
                        'caminho': caminho,
                        'tamanho': f"{tamanho/1024:.1f} KB",
                        'data_modificacao': data_modificacao,
                        'tipo': 'CSV'
                    })
            
            return arquivos
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return []
    
    @staticmethod
    def limpar_arquivos_antigos(dias=7):
        """Remove arquivos mais antigos que X dias"""
        try:
            pasta_dados = os.path.join("web", "data")
            if not os.path.exists(pasta_dados):
                return 0
            
            removidos = 0
            agora = datetime.now()
            
            for arquivo in os.listdir(pasta_dados):
                if arquivo.endswith('.csv'):
                    caminho = os.path.join(pasta_dados, arquivo)
                    idade = agora - datetime.fromtimestamp(os.path.getmtime(caminho))
                    
                    if idade.days > dias:
                        os.remove(caminho)
                        removidos += 1
                        print(f"🗑️  Arquivo removido: {arquivo}")
            
            return removidos
        except Exception as e:
            print(f"❌ Erro ao limpar arquivos: {e}")
            return 0


# Teste rápido do módulo
if __name__ == "__main__":
    print("🧪 Testando módulo de exportação...")
    
    # Teste 1: Exportar dados de exemplo
    dados_teste = [
        {'id': 1, 'nome': 'Teste 1', 'valor': 100.50},
        {'id': 2, 'nome': 'Teste 2', 'valor': 200.75},
        {'id': 3, 'nome': 'Teste 3', 'valor': 300.25}
    ]
    
    exportador = ExportadorCSV()
    caminho = exportador.exportar_calculos(dados_teste, "teste_exportacao.csv")
    
    if caminho:
        print(f"✅ Teste 1 OK - Arquivo criado: {caminho}")
    else:
        print("❌ Teste 1 FALHOU")
    
    # Teste 2: Listar arquivos
    gerenciador = GerenciadorDownloads()
    arquivos = gerenciador.listar_arquivos_disponiveis()
    print(f"\n📁 Arquivos disponíveis: {len(arquivos)}")
    
    for arquivo in arquivos:
        print(f"  - {arquivo['nome']} ({arquivo['tamanho']})")