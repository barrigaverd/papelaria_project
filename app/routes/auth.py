# 1. IMPORTAÇÕES
# Importe Blueprint, render_template, redirect, url_for, request, flash
from flask import Blueprint, render_template, redirect, url_for, request, flash
# Importe login_user do flask_login
from flask_login import login_user, login_required, logout_user
# Importe check_password_hash de werkzeug.security
from werkzeug.security import check_password_hash
# Importe seu modelo de Usuario
from models import Usuario

# 2. DEFINIÇÃO DO BLUEPRINT
# Crie o blueprint de autenticação: auth = Blueprint('auth', __name__)
auth = Blueprint('auth', __name__)

# 3. ROTA DE LOGIN
# Crie a rota '/login' aceitando métodos GET e POST
@auth.route("/login", methods = ("GET", "POST"))
def login_cliente():
# Se for GET: Apenas retorne o render_template do arquivo html que criamos.
    if request.method == "GET":
        return render_template('auth/login.html')
# Se for POST:
    if request.method == "POST":
# - Pegue o 'username' e a 'password' que vieram do formulário (request.form)
        username = request.form["username"]
        password = request.form["password"]
# - Busque o usuário no banco de dados filtrando pelo username
        user = Usuario.query.filter_by(username=username).first()
# - VERIFICAÇÃO:
#   - Se o usuário existir E a senha bater (use check_password_hash):
        if user and check_password_hash(user.password_hash, password):
#     - Chame login_user(usuario)
            login_user(user)
#     - Mande um flash de "Sucesso"
            flash(f"Usuario {user.username} logado com sucesso!")
#     - Redirecione para a página principal (estoque/dashboard)
            return redirect(url_for('main.dashboard'))
#   - Se algo falhar:
        else:  
#     - Mande um flash de "Usuário ou senha inválidos" com categoria 'error'
            flash("Usuário ou senha inválidos", "error")
#     - Retorne o render_template de login para ele tentar de novo
            return render_template('auth/login.html')
        
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso!")
    return redirect(url_for('auth.login_cliente'))