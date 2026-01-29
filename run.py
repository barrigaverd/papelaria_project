from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager
from flask_migrate import Migrate
from app.routes.auth import auth
from app.routes.main import main
from app.routes.estoque import estoque





# Instanciação das extensões (serão ligadas ao app depois)

migrate = Migrate()

def create_app():
    """Factory Function: Cria e configura a instância do App Flask."""
    import cli
    
    app = Flask(__name__)
    
    # Aplica as configurações que definimos no config.py
    app.config.from_object(Config)

    
    # Inicializa o banco de dados e as migrações no contexto do app
    db.init_app(app)
    cli.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    
    from models import Papelaria, Usuario, Produto, Cliente, Movimentacao
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(estoque)
    
    #   - Defina a rota de login padrão: login_manager.login_view = 'auth.login_cliente'
    login_manager.login_view = 'auth.login_cliente'
    #   - Opcional: Defina a categoria da mensagem de erro (ex: 'info' ou 'danger')
    
    return app

app = create_app()
# Ponto de execução do servidor de desenvolvimento
if __name__ == '__main__':
    app.run()


    