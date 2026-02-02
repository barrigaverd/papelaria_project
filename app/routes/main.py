# 1. IMPORTAÇÕES
# Importe Blueprint, render_template, redirect, url_for
from flask import Blueprint, render_template, redirect, url_for, flash, request
# Importe login_required de flask_login
from flask_login import login_required, current_user
from models import Produto, Movimentacao, Categoria, Usuario, Despesa, Servico
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
from datetime import datetime, timedelta
from sqlalchemy import func

@main.route('/dashboard')
@login_required
def dashboard():
    hoje = datetime.now().date()
    sete_dias_atras = hoje - timedelta(days=6)
    
    # 1. KPIs Básicos
    vendas_hoje = Movimentacao.query.filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        func.date(Movimentacao.data) == hoje
    ).all()
    faturamento_dia = float(sum(v.valor for v in vendas_hoje) or 0)

    despesas_hoje = Despesa.query.filter(
        Despesa.papelaria_id == current_user.papelaria_id,
        Despesa.data_vencimento == hoje
    ).all()
    total_despesas_dia = float(sum(d.valor for d in despesas_hoje) or 0)

    produtos_estoque = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    capital_investido = float(sum((p.preco_custo or 0) * p.estoque_atual for p in produtos_estoque) or 0)

    # 2. Dados para o Gráfico (Últimos 7 dias)
    labels_grafico = []
    dados_vendas = []
    dados_despesas = []

    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        labels_grafico.append(dia.strftime('%d/%m'))
        
        v_dia = db.session.query(func.sum(Movimentacao.valor)).filter(
            Movimentacao.papelaria_id == current_user.papelaria_id,
            Movimentacao.tipo == 'SAIDA',
            func.date(Movimentacao.data) == dia
        ).scalar() or 0
        
        d_dia = db.session.query(func.sum(Despesa.valor)).filter(
            Despesa.papelaria_id == current_user.papelaria_id,
            func.date(Despesa.data_vencimento) == dia
        ).scalar() or 0
        
        dados_vendas.append(float(v_dia))
        dados_despesas.append(float(d_dia))

    # 3. Alerta de Estoque (Ajustado para 5 unidades como padrão)
    estoque_baixo = Produto.query.filter(
        Produto.papelaria_id == current_user.papelaria_id,
        Produto.estoque_atual <= 5 
    ).limit(5).all()

    return render_template('dashboard.html', 
                           faturamento_dia=faturamento_dia,
                           total_despesas_dia=total_despesas_dia,
                           capital_investido=capital_investido,
                           total_produtos=len(produtos_estoque),
                           estoque_baixo=estoque_baixo,
                           labels_grafico=labels_grafico,
                           dados_vendas=dados_vendas,
                           dados_despesas=dados_despesas,
                           hoje=hoje)