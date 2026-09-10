from sqlalchemy import select, text

from src.db import Session
from src.models import Product

def simple_select():
    with Session() as s:
        with s.begin():
            # Prepara a query
            query = select(Product)
            print(f"Query produzida: {query}")
            # Executa
            res = s.execute(query).all()
            print(f"Resultado obtido {res[0:10:3]}")


if __name__ == "__main__":
    simple_select()