import logging

import rich
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.db import Session
from src.models import *

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(name)s %(funcName)s %(message)s", level=logging.INFO)


def adding_countries():
    """Para remover ou adicionar entidades, basta acessar o atributo virtual mapeado"""
    with Session() as s, s.begin():
        product = s.get(Product, 20)

        if not product:
            return

        logger.info("Adicionando países para produto %s", product.name)
        country1 = s.get(Country, 1)
        country2 = s.get(Country, 2)

        if country1 and country2:
            product.countries.append(country1)
            product.countries.append(country2)


def removing_countries():
    # Removendo os países adicionados anteriormente
    with Session() as s, s.begin():
        product = s.get(Product, 20)

        if not product:
            logger.error("Produto com id 20 não existe")
            return

        # Limpando a associação
        product.countries = [c for c in product.countries if c.id != 2 and c.id != 3]

def joining_countries():
    with Session() as s:
        query = (
            select(Product)
            .options(selectinload(Product.countries))
        )
        res = s.scalars(query).all()

        for r in res:
            rich.print(f"{r} made in {r.countries}")

def products_with_more_than_one_country():
    with Session() as s:
        """
        SELECT p.name, COUNT(c.id) FROM products p
        INNER JOIN products_countries pc ON p.id = pc.product_id
        INNER JOIN countries c ON c.id = pc.country_id
        GROUP BY p.name
        HAVING COUNT(c.id) > 1;
        """
        p_count = func.count(Country.id).label(None)
        query = (
            select(Product.name, p_count)
            .join(Product.countries)
            .group_by(Product.name)
            .having(p_count > 1)
            .order_by( p_count.desc())
        )
        res = s.execute(query).all()
        for name, qtd in res:
            rich.print(name, qtd)

def manufacturers_that_operates_in_uk():
    """
        SELECT m.*, c.name FROM manufacturers m
        INNER JOIN products p ON p.manufacturer_id = m.id
        INNER JOIN products_countries pc ON pc.product_id = p.id
        INNER JOIN countries c ON pc.country_id = c.id
        WHERE c.name = 'UK';
    """
    with Session() as s:
        query = (
            select(Manufacturer, Country.name)
            .join(Manufacturer.products)
            .join(Product.countries)
            .where(Country.name == 'UK')
            .distinct()
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(r)

def manufacturers_that_operates_in_more_than_one_country():
    """
    SELECT m.name,  COUNT(DISTINCT c.id) as "Numero de países" FROM manufacturers m
    INNER JOIN products p ON p.manufacturer_id = m.id
    INNER JOIN products_countries pc ON pc.product_id = p.id
    INNER JOIN countries c ON pc.country_id = c.id
    GROUP BY m.name
    HAVING COUNT(DISTINCT c.id) > 1
    ORDER BY "Numero de países" DESC;
    :return:
    """
    with Session() as s:
        c_count = func.count(Country.id.distinct()).label(None)
        query = (
            select(Manufacturer, c_count)
            .join(Manufacturer.products)
            .join(Product.countries)
            .group_by(Manufacturer)
            .having(c_count > 1)
            .order_by(c_count.desc())
        )
        res = s.execute(query).all()

        for r in res:
            rich.print(r[0], r[1])

def removing_an_association() -> None:
    with Session() as s, s.begin():
        product = s.get(Product, 139)
        country_to_be_removed = s.get(Country, 22)

        if not product and not country_to_be_removed:
            return

        if country_to_be_removed not in product.countries:
            return

        rich.print(product.countries, type(product.countries))
        product.countries.remove(country_to_be_removed)

def deleting_an_associated_entity():
    with Session() as s, s.begin():
        entity = s.get(Country, 3)
        
        if not entity:
            return
        
        s.delete(entity)
        

if __name__ == "__main__":
    #removing_countries()
    # joining_countries()
    # products_with_more_than_one_country()
    # manufacturers_that_operates_in_uk()
    # manufacturers_that_operates_in_more_than_one_country()
    # removing_an_association()
    deleting_an_associated_entity()