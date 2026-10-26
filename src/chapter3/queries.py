import rich
from psycopg2.errors import NotNullViolation
from sqlalchemy import func, label, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, subqueryload

from src import models
from src.db import Session


def find_product_by_name(name: str):
    with Session() as s, s.begin():
        query = select(models.Product).where(models.Product.name.ilike(f"%{name}%"))

        result = s.scalars(query).all()

        rich.print("[bold green underline]Resultado[/bold green underline]")
        for r in result:
            rich.print(f"[bold underline]Produto {r.name} by {r.manufacturer}[/bold underline]")
            rich.print(
                f"[bold underline]Todos os produtos de {r.manufacturer.name}[/bold underline]: {r.manufacturer.products} "
            )


def find_manufacturer(name: str):
    with Session() as s, s.begin():
        query = select(models.Manufacturer).where(models.Manufacturer.name.ilike(f"%{name}%"))

        res: models.Manufacturer | None = s.scalar(query)

        if res:
            rich.print(
                f"[bold underline]Produtos feitos por {name.lower()}[/bold underline]: {res.products}"
            )
            rich.print(
                f"[bold underline]Acessando novamente os produtos {res.products}[/bold underline]"
            )  # Não houve consulta novamente devido ao cache


def find_product(name: str):
    with Session() as s, s.begin():
        query = select(models.Product).where(models.Product.name.ilike(f"%{name}%"))

        res: models.Product | None = s.scalar(query)

        if res:
            rich.print(
                f"[bold underline]Fabricante de {name.lower()}[/bold underline]: {res.manufacturer}"
            )
            rich.print(
                f"[bold underline]Acessando novamente o fabricante {res.manufacturer}[/bold underline]"
            )  # Não houve consulta novamente devido ao cache


def join1():
    with Session() as s, s.begin():
        query = select(models.Product.name, models.Manufacturer.name).join(
            models.Manufacturer.products
        )
        rich.print(f"[bold green]Query gerada[/bold green]: {query}")

        res = s.execute(query).all()
        rich.print(res)


def join2():
    """Conta produtos por fabricantes"""
    with Session() as s, s.begin():
        num_prod = func.count(models.Product.name).label("num_prod")
        query = (
            select(models.Manufacturer.name, num_prod)
            .join(models.Product)
            .group_by(models.Manufacturer.name)
            .order_by(num_prod.desc())
        )
        result = s.execute(query).all()

        for man, qtd in result:
            rich.print(f"[bold green]{man}: {qtd} pcs[/bold green]")


def lazy_loading():
    """Padrão do select é lazy"""
    with Session() as s, s.begin():
        query = select(models.Product)
        result = s.scalars(query)  # 1 query para produtos

        for product in result:
            rich.print(
                f"{product.name}, {product.manufacturer.name}"
            )  # Executa queries repetidas para o manufacturer


"""
O padrão do SQLAlchemy é carregamento lazy.
Podemos alterar o carregamento padrão usando um loader, ou definindo no relacionamento do modelo.
"""


def eager_loading():
    with Session() as s, s.begin():
        query = select(models.Product).options(
            joinedload(models.Product.manufacturer)
        )  # 1 query com join

        res = s.scalars(query).all()
        for r in res:
            rich.print(r, r.manufacturer)


def eager_loading_subquery():
    """Carregamento eager usando uma subquery SELECT ... FROM (SELECT ...)"""
    with Session() as s, s.begin():
        query = select(models.Product).options(
            subqueryload(models.Product.manufacturer)
        )  # 1 query com join

        res = s.scalars(query).all()
        for r in res:
            rich.print(r, r.manufacturer)


def deleting_one():
    """
    Deletar do lado 1 não costuma causar problemas, pois não haveria ferimento de integridade relacional.
    A(b_id) B -> Deletar A não interfere em B
    A(b_id) B(x) -> Deletar B faz com que A aponte para valores que não existem, causando erro de integridade relacional
    """
    with Session() as s, s.begin():
        rich.print("Deletando entidade do lado 1")
        p: models.Product | None = s.get(models.Product, 20)

        if p:
            s.delete(p)
            rich.print("Deletado com sucesso")

        try:
            rich.print("Tentando deletar uma entidade do lado N. Vai gerar erro de referência")
            m: models.Manufacturer | None = s.get(models.Manufacturer, 14)
            if m:
                s.delete(m)
        except (IntegrityError, NotNullViolation):
            rich.print("[bold red]Erro de integridade referencial[/bold red]")


if __name__ == "__main__":
    # find_product_by_name('Cor')
    # find_manufacturer('teXas')
    # find_product('Electron')
    # join1()
    # join2()
    # lazy_loading()
    # eager_loading()
    # eager_loading_subquery()
    deleting_one()
