from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from db import engine_all_access
from models import Product


def basic_transaction():
    """
    Exemplo básico de uma transação.
    Sessão é aberto com um gerenciador de contexto with as
    O uso de try except garante que a transação será sempre consistente
    """
    with Session(engine_all_access) as session:
        try:
            pc = Product(name="Macintosh", year=1980, manufacturer="Apple")
            session.add(pc)
            session.commit()
            session.refresh(pc) # Atualiza com os dados inseridos no banco
        except SQLAlchemyError as exc:
            session.rollback()
            print(f"Error while adding new product {exc}")
        finally:
            print(pc)

def better_transaction():
    """
    Exemplo mais sofisticado de transação.
    Função sessionmaker é uma factory, que cria uma classe para a sessão, de maneira que ela pode ser reaproveitada
    em vários módulos.
    O try, except, commit e rollback é substituído pelo gerenciador de contexto + método begin.
    Qualquer erro faz o rollback da transação
    """
    Session = sessionmaker(engine_all_access)

    with Session() as session:
        with session.begin():
            wc =  Product(name="Water Cooler", manufacturer="Dell", year=2016)
            session.add(wc)
            print(wc)