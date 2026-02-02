import os
from run import create_app
from extensions import db
from models import Papelaria, Usuario, FormaPagamento, Categoria, Movimentacao, Produto, Servico, Cliente, Despesa
from werkzeug.security import generate_password_hash

app = create_app()

def excluir_papelaria():
    with app.app_context():
        papelarias = Papelaria.query.all()
        if not papelarias:
            print("\n❌ Nenhuma papelaria cadastrada.")
            return

        print("\n--- 🗑️ EXCLUIR PAPELARIA ---")
        for p in papelarias:
            print(f"[{p.id}] - {p.nome_fantasia} (CNPJ: {p.cnpj_cpf})")
        
        try:
            id_excluir = int(input("\nDigite o ID da papelaria que deseja apagar (ou 0 para cancelar): "))
            if id_excluir == 0: return

            papelaria = Papelaria.query.get(id_excluir)
            if papelaria:
                confirmar = input(f"⚠️ TEM CERTEZA? Isso apagará TODOS os dados de '{papelaria.nome_fantasia}' (Vendas, Produtos, Logos, etc). [S/N]: ")
                if confirmar.upper() == 'S':
                    # 1. Remove o arquivo da logo do disco se existir
                    if papelaria.logo_path:
                        logo_full_path = os.path.join(app.root_path, 'static', papelaria.logo_path)
                        if os.path.exists(logo_full_path):
                            os.remove(logo_full_path)
                    
                    # 2. O SQLAlchemy cuida do restante se as relações tiverem cascade='all, delete-orphan'
                    # Caso contrário, apagamos manualmente as tabelas ligadas:
                    Usuario.query.filter_by(papelaria_id=id_excluir).delete()
                    Produto.query.filter_by(papelaria_id=id_excluir).delete()
                    Servico.query.filter_by(papelaria_id=id_excluir).delete()
                    Movimentacao.query.filter_by(papelaria_id=id_excluir).delete()
                    Despesa.query.filter_by(papelaria_id=id_excluir).delete()
                    Cliente.query.filter_by(papelaria_id=id_excluir).delete()
                    FormaPagamento.query.filter_by(papelaria_id=id_excluir).delete()
                    Categoria.query.filter_by(papelaria_id=id_excluir).delete()
                    
                    db.session.delete(papelaria)
                    db.session.commit()
                    print(f"\n✅ Papelaria {id_excluir} removida com sucesso!")
            else:
                print("\n❌ ID não encontrado.")
        except ValueError:
            print("\n❌ Entrada inválida.")

def cadastrar_papelaria():
    with app.app_context():
        print("\n--- 📦 CADASTRAR NOVA PAPELARIA ---")
        nome_loja = input("Nome da Papelaria: ")
        username_admin = input("Usuário Admin: ")
        
        # 1. Verificação de segurança: O username deve ser único no sistema todo
        if Usuario.query.filter_by(username=username_admin).first():
            print(f"\n❌ Erro: O usuário '{username_admin}' já está cadastrado. Tente outro nome.")
            return

        senha_admin = input("Senha Admin: ")

        # 2. Criar a Papelaria (Tenant)
        nova_papelaria = Papelaria(
            nome_fantasia=nome_loja, 
            cnpj_cpf="00.000.000/0001-00" # Valor padrão inicial
        )
        db.session.add(nova_papelaria)
        db.session.flush() # Gera o ID da papelaria para usarmos nos relacionamentos abaixo

        # 3. Criar o Usuário Administrador da Loja
        admin = Usuario(
            username=username_admin, 
            password_hash=generate_password_hash(senha_admin), 
            papelaria_id=nova_papelaria.id
        )
        db.session.add(admin)

        # 4. Definir as Categorias Padrão (Agora com o campo 'tipo' obrigatório)
        # Os tipos devem corresponder ao que você definiu no modelo (ex: Produto, Serviço)
        categorias_padrao = [
            {'desc': 'Escolar', 'tipo': 'Produto'},
            {'desc': 'Escritório', 'tipo': 'Produto'},
            {'desc': 'Serviços', 'tipo': 'Serviço'},
            {'desc': 'Presentes', 'tipo': 'Produto'}
        ]

        for c in categorias_padrao:
            db.session.add(Categoria(
                descricao=c['desc'], 
                tipo=c['tipo'], 
                papelaria_id=nova_papelaria.id
            ))

        # 5. Definir Formas de Pagamento Padrão
        for f in ['Dinheiro', 'Cartão de Crédito', 'Pix']:
            db.session.add(FormaPagamento(
                nome=f, 
                papelaria_id=nova_papelaria.id
            ))

        # 6. Salvar tudo no banco de dados
        try:
            db.session.commit()
            print(f"\n✅ Loja '{nome_loja}' criada com sucesso!")
            print(f"🔑 Usuário: {username_admin} | Senha: {senha_admin}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao salvar no banco de dados: {e}")

if __name__ == "__main__":
    while True:
        print("\n======= 🔧 PAINEL DE CONTROLE SAAS =======")
        print("1. Cadastrar Nova Papelaria")
        print("2. Excluir Papelaria Existente")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1': cadastrar_papelaria()
        elif opcao == '2': excluir_papelaria()
        elif opcao == '3': break
        else: print("Opção inválida.")