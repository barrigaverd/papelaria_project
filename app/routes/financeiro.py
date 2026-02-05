from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Transacao # Sua tabela de transações
from sqlalchemy import func
from datetime import datetime, timedelta
from extensions import db


# Define o Blueprint
financeiro = Blueprint('financeiro', __name__)

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import Transacao
from extensions import db
from sqlalchemy import func, extract
from datetime import datetime
import calendar

financeiro = Blueprint('financeiro', __name__)

@financeiro.route('/financeiro')
@login_required
def dashboard():
    # 1. CAPTURAR FILTROS DA URL (Default: Mês e Ano atuais)
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    
    ano_sel = request.args.get('ano', default=ano_atual, type=int)
    mes_sel = request.args.get('mes', default=mes_atual, type=int)

    # 2. FILTRAR TRANSAÇÕES DO PERÍODO SELECIONADO
    query_base = Transacao.query.filter(
        Transacao.usuario_id == current_user.id,
        extract('year', Transacao.data) == ano_sel,
        extract('month', Transacao.data) == mes_sel
    )

    # 3. DADOS PARA O GRÁFICO DE LINHA (Dias do Mês)
    # Agrupa por dia para mostrar a evolução no mês selecionado
    dados_grafico = db.session.query(
        func.strftime('%d', Transacao.data).label('dia'),
        func.sum(Transacao.valor)
    ).filter(
        Transacao.usuario_id == current_user.id,
        Transacao.tipo == 'receita',
        extract('year', Transacao.data) == ano_sel,
        extract('month', Transacao.data) == mes_sel
    ).group_by('dia').all()

    labels_grafico = [f"Dia {d[0]}" for d in dados_grafico]
    valores_grafico = [float(d[1]) for d in dados_grafico]

    # 4. CÁLCULOS DOS CARDS (Resumo do mês selecionado)
    entradas_mes = db.session.query(func.sum(Transacao.valor)).filter(
        Transacao.usuario_id == current_user.id,
        Transacao.tipo == 'receita',
        extract('year', Transacao.data) == ano_sel,
        extract('month', Transacao.data) == mes_sel
    ).scalar() or 0

    saidas_mes = db.session.query(func.sum(Transacao.valor)).filter(
        Transacao.usuario_id == current_user.id,
        Transacao.tipo == 'despesa',
        extract('year', Transacao.data) == ano_sel,
        extract('month', Transacao.data) == mes_sel
    ).scalar() or 0

    # 5. DADOS PARA O GRÁFICO DE PIZZA (Categorias do mês)
    dados_categoria = db.session.query(
        Transacao.categoria,
        func.sum(Transacao.valor)
    ).filter(
        Transacao.usuario_id == current_user.id,
        Transacao.tipo == 'despesa',
        extract('year', Transacao.data) == ano_sel,
        extract('month', Transacao.data) == mes_sel
    ).group_by(Transacao.categoria).all()

    labels_cat = [d[0] for d in dados_categoria]
    valores_cat = [float(d[1]) for d in dados_categoria]

    # Lista de anos para o filtro (Ex: do ano passado até o próximo)
    anos_disponiveis = [ano_atual - 1, ano_atual, ano_atual + 1]
    meses_nome = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]

    return render_template('financeiro.html', 
                           labels_grafico=labels_grafico, 
                           valores_grafico=valores_grafico,
                           labels_cat=labels_cat,
                           valores_cat=valores_cat,
                           entradas_mes=entradas_mes,
                           saidas_mes=saidas_mes,
                           saldo_total=entradas_mes - saidas_mes,
                           mes_sel=mes_sel,
                           ano_sel=ano_sel,
                           anos_disponiveis=anos_disponiveis,
                           meses_nome=meses_nome)