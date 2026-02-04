# Configurações para o sistema futurista
import os

class FuturisticConfig:
    # Templates renomeados
    TEMPLATES = {
        'base': 'base_futuristic.html',
        'index': 'index_futuristic.html',
        'dashboard': 'dashboard_futuristic.html',
        'analytics': 'analytics_futuristic.html',
        'insights': 'insights_futuristic.html',
        'transactions': 'transactions_futuristic.html',
        'goals': 'goals_futuristic.html',
        'ia_financeira': 'ia_financeira_futuristic.html',
        'perfil': 'perfil_futuristic.html',
        'sobre': 'sobre_futuristic.html',
        'register': 'register_futuristic.html',
        'login': 'login_futuristic.html'
    }
    
    # Cores do tema neon
    COLORS = {
        'neon_blue': '#00f3ff',
        'neon_purple': '#b967ff',
        'neon_green': '#00ff9d',
        'neon_pink': '#ff00ff',
        'bg_dark': '#0a0a1a',
        'bg_card': 'rgba(255, 255, 255, 0.05)'
    }
    
    # Configurações de UI
    UI = {
        'enable_particles': True,
        'enable_animations': True,
        'enable_sounds': False,
        'particles_count': 50,
        'theme': 'dark'
    }