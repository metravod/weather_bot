from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, User
from settings import database_config


def add_user(tg_id):
    engine = create_engine(database_config.url, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if user is None:
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        session.commit()
