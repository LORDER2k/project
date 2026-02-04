"""
Módulo para armazenar dados em arquivo
"""

import json
import os
from datetime import datetime

class Armazenamento:
    def __init__(self, arquivo="dados_contabilidade.json"):
        self.arquivo = arquivo
        self.dados = self.carregar()
    
    def carregar(self):
        """Carrega dados do arquivo"""
        if os.path.exists(self.arquivo):
            try:
                with open(self.arquivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"empresa": {}, "calculos": [], "despesas": []}
        return {"empresa": {}, "calculos": [], "despesas": []}
    
    def salvar(self):
        """Salva dados no arquivo"""
        try:
            with open(self.arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def adicionar_calculo(self, tipo, valores, resultado):
        """Adiciona um cálculo ao histórico"""
        calculo = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "valores": valores,
            "resultado": resultado
        }
        self.dados["calculos"].append(calculo)
        self.salvar()
        return calculo
    
    def adicionar_despesa(self, nome, valor, categoria):
        """Adiciona uma despesa"""
        despesa = {
            "data": datetime.now().strftime("%Y-%m-%d"),
            "nome": nome,
            "valor": valor,
            "categoria": categoria
        }
        self.dados["despesas"].append(despesa)
        self.salvar()
        return despesa
    
    def get_relatorio_mensal(self, mes, ano):
        """Gera relatório mensal"""
        relatorio = {
            "mes": mes,
            "ano": ano,
            "total_despesas": 0,
            "total_impostos": 0,
            "despesas_por_categoria": {}
        }
        
        # Filtra despesas do mês
        for despesa in self.dados.get("despesas", []):
            if despesa["data"].startswith(f"{ano}-{mes:02d}"):
                relatorio["total_despesas"] += despesa["valor"]
                categoria = despesa.get("categoria", "Outros")
                relatorio["despesas_por_categoria"][categoria] = \
                    relatorio["despesas_por_categoria"].get(categoria, 0) + despesa["valor"]
        
        return relatorio