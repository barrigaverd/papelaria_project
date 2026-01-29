from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
from models import Produto, Movimentacao
from extensions import db

estoque = Blueprint('estoque', __name__)

@estoque.route('/produtos')
@login_required
def lista_produtos():
    produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    return render_template('estoque/lista.html', produtos=produtos)

@estoque.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        preco_venda = request.form['preco_venda']
        estoque_atual = request.form['estoque_atual']

        novo_p = Produto(
            nome=nome,
            preco_venda=preco_venda,
            estoque_atual=estoque_atual,
            papelaria_id=current_user.papelaria_id
        )
        db.session.add(novo_p)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('estoque.lista_produtos'))

@estoque.route('/venda/<int:produto_id>', methods=['POST'])
@login_required
def registrar_venda(produto_id):
    produto = Produto.query.get(produto_id)
    if produto.papelaria_id == current_user.papelaria_id:
        quant = float(request.form['quantidade'])
        if quant <= produto.estoque_atual:
            produto.estoque_atual -= quant
            
            movimentacao = Movimentacao(
                tipo = "ENTRADA",
                categoria = "Venda",
                valor = float(produto.preco_venda * quant),
                papelaria_id = current_user.papelaria_id,
                produto_id = produto.id  
            )
            db.session.add(movimentacao)
            db.session.commit()
            flash("Venda registrada com sucesso!", "success")
            return redirect(url_for('estoque.lista_produtos'))

        else:
            flash("Quantidade insuficiente em estoque", "error")
            return redirect(url_for('estoque.lista_produtos'))
    else:
        return abort(403)