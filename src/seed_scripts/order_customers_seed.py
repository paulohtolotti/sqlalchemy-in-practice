import csv
import sys
from datetime import datetime
from decimal import Decimal

import rich
from sqlalchemy import delete, func, select

from src.db import Session
from src.models import Customer, Order, OrderItem, Product


def clean():
    """Limpa base de dados de clientes, pedidos e itens"""
    with Session() as s, s.begin():
        s.execute(delete(OrderItem))
        s.execute(delete(Order))
        s.execute(delete(Customer))

    rich.print("Base limpa")


def _get_reader():
    with open("data/orders_customers.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        yield from reader
        rich.print(f"Closing reader at {sys._getframe().f_code.co_name}")


def find_product_by_name(session, name: str) -> Product | None:
    query = select(Product).where(func.lower(Product.name) == name.lower())
    return session.scalar(query)


def order_item_factory(product: Product, quantity: str, unit_price: str):
    return OrderItem(product=product, quantity=int(quantity), unit_price=Decimal(unit_price))


def seed():
    reader = _get_reader()

    all_products: dict[str, Product] = {}
    all_customers: dict[str, Customer] = {}
    with Session() as s, s.begin():
        for row in reader:
            order_items_list: set[OrderItem] = set()
            if row["name"] not in all_customers:
                customer = Customer(name=row["name"], address=row["address"], phone=row["phone"])
                all_customers[row["name"]] = customer

            order = Order(
                customer=all_customers[row["name"]],
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
            )

            all_customers[row["name"]].orders.add(order)
            s.add(order)

            product1: Product | None = all_products.get(row["product1"], None)

            if not product1:
                product1 = find_product_by_name(session=s, name=row["product1"])
                if not product1:
                    rich.print(f"Produto {row['product1']} não encontrado. Pulando...")
                    continue

            all_products[row["product1"]] = product1

            order_items_list.add(
                order_item_factory(
                    product=all_products[row["product1"]],
                    quantity=row["quantity1"],
                    unit_price=row["unit_price1"],
                )
            )

            if row["product2"]:
                product2 = all_products.get(row["product2"], None)

                if not product2:
                    product2: Product | None = find_product_by_name(
                        session=s, name=row["product2"]
                    )

                if not product2:
                    rich.print(f"Produto {row['product2']} não encontrado. Pulando...")
                    continue

                all_products[row["product2"]] = product2

                order_items_list.add(
                    order_item_factory(
                        product=all_products[row["product2"]],
                        quantity=row["quantity2"],
                        unit_price=row["unit_price2"],
                    )
                )

            if row["product3"]:
                product3: Product | None = all_products.get(row["product3"], None)
                if not product3:
                    product3 = find_product_by_name(session=s, name=row["product3"])

                if not product3:
                    rich.print(f"Produto {row['product3']} não encontrado. Pulando...")
                    continue

                all_products[row["product3"]] = product3

                order_items_list.add(
                    order_item_factory(
                        product=all_products[row["product3"]],
                        quantity=row["quantity3"],
                        unit_price=row["unit_price3"],
                    )
                )

            for o in order_items_list:
                order.order_items.append(o)


def main():
    clean()
    seed()


if __name__ == "__main__":
    main()
