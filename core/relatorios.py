"""
Módulo de Relatórios Avançados
Autor: Sistema de Contabilidade
"""

import json
import csv
from datetime import datetime
import os

class GeradorRelatorios:
    """Gera relatórios avançados de contabilidade"""
    
    def __init__(self):
        self.data_geracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def gerar_relatorio_tributario(self, resultados_impostos, periodo="mensal"):
        """
        Gera relatório tributário completo
        
        Args:
            resultados_impostos: Lista de resultados de impostos
            periodo: 'mensal', 'trimestral', 'anual'
        
        Returns:
            Dicionário com relatório completo
        """
        print("\n" + "="*60)
        print("📊 GERANDO RELATÓRIO TRIBUTÁRIO")
        print("="*60)
        
        if not resultados_impostos:
            print("⚠️ Nenhum dado para gerar relatório")
            return {}
        
        # Totais
        total_faturamento = sum(r.get('faturamento', 0) for r in resultados_impostos)
        total_impostos = sum(r.get('imposto', 0) for r in resultados_impostos)
        total_liquido = total_faturamento - total_impostos
        
        # Médias
        num_resultados = len(resultados_impostos)
        media_faturamento = total_faturamento / num_resultados if num_resultados > 0 else 0
        media_impostos = total_impostos / num_resultados if num_resultados > 0 else 0
        
        # Análise por faixa
        faixas = {}
        for resultado in resultados_impostos:
            faixa = resultado.get('faixa', 'Desconhecida')
            if faixa not in faixas:
                faixas[faixa] = {'quantidade': 0, 'total_imposto': 0}
            faixas[faixa]['quantidade'] += 1
            faixas[faixa]['total_imposto'] += resultado.get('imposto', 0)
        
        relatorio = {
            'cabecalho': {
                'titulo': f'Relatório Tributário - {periodo.upper()}',
                'data_geracao': self.data_geracao,
                'periodo': periodo,
                'empresa': 'Sua Empresa LTDA'
            },
            'resumo': {
                'total_faturamento': total_faturamento,
                'total_impostos': total_impostos,
                'total_liquido': total_liquido,
                'aliquota_media': (total_impostos / total_faturamento * 100) if total_faturamento > 0 else 0,
                'num_calculos': num_resultados
            },
            'medias': {
                'media_faturamento': media_faturamento,
                'media_impostos': media_impostos,
                'media_liquido': media_faturamento - media_impostos
            },
            'faixas_tributarias': faixas,
            'detalhamento': resultados_impostos
        }
        
        # Exibir relatório
        self._exibir_relatorio_tela(relatorio)
        
        return relatorio
    
    def _exibir_relatorio_tela(self, relatorio):
        """Exibe relatório formatado na tela"""
        cab = relatorio['cabecalho']
        res = relatorio['resumo']
        med = relatorio['medias']
        
        print(f"\n📋 {cab['titulo']}")
        print(f"📅 Gerado em: {cab['data_geracao']}")
        print(f"🏢 Empresa: {cab['empresa']}")
        print(f"📅 Período: {cab['periodo']}")
        
        print("\n" + "-"*50)
        print("📈 RESUMO FINANCEIRO")
        print("-"*50)
        print(f"💰 Faturamento Total: R$ {res['total_faturamento']:,.2f}")
        print(f"🏦 Impostos Totais: R$ {res['total_impostos']:,.2f}")
        print(f"💵 Faturamento Líquido: R$ {res['total_liquido']:,.2f}")
        print(f"📊 Alíquota Média: {res['aliquota_media']:.2f}%")
        print(f"🔢 Número de Cálculos: {res['num_calculos']}")
        
        print("\n" + "-"*50)
        print("📊 MÉDIAS POR CÁLCULO")
        print("-"*50)
        print(f"📈 Média Faturamento: R$ {med['media_faturamento']:,.2f}")
        print(f"🏛️  Média Impostos: R$ {med['media_impostos']:,.2f}")
        print(f"💎 Média Líquido: R$ {med['media_liquido']:,.2f}")
        
        if 'faixas_tributarias' in relatorio:
            print("\n" + "-"*50)
            print("🎯 DISTRIBUIÇÃO POR FAIXA TRIBUTÁRIA")
            print("-"*50)
            for faixa, dados in relatorio['faixas_tributarias'].items():
                print(f"   {faixa}: {dados['quantidade']} cálculos | R$ {dados['total_imposto']:,.2f}")
        
        print("\n" + "="*60)
        print("✅ RELATÓRIO GERADO COM SUCESSO!")
        print("="*60)
    
    def exportar_relatorio_json(self, relatorio, nome_arquivo="relatorio_tributario.json"):
        """Exporta relatório para JSON"""
        try:
            caminho = os.path.join('data', nome_arquivo)
            
            # Criar pasta data se não existir
            os.makedirs('data', exist_ok=True)
            
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Relatório JSON exportado: {caminho}")
            return caminho
        except Exception as e:
            print(f"❌ Erro ao exportar JSON: {e}")
            return None
    
    def exportar_relatorio_csv(self, relatorio, nome_arquivo="relatorio_tributario.csv"):
        """Exporta relatório para CSV"""
        try:
            caminho = os.path.join('data', nome_arquivo)
            os.makedirs('data', exist_ok=True)
            
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow(['RELATÓRIO TRIBUTÁRIO'])
                writer.writerow(['Data Geração', relatorio['cabecalho']['data_geracao']])
                writer.writerow(['Empresa', relatorio['cabecalho']['empresa']])
                writer.writerow(['Período', relatorio['cabecalho']['periodo']])
                writer.writerow([])
                
                # Resumo
                writer.writerow(['RESUMO FINANCEIRO'])
                writer.writerow(['Item', 'Valor (R$)'])
                writer.writerow(['Faturamento Total', relatorio['resumo']['total_faturamento']])
                writer.writerow(['Impostos Totais', relatorio['resumo']['total_impostos']])
                writer.writerow(['Faturamento Líquido', relatorio['resumo']['total_liquido']])
                writer.writerow(['Alíquota Média (%)', relatorio['resumo']['aliquota_media']])
                writer.writerow([])
                
                # Detalhamento
                writer.writerow(['DETALHAMENTO POR CÁLCULO'])
                writer.writerow(['Nº', 'Faturamento', 'Faixa', 'Imposto', 'Líquido'])
                
                for i, calc in enumerate(relatorio.get('detalhamento', []), 1):
                    writer.writerow([
                        i,
                        calc.get('faturamento', 0),
                        calc.get('faixa', ''),
                        calc.get('imposto', 0),
                        calc.get('liquido', 0)
                    ])
            
            print(f"✅ Relatório CSV exportado: {caminho}")
            return caminho
        except Exception as e:
            print(f"❌ Erro ao exportar CSV: {e}")
            return None


