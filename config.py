import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o sistema
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configurações básicas do aplicativo Flask."""
    
    # Busca a SECRET_KEY do .env; se não achar, usa uma string padrão (não seguro)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-nunca-vai-adivinhar'
    
    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Desativa a notificação de modificações do SQLAlchemy (economiza memória)
    SQLALCHEMY_TRACK_MODIFICATIONS = False