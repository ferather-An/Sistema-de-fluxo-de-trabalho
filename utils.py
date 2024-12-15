from database import SessionLocal
from models import Funcionario

def inicializar_funcionarios():
    funcionarios_nomes = ["Ana Júlia", "André", "Italo", "Isabel", "Larissa", "João", "Mateus", "Raissa", "Raul"]
    db = SessionLocal()
    for nome in funcionarios_nomes:
        funcionario_existente = db.query(Funcionario).filter_by(nome=nome).first()
        if not funcionario_existente:
            novo_funcionario = Funcionario(nome=nome)
            db.add(novo_funcionario)
            db.commit()
            db.refresh(novo_funcionario)
            print(f"Funcionário '{nome}' cadastrado com sucesso!")
    db.close()