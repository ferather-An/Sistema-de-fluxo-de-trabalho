import logging
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Session
from models import Base, Cliente, Proposta, Funcionario, Usuario
from datetime import datetime
from passlib.context import CryptContext

# Configuração do logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def cadastrar_cliente(db: Session, cnpj_cpf: str, nome_requerente: str, telefone: str, email: str):
    try:
        cliente_existente = db.query(Cliente).filter_by(cnpj_cpf=cnpj_cpf).first()
        if cliente_existente:
            logging.info(f"Cliente com CNPJ/CPF {cnpj_cpf} já cadastrado.")
            return cliente_existente.id
        novo_cliente = Cliente(
            cnpj_cpf=cnpj_cpf,
            nome_requerente=nome_requerente,
            telefone=telefone,
            email=email
        )
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        logging.info(f"Cliente '{nome_requerente}' cadastrado com sucesso! ID: {novo_cliente.id}, Dados: {novo_cliente}")
        print(f"Cliente '{nome_requerente}' cadastrado com sucesso! ID: {novo_cliente.id}")
        print(f"Dados do Cliente: CNPJ/CPF: {novo_cliente.cnpj_cpf}, Nome: {novo_cliente.nome_requerente}, Telefone: {novo_cliente.telefone}, Email: {novo_cliente.email}")
        
        # Confirmação e edição de dados
        while True:
            confirmacao = input("Os dados estão corretos? (s/n): ").lower()
            if confirmacao == 's':
                return novo_cliente.id
            elif confirmacao == 'n':
                campo = input("Qual campo você deseja editar? (cnpj_cpf/nome_requerente/telefone/email): ").lower()
                novo_valor = input(f"Digite o novo valor para {campo}: ")
                setattr(novo_cliente, campo, novo_valor)
                db.commit()
                db.refresh(novo_cliente)
                logging.info(f"Cliente '{nome_requerente}' atualizado com sucesso! ID: {novo_cliente.id}, Dados: {novo_cliente}")
                print(f"Cliente '{nome_requerente}' atualizado com sucesso! ID: {novo_cliente.id}")
                print(f"Dados do Cliente: CNPJ/CPF: {novo_cliente.cnpj_cpf}, Nome: {novo_cliente.nome_requerente}, Telefone: {novo_cliente.telefone}, Email: {novo_cliente.email}")
            else:
                print("Opção inválida. Por favor, digite 's' para sim ou 'n' para não.")
    except Exception as e:
        logging.error(f"Erro ao cadastrar cliente: {e}")

def cadastrar_proposta(db: Session, cliente_id: int, orgao_ambiental: str, tipo_processo: str,
                       renovacao: bool, numero_documento: str, validade: str, mensal: bool,
                       responsavel_id: int = None, tipo_trabalho: str = None, data_hora_reuniao: str = None,
                       prazo_entrega: str = None, observacoes: str = None):
    try:
        cliente = db.query(Cliente).filter_by(id=cliente_id).first()
        if not cliente:
            logging.info("Cliente não encontrado. Verifique o ID.")
            return
        nova_proposta = Proposta(
            cliente_id=cliente_id,
            orgao_ambiental=orgao_ambiental,
            tipo_processo=tipo_processo,
            renovacao=renovacao,
            numero_documento=numero_documento if renovacao else None,
            validade=datetime.strptime(validade, "%Y-%m-%d"),
            mensal=mensal,
            responsavel_id=responsavel_id,
            tipo_trabalho=tipo_trabalho,
            data_hora_reuniao=datetime.strptime(data_hora_reuniao, "%Y-%m-%d %H:%M") if data_hora_reuniao else None,
            prazo_entrega=datetime.strptime(prazo_entrega, "%Y-%m-%d %H:%M") if prazo_entrega else None,
            observacoes=observacoes
        )
        db.add(nova_proposta)
        db.commit()
        logging.info(f"Proposta cadastrada com sucesso! ID: {nova_proposta.id}, Dados: {nova_proposta}")
    except Exception as e:
        logging.error(f"Erro ao cadastrar proposta: {e}")

def cadastrar_funcionario(db: Session, nome: str):
    try:
        funcionario_existente = db.query(Funcionario).filter_by(nome=nome).first()
        if funcionario_existente:
            logging.info(f"Funcionário '{nome}' já cadastrado.")
            return funcionario_existente.id
        novo_funcionario = Funcionario(nome=nome)
        db.add(novo_funcionario)
        db.commit()
        db.refresh(novo_funcionario)
        logging.info(f"Funcionário '{nome}' cadastrado com sucesso! ID: {novo_funcionario.id}, Dados: {novo_funcionario}")
        return novo_funcionario.id
    except Exception as e:
        logging.error(f"Erro ao cadastrar funcionário: {e}")

def cadastrar_usuario(db: Session, username: str, password: str, is_admin: bool):
    try:
        hashed_password = Usuario.hash_password(password)
        novo_usuario = Usuario(username=username, hashed_password=hashed_password, is_admin=is_admin)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        logging.info(f"Usuário '{username}' cadastrado com sucesso! ID: {novo_usuario.id}, Dados: {novo_usuario}")
    except Exception as e:
        logging.error(f"Erro ao cadastrar usuário: {e}")

def autenticar_usuario(db: Session, username: str, password: str):
    try:
        usuario = db.query(Usuario).filter_by(username=username).first()
        if usuario and usuario.verify_password(password):
            logging.info(f"Usuário '{username}' autenticado com sucesso!")
            return usuario
        logging.warning(f"Falha na autenticação do usuário '{username}'.")
        return None
    except Exception as e:
        logging.error(f"Erro ao autenticar usuário: {e}")