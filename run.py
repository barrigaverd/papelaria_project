from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager
from flask_migrate import Migrate
from app.routes.auth import auth
from app.routes.main import main
from app.routes.estoque import estoque
from app.routes.vendas import vendas
from app.routes.clientes import clientes
from app.routes.servicos import servicos
from app.routes.configuracoes import configuracoes
from dotenv import load_dotenv
# Instanciação das extensões (serão ligadas ao app depois)
load_dotenv()
migrate = Migrate()

def create_app():
    """Factory Function: Cria e configura a instância do App Flask."""
    import cli
    
    app = Flask(__name__)
    
    # 1. Primeiro carrega o que estiver no arquivo Config
    app.config.from_object(Config)
    
    # 2. DEPOIS você força as configurações manuais para garantir que nada as apague
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///papelaria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma-chave-qualquer-temporaria'
    
    # Agora sim, inicializa o banco com a URI correta na memória
    db.init_app(app)
    cli.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)    
    
    from models import Papelaria, Usuario, Produto, Cliente, Movimentacao
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(estoque)
    app.register_blueprint(vendas, url_prefix='/vendas')
    app.register_blueprint(configuracoes, url_prefix='/configuracoes')
    app.register_blueprint(clientes, url_prefix='/clientes')
    app.register_blueprint(servicos, url_prefix='/servicos')
    
    
    #   - Defina a rota de login padrão: login_manager.login_view = 'auth.login_cliente'
    login_manager.login_view = 'auth.login_cliente'
    #   - Opcional: Defina a categoria da mensagem de erro (ex: 'info' ou 'danger')
    
    return app

app = create_app()
# Ponto de execução do servidor de desenvolvimento
if __name__ == '__main__':
    app.run()


    