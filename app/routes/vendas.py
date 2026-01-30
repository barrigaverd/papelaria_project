from flask import Blueprint, render_template, request, jsonify # Adicione render_template, request e jsonify aqui
from flask_login import login_required, current_user
from models import Produto, Movimentacao # Garanta que Movimentacao esteja importado
from extensions import db
from datetime import datetime


vendas = Blueprint('vendas', __name__)

@vendas.route('/caixa')
@login_required
def caixa():
    # Busca os produtos da papelaria logada
    produtos = Produto.query.filter_by(papelaria_id=current_user.papelaria_id).all()
    
    # DEBUG: Verifique se aparece um número maior que 0 no seu terminal
    print(f">>> Produtos encontrados para o caixa: {len(produtos)}")
    
    # IMPORTANTE: O nome aqui deve ser 'produtos'
    return render_template('vendas/caixa.html', produtos=produtos)

@vendas.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    dados = request.get_json()
    itens = dados.get('itens')
    forma_pagamento = dados.get('forma_pagamento') # DINHEIRO, PIX ou CARTAO

    if not itens:
        return jsonify({'status': 'error', 'message': 'O cupom está vazio.'}), 400

    try:
        # Iniciamos o processamento dos itens
        for item in itens:
            produto = Produto.query.get(item['produto_id'])
            
            # Verificação de segurança SaaS
            if not produto or produto.papelaria_id != current_user.papelaria_id:
                continue

            qtd_vendida = int(item['quantidade'])
            
            # 1. Baixa o estoque no banco
            produto.estoque_atual -= qtd_vendida

            # 2. Registra a movimentação (Histórico de Vendas)
            # DICA: Se o seu model Movimentacao ainda não tiver a coluna 'forma_pagamento',
            # você pode adicionar depois. Por ora, vamos focar no registro da saída.
            nova_venda = Movimentacao(
                produto_id=produto.id,
                papelaria_id=current_user.papelaria_id,
                tipo='SAIDA',
                categoria='VENDA',           # Adicionado para resolver o erro da imagem
                descricao='Venda PDV',       # Adicionado para evitar erro similar em 'descricao'
                quantidade=qtd_vendida,
                valor=float(item['preco_venda']) * qtd_vendida,
                forma_pagamento=forma_pagamento, # Agora salvando o que veio do JavaScript
                data=datetime.utcnow()
            )
            db.session.add(nova_venda)

        # 3. Salva todas as alterações de uma vez
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Venda finalizada com sucesso!'})

    except Exception as e:
        db.session.rollback() # Se der qualquer erro, cancela a baixa de estoque
        return jsonify({'status': 'error', 'message': str(e)}), 500