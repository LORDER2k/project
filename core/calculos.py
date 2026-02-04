"""
core/calculos.py - Lógica de cálculo contábil
"""

import json
from datetime import datetime
from typing import Dict, Any, Tuple

class CalculadoraContabil:
    """Classe principal para cálculos contábeis"""
    
    @staticmethod
    def calcular_dre(dados: Dict[str, float]) -> Dict[str, Any]:
        """
        Calcula Demonstração do Resultado do Exercício completa
        
        Args:
            dados: {
                'receita_bruta': float,
                'custo_vendas': float,
                'despesas_operacionais': float,
                'despesas_financeiras': float,
                'outros_rendimentos': float,
                'impostos': float
            }
        
        Returns:
            Dict com todos os resultados formatados
        """
        try:
            # Extrai valores
            rb = float(dados.get('receita_bruta', 0))
            cv = float(dados.get('custo_vendas', 0))
            do = float(dados.get('despesas_operacionais', 0))
            df = float(dados.get('despesas_financeiras', 0))
            ori = float(dados.get('outros_rendimentos', 0))
            imp = float(dados.get('impostos', 0))
            
            # Validações
            if rb < 0:
                raise ValueError("Receita bruta não pode ser negativa")
            
            # Cálculos principais
            lucro_bruto = rb - cv
            lucro_operacional = lucro_bruto - do
            lucro_antes_ir = lucro_operacional - df + ori
            lucro_liquido = lucro_antes_ir - imp
            
            # Margens (em percentual)
            margem_bruta = (lucro_bruto / rb * 100) if rb > 0 else 0
            margem_operacional = (lucro_operacional / rb * 100) if rb > 0 else 0
            margem_liquida = (lucro_liquido / rb * 100) if rb > 0 else 0
            
            # Receita líquida (após deduções)
            deducoes = float(dados.get('deducoes_receita', 0))
            receita_liquida = rb - deducoes
            
            # Análise de resultados
            analise = CalculadoraContabil._analisar_resultados(
                margem_liquida=margem_liquida,
                lucro_liquido=lucro_liquido,
                lucro_bruto=lucro_bruto
            )
            
            # Retorna resultados completos
            return {
                'sucesso': True,
                'dados_entrada': dados,
                'calculos': {
                    'receita_bruta': rb,
                    'receita_liquida': receita_liquida,
                    'lucro_bruto': lucro_bruto,
                    'lucro_operacional': lucro_operacional,
                    'lucro_antes_ir': lucro_antes_ir,
                    'lucro_liquido': lucro_liquido,
                    'margem_bruta': margem_bruta,
                    'margem_operacional': margem_operacional,
                    'margem_liquida': margem_liquida,
                    'data_calculo': datetime.now().isoformat()
                },
                'formatado': {
                    'receita_bruta': CalculadoraContabil._formatar_moeda(rb),
                    'receita_liquida': CalculadoraContabil._formatar_moeda(receita_liquida),
                    'lucro_bruto': CalculadoraContabil._formatar_moeda(lucro_bruto),
                    'lucro_operacional': CalculadoraContabil._formatar_moeda(lucro_operacional),
                    'lucro_antes_ir': CalculadoraContabil._formatar_moeda(lucro_antes_ir),
                    'lucro_liquido': CalculadoraContabil._formatar_moeda(lucro_liquido),
                    'margem_bruta': f"{margem_bruta:.2f}%",
                    'margem_operacional': f"{margem_operacional:.2f}%",
                    'margem_liquida': f"{margem_liquida:.2f}%"
                },
                'analise': analise,
                'tabela_detalhada': CalculadoraContabil._gerar_tabela_dre(dados)
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'mensagem': 'Erro ao calcular DRE'
            }
    
    @staticmethod
    def calcular_balanco(dados: Dict[str, float]) -> Dict[str, Any]:
        """
        Calcula Balanço Patrimonial
        
        Args:
            dados: {
                'ativo_circulante': float,
                'ativo_nao_circulante': float,
                'passivo_circulante': float,
                'passivo_nao_circulante': float,
                'patrimonio_liquido': float
            }
        """
        try:
            # Extrai valores
            ac = float(dados.get('ativo_circulante', 0))
            anc = float(dados.get('ativo_nao_circulante', 0))
            pc = float(dados.get('passivo_circulante', 0))
            pnc = float(dados.get('passivo_nao_circulante', 0))
            pl = float(dados.get('patrimonio_liquido', 0))
            
            # Cálculos
            ativo_total = ac + anc
            passivo_total = pc + pnc
            
            # Equação fundamental
            equilibrio = abs(ativo_total - (passivo_total + pl))
            
            # Indicadores
            liquidez_corrente = ac / pc if pc > 0 else 0
            endividamento_total = (passivo_total / ativo_total * 100) if ativo_total > 0 else 0
            composicao_endividamento = (pc / passivo_total * 100) if passivo_total > 0 else 0
            
            return {
                'sucesso': True,
                'calculos': {
                    'ativo_total': ativo_total,
                    'passivo_total': passivo_total,
                    'patrimonio_liquido': pl,
                    'equilibrio': equilibrio,
                    'liquidez_corrente': liquidez_corrente,
                    'endividamento_total': endividamento_total,
                    'composicao_endividamento': composicao_endividamento
                },
                'formatado': {
                    'ativo_total': CalculadoraContabil._formatar_moeda(ativo_total),
                    'passivo_total': CalculadoraContabil._formatar_moeda(passivo_total),
                    'patrimonio_liquido': CalculadoraContabil._formatar_moeda(pl),
                    'liquidez_corrente': f"{liquidez_corrente:.2f}",
                    'endividamento_total': f"{endividamento_total:.2f}%",
                    'composicao_endividamento': f"{composicao_endividamento:.2f}%"
                }
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    @staticmethod
    def calcular_fluxo_caixa(dados: Dict[str, float]) -> Dict[str, Any]:
        """Calcula Fluxo de Caixa"""
        # Implementação similar...
        pass
    
    # ===== MÉTODOS AUXILIARES =====
    
    @staticmethod
    def _analisar_resultados(margem_liquida: float, lucro_liquido: float, lucro_bruto: float) -> Dict[str, Any]:
        """Analisa os resultados financeiros"""
        analise = {
            'rentabilidade': '',
            'recomendacoes': [],
            'alertas': []
        }
        
        # Análise de rentabilidade
        if margem_liquida > 20:
            analise['rentabilidade'] = 'EXCELENTE'
        elif margem_liquida > 15:
            analise['rentabilidade'] = 'ALTA'
        elif margem_liquida > 10:
            analise['rentabilidade'] = 'MODERADA'
        elif margem_liquida > 5:
            analise['rentabilidade'] = 'BAIXA'
        else:
            analise['rentabilidade'] = 'CRÍTICA'
            analise['alertas'].append('Rentabilidade muito baixa. Recomenda-se revisão de custos e preços.')
        
        # Recomendações baseadas nos resultados
        if lucro_liquido < 0:
            analise['alertas'].append('Prejuízo identificado. Necessário revisão urgente do negócio.')
        
        if lucro_bruto / lucro_liquido > 5 and lucro_liquido > 0:
            analise['recomendacoes'].append('Alta carga tributária. Avalie planejamento tributário.')
        
        return analise
    
    @staticmethod
    def _gerar_tabela_dre(dados: Dict[str, float]) -> list:
        """Gera tabela detalhada da DRE"""
        tabela = [
            {
                'descricao': 'Receita Bruta',
                'valor': dados.get('receita_bruta', 0),
                'tipo': 'receita'
            },
            {
                'descricao': '(-) Deduções da Receita',
                'valor': -dados.get('deducoes_receita', 0),
                'tipo': 'deducao'
            },
            {
                'descricao': 'Receita Líquida',
                'valor': dados.get('receita_bruta', 0) - dados.get('deducoes_receita', 0),
                'tipo': 'total',
                'calculado': True
            },
            {
                'descricao': '(-) Custo das Vendas',
                'valor': -dados.get('custo_vendas', 0),
                'tipo': 'custo'
            },
            {
                'descricao': 'Lucro Bruto',
                'valor': dados.get('receita_bruta', 0) - dados.get('custo_vendas', 0),
                'tipo': 'total',
                'calculado': True
            },
            {
                'descricao': '(-) Despesas Operacionais',
                'valor': -dados.get('despesas_operacionais', 0),
                'tipo': 'despesa'
            },
            {
                'descricao': 'Lucro Operacional',
                'valor': (dados.get('receita_bruta', 0) - dados.get('custo_vendas', 0)) - dados.get('despesas_operacionais', 0),
                'tipo': 'total',
                'calculado': True
            },
            {
                'descricao': '(-) Despesas Financeiras',
                'valor': -dados.get('despesas_financeiras', 0),
                'tipo': 'despesa'
            },
            {
                'descricao': '(+) Outros Rendimentos',
                'valor': dados.get('outros_rendimentos', 0),
                'tipo': 'receita'
            },
            {
                'descricao': 'Lucro Antes do IR',
                'valor': ((dados.get('receita_bruta', 0) - dados.get('custo_vendas', 0)) - 
                         dados.get('despesas_operacionais', 0) - 
                         dados.get('despesas_financeiras', 0) + 
                         dados.get('outros_rendimentos', 0)),
                'tipo': 'total',
                'calculado': True
            },
            {
                'descricao': '(-) Impostos',
                'valor': -dados.get('impostos', 0),
                'tipo': 'imposto'
            },
            {
                'descricao': 'Lucro Líquido',
                'valor': ((dados.get('receita_bruta', 0) - dados.get('custo_vendas', 0)) - 
                         dados.get('despesas_operacionais', 0) - 
                         dados.get('despesas_financeiras', 0) + 
                         dados.get('outros_rendimentos', 0) - 
                         dados.get('impostos', 0)),
                'tipo': 'total-final',
                'calculado': True,
                'destaque': True
            }
        ]
        
        # Formata valores
        for item in tabela:
            item['valor_formatado'] = CalculadoraContabil._formatar_moeda(abs(item['valor']))
            if item['valor'] < 0:
                item['valor_formatado'] = f"({item['valor_formatado']})"
        
        return tabela
    
    @staticmethod
    def _formatar_moeda(valor: float) -> str:
        """Formata valor como moeda brasileira"""
        try:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return "R$ 0,00"
    
    @staticmethod
    def _formatar_percentual(valor: float) -> str:
        """Formata valor como percentual"""
        try:
            return f"{valor:.2f}%"
        except:
            return "0.00%"

# Funções de conveniência para importação direta
def calcular_dre(dados: Dict[str, float]) -> Dict[str, Any]:
    return CalculadoraContabil.calcular_dre(dados)

def calcular_balanco(dados: Dict[str, float]) -> Dict[str, Any]:
    return CalculadoraContabil.calcular_balanco(dados)

def formatar_moeda(valor: float) -> str:
    return CalculadoraContabil._formatar_moeda(valor)

def formatar_percentual(valor: float) -> str:
    return CalculadoraContabil._formatar_percentual(valor)