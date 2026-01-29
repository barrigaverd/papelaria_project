# 1. IMPORTAÇÕES
# Importe o 'click' (é a biblioteca que o Flask usa para comandos de terminal)
import click
# Importe 'generate_password_hash' de 'werkzeug.security' (para a senha segura)
from werkzeug.security import generate_password_hash
# Importe o objeto 'db' de 'extensions'
from extensions import db
# Importe os modelos 'Papelaria' e 'Usuario' de 'models'
from models import Papelaria, Usuario

# -------------------------------------------------------------------------

# 2. DEFINIÇÃO DO COMANDO
# Use o decorador @click.command('setup-inicial') para dar nome ao comando
@click.command('setup-inicial')
def setup_inicial():
    """Cria a primeira papelaria e o administrador do sistema."""
    
    # PASSO A: Criar a Papelaria
    # Use click.echo para imprimir uma mensagem de boas-vindas
    click.echo("Bem vindo")
    # Use click.prompt para pedir o "Nome da Papelaria" e guarde em uma variável
    nome_papelaria = click.prompt('Nome da Papelaria')
    
    # Instancie a classe Papelaria com o nome fornecido
    paper = Papelaria()
    paper.nome_fantasia = nome_papelaria
    # Adicione ao db.session e dê commit (precisamos do ID gerado antes de seguir)
    db.session.add(paper)
    db.session.commit()
    
    # PASSO B: Criar o Usuário Administrador
    # Use click.prompt para pedir o "Username do Admin"
    username = click.prompt('Username do Admin')
    # Use click.prompt para pedir a "Senha", mas adicione o argumento hide_input=True
    senha = click.prompt('Senha', hide_input = True)
    # Gere o hash da senha usando generate_password_hash
    senha_hash = generate_password_hash(senha)
    
    # Instancie a classe Usuario passando:
    user = Usuario()
    # - username
    user.username = username
    # - password_hash (o hash que você gerou, não a senha limpa!)
    user.password_hash = senha_hash
    # - papelaria_id (use o .id da papelaria que você acabou de salvar)
    user.papelaria_id = paper.id
    
    # Adicione ao db.session e dê commit
    db.session.add(user)
    db.session.commit()
    # PASSO C: Finalização
    # Use click.echo para mostrar uma mensagem de sucesso com o nome da papelaria
    click.echo(f"Papelaria de nome: {nome_papelaria} cadastrada com sucesso!")

# -------------------------------------------------------------------------

# 3. REGISTRO NO APLICATIVO
# Crie uma função chamada init_app(app):
def init_app(app):
    app.cli.add_command(setup_inicial)
# Dentro dela, use app.cli.add_command(setup_inicial)