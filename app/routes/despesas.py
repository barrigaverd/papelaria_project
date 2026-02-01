from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Despesa, db, Categoria
from datetime import datetime, timedelta

despesas = Blueprint('despesas', __name__)

@despesas.route('/despesas')
@login_required
def lista():
    # 1. Filtros de Data (Padrão: Início do mês atual até o fim do mês)
    hoje = datetime.now()
    primeiro_dia_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    ultimo_dia_mes = (hoje.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    data_inicio = request.args.get('data_inicio', primeiro_dia_mes)
    data_fim = request.args.get('data_fim', ultimo_dia_mes.strftime('%Y-%m-%d'))

    # 2. Query com Filtro de Período
    query = Despesa.query.filter_by(papelaria_id=current_user.papelaria_id)
    query = query.filter(Despesa.data_vencimento >= data_inicio, Despesa.data_vencimento <= data_fim)
    
    despesas = query.order_by(Despesa.data_vencimento.asc()).all()

    # 3. Categorias e Totais (Baseados no filtro)
    categorias = Categoria.query.filter_by(papelaria_id=current_user.papelaria_id, tipo='Despesa').all()
    total_pendente = sum(d.valor for d in despesas if d.status == 'Pendente')
    total_pago = sum(d.valor for d in despesas if d.status == 'Pago')

    return render_template('despesas/lista.html', 
                           despesas=despesas, 
                           categorias=categorias,
                           total_pendente=total_pendente,
                           total_pago=total_pago,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           now=hoje)

@despesas.route('/despesas/novo', methods=['POST'])
@login_required
def novo():
    # Pegue o valor com o nome EXATO que está no "name" do <select> do HTML
    cat_id = request.form.get('categoria_id') 

    nova_d = Despesa(
        descricao=request.form.get('descricao'),
        valor=float(request.form.get('valor') or 0),
        categoria_id=cat_id, # Certifique-se de que o nome aqui é categoria_id
        data_vencimento=datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d'),
        observacao=request.form.get('observacao'),
        papelaria_id=current_user.papelaria_id
    )
    db.session.add(nova_d)
    db.session.commit()
    flash("Despesa lançada!", "success")
    return redirect(url_for('despesas.lista'))

@despesas.route('/despesas/pagar/<int:id>', methods=['POST'])
@login_required
def pagar(id):
    d = Despesa.query.get_or_404(id)
    d.status = 'Pago'
    d.data_pagamento = datetime.now()
    db.session.commit()
    flash("Conta marcada como paga!", "success")
    return redirect(url_for('despesas.lista'))

@despesas.route('/despesas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    d = Despesa.query.get_or_404(id)
    
    # Segurança: Garante que a despesa pertence à papelaria logada
    if d.papelaria_id != current_user.papelaria_id:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for('despesas.lista'))

    db.session.delete(d)
    db.session.commit()
    flash("Despesa removida com sucesso!", "warning")
    return redirect(url_for('despesas.lista'))