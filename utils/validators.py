# utils/validators.py
import re
from datetime import datetime

def validate_date(date_str: str) -> bool:
    """
    Valida se a data está no formato YYYY-MM-DD.
    Retorna True se válido, False caso contrário.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_currency(value: str) -> bool:
    """
    Valida se o valor é um número válido para moeda.
    Aceita formatos como '1234.56' ou '1234,56'.
    """
    pattern = r"^\d+([.,]\d{1,2})?$"
    return bool(re.match(pattern, value))

def validate_percentage(value: str) -> bool:
    """
    Valida se o valor é um percentual válido.
    Exemplo: '12.34%' ou '0.5'
    """
    pattern = r"^\d+(\.\d+)?%?$"
    return bool(re.match(pattern, value))

def validate_cnpj(cnpj: str) -> bool:
    """
    Valida se o CNPJ tem 14 dígitos numéricos.
    Não faz validação matemática completa, apenas formato.
    """
    cnpj = re.sub(r"\D", "", cnpj)  # remove caracteres não numéricos
    return len(cnpj) == 14

def validate_email(email: str) -> bool:
    """
    Valida se o email está em formato correto.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))