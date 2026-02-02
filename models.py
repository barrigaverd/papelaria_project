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
    id = db.Column(db.Integer, primary_key=True)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    
    # --- NOVOS CAMPOS ---
    cnpj_cpf = db.Column(db.String(20))
    email = db.Column(db.String(100))
    site = db.Column(db.String(100))
    telefones = db.Column(db.String(100)) # Pode salvar como "9999-9999, 8888-8888"
    chave_pix = db.Column(db.String(100))
    logo_path = db.Column(db.String(200)) # Caminho para a imagem da logo
    
    # Endereço
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(150))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    complemento = db.Column(db.String(100))

    # Relacionamentos que você já tem...
    usuarios = db.relationship('Usuario', backref='papelaria', cascade='all, delete-orphan')
    produtos = db.relationship('Produto', backref='papelaria', cascade='all, delete-orphan')
    clientes = db.relationship('Cliente', backref='papelaria', cascade='all, delete-orphan')
    movimentacoes = db.relationship('Movimentacao', backref='papelaria', cascade='all, delete-orphan')
    despesas = db.relationship('Despesa', backref='papelaria', cascade='all, delete-orphan')
    categorias = db.relationship('Categoria', backref='papelaria', cascade='all, delete-orphan')
    formas_pagamento = db.relationship('FormaPagamento', backref='papelaria', cascade='all, delete-orphan')
    servicos = db.relationship('Servico', backref='papelaria', cascade='all, delete-orphan')
    # ...
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

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False)
    preco_custo = db.Column(db.Float, default=0.0) # Novo campo
    preco_venda = db.Column(db.Float, nullable=False)
    estoque_atual = db.Column(db.Integer, default=0)
    
    # Relacionamento com Categoria
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'


# -------------------------------------------------------------------------

# No arquivo models.py

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
    
    # Dados Obrigatórios
    nome = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    
    # Endereço (Opcionais)
    logradouro = db.Column(db.String(150))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2)) # UF: SP, RJ, etc.
    complemento = db.Column(db.String(100))
    
    # Documentação e Pessoal (Opcionais)
    data_nascimento = db.Column(db.Date)
    cpf = db.Column(db.String(14))

    def __repr__(self):
        return f'<Cliente {self.nome}>'


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
    forma_pagamento = db.Column(db.String(20), nullable=True)
    quantidade = db.Column(db.Integer, nullable=False)
# - data: Data/Hora (db.DateTime, use o valor padrão datetime.utcnow).
    data = db.Column(db.DateTime, default=datetime.now)
# - produto_id: Inteiro, Chave Estrangeira apontando para Produto.
    produto = db.relationship('Produto', backref='movimentacoes')
    servico = db.relationship('Servico', backref='movimentacoes')
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=True)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=True)

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    cliente = db.relationship('Cliente', backref='compras')
    venda_id = db.Column(db.String(36), nullable=True)
#   IMPORTANTE: Este campo deve permitir valores nulos (nullable=True), 
#   pois serviços avulsos não têm um produto associado.

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
    descricao = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # Ex: "Produto", "Serviço", "Despesa"
    
    # Relacionamento para contar quantos produtos usam esta categoria
    # (Assumindo que adicionaremos categoria_id no modelo Produto depois)
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.descricao}>'
    
class FormaPagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'), nullable=False)
    nome = db.Column(db.String(50), nullable=False) # Ex: Dinheiro, Pix, Cartão de Crédito
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<FormaPagamento {self.nome}>'
    
class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(150), nullable=False)
    custo = db.Column(db.Float, default=0.0)
    preco = db.Column(db.Float, nullable=False)
    observacao = db.Column(db.Text)
    
    # Relacionamento com Categoria (Reutilizando as existentes)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    categoria = db.relationship('Categoria', backref='servicos')
    
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'))

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(150), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Pendente') # Pendente, Pago
    observacao = db.Column(db.Text)
    
    # Relacionamento com Categoria (usando a sua classe existente)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    categoria = db.relationship('Categoria', backref='despesas')
    # Categoria terá um backref 'despesas' automaticamente se você usar relationship
    
    papelaria_id = db.Column(db.Integer, db.ForeignKey('papelaria.id'))