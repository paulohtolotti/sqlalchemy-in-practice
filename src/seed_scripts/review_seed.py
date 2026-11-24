import csv
import datetime

from sqlalchemy import delete, func, select

from src.db import Session
from src.models import Customer, Product, ProductReview

session = Session()


def _get_reader():
    with open("data/product_reviews.csv", "r", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def get_customer(name: str) -> Customer:
    """
    Busca um cliente por nome. Assume que o cliente sempre existe,
    visto que os dados são via seed.
    Args:
        name: nome do cliente

    Returns:
        cliente salvo no banco de dados, de forma completa.
    """
    customer = select(Customer).where(func.lower(Customer.name) == name.lower())
    return session.scalar(customer)  # type: ignore


def get_product(name: str) -> Product:
    """
    Busca um produto por nome. Assume que o produto sempre existe,
    visto que os dados são via seed.
    Args:
        name: nome do produto

    Returns:
        produto salvo no banco de dados, de forma completa.
    """
    product = select(Product).where(func.lower(Product.name) == name.lower())
    return session.scalar(product)  # type: ignore


def seed():
    reader = _get_reader()
    all_products: dict[str, Product] = {}
    all_customers: dict[str, Customer] = {}
    products_reviews = []
    with session.begin():
        for row in reader:
            customer = all_customers.get(row["customer"], None)
            product = all_products.get(row["product"], None)

            if not customer:
                customer = get_customer(row["customer"])
            if not product:
                product = get_product(row["product"])

            products_reviews.append(
                ProductReview(
                    rating=int(row["rating"]),
                    timestamp=datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
                    comment=row["comment"] or None,
                    customer=customer,
                    product=product,
                )
            )
        session.add_all(products_reviews)


def clean():
    with session.begin():
        session.execute(delete(ProductReview))


if __name__ == "__main__":
    clean()
    seed()
