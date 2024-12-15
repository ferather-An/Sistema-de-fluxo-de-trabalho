from database import SessionLocal, init_db
from crud import cadastrar_cliente, cadastrar_proposta, cadastrar_funcionario, cadastrar_usuario, autenticar_usuario
from utils import inicializar_funcionarios
from email_utils import enviar_email
from models import Funcionario, Proposta
from datetime import datetime, timedelta

def verificar_prazos():
    db = SessionLocal()
    propostas = db.query(Proposta).all()
    for proposta in propostas:
        if proposta.prazo_entrega and proposta.prazo_entrega - datetime.now() <= timedelta(days=3):
            funcionario = db.query(Funcionario).filter_by(id=proposta.responsavel_id).first()
            if funcionario:
                assunto = "Prazo de Entrega Aproximando"
                mensagem = f"Olá {funcionario.nome},\n\nO prazo de entrega da proposta '{proposta.tipo_processo}' para o cliente '{proposta.cliente.nome_requerente}' está se aproximando. O prazo é {proposta.prazo_entrega}.\n\nPor favor, certifique-se de que todas as tarefas necessárias sejam concluídas a tempo.\n\nObrigado!"
                enviar_email(funcionario.email, assunto, mensagem)
    db.close()

def main():
    init_db()
    inicializar_funcionarios()

    print("Sistema de Propostas - Azevedo Ambiental")
    
    usuario_logado = None

    while True:
        if not usuario_logado:
            print("\n1. Cadastrar Usuário\n2. Login\n3. Sair")
            escolha = input("Escolha uma opção: ")
            
            if escolha == "1":
                username = input("Nome de Usuário: ")
                password = input("Senha: ")
                is_admin = input("É administrador? (s/n): ").lower() == 's'
                db = SessionLocal()
                cadastrar_usuario(db, username, password, is_admin)
                db.close()
            
            elif escolha == "2":
                username = input("Nome de Usuário: ")
                password = input("Senha: ")
                db = SessionLocal()
                usuario_logado = autenticar_usuario(db, username, password)
                db.close()
                if usuario_logado:
                    print(f"Bem-vindo {username}!")
                else:
                    print("Nome de usuário ou senha incorretos.")
            
            elif escolha == "3":
                break
            
            else:
                print("Opção inválida.")
        else:
            print("\n1. Cadastrar Cliente\n2. Cadastrar Proposta\n3. Verificar Prazos e Enviar Notificações\n4. Logout")
            escolha = input("Escolha uma opção: ")
            
            if escolha == "1":
                cnpj_cpf = input("CNPJ/CPF: ")
                nome_requerente = input("Nome do Requerente: ")
                telefone = input("Telefone: ")
                email = input("Email: ")
                db = SessionLocal()
                cadastrar_cliente(db, cnpj_cpf, nome_requerente, telefone, email)
                db.close()
            
            elif escolha == "2":
                cliente_id = int(input("ID do Cliente: "))
                orgao_ambiental = input("Órgão Ambiental (Municipal/INEA/ANA/CETESB): ")
                tipo_processo = input("Tipo de Processo (LO, Avaliação Preliminar, LI, Certificados): ")
                renovacao = input("É renovação? (s/n): ").lower() == 's'
                numero_documento = input("Número da Documentação (se for renovação): ") if renovacao else None
                validade = input("Validade da Proposta (YYYY-MM-DD): ")
                mensal = input("É mensal? (s/n): ").lower() == 's'
                
                # Responsável pelo trabalho
                print("\nSelecione o responsável pelo trabalho:")
                db = SessionLocal()
                funcionarios = db.query(Funcionario).all()
                for idx, funcionario in enumerate(funcionarios):
                    print(f"{idx + 1}. {funcionario.nome}")
                responsavel_idx = int(input("Escolha uma opção: ")) - 1
                responsavel_id = funcionarios[responsavel_idx].id
                
                tipo_trabalho = input("Tipo de Trabalho (reunir documentação/planta/vistoria/cotação/relatório/criação de planilhas/cálculos): ")
                data_hora_reuniao = input("Data e Hora da Reunião (YYYY-MM-DD HH:MM): ")
                prazo_entrega = input("Prazo de Entrega (YYYY-MM-DD HH:MM): ")
                observacoes = input("Observações: ")
                
                cadastrar_proposta(db, cliente_id, orgao_ambiental, tipo_processo, renovacao, numero_documento, validade, mensal,
                                   responsavel_id, tipo_trabalho, data_hora_reuniao, prazo_entrega, observacoes)
                db.close()
            
            elif escolha == "3":
                verificar_prazos()
            
            elif escolha == "4":
                usuario_logado = None1
            
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main()