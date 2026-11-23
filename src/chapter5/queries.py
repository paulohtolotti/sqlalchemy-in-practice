from decimal import Decimal

import rich
from sqlalchemy import select

from src.db import Session
from src.models import Customer, Order, OrderItem, Product


def create_customer():
    with Session() as s, s.begin():
        customer = Customer(name="John Foo", phone="11995884156", address="Green Dolphin Street")
        s.add(customer)
        print(customer.id)


def query_customer():
    with Session() as s:
        res = s.scalars(select(Customer))
        for r in res:
            rich.print(f"{r}")


def order_item_factory(
    product: Product, unit_price: Decimal = Decimal("10.50"), quantity: int = 1
):
    return OrderItem(product=product, quantity=quantity, unit_price=unit_price)


def create_order():
    with Session() as s, s.begin():
        customer: Customer | None = s.get(Customer, "078d42a9-6c0b-4318-8db9-226fea5e1347")
        rich.print(f"{customer}")
        if not customer:
            return

        product1: Product | None = s.get(Product, 1)
        product2: Product | None = s.get(Product, 2)
        rich.print(f"{product1} {product2}")
        if not product2 or not product1:
            return

        order = Order(
            customer=customer,
            order_items=[
                order_item_factory(product=product1, quantity=2, unit_price=Decimal("250.75")),
                order_item_factory(product=product2, quantity=100, unit_price=Decimal("30.00")),
            ],
        )
        s.add(order)
        s.flush()
        rich.print(f"{order.id.hex} at {order.timestamp}")


def deletes():
    with Session() as s, s.begin():
        p = s.get(Product, 1)  # Produto associado a uma ordem
        # Levanta erro pois a tabela OrderItem têm uma PK que aponta para products.id
        if not p:
            return

        # if p:
        #     s.delete(p)

        order_item = s.get(
            OrderItem, {"order_id": "dd15aa12-4ec5-41cc-afa5-3579ebe5d324", "product_id": 1}
        )
        s.delete(order_item)


if __name__ == "__main__":
    # create_customer()
    # query_customer()
    # create_order()
    deletes()
