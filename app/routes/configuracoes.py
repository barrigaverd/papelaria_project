from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Categoria, FormaPagamento

configuracoes = Blueprint('configuracoes', __name__)

# --- CATEGORIAS ---
@configuracoes.route('/categorias')
@login_required
def lista_categorias():
    categorias = Categoria.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    return render_template('configuracoes/categorias.html', categorias=categorias)

@configuracoes.route('/categorias/nova', methods=['POST'])
@login_required
def nova_categoria():
    nova_cat = Categoria(
        descricao=request.form.get('descricao'),
        tipo=request.form.get('tipo'),
        papelaria_id=current_user.papelaria_id
    )
    db.session.add(nova_cat)
    db.session.commit()
    flash('Categoria criada!', 'success')
    return redirect(url_for('configuracoes.lista_categorias'))

@configuracoes.route('/categorias/editar/<int:id>', methods=['POST'])
@login_required
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.papelaria_id == current_user.papelaria_id:
        categoria.descricao = request.form.get('descricao')
        categoria.tipo = request.form.get('tipo')
        db.session.commit()
        flash('Categoria atualizada!', 'success')
    return redirect(url_for('configuracoes.lista_categorias'))

@configuracoes.route('/categorias/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.papelaria_id == current_user.papelaria_id:
        if len(categoria.produtos) > 0:
            flash('Não exclua categorias com produtos vinculados!', 'warning')
        else:
            db.session.delete(categoria)
            db.session.commit()
            flash('Categoria removida!', 'success')
    return redirect(url_for('configuracoes.lista_categorias'))

# --- FORMAS DE PAGAMENTO ---
@configuracoes.route('/pagamentos')
@login_required
def lista_pagamentos():
    pagamentos = FormaPagamento.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    return render_template('configuracoes/pagamentos.html', pagamentos=pagamentos)

@configuracoes.route('/pagamentos/novo', methods=['POST'])
@login_required
def novo_pagamento():
    novo_pago = FormaPagamento(
        nome=request.form.get('nome'),
        papelaria_id=current_user.papelaria_id
    )
    db.session.add(novo_pago)
    db.session.commit()
    flash('Pagamento cadastrado!', 'success')
    return redirect(url_for('configuracoes.lista_pagamentos'))

@configuracoes.route('/pagamentos/editar/<int:id>', methods=['POST'])
@login_required
def editar_pagamento(id):
    pago = FormaPagamento.query.get_or_404(id)
    if pago.papelaria_id == current_user.papelaria_id:
        pago.nome = request.form.get('nome')
        db.session.commit()
        flash('Pagamento atualizado!', 'success')
    return redirect(url_for('configuracoes.lista_pagamentos'))

@configuracoes.route('/pagamentos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_pagamento(id):
    pago = FormaPagamento.query.get_or_404(id)
    if pago.papelaria_id == current_user.papelaria_id:
        db.session.delete(pago)
        db.session.commit()
        flash('Pagamento removido!', 'warning')
    return redirect(url_for('configuracoes.lista_pagamentos'))