import sqlalchemy
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import NoResultFound

from src.db import Session
from src.models import Product
def separator():
    print("-"*50)
    print("#"*50)
    print("-"*50)

def simple_select():
    with Session() as s:
        with s.begin():
            # Prepara a query
            query = select(Product)
            print(f"Query produzida: {query}")
            # Executa
            res = s.execute(query).all()
            print(f"Resultado obtido {res[0:10:3]}.\n Res é uma lista de {type(res[0])}")
            res2 = s.execute(query).first()
            print(f"Primeiro resultado {res2}")

def select_with_scalars():
    """
    Quando sabemos que o resultado da query é uma equivalência 1-1 tupla-linha, podemos usar o método scalar
    """
    with Session() as s:
        with s.begin():
            query = select(Product)
            res = s.scalars(query).all()
            res2 = s.scalar(query)
            res3 = s.scalars(query).first()
            # Res2 e Res3 são equivalentes. Sendo res2 apenas um shorthand
            print(f"Resultado {res}, do tipo {type(res)}")

def select_with_filter():
    with Session() as s:
        with s.begin():
            query = select(Product).where(Product.id >= 145)
            query2 = select(Product).where(Product.id > 10).limit(3)
            non_existing_query = select(Product).where(Product.name == "Peão")
            query4 = select(Product).where(Product.name.contains("p")).order_by(Product.name.desc())

            result = s.execute(query).all()
            result2 = s.scalars(query2).first()
            try:
                result3 = s.scalars(non_existing_query).one()
            except NoResultFound as err:
                print("No row as found")

            result4 = s.scalars(non_existing_query).first()
            result5 = s.scalars(query4).all()

            for r in result:
                print(result)

            separator()
            print(result2)
            separator()
            print("Empty" if not result4 else result4)
            separator()
            print(result5)

def select_where_variations():
    with Session() as session:
        with session.begin():
            q1 = (select(Product)
                  .where(Product.year > 2000)
                  .where(Product.name.contains("z"))
            )
            q2 = select(Product).where(Product.year > 1975, Product.manufacturer == "Comodore")
            q3 = (
                select(Product)
                .where(or_(
                    Product.manufacturer == "Radio Shack",
                    Product.manufacturer == "Sord Computer Corporation"
                ))
            )
            q4 = (
                select(Product)
                .where(Product.year.between(1960, 1979))
                .order_by(Product.year.desc(), Product.name.asc())
            )

            res = session.scalars(q2).all()
            res2 = session.scalars(q3).all()
            res4 = session.scalars(q4).all()

            print(res)
            separator()
            print(res2)
            separator()
            for r in res4:
                print(f"{r.name} by {r.manufacturer}- {r.year}")

def projections():
    with Session() as session:
        with session.begin():
            query_names = select(Product.name).distinct().limit(10)
            query_names_manufacturers = select(Product.name, Product.manufacturer).limit(10)

            names = session.scalars(query_names).all()
            # Com scalars apenas um resultado por linha é obtido, descartando uma das colunas da projeção
            # names_manufacturers = session.scalars(query_names_manufacturers).all()
            names_manufacturers = session.execute(query_names_manufacturers).all()

            separator()
            for name in names:
                print(name)
            separator()
            print(names_manufacturers)
            for name, manu in names_manufacturers:
                print(f"{name} - {manu}")
            separator()

def aggregations():
    with Session() as session:
        with session.begin():
            query_unique_manufactures = select(func.count(Product.id)).distinct()
            query_current_user = select(func.current_user())
            query_sum = select(func.sum(Product.year))
            query_min_max = select(func.min(Product.year), func.max(Product.year))
            query_manufacturers = select(Product.manufacturer).distinct()
            query_manufacturers2 = select(Product.manufacturer).distinct().group_by(Product.manufacturer)
            query_manufacturers_products = (
                select(
                    Product.manufacturer,
                    func.count()
                ).group_by(Product.manufacturer)
            )
            # Por ser executada antes do agrupamento a clausula where não pode ser para filtrar agregações.
            # Nessa caso usamos o having
            num_products = func.count().label(None)

            query_manufacturers_products_2 = (
                select(
                    Product.manufacturer,
                    num_products
                )
                .group_by(Product.manufacturer)
                .having(num_products >= 6)
            )

            res = session.scalar(query_unique_manufactures)
            res2 = session.scalar(query_current_user)
            res3 = session.scalar(query_sum)
            res4 = session.execute(query_min_max)
            res5 = session.scalars(query_manufacturers).all() # Podemos usar pois há somente 1 coluna por linha na seleção
            res6 = session.scalars(query_manufacturers2).all()
            res7 = session.execute(query_manufacturers_products).all()
            res8 = session.execute(query_manufacturers_products_2).all()

            print(res)
            separator()
            print(res2)
            separator()
            print(res3)
            separator()
            print(res4)
            separator()
            print(res5, len(res5))
            separator()
            print(res6, len(res6))
            separator()
            for manu, qty in res7:
                print(f"{manu} produced {qty} products")
            separator()
            for manu, qty in res8:
                print(f"{manu} produced {qty} products")

if __name__ == "__main__":
    #simple_select()
    # select_with_scalars()
    # select_with_filter()
    # select_where_variations()
    # projections()
    aggregations()