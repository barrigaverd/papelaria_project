from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from models import Produto, Servico, Movimentacao, FormaPagamento, Cliente
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func
import uuid

vendas = Blueprint('vendas', __name__)

@vendas.route('/caixa')
@login_required
def caixa():
    # Carrega dados iniciais para o PDV
    formas_pagamento = FormaPagamento.query.filter_by(
        papelaria_id=current_user.papelaria_id, 
        ativo=True
    ).all()
    clientes = Cliente.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    now = datetime.now()
    
    return render_template('vendas/caixa.html', 
                           formas_pagamento=formas_pagamento, 
                           now=now, 
                           clientes=clientes)

@vendas.route('/buscar_itens')
@login_required
def buscar_itens():
    query = request.args.get('q', '').strip()
    
    # Se a busca estiver vazia, pegamos os primeiros 50 itens em ordem alfabética
    if not query:
        produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).order_by(Produto.nome.asc()).limit(50).all()
        servicos = Servico.query.filter_by(papelaria_id=current_user.papelaria_id).order_by(Servico.descricao.asc()).limit(50).all()
    else:
        # Lógica de busca que você já tem...
        produtos = Produto.query.filter(Produto.nome.ilike(f'%{query}%')).all()
        servicos = Servico.query.filter(Servico.descricao.ilike(f'%{query}%')).all()

    # Formata a lista para o JSON
    res = []
    for p in produtos:
        res.append({'id': p.id, 'nome': p.nome, 'preco': p.preco_venda, 'estoque': p.estoque_atual, 'tipo': 'produto'})
    for s in servicos:
        res.append({'id': s.id, 'nome': s.descricao, 'preco': s.preco, 'estoque': 'N/A', 'tipo': 'serviço'})
    
    return jsonify(res)

@vendas.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    dados = request.get_json()
    itens = dados.get('itens')
    cliente_id = dados.get('cliente_id')
    venda_id = str(uuid.uuid4()) # Gera o ID único da venda
    
    # Pegamos a data enviada ou usamos a atual
    data_venda_str = dados.get('data_venda')
    data_final = datetime.strptime(data_venda_str, '%Y-%m-%d') if data_venda_str else datetime.now()

    for item in itens:
        # --- AQUI ESTÁ A CORREÇÃO ---
        # Precisamos descobrir o nome do item para salvar no cupom
        nome_para_descricao = ""
        
        if item['tipo'] == 'produto':
            prod = Produto.query.get(item['id'])
            nome_para_descricao = prod.nome # Pega o nome da tabela Produto
            # Aproveite para baixar o estoque aqui
            prod.estoque_atual -= int(item['quantidade'])
        else:
            serv = Servico.query.get(item['id'])
            nome_para_descricao = serv.descricao # Pega a descrição da tabela Servico

        # Criamos a movimentação com a descrição preenchida
        nova_mov = Movimentacao(
            papelaria_id=current_user.papelaria_id,
            tipo='SAIDA',
            categoria='Venda' if item['tipo'] == 'produto' else 'Serviço',
            descricao=nome_para_descricao, # <--- AGORA O NOME VAI PARA O CUPOM
            valor=float(item['preco']) * int(item['quantidade']),
            quantidade=int(item['quantidade']),
            produto_id=item['id'] if item['tipo'] == 'produto' else None,
            servico_id=item['id'] if item['tipo'] == 'servico' else None,
            venda_id=venda_id,
            cliente_id=cliente_id if cliente_id else None,
            data=data_final
        )
        db.session.add(nova_mov)

    db.session.commit()
    return jsonify({"status": "sucesso", "venda_id": venda_id})

