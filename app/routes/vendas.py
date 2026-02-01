from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for # Adicione render_template, request e jsonify aqui
from flask_login import login_required, current_user
from models import Produto, Movimentacao, FormaPagamento, Cliente # Garanta que Movimentacao esteja importado
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func


vendas = Blueprint('vendas', __name__)

@vendas.route('/caixa')
@login_required
def caixa():
    # Busca os produtos da papelaria logada
    produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    formas_pagamento = FormaPagamento.query.filter_by(
        papelaria_id=current_user.papelaria_id, 
        ativo=True
    ).all()
    now=datetime.now()
    clientes = Cliente.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    
    return render_template('vendas/caixa.html', produtos=produtos, formas_pagamento=formas_pagamento, now=now, clientes=clientes)

@vendas.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    dados = request.get_json()
    itens = dados.get('itens', [])
    lista_pagos = dados.get('pagamentos', []) # Agora é uma lista
    data_str = dados.get('data_venda')

    # Concatenamos as formas para o banco: "Dinheiro (R$ 10), Pix (R$ 20)"
    formas_resumo = ", ".join([f"{p['forma']} (R$ {p['valor']:.2f})" for p in lista_pagos])

    if data_str:
        data_final = datetime.combine(datetime.strptime(data_str, '%Y-%m-%d'), datetime.now().time())
    else:
        data_final = datetime.now()

    for item in itens:
        produto = Produto.query.get(item['produto_id'])
        if produto:
            nova_venda = Movimentacao(
                produto_id=produto.id,
                papelaria_id=current_user.papelaria_id,
                tipo='SAIDA',
                categoria='Venda PDV', # Categoria obrigatória
                valor=item['preco_venda'] * item['quantidade'],
                quantidade=item['quantidade'],
                forma_pagamento=formas_resumo,
                data=data_final
            )
            produto.estoque_atual -= item['quantidade']
            db.session.add(nova_venda)
    
    db.session.commit()
    return jsonify({'status': 'success'})
    
@vendas.route('/relatorio')
@login_required
def relatorio():
    # 1. Filtros de Data (Default: últimos 30 dias)
    data_fim = request.args.get('data_fim', datetime.now().strftime('%Y-%m-%d'))
    data_inicio = request.args.get('data_inicio', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    page = request.args.get('page', 1, type=int)

    # Convertendo strings para objetos datetime para o filtro do banco
    dt_ini = datetime.strptime(data_inicio, '%Y-%m-%d')
    dt_fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1) # Inclui o dia final até 23:59

    # 2. Query Base
    query = Movimentacao.query.filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        Movimentacao.data >= dt_ini,
        Movimentacao.data < dt_fim
    )

    # 3. Cálculos do Mini-Dashboard
    total_vendas_valor = db.session.query(func.sum(Movimentacao.valor)).filter(
        Movimentacao.papelaria_id == current_user.papelaria_id,
        Movimentacao.tipo == 'SAIDA',
        Movimentacao.data >= dt_ini,
        Movimentacao.data < dt_fim
    ).scalar() or 0

    qtd_vendas = query.count()
    ticket_medio = total_vendas_valor / qtd_vendas if qtd_vendas > 0 else 0

    # 4. Paginação da Lista
    pagination = query.order_by(Movimentacao.data.desc()).paginate(page=page, per_page=25)
    vendas_lista = pagination.items

    formas_pagamento_global = FormaPagamento.query.filter_by(papelaria_id=current_user.papelaria_id).all()

    return render_template('vendas/relatorio.html', 
                           vendas=vendas_lista, 
                           pagination=pagination,
                           total_valor=total_vendas_valor,
                           qtd_vendas=qtd_vendas,
                           ticket_medio=ticket_medio,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           formas_pagamento_global=formas_pagamento_global)

@vendas.route('/relatorio/editar/<int:id>', methods=['POST'])
@login_required
def editar_venda_item(id):
    mov = Movimentacao.query.get_or_404(id)
    if mov.papelaria_id != current_user.papelaria_id:
        abort(403)

    # Dados antigos para o cálculo de estoque
    produto = mov.produto
    qtd_antiga = mov.quantidade or 1
    
    # Novos dados do formulário
    nova_qtd = int(request.form.get('quantidade'))
    novo_preco_unit = float(request.form.get('preco_venda'))
    nova_forma = request.form.get('forma_pagamento')

    # Ajuste de Estoque Matemático:
    # Estoque = Estoque + (Qtd Antiga - Qtd Nova)
    if produto:
        diferenca = qtd_antiga - nova_qtd
        produto.estoque_atual += diferenca

    # Atualiza a movimentação
    mov.quantidade = nova_qtd
    mov.valor = nova_qtd * novo_preco_unit
    mov.forma_pagamento = nova_forma
    
    db.session.commit()
    flash("Venda e estoque atualizados com sucesso!", "success")
    return redirect(url_for('vendas.relatorio'))

@vendas.route('/relatorio/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_venda(id):
    # Busca a movimentação (venda)
    mov = Movimentacao.query.get_or_404(id)
    
    # Segurança: garante que a venda pertence à papelaria do usuário logado
    if mov.papelaria_id != current_user.papelaria_id:
        abort(403)
    
    # 1. Devolve o produto ao estoque (se houver um produto vinculado)
    if mov.produto:
        # Soma a quantidade da venda de volta ao estoque atual
        mov.produto.estoque_atual += (mov.quantidade or 1)
    
    # 2. Apaga o registro da venda
    db.session.delete(mov)
    db.session.commit()
    
    flash("Venda excluída e estoque atualizado com sucesso!", "warning")
    return redirect(url_for('vendas.relatorio'))