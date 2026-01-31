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

@main.route('/configuracoes/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        tipo = request.form.get('tipo')
        
        nova_cat = Categoria(
            descricao=descricao,
            tipo=tipo,
            papelaria_id=current_user.papelaria_id
        )
        db.session.add(nova_cat)
        db.session.commit()
        return redirect(url_for('main.categorias'))

    # Busca as categorias e conta os produtos vinculados
    categorias_lista = Categoria.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    return render_template('configuracoes/categorias.html', categorias=categorias_lista)

# ROTA DE EDIÇÃO
@main.route('/configuracoes/categorias/editar/<int:id>', methods=['POST'])
@login_required
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    # Segurança: verifica se a categoria pertence à papelaria logada
    if categoria.papelaria_id != current_user.papelaria_id:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('main.categorias'))
    
    categoria.descricao = request.form.get('descricao')
    categoria.tipo = request.form.get('tipo')
    
    db.session.commit()
    flash('Categoria atualizada com sucesso!', 'success')
    return redirect(url_for('main.categorias'))

# ROTA DE EXCLUSÃO
@main.route('/configuracoes/categorias/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    if categoria.papelaria_id != current_user.papelaria_id:
        return redirect(url_for('main.categorias'))
    
    # Trava de segurança: não exclui se tiver produtos
    if len(categoria.produtos) > 0:
        flash('Não é possível excluir uma categoria que possui produtos vinculados!', 'warning')
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria removida com sucesso!', 'success')
        
    return redirect(url_for('main.categorias'))