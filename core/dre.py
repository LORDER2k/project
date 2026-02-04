"""
Módulo específico para DRE
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class ItemDRE:
    """Item individual da DRE"""
    descricao: str
    valor: float
    percentual_receita: float = 0.0
    categoria: str = ""

class DRE:
    """Classe para gerenciar Demonstração do Resultado do Exercício"""
    
    def __init__(self, empresa: str, periodo: str):
        self.empresa = empresa
        self.periodo = periodo
        self.data_criacao = datetime.now()
        self.itens: List[ItemDRE] = []
        self.resultados = {}
        
    def adicionar_item(self, descricao: str, valor: float, categoria: str = ""):
        """Adiciona um item à DRE"""
        item = ItemDRE(
            descricao=descricao,
            valor=valor,
            categoria=categoria
        )
        self.itens.append(item)
        return item
    
    def calcular(self) -> Dict[str, Any]:
        """Calcula a DRE completa"""
        receita_bruta = self._obter_valor_por_descricao("Receita Bruta")
        
        # Calcula percentuais
        for item in self.itens:
            if receita_bruta > 0:
                item.percentual_receita = (item.valor / receita_bruta) * 100
        
        # Organiza resultados
        self.resultados = {
            'empresa': self.empresa,
            'periodo': self.periodo,
            'data_calculo': self.data_criacao.isoformat(),
            'itens': [item.__dict__ for item in self.itens],
            'total_receitas': sum(item.valor for item in self.itens if item.categoria == 'receita'),
            'total_despesas': sum(item.valor for item in self.itens if item.categoria == 'despesa'),
            'lucro_liquido': 0  # Será calculado
        }
        
        return self.resultados
    
    def _obter_valor_por_descricao(self, descricao: str) -> float:
        """Busca valor por descrição do item"""
        for item in self.itens:
            if item.descricao == descricao:
                return item.valor
        return 0.0
    
    def to_dataframe(self):
        """Converte para pandas DataFrame"""
        import pandas as pd
        
        dados = []
        for item in self.itens:
            dados.append({
                'Descrição': item.descricao,
                'Valor (R$)': item.valor,
                '% Receita': item.percentual_receita,
                'Categoria': item.categoria
            })
        
        return pd.DataFrame(dados)
    
    def gerar_relatorio(self) -> str:
        """Gera relatório textual da DRE"""
        relatorio = []
        relatorio.append(f"DRE - {self.empresa}")
        relatorio.append(f"Período: {self.periodo}")
        relatorio.append("=" * 50)
        
        for item in self.itens:
            linha = f"{item.descricao:30} R$ {item.valor:15,.2f} {item.percentual_receita:6.2f}%"
            relatorio.append(linha)
        
        return "\n".join(relatorio)