from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
from models import Produto, Movimentacao, Categoria
from extensions import db

estoque = Blueprint('estoque', __name__)

@estoque.route('/produtos')
@login_required
def lista_produtos():
    # Pegamos o número da página e o termo de busca da URL
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Produto.query.filter_by(papelaria_id=current_user.papelaria_id)

    # Se houver busca, filtra pelo nome
    if search:
        query = query.filter(Produto.nome.ilike(f'%{search}%'))

    # Ordena por nome e pagina (25 por página)
    pagination = query.order_by(Produto.nome.asc()).paginate(page=page, per_page=25)
    
    produtos = pagination.items
    categorias = Categoria.query.filter_by(papelaria_id=current_user.papelaria_id).all()

    return render_template('estoque/lista.html', 
                           produtos=produtos, 
                           pagination=pagination, 
                           categorias=categorias,
                           search=search)

@estoque.route('/produtos/novo', methods=['POST'])
@login_required
def novo_produto():
    nome = request.form.get('nome')
    preco_custo = float(request.form.get('preco_custo') or 0)
    preco_venda = float(request.form.get('preco_venda'))
    estoque_atual = int(request.form.get('estoque_atual') or 0)
    categoria_id = request.form.get('categoria_id') or None

    novo_prod = Produto(
        nome=nome,
        preco_custo=preco_custo,
        preco_venda=preco_venda,
        estoque_atual=estoque_atual,
        categoria_id=categoria_id,
        papelaria_id=current_user.papelaria_id
    )
    db.session.add(novo_prod)
    db.session.commit()
    flash('Produto cadastrado com sucesso!', 'success')
    return redirect(url_for('estoque.lista_produtos'))

@estoque.route('/produtos/editar/<int:id>', methods=['POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.filter_by(id=id, papelaria_id=current_user.papelaria_id).first_or_404()
    
    # Atualizando TODOS os campos agora
    produto.nome = request.form.get('nome')
    produto.preco_custo = float(request.form.get('preco_custo') or 0)
    produto.preco_venda = float(request.form.get('preco_venda'))
    produto.estoque_atual = int(request.form.get('estoque_atual'))
    produto.categoria_id = request.form.get('categoria_id') or None
    
    db.session.commit()
    flash(f"Produto '{produto.nome}' atualizado!", "success")
    return redirect(url_for('estoque.lista_produtos'))

@estoque.route('/venda/<int:produto_id>', methods=['POST'])
@login_required
def registrar_venda(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    if produto.papelaria_id == current_user.papelaria_id:
        # Usando int para quantidade inteira (canetas, cadernos)
        qtd = int(request.form['quantidade'])
        
        if qtd <= produto.estoque_atual:
            produto.estoque_atual -= qtd
            
            movimentacao = Movimentacao(
                tipo = "SAIDA", # Venda é saída de mercadoria
                categoria = "Venda Rápida",
                valor = float(produto.preco_venda * qtd),
                quantidade = qtd,
                papelaria_id = current_user.papelaria_id,
                produto_id = produto.id  
            )
            db.session.add(movimentacao)
            db.session.commit()
            flash("Venda registrada!", "success")
        else:
            flash("Estoque insuficiente!", "danger")
    return redirect(url_for('estoque.lista_produtos'))

@estoque.route('/produtos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    # Busca o produto garantindo que pertence à papelaria do usuário logado
    produto = Produto.query.filter_by(id=id, papelaria_id=current_user.papelaria_id).first_or_404()
    
    db.session.delete(produto)
    db.session.commit()
    
    flash(f"Produto excluído com sucesso!", "warning")
    return redirect(url_for('estoque.lista_produtos'))