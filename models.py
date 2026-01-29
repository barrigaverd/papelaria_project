# 1. IMPORTAÇÕES NECESSÁRIAS
# Importe o objeto 'db' que você criou no app.py (ou de onde ele estiver instanciado)
from extensions import db, login_manager
# Importe o 'UserMixin' do 'flask_login' para a classe de Usuário
from flask_login import UserMixin
# Importe o 'datetime' para gerenciar as datas das movimentações
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# -------------------------------------------------------------------------

# 2. MODELO: PAPELARIA (O TENANT/CLIENTE DO SAAS)
# Crie uma classe que represente a loja/papelaria.
class Papelaria(db.Model):
# Ela deve herdar de db.Model.
# Atributos:
# - id: Inteiro, chave primária.
    id = db.Column(db.Integer, primary_key=True)
# - nome_fantasia: Texto (String), obrigatório.
    nome_fantasia = db.Column(db.String(100), nullable=False)
# - Relacionamentos: Crie relações (db.relationship) para Usuários, Produtos e Movimentações.
    usuarios = db.relationship('Usuario', backref='papelaria', lazy=True)
    produtos = db.relationship('Produto', backref='papelaria', lazy=True)
    movimentacoes = db.relationship('Movimentacao', backref='papelaria', lazy=True)
    
#   Dica: Use 'backref' para facilitar o acesso (ex: produto.papelaria.nome).

# -------------------------------------------------------------------------

# 3. MODELO: USUARIO
# Crie a classe de Usuário herdando de db.Model e UserMixin.
class Usuario(db.Model, UserMixin):
# Atributos:
# - id: Inteiro, chave primária.
    id = db.Column(db.Integer, primary_key=True)
# - papelaria_id: Inteiro, Chave Estrangeira (db.ForeignKey) apontando para a tabela Papelaria.
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
# - username: Texto, único e obrigatório.
    username = db.Column(db.String(80), unique=True, nullable=False)
# - password_hash: Texto, para armazenar a senha criptografada.
    password_hash = db.Column(db.String(128))


# -------------------------------------------------------------------------

# 4. MODELO: PRODUTO (ESTOQUE)
# Crie a classe de Produto herdando de db.Model.
class Produto(db.Model):
# Atributos:
# - id: Inteiro, chave primária.
    id = db.Column(db.Integer, primary_key=True)
# - papelaria_id: Inteiro, Chave Estrangeira apontando para Papelaria.
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
# - nome: Texto, obrigatório.
    nome = db.Column(db.String(100), nullable=False)
# - preco_venda: Numérico (db.Numeric com precisão de 2 casas decimais para dinheiro).
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
# - estoque_atual: Inteiro, valor padrão inicial deve ser 0.
    estoque_atual = db.Column(db.Integer, default=0)


# -------------------------------------------------------------------------

# 5. MODELO: CLIENTE
# Crie a classe de Cliente herdando de db.Model.
class Cliente(db.Model):
# Atributos:
# - id: Inteiro, chave primária.
    id = db.Column(db.Integer, primary_key=True)
# - papelaria_id: Inteiro, Chave Estrangeira apontando para Papelaria.
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
# - nome: Texto, obrigatório.
    nome = db.Column(db.String(100), nullable=False)
# - telefone: Texto (String).
    telefone = db.Column(db.String(20))


# -------------------------------------------------------------------------

# 6. MODELO: MOVIMENTACAO (FINANCEIRO)
# Crie a classe que registrará entradas, saídas e serviços.
class Movimentacao(db.Model):
# Atributos:
# - id: Inteiro, chave primária.
    id = db.Column(db.Integer, primary_key=True)
# - papelaria_id: Inteiro, Chave Estrangeira apontando para Papelaria.
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
# - tipo: Texto (sugestão: String de 10 caracteres para 'ENTRADA' ou 'SAIDA').
    tipo = db.Column(db.String(10), nullable=False)
# - categoria: Texto (ex: 'Serviço', 'Venda', 'Aluguel').
    categoria = db.Column(db.String(20), nullable=False)
# - descricao: Texto, para detalhes como "Cópia Colorida".
    descricao = db.Column(db.String(100))
# - valor: Numérico (db.Numeric com 2 casas decimais).
    valor = db.Column(db.Numeric(10, 2), nullable=False)
# - data: Data/Hora (db.DateTime, use o valor padrão datetime.utcnow).
    data = db.Column(db.DateTime, default=datetime.utcnow)
# - produto_id: Inteiro, Chave Estrangeira apontando para Produto.
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=True)
#   IMPORTANTE: Este campo deve permitir valores nulos (nullable=True), 
#   pois serviços avulsos não têm um produto associado.