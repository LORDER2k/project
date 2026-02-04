# utils/formatters.py
import locale
from datetime import datetime

# Configura o locale para Brasil (moeda e números)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    # Caso o sistema não tenha suporte ao locale pt_BR
    locale.setlocale(locale.LC_ALL, '')

def format_currency(value: float) -> str:
    """
    Formata um número como moeda brasileira (R$).
    Exemplo: 1234.56 -> 'R$ 1.234,56'
    """
    return locale.currency(value, grouping=True)

def format_date(date_str: str) -> str:
    """
    Converte uma data no formato YYYY-MM-DD para DD/MM/YYYY.
    Exemplo: '2026-02-04' -> '04/02/2026'
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")

def format_percentage(value: float) -> str:
    """
    Formata um número como percentual com duas casas decimais.
    Exemplo: 0.1234 -> '12,34%'
    """
    return f"{value:.2%}"

def format_number(value: float, decimals: int = 2) -> str:
    """
    Formata um número com separador de milhar e casas decimais.
    Exemplo: 1234567.891 -> '1.234.567,89'
    """
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")