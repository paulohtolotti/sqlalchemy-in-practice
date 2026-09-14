from sqlalchemy import select

from src.db import Session
from src.models import Product


def exercise1():
    with Session() as session, session.begin():
        query = select(Product).order_by(Product.name.asc()).where(Product.year == 1983).limit(3)
        res = session.scalars(query).all()
        for idx, r in enumerate(res, start=1):
            print(f"#{idx}: {r}")


if __name__ == "__main__":
    exercise1()

