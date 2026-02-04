// Futuristic UI - Interface Futurista Neon

class FuturisticUI {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'dark';
        this.effectsEnabled = localStorage.getItem('effectsEnabled') !== 'false';
        this.particlesCount = 50;
        this.init();
    }
    
    init() {
        this.applyTheme();
        this.setupEventListeners();
        this.initParticles();
        this.initGlowEffects();
    }
    
    // Aplicar tema
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        
        // Atualizar botão de tema
        const themeBtn = document.querySelector('[onclick="toggleTheme()"]');
        if (themeBtn) {
            const icon = this.theme === 'dark' ? 'fa-moon' : 'fa-sun';
            themeBtn.innerHTML = `<i class="fas ${icon}"></i> Tema`;
        }
    }
    
    // Alternar tema
    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
        this.showNotification(`Tema alterado para ${this.theme === 'dark' ? 'Escuro' : 'Claro'}`);
    }
    
    // Alternar efeitos
    toggleEffects() {
        this.effectsEnabled = !this.effectsEnabled;
        localStorage.setItem('effectsEnabled', this.effectsEnabled);
        
        const effects = document.querySelectorAll('.particles, .scanline, .holographic-grid');
        effects.forEach(effect => {
            effect.style.display = this.effectsEnabled ? 'block' : 'none';
        });
        
        this.showNotification(`Efeitos ${this.effectsEnabled ? 'ativados' : 'desativados'}`);
    }
    
    // Inicializar partículas
    initParticles() {
        if (!this.effectsEnabled) return;
        
        const container = document.getElementById('particles');
        if (!container) return;
        
        // Limpar partículas existentes
        container.innerHTML = '';
        
        // Gerar novas partículas
        for (let i = 0; i < this.particlesCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Posição aleatória
            const left = Math.random() * 100;
            const delay = Math.random() * 20;
            const duration = 15 + Math.random() * 15;
            const size = 1 + Math.random() * 3;
            
            // Aplicar estilos
            particle.style.left = `${left}%`;
            particle.style.animationDelay = `${delay}s`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            // Cor aleatória
            const colors = ['#00f3ff', '#b967ff', '#00ff9d', '#ff00ff'];
            const color = colors[Math.floor(Math.random() * colors.length)];
            particle.style.background = color;
            particle.style.boxShadow = `0 0 ${size * 3}px ${color}`;
            
            container.appendChild(particle);
        }
    }
    
    // Efeitos de brilho
    initGlowEffects() {
        // Adicionar hover glow a elementos com classe glow-hover
        document.querySelectorAll('.glow-hover').forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transition = 'all 0.3s ease';
            });
        });
    }
    
    // Notificações futuristas
    showNotification(message, type = 'info') {
        const container = document.createElement('div');
        container.className = `neon-notification notification-${type}`;
        
        // Ícone baseado no tipo
        const icons = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle'
        };
        
        container.innerHTML = `
            <div class="notification-content glass-card">
                <i class="fas ${icons[type] || icons.info} me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(container);
        
        // Animar entrada
        setTimeout(() => {
            container.classList.add('show');
        }, 10);
        
        // Remover após 5 segundos
        setTimeout(() => {
            container.classList.remove('show');
            setTimeout(() => {
                container.remove();
            }, 300);
        }, 5000);
    }
    
    // Modal futurista
    showModal(title, content, options = {}) {
        const modalId = 'dynamicModal_' + Date.now();
        const modalHTML = `
            <div class="modal fade neon-modal" id="${modalId}" tabindex="-1">
                <div class="modal-dialog ${options.size === 'large' ? 'modal-lg' : options.size === 'small' ? 'modal-sm' : ''}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title neon-text">
                                ${options.icon ? `<i class="fas fa-${options.icon} me-2"></i>` : ''}
                                ${title}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                        ${options.footer ? `
                        <div class="modal-footer">
                            ${options.footer}
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Adicionar modal ao body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        modal.show();
        
        // Remover modal após fechar
        document.getElementById(modalId).addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
        
        return modal;
    }
    
    // Loading spinner futurista
    showLoading(message = 'Carregando...') {
        const loadingId = 'loading_' + Date.now();
        const loadingHTML = `
            <div class="neon-loading-overlay" id="${loadingId}">
                <div class="loading-content glass-card">
                    <div class="neon-spinner"></div>
                    <p class="mt-3">${message}</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
        
        return {
            hide: () => {
                const element = document.getElementById(loadingId);
                if (element) {
                    element.classList.add('fade-out');
                    setTimeout(() => element.remove(), 300);
                }
            }
        };
    }
    
    // Confirmação futurista
    confirm(message, callback) {
        const content = `
            <div class="text-center">
                <i class="fas fa-question-circle fa-3x neon-text mb-3"></i>
                <p>${message}</p>
            </div>
        `;
        
        const footer = `
            <button type="button" class="neon-btn" data-bs-dismiss="modal">Cancelar</button>
            <button type="button" class="neon-btn neon-btn-primary" id="confirmBtn">Confirmar</button>
        `;
        
        const modal = this.showModal('Confirmação', content, { footer, icon: 'question-circle' });
        
        document.getElementById('confirmBtn').addEventListener('click', function() {
            modal.hide();
            callback(true);
        });
    }
    
    // Configurar event listeners
    setupEventListeners() {
        // Teclas de atalho
        document.addEventListener('keydown', (e) => {
            // Ctrl + N: Nova transação
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                quickAction('add_transaction');
            }
            
            // Ctrl + S: Salvar/Atualizar
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.showNotification('Sistema atualizado', 'success');
            }
            
            // Ctrl + E: Exportar
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                exportSystem();
            }
            
            // F1: Ajuda
            if (e.key === 'F1') {
                e.preventDefault();
                this.showHelp();
            }
        });
        
        // Efeitos de hover com som (opcional)
        if (typeof Audio !== 'undefined') {
            const hoverSound = new Audio('/static/assets/hover-sound.mp3');
            hoverSound.volume = 0.1;
            
            document.querySelectorAll('.neon-btn, .nav-link').forEach(btn => {
                btn.addEventListener('mouseenter', () => {
                    hoverSound.currentTime = 0;
                    hoverSound.play().catch(() => {});
                });
            });
        }
    }
    
    // Mostrar ajuda
    showHelp() {
        const content = `
            <div class="neon-help">
                <h6 class="neon-text mb-3">Atalhos do Sistema</h6>
                <div class="row">
                    <div class="col-md-6">
                        <div class="help-item mb-2">
                            <kbd>Ctrl</kbd> + <kbd>N</kbd>
                            <span>Nova Transação</span>
                        </div>
                        <div class="help-item mb-2">
                            <kbd>Ctrl</kbd> + <kbd>S</kbd>
                            <span>Salvar/Atualizar</span>
                        </div>
                        <div class="help-item mb-2">
                            <kbd>Ctrl</kbd> + <kbd>E</kbd>
                            <span>Exportar Dados</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="help-item mb-2">
                            <kbd>F1</kbd>
                            <span>Ajuda</span>
                        </div>
                        <div class="help-item mb-2">
                            <kbd>F5</kbd>
                            <span>Atualizar Página</span>
                        </div>
                        <div class="help-item mb-2">
                            <kbd>Esc</kbd>
                            <span>Fechar Modal</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.showModal('Ajuda - Atalhos do Sistema', content, { 
            icon: 'question-circle',
            size: 'small' 
        });
    }
    
    // Animar elementos ao rolar
    initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slide-up');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        // Observar elementos com classe 'animate-on-scroll'
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }
    
    // Efeito de digitação
    typewriter(element, text, speed = 50) {
        let i = 0;
        element.textContent = '';
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }
}

// Inicializar UI
const futuristicUI = new FuturisticUI();

// Funções globais
function toggleTheme() {
    futuristicUI.toggleTheme();
}

function toggleEffects() {
    futuristicUI.toggleEffects();
}

function showNeonNotification(message, type = 'info') {
    futuristicUI.showNotification(message, type);
}

function generateParticles(count) {
    futuristicUI.particlesCount = count;
    futuristicUI.initParticles();
}

// Exportar sistema
function exportSystem() {
    const loading = futuristicUI.showLoading('Preparando exportação...');
    
    // Simular exportação
    setTimeout(() => {
        loading.hide();
        futuristicUI.showNotification('Exportação concluída!', 'success');
        
        // Abrir modal de exportação
        const content = `
            <div class="text-center">
                <i class="fas fa-file-export fa-3x neon-text mb-3"></i>
                <h6>Exportar Dados</h6>
                <div class="row mt-4">
                    <div class="col-6">
                        <button class="neon-btn w-100 mb-2" onclick="exportAsPDF()">
                            <i class="fas fa-file-pdf me-2"></i>PDF
                        </button>
                    </div>
                    <div class="col-6">
                        <button class="neon-btn w-100 mb-2" onclick="exportAsExcel()">
                            <i class="fas fa-file-excel me-2"></i>Excel
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        futuristicUI.showModal('Exportar Dados', content, { icon: 'file-export' });
    }, 1500);
}

function exportAsPDF() {
    showNeonNotification('Gerando PDF...', 'info');
    // Implementar geração de PDF
}

function exportAsExcel() {
    showNeonNotification('Gerando Excel...', 'info');
    // Implementar geração de Excel
}

// Inicializar ao carregar
document.addEventListener('DOMContentLoaded', function() {
    // Iniciar animações de scroll
    futuristicUI.initScrollAnimations();
    
    // Efeito de digitação em elementos com classe typewriter
    document.querySelectorAll('.typewriter').forEach(el => {
        const text = el.textContent;
        futuristicUI.typewriter(el, text);
    });
});