@vendas.route('/relatorio')
@login_required
def relatorio():
    data_fim = request.args.get('data_fim', datetime.now().strftime('%Y-%m-%d'))
    data_inicio = request.args.get('data_inicio', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    page = request.args.get('page', 1, type=int)

    dt_ini = datetime.strptime(data_inicio, '%Y-%m-%d')
    dt_fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)

    total_valor = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        Movimentacao.data >= dt_ini,
        Movimentacao.data < dt_fim
    ).scalar() or 0
    total_produtos = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        Movimentacao.produto_id != None, # Filtra apenas o que tem produto_id
        Movimentacao.data >= dt_ini,
        Movimentacao.data < dt_fim
    ).scalar() or 0

    total_servicos = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        Movimentacao.servico_id != None, # Filtra apenas o que tem servico_id
        Movimentacao.data >= dt_ini,
        Movimentacao.data < dt_fim
    ).scalar() or 0
    query_agrupada = db.session.query(
        Movimentacao.venda_id,
        func.max(Movimentacao.data).label('data'),
        func.max(Movimentacao.forma_pagamento).label('forma_pagamento'),
        func.sum(Movimentacao.valor).label('total_venda'),
        func.max(Cliente.nome).label('nome_cliente') 
    ).join(Cliente, Movimentacao.cliente_id == Cliente.id, isouter=True) \
    .filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        Movimentacao.data >= dt_ini,
        Movimentacao.data < dt_fim
    ).group_by(Movimentacao.venda_id).order_by(func.max(Movimentacao.data).desc())

    pagination = query_agrupada.paginate(page=page, per_page=20)
    
    qtd_tickets = query_agrupada.count()
    ticket_medio = total_valor / qtd_tickets if qtd_tickets > 0 else 0

    itens_detalhados = Movimentacao.query.filter_by(
        papelaria_id=current_user.papelaria_id, 
        tipo='SAIDA'
    ).all()
    
    formas_pagamento_global = FormaPagamento.query.filter_by(papelaria_id=current_user.papelaria_id).all()

    return render_template('vendas/relatorio.html', 
                           vendas=pagination.items,
                           pagination=pagination,
                           total_valor=total_valor,
                           qtd_vendas=qtd_tickets,
                           ticket_medio=ticket_medio,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           detalhes=itens_detalhados,
                           formas_pagamento_global=formas_pagamento_global,
                           total_produtos=total_produtos,
                           total_servicos=total_servicos)

@vendas.route('/relatorio/editar/<int:id>', methods=['POST'])
@login_required
def editar_venda_item(id):
    mov = Movimentacao.query.get_or_404(id)
    if mov.papelaria_id != current_user.papelaria_id:
        abort(403)

    qtd_antiga = mov.quantidade
    nova_qtd = int(request.form.get('quantidade'))
    novo_preco_unit = float(request.form.get('preco_venda'))

    # Se for produto, ajusta estoque
    if mov.produto_id:
        diferenca = qtd_antiga - nova_qtd
        mov.produto.estoque_atual += diferenca

    mov.quantidade = nova_qtd
    mov.valor = nova_qtd * novo_preco_unit
    mov.forma_pagamento = request.form.get('forma_pagamento')
    
    db.session.commit()
    flash("Item atualizado com sucesso!", "success")
    return redirect(url_for('vendas.relatorio'))

@vendas.route('/relatorio/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_venda(id):
    mov = Movimentacao.query.get_or_404(id)
    if mov.papelaria_id != current_user.papelaria_id:
        abort(403)
    
    # Se for produto, devolve ao estoque
    if mov.produto_id:
        mov.produto.estoque_atual += mov.quantidade
    
    db.session.delete(mov)
    db.session.commit()
    flash("Item removido do ticket!", "warning")
    return redirect(url_for('vendas.relatorio'))

@vendas.route('/relatorio/estornar_ticket/<string:venda_id>', methods=['POST'])
@login_required
def estornar_ticket(venda_id):
    itens = Movimentacao.query.filter_by(
        venda_id=venda_id, 
        papelaria_id=current_user.papelaria_id
    ).all()

    try:
        for item in itens:
            if item.produto_id:
                item.produto.estoque_atual += item.quantidade
            db.session.delete(item)
        
        db.session.commit()
        flash(f"Venda #{venda_id} cancelada inteira!", "success")
    except:
        db.session.rollback()
        flash("Erro ao estornar.", "danger")

    return redirect(url_for('vendas.relatorio'))

@vendas.route('/cupom/<venda_id>')
@login_required
def gerar_cupom(venda_id):
    # Busca todas as movimentações com esse ID de venda
    itens = Movimentacao.query.filter_by(venda_id=venda_id).all()
    if not itens:
        return "Venda não encontrada", 404
        
    total = sum(item.valor for item in itens)
    # Pega o cliente do primeiro item (todos são iguais na mesma venda)
    cliente = itens[0].cliente
    
    return render_template('vendas/cupom.html', 
                           itens=itens, 
                           total=total, 
                           cliente=cliente, 
                           data=itens[0].data)