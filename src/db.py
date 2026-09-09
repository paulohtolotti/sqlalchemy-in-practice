from dotenv import load_dotenv
from os import environ

from sqlalchemy import MetaData, create_engine, Engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
try:
    DB_URL = environ['ALL_ACCESS_DB_CONN_STRING']
except KeyError as e:
    traceback = e.__traceback__
    print(f"Error while fetching database url string: {e.with_traceback(traceback)}")

engine_all_access: Engine = create_engine(DB_URL, echo=True, echo_pool=True)

class Model(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

if __name__ == "__main__":
    """
        Métodos de criação e deleção de tabelas.
        Não realizam alterações. Em produção é necessário usar uma ferramenta de migração.
    """
    Model.metadata.drop_all(engine_all_access)
    Model.metadata.create_all(engine_all_access)