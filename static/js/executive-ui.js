// Executive UI - Interface Executiva Futurista
// Este script adiciona efeitos executivos sem modificar o código original

class ExecutiveUI {
    constructor() {
        this.effectsEnabled = true;
        this.particlesCount = 30;
        this.init();
    }
    
    init() {
        console.log('🚀 Inicializando Interface Executiva Futurista...');
        
        // Aplicar classes executivas
        this.applyExecutiveClasses();
        
        // Iniciar efeitos
        if (this.effectsEnabled) {
            this.initParticles();
            this.initScanline();
            this.initGrid();
            this.initTypewriter();
        }
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Iniciar animações
        this.startAnimations();
    }
    
    // Aplicar classes CSS executivas
    applyExecutiveClasses() {
        // Body
        document.body.classList.add('executive-mode');
        
        // Navbar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.classList.add('executive-navbar');
        }
        
        // Navbar brand
        const navbarBrand = document.querySelector('.navbar-brand');
        if (navbarBrand) {
            navbarBrand.classList.add('executive-brand');
        }
        
        // Nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.add('executive-link');
        });
        
        // Cards
        document.querySelectorAll('.card').forEach(card => {
            card.classList.add('executive-card');
        });
        
        // Card headers
        document.querySelectorAll('.card-header').forEach(header => {
            header.classList.add('executive-header');
        });
        
        // Botões
        document.querySelectorAll('.btn').forEach(btn => {
            btn.classList.add('executive-btn');
            
            // Adicionar classe primária para botões primários
            if (btn.classList.contains('btn-primary')) {
                btn.classList.add('executive-btn-primary');
            }
        });
        
        // Tabelas
        document.querySelectorAll('.table').forEach(table => {
            table.classList.add('executive-table');
        });
        
        // Stats cards
        document.querySelectorAll('.stats-card').forEach(card => {
            card.classList.add('executive-stats');
        });
        
        // Chart containers
        document.querySelectorAll('.chart-container').forEach(container => {
            container.classList.add('executive-chart');
        });
        
        // Inputs
        document.querySelectorAll('.form-control').forEach(input => {
            input.classList.add('executive-input');
        });
        
        // Badges
        document.querySelectorAll('.badge').forEach(badge => {
            badge.classList.add('executive-badge');
        });
        
        // Progress bars
        document.querySelectorAll('.progress').forEach(progress => {
            progress.classList.add('executive-progress');
        });
        
        document.querySelectorAll('.progress-bar').forEach(bar => {
            bar.classList.add('executive-progress-bar');
        });
        
        // Footer
        const footer = document.querySelector('footer');
        if (footer) {
            footer.classList.add('executive-footer');
        }
        
        console.log('✅ Classes executivas aplicadas com sucesso!');
    }
    
    // Inicializar partículas
    initParticles() {
        const container = document.createElement('div');
        container.className = 'executive-particles';
        container.id = 'executiveParticles';
        document.body.appendChild(container);
        
        for (let i = 0; i < this.particlesCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Posição aleatória
            const left = Math.random() * 100;
            const delay = Math.random() * 20;
            const duration = 15 + Math.random() * 15;
            const size = 1 + Math.random() * 2;
            
            // Estilos
            particle.style.left = `${left}%`;
            particle.style.animationDelay = `${delay}s`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            // Cor aleatória
            const colors = ['#0066ff', '#00ffff', '#9d00ff', '#00ff88'];
            const color = colors[Math.floor(Math.random() * colors.length)];
            particle.style.background = color;
            particle.style.boxShadow = `0 0 ${size * 3}px ${color}`;
            
            container.appendChild(particle);
        }
    }
    
    // Inicializar scanline
    initScanline() {
        const scanline = document.createElement('div');
        scanline.className = 'executive-scanline';
        document.body.appendChild(scanline);
    }
    
    // Inicializar grid holográfico
    initGrid() {
        const grid = document.createElement('div');
        grid.className = 'executive-grid';
        document.body.appendChild(grid);
    }
    
    // Inicializar efeito typewriter
    initTypewriter() {
        // Encontrar elementos com texto importante
        const importantTexts = document.querySelectorAll('h1, h2, .navbar-brand');
        
        importantTexts.forEach(element => {
            if (!element.classList.contains('executive-typewriter')) {
                element.classList.add('executive-typewriter');
                
                // Capturar texto original
                const text = element.textContent;
                element.textContent = '';
                
                // Efeito de digitação
                let i = 0;
                const type = () => {
                    if (i < text.length) {
                        element.textContent += text.charAt(i);
                        i++;
                        setTimeout(type, 50);
                    }
                };
                
                // Iniciar após um delay
                setTimeout(type, 1000);
            }
        });
    }
    
    // Configurar event listeners
    setupEventListeners() {
        // Efeito de onda ao clicar
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('executive-wave') || 
                e.target.closest('.executive-wave')) {
                return;
            }
            
            // Adicionar efeito de onda a botões
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
                button.classList.add('executive-wave');
                
                setTimeout(() => {
                    button.classList.remove('executive-wave');
                }, 1000);
            }
        });
        
        // Teclas de atalho
        document.addEventListener('keydown', (e) => {
            // Ctrl + E: Ativar/desativar efeitos
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                this.toggleEffects();
            }
            
            // Ctrl + T: Alternar tema
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // F1: Mostrar ajuda
            if (e.key === 'F1') {
                e.preventDefault();
                this.showHelp();
            }
        });
        
        // Efeito hover glow
        document.querySelectorAll('.executive-glow').forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.transition = 'all 0.3s ease';
            });
        });
    }
    
    // Iniciar animações
    startAnimations() {
        // Animar elementos ao rolar
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slide-up');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        // Observar elementos importantes
        document.querySelectorAll('.card, .stats-card, .table').forEach(el => {
            observer.observe(el);
        });
        
        // Atualizar partículas periodicamente
        setInterval(() => {
            this.updateParticles();
        }, 30000);
    }
    
    // Atualizar partículas
    updateParticles() {
        const container = document.getElementById('executiveParticles');
        if (container) {
            container.innerHTML = '';
            this.initParticles();
        }
    }
    
    // Alternar efeitos
    toggleEffects() {
        this.effectsEnabled = !this.effectsEnabled;
        
        const effects = document.querySelectorAll('.executive-particles, .executive-scanline, .executive-grid');
        effects.forEach(effect => {
            effect.style.display = this.effectsEnabled ? 'block' : 'none';
        });
        
        this.showNotification(`Efeitos ${this.effectsEnabled ? 'ativados' : 'desativados'}`, 'info');
    }
    
    // Alternar tema
    toggleTheme() {
        document.body.classList.toggle('executive-dark-mode');
        this.showNotification('Tema alternado', 'info');
    }
    
    // Mostrar ajuda
    showHelp() {
        const helpModal = `
            <div class="modal fade" id="executiveHelpModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content executive-card">
                        <div class="modal-header executive-header">
                            <h5 class="modal-title">
                                <i class="fas fa-question-circle me-2"></i>
                                Atalhos do Sistema Executivo
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <kbd>Ctrl</kbd> + <kbd>E</kbd>
                                        <span class="ms-2">Alternar efeitos visuais</span>
                                    </div>
                                    <div class="mb-3">
                                        <kbd>Ctrl</kbd> + <kbd>T</kbd>
                                        <span class="ms-2">Alternar tema</span>
                                    </div>
                                    <div class="mb-3">
                                        <kbd>F1</kbd>
                                        <span class="ms-2">Abrir esta ajuda</span>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <kbd>F5</kbd>
                                        <span class="ms-2">Atualizar página</span>
                                    </div>
                                    <div class="mb-3">
                                        <kbd>Esc</kbd>
                                        <span class="ms-2">Fechar modais</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Adicionar modal ao body
        document.body.insertAdjacentHTML('beforeend', helpModal);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('executiveHelpModal'));
        modal.show();
        
        // Remover após fechar
        document.getElementById('executiveHelpModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    // Mostrar notificação
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `executive-notification notification-${type}`;
        
        const icons = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle'
        };
        
        notification.innerHTML = `
            <div class="executive-card p-3">
                <i class="fas ${icons[type] || icons.info} me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remover após 5 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que o Bootstrap esteja carregado
    setTimeout(() => {
        window.executiveUI = new ExecutiveUI();
        console.log('🎨 Interface Executiva Futurista carregada com sucesso!');
    }, 1000);
});

// Adicionar estilos para notificações
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
.executive-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    min-width: 300px;
    opacity: 0;
    transform: translateX(100%);
    transition: all 0.3s ease;
}

.executive-notification.show {
    opacity: 1;
    transform: translateX(0);
}

.notification-info .executive-card {
    border-left: 4px solid #0066ff;
}

.notification-success .executive-card {
    border-left: 4px solid #00ff88;
}

.notification-warning .executive-card {
    border-left: 4px solid #ffc107;
}

.notification-error .executive-card {
    border-left: 4px solid #ff3366;
}
`;

document.head.appendChild(notificationStyles);