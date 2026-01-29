from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Produto

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