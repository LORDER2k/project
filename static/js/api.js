/**
 * api.js - Comunicação com a API de cálculos
 */

class ContabilidadeAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * Calcula DRE
     * @param {Object} dados - Dados para cálculo
     * @returns {Promise} Resultado do cálculo
     */
    async calcularDRE(dados) {
        try {
            console.log('📤 Enviando dados para cálculo DRE:', dados);
            
            const response = await fetch(`${this.baseURL}/api/calcular/dre`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(dados)
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP ${response.status}`);
            }

            const resultado = await response.json();
            
            if (!resultado.sucesso) {
                throw new Error(resultado.erro || 'Erro ao calcular DRE');
            }

            console.log('✅ DRE calculada com sucesso:', resultado);
            return resultado;

        } catch (error) {
            console.error('❌ Erro na API calcularDRE:', error);
            throw error;
        }
    }

    /**
     * Calcula Balanço Patrimonial
     * @param {Object} dados - Dados para cálculo
     * @returns {Promise} Resultado do cálculo
     */
    async calcularBalanco(dados) {
        try {
            const response = await fetch(`${this.baseURL}/api/calcular/balanco`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(dados)
            });

            const resultado = await response.json();
            
            if (!resultado.sucesso) {
                throw new Error(resultado.erro || 'Erro ao calcular Balanço');
            }

            return resultado;

        } catch (error) {
            console.error('Erro na API calcularBalanco:', error);
            throw error;
        }
    }

    /**
     * Obtém dados de exemplo para DRE
     * @returns {Promise} Dados de exemplo
     */
    async obterExemploDRE() {
        try {
            const response = await fetch(`${this.baseURL}/api/exemplo/dre`);
            const resultado = await response.json();
            
            if (!resultado.sucesso) {
                throw new Error('Erro ao obter exemplo DRE');
            }

            return resultado.exemplo;

        } catch (error) {
            console.error('Erro ao obter exemplo DRE:', error);
            throw error;
        }
    }

    /**
     * Obtém dados de exemplo para Balanço
     * @returns {Promise} Dados de exemplo
     */
    async obterExemploBalanco() {
        try {
            const response = await fetch(`${this.baseURL}/api/exemplo/balanco`);
            const resultado = await response.json();
            
            if (!resultado.sucesso) {
                throw new Error('Erro ao obter exemplo Balanço');
            }

            return resultado.exemplo;

        } catch (error) {
            console.error('Erro ao obter exemplo Balanço:', error);
            throw error;
        }
    }

    /**
     * Obtém histórico de cálculos DRE
     * @returns {Promise} Histórico de cálculos
     */
    async obterHistoricoDRE() {
        try {
            const response = await fetch(`${this.baseURL}/api/historico/dre`);
            const resultado = await response.json();
            
            if (!resultado.sucesso) {
                throw new Error('Erro ao obter histórico');
            }

            return resultado.historico;

        } catch (error) {
            console.error('Erro ao obter histórico:', error);
            throw error;
        }
    }

    /**
     * Formata um valor como moeda
     * @param {number} valor - Valor a ser formatado
     * @returns {Promise} Valor formatado
     */
    async formatarMoeda(valor) {
        try {
            const response = await fetch(`${this.baseURL}/api/formatar/moeda`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({ valor: valor })
            });

            const resultado = await response.json();
            
            if (!resultado.sucesso) {
                throw new Error('Erro ao formatar moeda');
            }

            return resultado.formatado;

        } catch (error) {
            console.error('Erro ao formatar moeda:', error);
            throw error;
        }
    }

    /**
     * Verifica se a API está online
     * @returns {Promise} Status da API
     */
    async verificarStatus() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            const resultado = await response.json();
            return resultado.status === 'online';
        } catch (error) {
            console.error('API offline:', error);
            return false;
        }
    }
}

// Instância global da API
const api = new ContabilidadeAPI();

/**
 * Utilitários de formatação frontend (fallback se API offline)
 */
const Formatadores = {
    moeda(valor) {
        try {
            const num = parseFloat(valor) || 0;
            return num.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                minimumFractionDigits: 2
            });
        } catch {
            return 'R$ 0,00';
        }
    },
    
    percentual(valor) {
        try {
            const num = parseFloat(valor) || 0;
            return num.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }) + '%';
        } catch {
            return '0,00%';
        }
    },
    
    numero(valor) {
        try {
            const num = parseFloat(valor) || 0;
            return num.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        } catch {
            return '0,00';
        }
    }
};

export { ContabilidadeAPI, api, Formatadores };