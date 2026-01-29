# 1. IMPORTAÇÕES
# Importe Blueprint, render_template, redirect, url_for
from flask import Blueprint, render_template, redirect, url_for
# Importe login_required de flask_login
from flask_login import login_required, current_user
from models import Produto, Movimentacao
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
@main.route("/dashboard")
@login_required
# - Use o decorador @login_required
def dashboard():
    total_produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).count()
    alertas_estoque = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).filter(Produto.estoque_atual < 3).count()

    hoje = datetime.utcnow().date()
    vendas_hoje = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == "ENTRADA",
        func.date(Movimentacao.data) == hoje
        ).scalar() or 0

    return render_template("dashboard.html", total_produtos=total_produtos, alertas_estoque=alertas_estoque, vendas_hoje=vendas_hoje)