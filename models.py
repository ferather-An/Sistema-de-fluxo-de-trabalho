from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    @classmethod
    def hash_password(cls, password):
        return pwd_context.hash(password)

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnpj_cpf = Column(String, unique=True, nullable=False)
    nome_requerente = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    propostas = relationship("Proposta", back_populates="cliente")

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

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, unique=True, nullable=False)
    propostas = relationship("Proposta", back_populates="responsavel")