class AnaliseFinanceira:
    """Realiza análises financeiras avançadas"""
    
    @staticmethod
    def analisar_rentabilidade(receita_total, despesas_totais, investimento=0):
        """
        Analisa rentabilidade do negócio
        
        Returns:
            Análise completa de rentabilidade
        """
        print("\n" + "="*60)
        print("📈 ANÁLISE DE RENTABILIDADE")
        print("="*60)
        
        lucro_bruto = receita_total - despesas_totais
        
        # Margens
        margem_bruta = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0
        
        # ROI (Return on Investment)
        roi = (lucro_bruto / investimento * 100) if investimento > 0 else 0
        
        # Break-even point
        ponto_equilibrio = despesas_totais / (margem_bruta/100) if margem_bruta > 0 else 0
        
        # Análise
        analise_rentabilidade = ""
        if margem_bruta > 30:
            analise_rentabilidade = "EXCELENTE - Rentabilidade muito alta"
        elif margem_bruta > 20:
            analise_rentabilidade = "BOA - Rentabilidade satisfatória"
        elif margem_bruta > 10:
            analise_rentabilidade = "MODERADA - Rentabilidade aceitável"
        elif margem_bruta > 0:
            analise_rentabilidade = "BAIXA - Necessário melhorar"
        else:
            analise_rentabilidade = "CRÍTICA - Prejuízo operacional"
        
        # Resultado
        resultado = {
            'receita_total': receita_total,
            'despesas_totais': despesas_totais,
            'lucro_bruto': lucro_bruto,
            'margem_bruta': margem_bruta,
            'roi': roi,
            'ponto_equilibrio': ponto_equilibrio,
            'analise': analise_rentabilidade,
            'indicadores': {
                'lucratividade': 'Alta' if margem_bruta > 20 else 'Média' if margem_bruta > 10 else 'Baixa',
                'sustentabilidade': 'Boa' if margem_bruta > despesas_totais/receita_total*100 else 'Regular',
                'crescimento_potencial': 'Alto' if roi > 50 else 'Moderado' if roi > 20 else 'Baixo'
            }
        }
        
        # Exibir análise
        print(f"💰 Receita Total: R$ {receita_total:,.2f}")
        print(f"📉 Despesas Totais: R$ {despesas_totais:,.2f}")
        print(f"💵 Lucro Bruto: R$ {lucro_bruto:,.2f}")
        print(f"📊 Margem Bruta: {margem_bruta:.1f}%")
        
        if investimento > 0:
            print(f"📈 ROI (Retorno sobre Investimento): {roi:.1f}%")
        
        print(f"⚖️  Ponto de Equilíbrio: R$ {ponto_equilibrio:,.2f}")
        print(f"🔍 Análise: {analise_rentabilidade}")
        
        print("\n🎯 INDICADORES:")
        print(f"   Lucratividade: {resultado['indicadores']['lucratividade']}")
        print(f"   Sustentabilidade: {resultado['indicadores']['sustentabilidade']}")
        print(f"   Potencial de Crescimento: {resultado['indicadores']['crescimento_potencial']}")
        
        print("\n" + "="*60)
        
        return resultado


# Teste do módulo
if __name__ == "__main__":
    print("🧪 Testando módulo de relatórios...")
    
    # Dados de exemplo
    resultados_exemplo = [
        {'faturamento': 50000, 'faixa': 'Até R$ 180.000', 'imposto': 3000, 'liquido': 47000},
        {'faturamento': 75000, 'faixa': 'Até R$ 180.000', 'imposto': 4500, 'liquido': 70500},
        {'faturamento': 120000, 'faixa': 'Até R$ 360.000', 'imposto': 13440, 'liquido': 106560}
    ]
    
    # Teste Gerador de Relatórios
    gerador = GeradorRelatorios()
    relatorio = gerador.gerar_relatorio_tributario(resultados_exemplo, "trimestral")
    
    # Exportar relatórios
    gerador.exportar_relatorio_json(relatorio)
    gerador.exportar_relatorio_csv(relatorio)
    
    # Teste Análise Financeira
    print("\n" + "="*60)
    analise = AnaliseFinanceira()
    resultado_analise = analise.analisar_rentabilidade(
        receita_total=200000,
        despesas_totais=120000,
        investimento=50000
    )
    
    print("✅ Teste concluído com sucesso!")