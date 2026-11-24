import locale
from decimal import Decimal

import rich
from rich.console import Console
from sqlalchemy import func, select

from src.db import Session
from src.models import Customer, Order, OrderItem, Product, ProductReview

console = Console()
locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")


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


def write_only_relationship():
    with Session() as s:
        customer = s.scalar(select(Customer).where(Customer.name == "Hayden Collins"))

        if not customer:
            return

        rich.print(customer)
        # Orders é uma coleção, não dispara lazy loading ao acessá-la, pois foi mapeado com WriteOnly
        rich.print(f"Orders de {customer.name}: {customer.orders}")

        # Podemos acessar os atributos usando o method select
        orders = s.execute(customer.orders.select().order_by(Order.timestamp.desc()))
        for o in orders:
            rich.print(o)


def total_clientes_ordens():
    with Session() as s:
        c_total = s.scalar(select(func.count(Customer.id)))
        p_total = s.scalar(select(func.count(Order.id)))
        console.print(
            f"[blue underline]Total clientes[/blue underline] {c_total} x [blue underline]Total de pedidos[/blue underline] {p_total}"
        )


def total_produto_pedido():
    with Session() as s:
        total_item = (OrderItem.quantity * OrderItem.unit_price).label(None)
        query = (
            select(Product.name, total_item)
            .join(Product.order_items)
            .order_by(total_item.desc())
            .limit(5)
        )
        res = s.execute(query).all()

        for r in res:
            console.print(r)


def total_vendido_produto():
    """
    SELECT p.name, SUM(oi.unit_price * oi.quantity) as "Total"
    FROM products p
    INNER JOIN orders_items oi ON oi.product_id = p.id
    GROUP BY p.id
    ORDER BY "Total" DESC, p.id ASC;
    """
    with Session() as s:
        total = func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
        query = (
            select(Product.name, total)
            .join(Product.order_items)
            .group_by(Product.id)
            .order_by(total.desc())
        )
        res = s.execute(query).all()
        for r in res:
            console.print(f"{r[0]} vendeu {locale.currency(r[1], grouping=True)}")


def total_por_pedido():
    """
    SELECT oi.order_id as "ID Pedido", SUM(oi.quantity * oi.unit_price) as "Total Pedido"
    FROM orders_items oi
    GROUP BY oi.order_id
    ORDER BY  SUM(oi.quantity * oi.unit_price) DESC;
    """
    with Session() as s:
        total = func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
        query = (
            select(OrderItem.order_id, total).group_by(OrderItem.order_id).order_by(total.desc())
        )
        res = s.execute(query).all()
        for r in res:
            console.print(f"Pedido {r[0]}: total {locale.currency(r[1], grouping=True)}")


def produtos_mais_vendidos():
    """
    SELECT p.name, SUM(oi.quantity) as "Total unidades"
    FROM products p
    INNER JOIN orders_items oi ON p.id = oi.product_id
    GROUP BY p.id
    ORDER BY SUM(oi.quantity) DESC;
    """
    with Session() as s:
        total_unidades = func.sum(OrderItem.quantity).label(None)
        query = (
            select(Product.name, total_unidades)
            .join(Product.order_items)
            .group_by(Product.id)
            .order_by(total_unidades.desc())
            .limit(5)
        )
        res = s.execute(query).all()

        for r in res:
            console.print(f"{r[0]} vendeu {r[1]} unidades")


def total_pedidos_em_novembro():
    """
    SELECT o.id as "ID Ordem", SUM(oi.quantity * oi.unit_price) as "Total"
    FROM orders o
    INNER JOIN orders_items oi ON o.id = oi.order_id
    WHERE o.timestamp BETWEEN '11-01-2022' AND '11-30-2022'
    GROUP BY o.id
    ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    LIMIT 5;
    """
    with Session() as s:
        total_pedido = func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
        query = (
            select(Order.id, total_pedido)
            .join(Order.order_items)
            .where(Order.timestamp.between("11-01-2022", "12-01-2022"))
            .group_by(Order.id)
            .order_by(total_pedido.desc())
            .limit(5)
        )
        res = s.execute(query).all()
        for r in res:
            console.print(f"Order {r[0]} total {locale.currency(r[1], grouping=True)}")


