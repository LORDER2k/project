# core/balanco.py - VERSÃO CORRIGIDA
class BalancoPatrimonial:
    def __init__(self, dados_contabeis):
        self.dados = dados_contabeis
        self.empresa = dados_contabeis.empresa
        
    def gerar(self):
        """Gera o balanço patrimonial"""
        if not self.empresa:
            raise ValueError("Empresa não definida nos dados contábeis")
        
        # Coletar saldos
        ativo_circulante = {}
        ativo_nao_circulante = {}
        passivo_circulante = {}
        passivo_nao_circulante = {}
        patrimonio = {}
        
        # Processar contas do plano de contas
        # O plano de contas tem a estrutura: categoria -> subcategoria -> conta_nome -> {info}
        for categoria, subcategorias in self.dados.plano_contas.items():
            if isinstance(subcategorias, dict):
                for subcat, contas in subcategorias.items():
                    if isinstance(contas, dict):
                        for conta_nome, conta_info in contas.items():
                            # Verificar se conta_info é um dicionário
                            if isinstance(conta_info, dict) and 'saldo' in conta_info:
                                saldo = conta_info['saldo']
                                
                                if saldo != 0:
                                    # Classificar a conta
                                    if categoria == 'ativo':
                                        if subcat == 'circulante':
                                            ativo_circulante[conta_nome] = saldo
                                        elif subcat == 'nao_circulante':
                                            ativo_nao_circulante[conta_nome] = saldo
                                    elif categoria == 'passivo':
                                        if subcat == 'circulante':
                                            passivo_circulante[conta_nome] = saldo
                                        elif subcat == 'nao_circulante':
                                            passivo_nao_circulante[conta_nome] = saldo
                                    elif categoria == 'patrimonio':
                                        patrimonio[conta_nome] = saldo
                            else:
                                # Se conta_info for apenas um número (saldo direto)
                                if isinstance(conta_info, (int, float)):
                                    saldo = conta_info
                                    # Classificar a conta (lógica simplificada)
                                    if 'caixa' in conta_nome or 'bancos' in conta_nome:
                                        ativo_circulante[conta_nome] = saldo
        
        # Calcular totais
        total_ativo = sum(ativo_circulante.values()) + sum(ativo_nao_circulante.values())
        total_passivo = sum(passivo_circulante.values()) + sum(passivo_nao_circulante.values())
        total_patrimonio = sum(patrimonio.values())
        
        balanco = {
            'empresa': self.empresa['nome'],
            'periodo': self.empresa['periodo'],
            'ativo': {
                'circulante': ativo_circulante,
                'nao_circulante': ativo_nao_circulante,
                'total': total_ativo
            },
            'passivo': {
                'circulante': passivo_circulante,
                'nao_circulante': passivo_nao_circulante,
                'total': total_passivo
            },
            'patrimonio_liquido': {
                'contas': patrimonio,
                'total': total_patrimonio
            },
            'equilibrio': abs(total_ativo - (total_passivo + total_patrimonio)) < 0.01
        }
        
        return balanco
    
    def imprimir(self):
        """Imprime o balanço patrimonial formatado"""
        try:
            balanco = self.gerar()
        except Exception as e:
            print(f"\n❌ Erro ao gerar balanço: {e}")
            # Tentar método alternativo
            return self.imprimir_simplificado()
        
        print(f"\n{'='*80}")
        print(f"{'BALANÇO PATRIMONIAL':^80}")
        print(f"{'='*80}")
        print(f"Empresa: {balanco['empresa']}")
        print(f"Período: {balanco['periodo']}")
        print(f"{'='*80}")
        
        # ATIVO
        print(f"\n{'ATIVO':<40}{'VALOR (R$)':>40}")
        print(f"{'-'*80}")
        
        print(f"{'  Ativo Circulante':<40}")
        for conta, valor in balanco['ativo']['circulante'].items():
            if valor != 0:
                print(f"    • {conta.capitalize():<36} R$ {valor:>12,.2f}")
        
        print(f"{'  Ativo Não Circulante':<40}")
        for conta, valor in balanco['ativo']['nao_circulante'].items():
            if valor != 0:
                print(f"    • {conta.capitalize():<36} R$ {valor:>12,.2f}")
        
        print(f"{'-'*80}")
        print(f"{'TOTAL DO ATIVO':<40} R$ {balanco['ativo']['total']:>12,.2f}")
        
        # PASSIVO E PATRIMÔNIO
        print(f"\n{'PASSIVO E PATRIMÔNIO LÍQUIDO':<40}{'VALOR (R$)':>40}")
        print(f"{'-'*80}")
        
        print(f"{'  Passivo Circulante':<40}")
        for conta, valor in balanco['passivo']['circulante'].items():
            if valor != 0:
                print(f"    • {conta.capitalize():<36} R$ {valor:>12,.2f}")
        
        print(f"{'  Passivo Não Circulante':<40}")
        for conta, valor in balanco['passivo']['nao_circulante'].items():
            if valor != 0:
                print(f"    • {conta.capitalize():<36} R$ {valor:>12,.2f}")
        
        print(f"{'  Patrimônio Líquido':<40}")
        for conta, valor in balanco['patrimonio_liquido']['contas'].items():
            if valor != 0:
                print(f"    • {conta.capitalize():<36} R$ {valor:>12,.2f}")
        
        print(f"{'-'*80}")
        total_passivo_pl = balanco['passivo']['total'] + balanco['patrimonio_liquido']['total']
        print(f"{'TOTAL PASSIVO + PL':<40} R$ {total_passivo_pl:>12,.2f}")
        
        # VERIFICAÇÃO
        print(f"\n{'='*80}")
        if balanco['equilibrio']:
            print(f"{'✓ EQUILÍBRIO CONTÁBIL VERIFICADO':^80}")
            print(f"{'Ativo = Passivo + Patrimônio Líquido':^80}")
            print(f"R$ {balanco['ativo']['total']:,.2f} = R$ {total_passivo_pl:,.2f}")
        else:
            print(f"{'✗ EQUILÍBRIO NÃO VERIFICADO':^80}")
            diferenca = abs(balanco['ativo']['total'] - total_passivo_pl)
            print(f"{'Diferença: R$':<40} {diferenca:>12,.2f}")
        
        print(f"{'='*80}")
        
        return balanco
    
    def imprimir_simplificado(self):
        """Método simplificado alternativo"""
        print(f"\n{'='*60}")
        print(f"{'BALANÇO PATRIMONIAL SIMPLIFICADO':^60}")
        print(f"{'='*60}")
        print(f"Empresa: {self.empresa['nome']}")
        print(f"Período: {self.empresa['periodo']}")
        
        # Coletar saldos manualmente
        print(f"\n{'Conta':<30} {'Saldo':>20}")
        print(f"{'-'*50}")
        
        # Listar todas as contas com saldo
        for categoria, subcategorias in self.dados.plano_contas.items():
            if isinstance(subcategorias, dict):
                for subcat, contas in subcategorias.items():
                    if isinstance(contas, dict):
                        for conta_nome, conta_info in contas.items():
                            if isinstance(conta_info, dict):
                                saldo = conta_info.get('saldo', 0)
                            elif isinstance(conta_info, (int, float)):
                                saldo = conta_info
                            else:
                                saldo = 0
                            
                            if saldo != 0:
                                print(f"{conta_nome.capitalize():<30} R$ {saldo:>15,.2f}")
        
        print(f"{'='*60}")
        
        return {"status": "balanço simplificado"}