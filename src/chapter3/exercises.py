import rich
from sqlalchemy import or_, select, text
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from src.db import Session
from src.models import *


def exercise1_join():
    with (Session() as s, s.begin()):
        text_query = text(
            """
            SELECT
                p.id, p.name
            FROM products p
            INNER JOIN manufacturers m
            ON p.manufacturer_id = m.id
            """
        )
        query = (
            select(Product)
            .join(Product.manufacturer)
        )
        result = s.scalars(query).all()


        for idx, r in enumerate(result):
            if idx == 20:
                break

            rich.print(r, r.manufacturer)


def tipos_de_join():
    with Session() as s:
        rich.print("=" * 50, "Select in load: usa um segunda Query com IN para buscar os dados da entidade associada")
        join_usando_in = (
            select(Product)
            .options(selectinload(Product.manufacturer))
        )
        """
        Query acima é traduzida para:
        a) SELECT * FROM products p;
        B) SELECT * FROM manufacturers m WHERE m.id IN (1, 2, 3....)
        """
        res = s.scalars(join_usando_in).all()

        for idx, entity in enumerate(res):
            if idx == 10:
                break
            rich.print(entity, entity.manufacturer )
        
        rich.print("="*50, "Joined Load: usa um left join para buscar os dados da entidade associada")
        left_join = (
            select(Product)
            .options(joinedload(Product.manufacturer))
        )
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

        rich.print("="*50, "contains eager: aproveita o join")
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
    tipos_de_join()