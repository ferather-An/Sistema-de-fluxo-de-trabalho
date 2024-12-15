import logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from passlib.context import CryptContext

# Configuração do logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do banco de dados
DATABASE_URL = "sqlite:///propostas.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo de Clientes
class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnpj_cpf = Column(String, unique=True, nullable=False)
    nome_requerente = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    propostas = relationship("Proposta", back_populates="cliente")

# Modelo de Propostas
class Proposta(Base):
    __tablename__ = 'propostas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    orgao_ambiental = Column(String, nullable=False)  # Ex: Municipal, INEA
    tipo_processo = Column(String, nullable=False)  # Ex: LO, LI
    renovacao = Column(Boolean, default=False)  # True se for renovação
    numero_documento = Column(String, nullable=True)  # Número se for renovação
    validade = Column(Date, nullable=False)
    mensal = Column(Boolean, default=False)  # True se for mensal
    responsavel_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=True)
    tipo_trabalho = Column(String, nullable=True)
    data_hora_reuniao = Column(DateTime, nullable=True)
    prazo_entrega = Column(DateTime, nullable=True)
    observacoes = Column(String, nullable=True)
    cliente = relationship("Cliente", back_populates="propostas")
    responsavel = relationship("Funcionario", back_populates="propostas")

# Modelo de Funcionários
class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, unique=True, nullable=False)
    propostas = relationship("Proposta", back_populates="responsavel")

# Criar tabelas no banco
try:
    Base.metadata.create_all(engine)
    logging.info("Tabelas criadas com sucesso.")
except Exception as e:
    logging.error(f"Erro ao criar tabelas: {e}")

# Funções de Cadastro
def cadastrar_cliente(cnpj_cpf, nome_requerente, telefone, email):
    try:
        cliente_existente = session.query(Cliente).filter_by(cnpj_cpf=cnpj_cpf).first()
        if cliente_existente:
            logging.info(f"Cliente com CNPJ/CPF {cnpj_cpf} já cadastrado.")
            return cliente_existente.id
        novo_cliente = Cliente(
            cnpj_cpf=cnpj_cpf,
            nome_requerente=nome_requerente,
            telefone=telefone,
            email=email
        )
        session.add(novo_cliente)
        session.commit()
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
                session.commit()
                session.refresh(novo_cliente)
                logging.info(f"Cliente '{nome_requerente}' atualizado com sucesso! ID: {novo_cliente.id}, Dados: {novo_cliente}")
                print(f"Cliente '{nome_requerente}' atualizado com sucesso! ID: {novo_cliente.id}")
                print(f"Dados do Cliente: CNPJ/CPF: {novo_cliente.cnpj_cpf}, Nome: {novo_cliente.nome_requerente}, Telefone: {novo_cliente.telefone}, Email: {novo_cliente.email}")
            else:
                print("Opção inválida. Por favor, digite 's' para sim ou 'n' para não.")
    except Exception as e:
        logging.error(f"Erro ao cadastrar cliente: {e}")

def cadastrar_proposta(cliente_id, orgao_ambiental, tipo_processo, renovacao, numero_documento, validade, mensal,
                       responsavel_id=None, tipo_trabalho=None, data_hora_reuniao=None,
                       prazo_entrega=None, observacoes=None):
    try:
        cliente = session.query(Cliente).filter_by(id=cliente_id).first()
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
        session.add(nova_proposta)
        session.commit()
        logging.info(f"Proposta cadastrada com sucesso! ID: {nova_proposta.id}, Dados: {nova_proposta}")
    except Exception as e:
        logging.error(f"Erro ao cadastrar proposta: {e}")

def cadastrar_funcionario(nome):
    try:
        funcionario_existente = session.query(Funcionario).filter_by(nome=nome).first()
        if funcionario_existente:
            logging.info(f"Funcionário '{nome}' já cadastrado.")
            return funcionario_existente.id
        novo_funcionario = Funcionario(nome=nome)
        session.add(novo_funcionario)
        session.commit()
        logging.info(f"Funcionário '{nome}' cadastrado com sucesso! ID: {novo_funcionario.id}, Dados: {novo_funcionario}")
        return novo_funcionario.id
    except Exception as e:
        logging.error(f"Erro ao cadastrar funcionário: {e}")

# Interface de Teste
if __name__ == "__main__":
    # Cadastrar funcionários
    funcionarios_nomes = ["Ana Júlia", "André", "Italo", "Isabel", "João", "Mateus", "Raissa", "Raul"]
    for nome in funcionarios_nomes:
        cadastrar_funcionario(nome)

    print("Sistema de Propostas - Azevedo Ambiental")
    
    while True:
        print("\n1. Cadastrar Cliente\n2. Cadastrar Proposta\n3. Sair")
        escolha = input("Escolha uma opção: ")
        
        if escolha == "1":
            cnpj_cpf = input("CNPJ/CPF: ")
            nome_requerente = input("Nome do Requerente: ")
            telefone = input("Telefone: ")
            email = input("Email: ")
            cadastrar_cliente(cnpj_cpf, nome_requerente, telefone, email)
        
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
            for idx, nome in enumerate(funcionarios_nomes):
                print(f"{idx + 1}. {nome}")
            responsavel_idx = int(input("Escolha uma opção: ")) - 1
            responsavel_id = session.query(Funcionario).filter_by(nome=funcionarios_nomes[responsavel_idx]).first().id
            tipo_trabalho = input("Tipo de Trabalho (reunir documentação/planta/vistoria/cotação/relatório/criação de planilhas/cálculos): ")
            data_hora_reuniao = input("Data e Hora da Reunião (YYYY-MM-DD HH:MM): ")
            prazo_entrega = input("Prazo de Entrega (YYYY-MM-DD HH:MM): ")
            observacoes = input("Observações: ")
            
            cadastrar_proposta(cliente_id, orgao_ambiental, tipo_processo, renovacao, numero_documento, validade, mensal,
                               responsavel_id, tipo_trabalho, data_hora_reuniao, prazo_entrega, observacoes)
        
        elif escolha == "3":
            break
        
        else:
            print("Opção inválida.")