from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Servico, Categoria, db

servicos = Blueprint('servicos', __name__)

@servicos.route('/servicos')
@login_required
def lista():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    # Busca serviços da papelaria logada
    query = Servico.query.filter_by(papelaria_id=current_user.papelaria_id)
    if search:
        query = query.filter(Servico.descricao.ilike(f'%{search}%'))
    
    pagination = query.paginate(page=page, per_page=10)
    
    # O SEGREDO: Busca as categorias globais da papelaria para os modais
    categorias = Categoria.query.all()
    
    return render_template('servicos/lista.html', 
                           pagination=pagination, 
                           categorias=categorias, # Enviando para o HTML
                           search=search)

@servicos.route('/servicos/novo', methods=['POST'])
@login_required
def novo():
    novo_s = Servico(
        descricao=request.form.get('descricao'),
        categoria_id=request.form.get('categoria_id'),
        custo=float(request.form.get('custo') or 0),
        preco=float(request.form.get('preco')),
        observacao=request.form.get('observacao'),
        papelaria_id=current_user.papelaria_id
    )
    db.session.add(novo_s)
    db.session.commit()
    flash("Serviço cadastrado com sucesso!", "success")
    return redirect(url_for('servicos.lista'))

# Adicionar aqui também as rotas de editar e excluir (seguindo o padrão dos clientes)
@servicos.route('/servicos/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    servico = Servico.query.get_or_404(id)
    
    if servico.papelaria_id != current_user.papelaria_id:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for('servicos.lista'))

    servico.descricao = request.form.get('descricao')
    servico.categoria_id = request.form.get('categoria_id')
    servico.custo = float(request.form.get('custo') or 0)
    servico.preco = float(request.form.get('preco'))
    servico.observacao = request.form.get('observacao')

    try:
        db.session.commit()
        flash(f"Serviço '{servico.descricao}' atualizado!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao atualizar serviço.", "danger")

    return redirect(url_for('servicos.lista'))

@servicos.route('/servicos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    servico = Servico.query.get_or_404(id)
    
    if servico.papelaria_id != current_user.papelaria_id:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for('servicos.lista'))

    try:
        db.session.delete(servico)
        db.session.commit()
        flash("Serviço removido com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao remover serviço.", "danger")

    return redirect(url_for('servicos.lista'))