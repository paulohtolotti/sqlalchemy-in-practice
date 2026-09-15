from sqlalchemy import func, or_, select

from src.db import Session
from src.models import Product


def exercise1():
    """Primeiros 3 Computadores, em ordem alfabética, do ano 1983"""
    with Session() as session, session.begin():
        query = select(Product).order_by(Product.name.asc()).where(Product.year == 1983).limit(3)
        res = session.scalars(query).all()
        for idx, r in enumerate(res, start=1):
            print(f"#{idx}: {r}")

def exercise2():
    """Computadores que usam a CPU Z80"""
    with Session() as session, session.begin():
        query = select(Product).where(Product.cpu.ilike("%Z80%"))
        result = session.scalars(query).all()

        for idx, r in enumerate(result):
            print(f"#{idx}: {r.name}, CPU: {r.cpu}")
            
def exercise3():
    """Computadores que usam a CPU Z80, 6502 ou compatíveis, criados antes de 1980 e em ordem alfabética"""
    with Session() as session, session.begin():
        query = (
            select(Product)
            .where(or_(Product.cpu.ilike("%Z80%"), Product.cpu.ilike("%6502%")))
            .where(Product.year < 1990)
            .order_by(Product.name.asc())
        )
        result = session.scalars(query).all()

        for idx, r in enumerate(result):
            print(f"#{idx}: {r.name}, CPU: {r.cpu} - {r.year}")

def exercise4():
    """Todos os fabricantes que construíram computadores na década de 80"""
    with Session() as session, session.begin():
        query = select(Product.manufacturer).where(Product.year.between(1980, 1989)).distinct()
        result = session.scalars(query).all()

        for idx, r in enumerate(result):
            print(f"#{idx}: {r}")

def exercise5():
    """Todos os fabricantes que começam com T, em ordem alfabética"""
    with Session() as session, session.begin():
        query = (
            select(Product.manufacturer)
            .where(Product.manufacturer.startswith("T"))
            .order_by(Product.manufacturer.asc())
        )
        result = session.scalars(query).all()
        
        for idx, r in enumerate(result):
            print(f"#{idx}: {r}")

def exercise6():
    """Primeiro e ultimo ano que um computador foi construído na Croácia e o nome do computaador"""
    with Session() as session, session.begin():
        query = (
            select(
                func.count(Product.country),
                func.min(Product.year),
                func.max(Product.year)
            )
            .group_by(Product.country)
            .having(Product.country == "Croatia")
        )
        res = session.execute(query).all()
        print(f"{res[0][0]} computadores foram produzidos na Croácia entre {res[0][1]} e {res[0][2]}")

def exercise7():
    """Contagem de computadores por ano juntamente com o ano. Anos sem computadores não aparecem"""
    with Session() as session, session.begin():
        counter = func.count(Product.year).label("counter")
        query = (
            select(
                counter,
                Product.year
            )
            .group_by(Product.year)
            .having(counter > 0)
            .order_by(counter.desc())
        )

        result = session.execute(query).all()
        for r in result:
            print(f"{r[1]}: {r[0]} computador(es) construído(s)")

def exercise8():
    """Número de fabricantes dos estados unidos"""
    with Session() as session, session.begin():
        query = (
            select(func.count(Product.manufacturer.distinct()))
            .where(Product.country == "USA")
        )
        res = session.scalar(query)
        print(f"Existem {res} fabricantes nos EUA")

if __name__ == "__main__":
    # exercise1()
    # exercise2()
    # exercise3()
    # exercise4()
    # exercise5()
    # exercise6()
    # exercise7()
    # exercise8()

