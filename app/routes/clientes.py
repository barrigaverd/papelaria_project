from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Cliente
from datetime import datetime

clientes = Blueprint('clientes', __name__)

@clientes.route('/clientes')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Cliente.query.filter_by(papelaria_id=current_user.papelaria_id)
    if search:
        query = query.filter(Cliente.nome.ilike(f'%{search}%'))
    
    pagination = query.order_by(Cliente.nome.asc()).paginate(page=page, per_page=20)
    return render_template('clientes/lista.html', pagination=pagination, search=search)

# No arquivo app/routes/clientes.py

@clientes.route('/clientes/novo', methods=['POST'])
@login_required
def novo():
    # Capturando a data de nascimento com segurança
    data_nasc_str = request.form.get('data_nascimento')
    data_nasc = datetime.strptime(data_nasc_str, '%Y-%m-%d').date() if data_nasc_str else None

    novo_cliente = Cliente(
        nome=request.form.get('nome'),
        whatsapp=request.form.get('whatsapp'),
        logradouro=request.form.get('logradouro'),
        bairro=request.form.get('bairro'),
        cidade=request.form.get('cidade'),
        estado=request.form.get('estado'),
        complemento=request.form.get('complemento'),
        cpf=request.form.get('cpf'),
        data_nascimento=data_nasc,
        papelaria_id=current_user.papelaria_id
    )
    db.session.add(novo_cliente)
    db.session.commit()
    flash('Cliente cadastrado com sucesso!', 'success')
    return redirect(url_for('clientes.lista'))

@clientes.route('/clientes/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    if cliente.papelaria_id == current_user.papelaria_id:
        cliente.nome = request.form.get('nome')
        cliente.telefone = request.form.get('telefone')
        db.session.commit()
        flash('Cadastro atualizado!', 'success')
    return redirect(url_for('clientes.lista'))

@clientes.route('/clientes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    cliente = Cliente.query.get_or_404(id)
    if cliente.papelaria_id == current_user.papelaria_id:
        # Verifica se o cliente tem compras antes de excluir (opcional)
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente removido!', 'warning')
    return redirect(url_for('clientes.lista'))