import rich
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from src.db import Session
from src.models import *


def exercise1_join():
    with Session() as s, s.begin():
        text_query = text(
            """
            SELECT
                p.*, m.*
            FROM products p
            INNER JOIN manufacturers m
            ON p.manufacturer_id = m.id
            WHERE m.name ILIKE '%apple%' OR m.name = 'Texas Instrumental'
            """
        )
        query = (
            select(Product)
            .join(Product.manufacturer)
            .where(
                or_(Manufacturer.name.ilike("%apple%"), Manufacturer.name == "Texas Instruments")
            )
            .options(contains_eager(Product.manufacturer))
        )
        result = s.scalars(query).all()
        result2 = s.execute(text_query).all()

        for r in result:
            rich.print(f"{r} by {r.manufacturer}")
        rich.print(25 * "=", "Query com text", 25 * "=")
        for r in result2:
            rich.print(f"{r}")


def exercise3():
    with Session() as s:
        query = (
            select(Product)
            .join(Product.manufacturer)
            .where(Manufacturer.name.ilike("%research%"))
            .options(contains_eager(Product.manufacturer))
        )
        res = s.scalars(query)
        for r in res:
            rich.print(f"{r} by {r.manufacturer.name}")


def exercise4():
    with Session() as s:
        query = (
            select(Manufacturer)
            .join(Manufacturer.products)
            .where(Product.cpu.ilike("%Z80%"))
            .options(contains_eager(Manufacturer.products))
        )
        res = s.scalars(
            query
        ).unique()  # Necessário pois uma entidade pode vir repetidas vezes pois é 1 - N

        for r in res:
            rich.print(f"{r} made {r.products}")


def exercise5():
    with Session() as s:
        query = (
            select(Manufacturer)
            .join(Manufacturer.products)
            .where(Product.cpu.notilike("%6502%"))
            .options(contains_eager(Manufacturer.products))
            .distinct()
        )
        res = s.scalars(query)
        for r in res:
            rich.print(f"{r} made {r.products}")


def exercise6():
    with Session() as s:
        """
        SELECT m.name, MIN(p.year) FROM manufacturers m
        INNER JOIN products p ON m.id = p.manufacturer_id
        GROUP BY m.name;
        """
        min_year = func.min(Product.year).label(None)
        query = (
            select(Manufacturer, min_year)
            .join(Manufacturer.products)
            .group_by(Manufacturer)
            .order_by(min_year)
        )
        res = s.execute(query).all()
        for man, year in res:
            rich.print(f"{man} {year}")


def exercise7():
    with Session() as s:
        """
        SELECT m.name, COUNT(p.id) as qtd_prod FROM manufacturers m
        INNER JOIN products p ON m.id = p.manufacturer_id
        GROUP BY m.name HAVING COUNT(p.id) BETWEEN 3 AND 5 ORDER BY qtd_prod DESC;
        
        OBS: Não podemos usar apelidos no HAVING porque ele é avaliado antes do COUNT()
        """
        qtd_prod = func.count(Product.id).label(None)
        query = (
            select(Manufacturer, qtd_prod)
            .join(Manufacturer.products)
            .having(qtd_prod.between(3, 5))
            .group_by(Manufacturer)
            .order_by(qtd_prod)
        )

        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r}")


def exercise8():
    with Session() as s:
        """
        SELECT m.name, (MAX(p.year) - MIN(p.year)) as "Anos operando"
        FROM manufacturers m INNER JOIN products p
        ON m.id = p.manufacturer_id
        GROUP BY m.name
        HAVING (MAX(p.year) - MIN(p.year)) > 5 
        ORDER BY "Anos operando" DESC;
        """
        years_operating = func.max(Product.year) - func.min(Product.year)
        query = (
            select(Manufacturer, years_operating)
            .join(Manufacturer.products)
            .group_by(Manufacturer)
            .having(years_operating > 5)
            .order_by(years_operating.desc())
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(r)


def tipos_de_join():
    with Session() as s:
        rich.print(
            "=" * 50,
            "Select in load: usa um segunda Query com IN para buscar os dados da entidade associada",
        )
        join_usando_in = select(Product).options(selectinload(Product.manufacturer))
        """
        Query acima é traduzida para:
        a) SELECT * FROM products p;
        B) SELECT * FROM manufacturers m WHERE m.id IN (1, 2, 3....)
        """
        res = s.scalars(join_usando_in).all()

        for idx, entity in enumerate(res):
            if idx == 10:
                break
            rich.print(entity, entity.manufacturer)

        rich.print(
            "=" * 50, "Joined Load: usa um left join para buscar os dados da entidade associada"
        )
        left_join = select(Product).options(joinedload(Product.manufacturer))
        """
        Query acima é traduzida para
        SELECT p.*, m.* FROM products p
        LEFT OUTER JOIN manufacturers m ON m.id = p.manufacturer_id
        """
        res2 = s.scalars(left_join).all()
        for idx, entity in enumerate(res2):
            if idx == 10:
                break
            rich.print(entity, entity.manufacturer)

        rich.print("=" * 50, "contains eager: aproveita o join")
        inner_join = (
            select(Product)
            .join(Product.manufacturer)
            .options(contains_eager(Product.manufacturer))
        )
        """
        A query acima é traduzida para
        SELECT p.*, m.* FROM products p
        INNER JOIN manufacturers m ON m.id = p.manufacturer_id
        """
        res3 = s.scalars(inner_join).all()
        for idx, entity in enumerate(res3):
            if idx == 10:
                break
            rich.print(entity, entity.manufacturer)


if __name__ == "__main__":
    # exercise1_join()
    # tipos_de_join()
    # exercise3()
    # exercise4()
    # exercise5()
    # exercise6()
    # exercise7()
    exercise8()
