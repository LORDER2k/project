/**
 * dre.js - Interface para cálculo de DRE
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do formulário
    const formDRE = document.getElementById('form-dre');
    const btnCalcular = document.getElementById('btn-calcular');
    const btnExemplo = document.getElementById('btn-exemplo');
    const btnLimpar = document.getElementById('btn-limpar');
    const loading = document.getElementById('loading');
    const resultadoContainer = document.getElementById('resultado-container');
    
    // Elementos de resultado
    const resultados = {
        receitaBruta: document.getElementById('result-receita-bruta'),
        receitaLiquida: document.getElementById('result-receita-liquida'),
        lucroBruto: document.getElementById('result-lucro-bruto'),
        lucroOperacional: document.getElementById('result-lucro-operacional'),
        lucroAntesIR: document.getElementById('result-lucro-antes-ir'),
        lucroLiquido: document.getElementById('result-lucro-liquido'),
        margemBruta: document.getElementById('result-margem-bruta'),
        margemOperacional: document.getElementById('result-margem-operacional'),
        margemLiquida: document.getElementById('result-margem-liquida')
    };
    
    // Tabela de detalhes
    const tabelaDetalhes = document.getElementById('tabela-detalhes-dre');
    const analiseContainer = document.getElementById('analise-container');
    
    // Inicialização
    inicializarEventos();
    verificarConexaoAPI();
    
    /**
     * Configura eventos dos elementos
     */
    function inicializarEventos() {
        if (btnCalcular) {
            btnCalcular.addEventListener('click', calcularDRE);
        }
        
        if (btnExemplo) {
            btnExemplo.addEventListener('click', carregarExemplo);
        }
        
        if (btnLimpar) {
            btnLimpar.addEventListener('click', limparFormulario);
        }
        
        if (formDRE) {
            formDRE.addEventListener('submit', function(e) {
                e.preventDefault();
                calcularDRE();
            });
        }
        
        // Auto-calculo em tempo real para alguns campos
        const camposAutoCalc = ['receita_bruta', 'custo_vendas', 'despesas_operacionais'];
        camposAutoCalc.forEach(campoId => {
            const campo = document.getElementById(campoId);
            if (campo) {
                campo.addEventListener('blur', atualizarPrevia);
            }
        });
    }
    
    /**
     * Verifica se a API está online
     */
    async function verificarConexaoAPI() {
        try {
            const online = await api.verificarStatus();
            const statusIndicator = document.getElementById('api-status');
            
            if (statusIndicator) {
                statusIndicator.textContent = online ? '✅ Online' : '❌ Offline';
                statusIndicator.className = online ? 'badge bg-success' : 'badge bg-danger';
            }
            
            return online;
        } catch (error) {
            console.warn('Não foi possível verificar status da API');
            return false;
        }
    }
    
    /**
     * Calcula DRE usando a API
     */
    async function calcularDRE() {
        try {
            // Validação básica
            if (!validarFormulario()) {
                return;
            }
            
            // Mostra loading
            mostrarLoading(true);
            limparResultados();
            
            // Coleta dados do formulário
            const dados = coletarDadosFormulario();
            
            // Envia para API
            const resultado = await api.calcularDRE(dados);
            
            // Exibe resultados
            exibirResultados(resultado);
            
        } catch (error) {
            console.error('Erro no cálculo:', error);
            mostrarErro(error.message || 'Erro ao calcular DRE');
            
        } finally {
            mostrarLoading(false);
        }
    }
    
    /**
     * Coleta dados do formulário
     */
    function coletarDadosFormulario() {
        const dados = {};
        const campos = [
            'receita_bruta',
            'deducoes_receita',
            'custo_vendas',
            'despesas_operacionais',
            'despesas_financeiras',
            'outros_rendimentos',
            'impostos'
        ];
        
        campos.forEach(campo => {
            const elemento = document.getElementById(campo);
            if (elemento) {
                dados[campo] = elemento.value || '0';
            }
        });
        
        return dados;
    }
    
    /**
     * Valida dados do formulário
     */
    function validarFormulario() {
        const receitaBruta = document.getElementById('receita_bruta');
        
        if (!receitaBruta || !receitaBruta.value) {
            mostrarErro('Informe a Receita Bruta');
            receitaBruta?.focus();
            return false;
        }
        
        if (parseFloat(receitaBruta.value) < 0) {
            mostrarErro('Receita Bruta não pode ser negativa');
            receitaBruta.focus();
            return false;
        }
        
        return true;
    }
    
    /**
     * Exibe resultados na interface
     */
    function exibirResultados(resultado) {
        // Mostra container de resultados
        if (resultadoContainer) {
            resultadoContainer.style.display = 'block';
            resultadoContainer.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Preenche valores principais
        for (const [chave, elemento] of Object.entries(resultados)) {
            if (elemento && resultado.formatado) {
                const valor = resultado.formatado[chave] || resultado.calculos?.[chave] || 'N/A';
                elemento.textContent = valor;
                
                // Destaca lucro líquido
                if (chave === 'lucroLiquido') {
                    const valorNumerico = resultado.calculos?.[chave] || 0;
                    elemento.parentElement.className = valorNumerico >= 0 
                        ? 'alert alert-success' 
                        : 'alert alert-danger';
                }
            }
        }
        
        // Preenche tabela de detalhes
        if (tabelaDetalhes && resultado.tabela_detalhada) {
            preencherTabelaDetalhes(resultado.tabela_detalhada);
        }
        
        // Exibe análise
        if (analiseContainer && resultado.analise) {
            exibirAnalise(resultado.analise);
        }
        
        // Salva nos cookies/localStorage para histórico
        salvarNoHistorico(resultado);
    }
    
    /**
     * Preenche tabela de detalhes da DRE
     */
    function preencherTabelaDetalhes(tabelaDados) {
        if (!tabelaDetalhes) return;
        
        const tbody = tabelaDetalhes.querySelector('tbody');
        if (!tbody) return;
        
        // Limpa tabela existente
        tbody.innerHTML = '';
        
        // Adiciona linhas
        tabelaDados.forEach(item => {
            const tr = document.createElement('tr');
            
            // Classe baseada no tipo
            if (item.tipo === 'total' || item.tipo === 'total-final') {
                tr.className = 'table-active fw-bold';
            }
            if (item.tipo === 'total-final') {
                tr.className += ' table-success';
            }
            
            // Coluna descrição
            const tdDesc = document.createElement('td');
            tdDesc.textContent = item.descricao;
            if (item.calculado) {
                tdDesc.style.fontStyle = 'italic';
            }
            
            // Coluna valor
            const tdValor = document.createElement('td');
            tdValor.className = 'text-end';
            tdValor.textContent = item.valor_formatado || Formatadores.moeda(item.valor);
            
            // Destaque para valores negativos
            if (item.valor < 0 && item.tipo !== 'total-final') {
                tdValor.className += ' text-danger';
            }
            
            tr.appendChild(tdDesc);
            tr.appendChild(tdValor);
            tbody.appendChild(tr);
        });
    }
    
    /**
     * Exibe análise dos resultados
     */
    function exibirAnalise(analise) {
        if (!analiseContainer) return;
        
        let html = `
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">📊 Análise dos Resultados</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <h6>Rentabilidade: 
                            <span class="badge ${getClasseRentabilidade(analise.rentabilidade)}">
                                ${analise.rentabilidade}
                            </span>
                        </h6>
                    </div>
        `;
        
        // Alertas
        if (analise.alertas && analise.alertas.length > 0) {
            html += `
                <div class="alert alert-warning">
                    <h6>⚠️ Alertas:</h6>
                    <ul class="mb-0">
                        ${analise.alertes.map(alerta => `<li>${alerta}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Recomendações
        if (analise.recomendacoes && analise.recomendacoes.length > 0) {
            html += `
                <div class="alert alert-info">
                    <h6>💡 Recomendações:</h6>
                    <ul class="mb-0">
                        ${analise.recomendacoes.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        html += `</div></div>`;
        analiseContainer.innerHTML = html;
    }
    
    /**
     * Retorna classe CSS baseada na rentabilidade
     */
    function getClasseRentabilidade(nivel) {
        const classes = {
            'EXCELENTE': 'bg-success',
            'ALTA': 'bg-primary',
            'MODERADA': 'bg-info',
            'BAIXA': 'bg-warning',
            'CRÍTICA': 'bg-danger'
        };
        return classes[nivel] || 'bg-secondary';
    }
    
    /**
     * Carrega dados de exemplo
     */
    async function carregarExemplo() {
        try {
            const exemplo = await api.obterExemploDRE();
            
            // Preenche campos com valores de exemplo
            for (const [campo, valor] of Object.entries(exemplo)) {
                const elemento = document.getElementById(campo);
                if (elemento) {
                    elemento.value = valor;
                }
            }
            
            // Mostra mensagem
            mostrarMensagem('✅ Dados de exemplo carregados! Clique em "Calcular" para ver os resultados.', 'success');
            
        } catch (error) {
            console.error('Erro ao carregar exemplo:', error);
            mostrarErro('Não foi possível carregar os dados de exemplo');
        }
    }
    
    /**
     * Limpa formulário e resultados
     */
    function limparFormulario() {
        // Limpa campos
        const campos = formDRE.querySelectorAll('input[type="number"], input[type="text"]');
        campos.forEach(campo => campo.value = '');
        
        // Limpa resultados
        limparResultados();
        
        // Esconde container
        if (resultadoContainer) {
            resultadoContainer.style.display = 'none';
        }
        
        // Foca no primeiro campo
        document.getElementById('receita_bruta')?.focus();
        
        mostrarMensagem('Formulário limpo com sucesso!', 'info');
    }
    
    /**
     * Limpa exibição de resultados
     */
    function limparResultados() {
        // Limpa valores
        for (const elemento of Object.values(resultados)) {
            if (elemento) elemento.textContent = 'R$ 0,00';
        }
        
        // Limpa tabela
        if (tabelaDetalhes) {
            const tbody = tabelaDetalhes.querySelector('tbody');
            if (tbody) tbody.innerHTML = '';
        }
        
        // Limpa análise
        if (analiseContainer) {
            analiseContainer.innerHTML = '';
        }
    }
    
    /**
     * Atualiza prévia rápida
     */
    function atualizarPrevia() {
        // Implementação opcional para cálculo rápido no frontend
    }
    
    /**
     * Salva cálculo no histórico local
     */
    function salvarNoHistorico(resultado) {
        try {
            const historico = JSON.parse(localStorage.getItem('historico_dre') || '[]');
            
            historico.unshift({
                data: new Date().toISOString(),
                lucro_liquido: resultado.calculos?.lucro_liquido || 0,
                margem_liquida: resultado.calculos?.margem_liquida || 0
            });
            
            // Mantém apenas últimos 20
            if (historico.length > 20) {
                historico.pop();
            }
            
            localStorage.setItem('historico_dre', JSON.stringify(historico));
            
        } catch (error) {
            console.warn('Não foi possível salvar histórico:', error);
        }
    }
    
    /**
     * Mostra/oculta indicador de loading
     */
    function mostrarLoading(mostrar) {
        if (loading) {
            loading.style.display = mostrar ? 'block' : 'none';
        }
        
        if (btnCalcular) {
            btnCalcular.disabled = mostrar;
            btnCalcular.innerHTML = mostrar 
                ? '<span class="spinner-border spinner-border-sm" role="status"></span> Calculando...'
                : '<i class="fas fa-calculator"></i> Calcular DRE';
        }
    }
    
    /**
     * Mostra mensagem de erro
     */
    function mostrarErro(mensagem) {
        mostrarMensagem(`❌ ${mensagem}`, 'danger');
    }
    
    /**
     * Mostra mensagem genérica
     */
    function mostrarMensagem(mensagem, tipo = 'info') {
        // Remove mensagens anteriores
        const mensagensAntigas = document.querySelectorAll('.mensagem-flutuante');
        mensagensAntigas.forEach(msg => msg.remove());
        
        // Cria nova mensagem
        const div = document.createElement('div');
        div.className = `mensagem-flutuante alert alert-${tipo} alert-dismissible fade show`;
        div.innerHTML = `
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Estilos
        div.style.position = 'fixed';
        div.style.top = '20px';
        div.style.right = '20px';
        div.style.zIndex = '9999';
        div.style.minWidth = '300px';
        div.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        
        document.body.appendChild(div);
        
        // Remove automaticamente após 5 segundos
        setTimeout(() => {
            if (div.parentNode) {
                div.classList.remove('show');
                setTimeout(() => div.remove(), 300);
            }
        }, 5000);
    }
});