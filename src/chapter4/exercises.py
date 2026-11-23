import rich
from sqlalchemy import func, or_, select
from sqlalchemy.orm import contains_eager, joinedload

from src.db import Session
from src.models import Country, Manufacturer, Product


def exercise1():
    # Produtos feitos nos EUA ou UK
    """
    SELECT p.*, c.name AS "País"
        FROM products p
    INNER JOIN products_countries pc ON pc.product_id = p.product_id
    INNER JOIN countries c ON pc.country_id = c.id
    WHERE c.name = 'UK' OR c.name = 'USA'
    """
    with Session() as s:
        query = (
            select(Product)
            .join(Product.countries)
            .where(
                or_(Country.name == 'UK', Country.name == 'USA')
            )
            .options(contains_eager(Product.countries))
            .distinct()
        )
        res = s.scalars(query).unique().all()
        rich.print(f"Total {len(res)}")
        for r in res:
            rich.print(f"{r} made on {r.countries}")

def exercise2():
    # Produto não feitos nos EUA ou UK. Se o produto for feito
    # nos EUA ou UK em conjunto com outro país, entra na query.
    """
    SELECT p.name, c.name as "País"
    FROM products p
    INNER JOIN products_countries pc ON p.id = pc.product_id
    INNER JOIN countries c ON c.id = pc.country_id
    WHERE c.name != 'UK' AND c.name != 'USA';

    ----Exemplo----
    Não entra
    Apple CD - UK
    Apple CD - USA

    Entra
    Apple CD 2 - UK
    Apple CD 2 - JP

    Entra
    Apple CD 3 - UK
    Apple CD 3 - USA
    Apple CD 3 - BR
    """
    with Session() as s:
        query = (
            select(Product)
            .join(Product.countries)
            .where(Country.name.notin_(['UK', 'USA']))
            .options(joinedload(Product.countries))
            .order_by(Product.id.asc())
            .distinct()
        )
        res = s.scalars(query).unique().all()
        rich.print(f"Total: {len(res)}")
        for r in res:
            rich.print(f"{r} made on {r.countries}")

def exercise3():
    # Países que produziram CPU Z80 ou clones
    """
    SELECT DISTINCT c.name as "País"
    FROM countries c
    INNER JOIN products_countries pc ON c.id = pc.country_id
    INNER JOIN products p ON p.id = pc.product_id
    WHERE p.cpu ILIKE '%Z80%';
    """
    with Session() as s:
        query = (
            select(Country)
            .join(Country.products)
            .where(Product.cpu.ilike("%Z80%"))
            .options(contains_eager(Country.products))
            .order_by(Country.name)
            .distinct()
        )
        res = s.scalars(query).unique().all()
        rich.print(f"Total: {len(res)}")
        for r in res:
            rich.print(f"{r} made {r.products}")

def exercise4():
    # Países que produziram coputadores na década de 1970
    """
    SELECT DISTINCT c.name FROM countries c
    INNER JOIN products_countries pc ON c.id = pc.country_id
    INNER JOIN products p ON p.id = pc.product_id
    WHERE p.year BETWEEN 1970 and 1979
    ORDER BY c.name;
    """
    with Session() as s:
        query = (
            select(Country.name)
            .join(Country.products)
            .where(Product.year.between(1970, 1979))
            .order_by(Country.name)
            .distinct()
        )
        res = s.execute(query).all()
        rich.print(f"Total {len(res)}")
        for r in res:
            rich.print(f"{r}")

def exercise5():
    # 5 países com mais produtos, desempate em ordem alfabética
    """
    SELECT c.name, COUNT(p.id) as "Qtd Produtos"
    FROM countries c
    INNER JOIN products_countries pc ON c.id = pc.country_id
    INNER JOIN products p ON p.id = pc.product_id
    GROUP BY c.name
    ORDER BY COUNT(p.id) DESC, c.name ASC
    LIMIT 5;
    """
    with Session() as s:
        p_count = func.count(Product.id).label(None)
        query = (
            select(Country.name, p_count)
            .join(Country.products)
            .order_by(p_count.desc(), Country.name.desc())
            .group_by(Country.name)
            .limit(5)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r[0]}: {r[1]} products")

def exercise6():
    """
    SELECT m.name, COUNT(p.id) as "Qtd Produtos" FROM manufacturers m
    INNER JOIN products p ON p.manufacturer_id = m.id
    INNER JOIN products_countries pc ON pc.product_id = p.id
    INNER JOIN countries c ON pc.country_id = c.id
    WHERE c.name IN ('UK', 'USA')
    GROUP BY m.name
    HAVING COUNT(p.id) > 3
    ORDER BY COUNT(p.id) DESC, m.name ASC;
    """
    with Session() as s:
        p_count = func.count(Product.id).label(None)
        query = (
            select(Manufacturer.name, p_count)
            .join(Manufacturer.products)
            .join(Product.countries)
            .where(Country.name.in_(['USA', 'UK']))
            .group_by(Manufacturer.name)
            .having(p_count > 3)
            .order_by(p_count.desc(), Manufacturer.name.asc())
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r[0]}: {r[1]}")

def exercise7():
    """
    SELECT m.name, COUNT(DISTINCT c.id) FROM manufacturers m
    INNER JOIN products p ON m.id = p.manufacturer_id
    INNER JOIN products_countries pc ON p.id = pc.product_id
    INNER JOIN countries c ON c.id = pc.country_id
    GROUP BY m.name
    HAVING COUNT(DISTINCT c.id) > 1;
    """
    with Session() as s:
        c_count = func.count(Country.id.distinct()).label(None)
        query = (
            select(Manufacturer.name, c_count)
            .join(Manufacturer.products)
            .join(Product.countries)
            .having(c_count > 1)
            .group_by(Manufacturer.name)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r[0]}: {r[1]}")

def exercise8():
    """
    SELECT p.name, COUNT(c.id) FROM products p
    INNER JOIN products_countries pc ON pc.product_id = p.id
    INNER JOIN countries c ON pc.country_id = c.id
    WHERE c.name IN ('USA', 'UK')
    GROUP BY p.name
    HAVING COUNT(c.id) > 1;
    """
    with Session() as s:
        query = (
            select(Product.name)
            .join(Product.countries)
            .where(Country.name.in_(['USA', 'UK']))
            .group_by(Product.name)
            .having(func.count(Country.id) > 1)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r}")

if __name__ == "__main__":
    # exercise1()
    # exercise2()
    # exercise3()
    # exercise4()
    # exercise5()
    # exercise6()
    exercise7()
    exercise8()