import logging
from sqlalchemy.orm import Session
from models import Usuario

def autenticar_admin(db: Session, username: str, password: str):
    try:
        usuario = db.query(Usuario).filter_by(username=username, is_admin=True).first()
        if usuario and usuario.verify_password(password):
            logging.info(f"Administrador '{username}' autenticado com sucesso!")
            return usuario
        logging.warning(f"Falha na autenticação do administrador '{username}'.")
        return None
    except Exception as e:
        logging.error(f"Erro ao autenticar administrador: {e}")