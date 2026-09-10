from sqlalchemy import select

from src.db import Session
from src.models import Product

def simple_select():
    with Session() as s:
        with s.begin():
            res = select(Product)
            print(f"Query produzida: {res}")

if __name__ == "__main__":
    simple_select()