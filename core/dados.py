# core/dados.py - VERSÃO COMPLETA CORRIGIDA
class DadosContabeis:
    def __init__(self):
        self.empresa = None
        self.transacoes = []
        self.plano_contas = {}
        self.saldos = {}
        self.definir_plano_contas_padrao()
    
    def definir_empresa(self, nome, cnpj, periodo):
        """Define os dados da empresa"""
        self.empresa = {
            'nome': nome,
            'cnpj': cnpj,
            'periodo': periodo
        }
        return self.empresa
    
    def definir_plano_contas_padrao(self):
        """Define um plano de contas padrão"""
        self.plano_contas = {
            # ATIVO
            'ativo': {
                'circulante': {
                    'caixa': {'tipo': 'devedor', 'saldo': 0.0},
                    'bancos': {'tipo': 'devedor', 'saldo': 0.0},
                    'clientes': {'tipo': 'devedor', 'saldo': 0.0},
                    'estoques': {'tipo': 'devedor', 'saldo': 0.0}
                },
                'nao_circulante': {
                    'imoveis': {'tipo': 'devedor', 'saldo': 0.0},
                    'veiculos': {'tipo': 'devedor', 'saldo': 0.0},
                    'equipamentos': {'tipo': 'devedor', 'saldo': 0.0}
                }
            },
            
            # PASSIVO
            'passivo': {
                'circulante': {
                    'fornecedores': {'tipo': 'credor', 'saldo': 0.0},
                    'emprestimos_cp': {'tipo': 'credor', 'saldo': 0.0},
                    'salarios_pagar': {'tipo': 'credor', 'saldo': 0.0}
                },
                'nao_circulante': {
                    'emprestimos_lp': {'tipo': 'credor', 'saldo': 0.0},
                    'financiamentos': {'tipo': 'credor', 'saldo': 0.0}
                }
            },
            
            # PATRIMÔNIO LÍQUIDO
            'patrimonio': {
                'capital_social': {'tipo': 'credor', 'saldo': 0.0},
                'lucros_acumulados': {'tipo': 'credor', 'saldo': 0.0},
                'reservas': {'tipo': 'credor', 'saldo': 0.0}
            },
            
            # RECEITAS
            'receitas': {
                'vendas': {'tipo': 'credor', 'saldo': 0.0},
                'servicos': {'tipo': 'credor', 'saldo': 0.0},
                'juros_recebidos': {'tipo': 'credor', 'saldo': 0.0}
            },
            
            # DESPESAS
            'despesas': {
                'cmv': {'tipo': 'devedor', 'saldo': 0.0},
                'salarios': {'tipo': 'devedor', 'saldo': 0.0},
                'aluguel': {'tipo': 'devedor', 'saldo': 0.0},
                'energia': {'tipo': 'devedor', 'saldo': 0.0},
                'telefone': {'tipo': 'devedor', 'saldo': 0.0},
                'manutencao': {'tipo': 'devedor', 'saldo': 0.0}
            }
        }
    
    def registrar_transacao(self, data, descricao, conta_debito, conta_credito, valor):
        """Registra uma transação contábil"""
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
        
        transacao = {
            'id': len(self.transacoes) + 1,
            'data': data,
            'descricao': descricao,
            'debito': conta_debito,
            'credito': conta_credito,
            'valor': float(valor)  # Garantir que seja float
        }
        
        self.transacoes.append(transacao)
        self.atualizar_saldos(conta_debito, conta_credito, float(valor))
        
        return transacao
    
    def atualizar_saldos(self, conta_debito, conta_credito, valor):
        """Atualiza os saldos das contas após uma transação"""
        valor = float(valor)
        
        # Encontrar a conta de débito
        for categoria in self.plano_contas.values():
            for subcategoria in categoria.values():
                if conta_debito in subcategoria:
                    conta = subcategoria[conta_debito]
                    if conta['tipo'] == 'devedor':
                        conta['saldo'] += valor
                    else:
                        conta['saldo'] -= valor
                
                if conta_credito in subcategoria:
                    conta = subcategoria[conta_credito]
                    if conta['tipo'] == 'credor':
                        conta['saldo'] += valor
                    else:
                        conta['saldo'] -= valor
    
    def obter_saldo_conta(self, conta_nome):
        """Obtém o saldo de uma conta específica"""
        for categoria in self.plano_contas.values():
            for subcategoria in categoria.values():
                if conta_nome in subcategoria:
                    saldo = subcategoria[conta_nome]['saldo']
                    return float(saldo) if saldo is not None else 0.0
        return 0.0
    
    def listar_transacoes(self):
        """Lista todas as transações"""
        if not self.transacoes:
            print("Nenhuma transação registrada.")
            return
        
        print(f"\n{'='*80}")
        print(f"{'TRANSAÇÕES CONTÁBEIS':^80}")
        print(f"{'='*80}")
        print(f"{'ID':<5} {'Data':<12} {'Descrição':<25} {'Débito':<15} {'Crédito':<15} {'Valor':>10}")
        print(f"{'-'*80}")
        
        for transacao in self.transacoes:
            print(f"{transacao['id']:<5} {transacao['data']:<12} {transacao['descricao'][:23]:<25} "
                  f"{transacao['debito'][:13]:<15} {transacao['credito'][:13]:<15} "
                  f"R$ {transacao['valor']:>8,.2f}")
    
    def listar_saldos(self):
        """Lista todos os saldos das contas"""
        print(f"\n{'='*60}")
        print(f"{'SALDOS DAS CONTAS':^60}")
        print(f"{'='*60}")
        print(f"{'Conta':<30} {'Tipo':<10} {'Saldo':>20}")
        print(f"{'-'*60}")
        
        for categoria, subcategorias in self.plano_contas.items():
            print(f"\n{categoria.upper()}:")
            for subcat, contas in subcategorias.items():
                if isinstance(contas, dict):
                    for conta_nome, conta_info in contas.items():
                        if isinstance(conta_info, dict):
                            tipo = conta_info.get('tipo', 'N/A')
                            saldo = conta_info.get('saldo', 0.0)
                        else:
                            tipo = 'N/A'
                            saldo = conta_info
                        
                        # Garantir que saldo seja número
                        try:
                            saldo_num = float(saldo)
                            print(f"  {conta_nome:<28} {tipo:<10} R$ {saldo_num:>15,.2f}")
                        except (ValueError, TypeError):
                            # Se não for número, mostrar como está
                            print(f"  {conta_nome:<28} {tipo:<10} R$ {str(saldo):>15}")
        
        print(f"{'='*60}")
    
    def exportar_transacoes_csv(self, arquivo='transacoes.csv'):
        """Exporta transações para CSV"""
        import csv
        
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Data', 'Descrição', 'Débito', 'Crédito', 'Valor'])
            
            for t in self.transacoes:
                writer.writerow([t['id'], t['data'], t['descricao'], 
                               t['debito'], t['credito'], t['valor']])
        
        return f"Transações exportadas para {arquivo}"