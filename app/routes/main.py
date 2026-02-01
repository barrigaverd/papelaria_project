# 1. IMPORTAÇÕES
# Importe Blueprint, render_template, redirect, url_for
from flask import Blueprint, render_template, redirect, url_for, flash, request
# Importe login_required de flask_login
from flask_login import login_required, current_user
from models import Produto, Movimentacao, Categoria, Usuario
from extensions import db
from sqlalchemy import func
from datetime import datetime


# 2. DEFINIÇÃO DO BLUEPRINT
# Crie o blueprint: main = Blueprint('main', __name__)
main = Blueprint('main', __name__)

# 3. ROTA INDEX (A RAIZ)
# Crie a rota '@main.route("/")'
@main.route("/")
def index():
# - Se o usuário estiver logado: redirecione para 'main.dashboard'
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
# - Se não: redirecione para 'auth.login_cliente'
    return redirect(url_for("auth.login_cliente"))


# 4. ROTA DASHBOARD
# Crie a rota '@main.route("/dashboard")'
@main.route('/dashboard')
@login_required
def dashboard():
    # 1. Total de Produtos
    total_produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).count()

    # 2. Capital Investido (Soma de Custo x Estoque)
    produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    capital_investido = sum((p.preco_custo or 0) * p.estoque_atual for p in produtos)

    # 3. Vendas do Dia (Opcional, mas legal ter)
    hoje = datetime.utcnow().date()
    vendas_hoje = Movimentacao.query.filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        db.func.date(Movimentacao.data) == hoje
    ).all()
    faturamento_dia = sum(v.valor for v in vendas_hoje)

    return render_template('dashboard.html', 
                           total_produtos=total_produtos,
                           capital_investido=capital_investido,
                           faturamento_dia=faturamento_dia)