def top5_produtos_mais_vendidos_novembro():
    """Busca os 5 produtos mais vendidos de novembro de 2022, trazendo seu nome e quantidade vendida
    SELECT p.name, SUM(oi.quantity) as "Total"
    FROM products p
    INNER JOIN orders_items oi ON p.id = oi.product_id
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.timestamp BETWEEN '11-01-2022' AND '12-01-2022'
    GROUP BY p.id
    ORDER BY SUM(oi.quantity) DESC
    LIMIT 5;
    """
    with Session() as s:
        total = func.sum(OrderItem.quantity).label(None)
        query = (
            select(Product.name, total)
            .join(Product.order_items)
            .join(OrderItem.order)
            .where(Order.timestamp.between("11-01-2022", "12-01-2022"))
            .group_by(Product.id)
            .order_by(total.desc())
            .limit(5)
        )
        res = s.execute(query).all()

        for r in res:
            console.print(f"{r[0]} vendeu {r[1]} unidades")


def unidades_vendida_mes_ano():
    """
    SELECT
        EXTRACT(MONTH FROM o.timestamp) as "Mês",
        EXTRACT(YEAR FROM o.timestamp) as "Ano",
        SUM(oi.quantity) as "Unidades vendidas"
    FROM orders o
    INNER JOIN orders_items oi ON o.id = oi.order_id
    WHERE o.timestamp BETWEEN '01-01-2022' AND '01-01-2023'
    GROUP BY EXTRACT(MONTH FROM o.timestamp), EXTRACT(YEAR FROM o.timestamp)
    ORDER BY "Mês", "Ano";
    """
    with Session() as s:
        month = func.extract("month", Order.timestamp).label(None)
        year = func.extract("year", Order.timestamp).label(None)
        units_sold = func.sum(OrderItem.quantity).label(None)

        query = (
            select(month, year, units_sold)
            .join(Order.order_items)
            .where(Order.timestamp.between("01-01-2022", "01-01-2023"))
            .group_by(month, year)
            .order_by(month, year)
        )
        res = s.execute(query).all()
        for r in res:
            console.print(f"{r[0]}/{r[1]}: {r[2]} unidades vendidas")


def media_avaliacoes():
    """
    SELECT avg(rating) FROM products_reviws;
    """
    with Session() as s:
        query = select(func.avg(ProductReview.rating))
        res = s.scalar(query)
        console.print(f"Média de avaliações: {res:.2f}")


def media_por_produto():
    """
    SELECT p.name, AVG(pr.rating) AS "Média"
    FROM products_reviews pr
    INNER JOIN products p ON pr.product_id = p.id
    GROUP BY p.id
    ORDER BY AVG(pr.rating) DESC;
    """
    with Session() as s:
        rating_avg = func.avg(ProductReview.rating).label(None)
        query = (
            select(Product.name, rating_avg)
            .join(Product.reviews)
            .group_by(Product.id)
            .order_by(rating_avg.desc())
        )
        res = s.execute(query).all()
        for r in res:
            console.print(f"{r[0]}: {r[1]:.2f}")


def percentual_de_avaliacoes_sem_comentarios():
    """
    SELECT
        p.name,
        100 - CAST(COUNT(pr.comment) AS decimal(10,2)) / CAST(COUNT(pr.rating) AS decimal(10,2)) * 100 AS "Percentual com comentários"
    from products p
    INNER JOIN products_reviews pr ON p.id = pr.product_id
    GROUP BY (p.name)
    ORDER BY p.name;
    """
    with Session() as s:
        records_with_comments = func.count(ProductReview.comment).label(None)
        total_records = func.count(ProductReview.rating).label(None)
        without_comments = 100 - 100 * (records_with_comments / total_records)

        query = (
            select(Product.name, without_comments)
            .join(Product.reviews)
            .group_by(Product.name)
            .order_by(Product.name)
        )
        res = s.execute(query).all()

        for r in res:
            console.print(f"{r[0]}: {r[1]:.2f}%  de avaliações sem comentários")


if __name__ == "__main__":
    # create_customer()
    # query_customer()
    # create_order()
    # deletes()
    # write_only_relationship()
    # total_clientes_ordens()
    # total_produto_pedido()
    # total_vendido_produto()
    # total_por_pedido()
    # produtos_mais_vendidos()
    # total_pedidos_em_novembro()
    # top5_produtos_mais_vendidos_novembro()
    # unidades_vendida_mes_ano()
    # media_avaliacoes()
    # media_por_produto()
    percentual_de_avaliacoes_sem_comentarios()
