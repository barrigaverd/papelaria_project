from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Categoria, FormaPagamento
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

configuracoes = Blueprint('configuracoes', __name__)

@configuracoes.route('/geral', methods=['GET', 'POST'])
@login_required
def geral():
    papelaria = current_user.papelaria
    
    if request.method == 'POST':
        # 1. Atualizar Dados da Empresa
        papelaria.nome_fantasia = request.form.get('nome_fantasia')
        papelaria.cnpj_cpf = request.form.get('cnpj_cpf')
        papelaria.email = request.form.get('email')
        papelaria.telefones = request.form.get('telefones')
        papelaria.chave_pix = request.form.get('chave_pix')
        papelaria.site = request.form.get('site')
        
        # Endereço
        papelaria.cep = request.form.get('cep')
        papelaria.logradouro = request.form.get('logradouro')
        papelaria.numero = request.form.get('numero')
        papelaria.bairro = request.form.get('bairro')
        papelaria.cidade = request.form.get('cidade')
        papelaria.estado = request.form.get('estado')
        papelaria.complemento = request.form.get('complemento')

        # 2. Tratamento da Logo (Upload)
        file = request.files.get('logo')
        if file and file.filename != '':
            # Gera o nome do arquivo
            extension = os.path.splitext(file.filename)[1]
            filename = f"logo_{papelaria.id}{extension}"
            
            # Caminho ABSOLUTO para salvar o arquivo (Onde o Python grava)
            # Isso evita o erro de "folder not found"
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
            os.makedirs(upload_path, exist_ok=True) # Cria a pasta se não existir
            
            full_path = os.path.join(upload_path, filename)
            file.save(full_path)
            
            # Caminho RELATIVO para o banco de dados (O que o HTML vai ler)
            # IMPORTANTE: Não deve começar com 'static/'
            papelaria.logo_path = f"uploads/logos/{filename}"
            
            # Força o commit imediatamente para garantir a gravação
            db.session.add(papelaria)
            db.session.commit()
        # 3. Alteração de Senha (se preenchida)
        nova_senha = request.form.get('nova_senha')
        if nova_senha:
            current_user.password_hash = generate_password_hash(nova_senha)

        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('configuracoes.geral'))

    return render_template('configuracoes/geral.html', papelaria=papelaria)

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