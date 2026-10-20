import rich
from sqlalchemy import select

from src import models
from src.db import Session


def find_product_by_name(name: str):
    with Session() as s, s.begin():
        query = select(
            models.Product
        ).where(
            models.Product.name
            .ilike(f"%{name}%")
        )

        result = s.scalars(query).all()

        rich.print("[bold green underline]Resultado[/bold green underline]")
        for r in result:
            rich.print(f"[bold underline]Produto {r.name} by {r.manufacturer}[/bold underline]")
            rich.print(f"[bold underline]Todos os produtos de {r.manufacturer.name}[/bold underline]: {r.manufacturer.products} ")

def find_manufacturer(name: str):
    with Session() as s, s.begin():
        query = select(
            models.Manufacturer
        ).where(
            models.Manufacturer.name.ilike(f"%{name}%")
        )

        res = s.scalar(query)

        rich.print(f"[bold underline]Produtos feitos por {name.lower()}[/bold underline]: {res.products}")

def join1():
    with Session() as s, s.begin():
        query = select(models.Product.name, models.Manufacturer.name).join(
            models.Manufacturer.products
        )
        rich.print(f"[bold green]Query gerada[/bold green]: {query}")
        
        res = s.execute(query).all()
        rich.print(res)
        
        

if __name__ == "__main__":
    # find_product_by_name('Cor')
    # find_manufacturer('teXas')
    join1()