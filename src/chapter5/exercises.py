import locale
from decimal import Decimal

import rich
from sqlalchemy import func, select
from sqlalchemy.orm import contains_eager

from src.db import Session
from src.models import Country, Customer, Manufacturer, Order, OrderItem, Product, ProductReview

locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8")


def print_money(amount: float | Decimal):
    return locale.currency(amount, grouping=True)


def pedidos_acima_de_300():
    total = func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
    with Session() as s:
        query = (
            select(Order, total)
            .join(Order.order_items)
            .group_by(Order.id)
            .having(total > 300)
            .order_by(total.desc())
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r[0]}: {print_money(r[1])}")


def pedidos_com_zx81():
    """
    SELECT o.* FROM orders o
    INNER JOIN orders_items oi ON oi.order_id = o.id
    INNER JOIN products p ON oi.product_id = p.id
    WHERE p.name IN ('ZX81');
    """
    with Session() as s:
        query = (
            select(Order)
            .join(Order.order_items)
            .join(OrderItem.product)
            .where(Product.name.in_(["ZX81"]))
            .options(contains_eager(Order.order_items))
        )
        res = s.scalars(query).unique()
        for r in res:
            rich.print(f"Pedido: {r}")


def pedidos_da_marca_amstrad():
    """
    SELECT o.*, p.name, m.id FROM orders o
    INNER JOIN orders_items oi ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    INNER JOIN manufacturers m ON m.id = p.manufacturer_id
    WHERE m.name = 'Amstrad';
    """
    with Session() as s:
        query = (
            select(Order)
            .join(Order.order_items)
            .join(OrderItem.product)
            .join(Product.manufacturer)
            .where(Manufacturer.name == "Amstrad")
        )
        res = s.scalars(query).all()
        rich.print(f"Total de pedidos Amstrad {len(res)}")
        for r in res:
            rich.print(r)


def pedidos_feitos_natal_mais_de_um_produto():
    """
    SELECT o.*, COUNT(oi.product_id) FROM orders o
    INNER JOIN orders_items oi ON o.id = oi.order_id
    WHERE o.timestamp BETWEEN '12-25-2022 00:00:00' AND '12-25-2022 23:59:59'
    GROUP BY o.id
    HAVING COUNT(oi.product_id) > 1;
    """
    with Session() as s:
        p_count = func.count(OrderItem.product_id).label(None)
        query = (
            select(Order, p_count)
            .join(Order.order_items)
            .where(Order.timestamp.between("12-25-2022 00:00:00", "12-25-2022 23:59:59"))
            .group_by(Order.id)
            .having(p_count > 1)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"Order {r[0]}: {r[1]} products")


def clientes_pedidos_mais_novos_mais_antigos():
    """
    SELECT c.name, MIN(o.timestamp), MAX(o.timestamp) FROM orders o
    INNER JOIN customers c ON c.id = o.customer_id
    GROUP BY c.id
    ORDER BY c.name;
    """
    with Session() as s:
        min_timestamp = func.min(Order.timestamp).label(None)
        max_timestamp = func.max(Order.timestamp).label(None)

        query = (
            select(Customer.name, min_timestamp, max_timestamp)
            .join(Customer.orders)
            .group_by(Customer.id)
            .order_by(Customer.name)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(
                f"{r[0]}: 1º pedido em {r[1].strftime('%d/%m/%Y %H:%M:%S')}.\t"
                f" último pedido em {r[2].strftime('%d/%m/%Y %H:%M:%S')}"
            )


def top5_fabricantes_com_mais_vendas():
    """
    SELECT m.name, m.id , SUM(oi.quantity * oi.unit_price) as "Total vendido"
    FROM orders_items oi
    INNER JOIN products p ON p.id = oi.product_id
    INNER JOIN manufacturers m ON m.id = p.manufacturer_id
    GROUP BY m.id
    ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    LIMIT 5;
    """
    with Session() as s:
        amount = func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
        query = (
            select(Manufacturer.name, amount)
            .join(Manufacturer.products)
            .join(Product.order_items)
            .group_by(Manufacturer.id)
            .order_by(amount.desc())
            .limit(5)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r[0]} vendeu {print_money(r[1])}")


def produtos_avaliacoes():
    """
    SELECT p.name, AVG(pr.rating) as "Média de avaliações", COUNT(pr.rating) as "Número de avaliações"
    FROM products p
    INNER JOIN products_reviews pr ON p.id = pr.product_id
    GROUP BY p.id
    ORDER BY COUNT(pr.rating) DESC;
    """
    rating_avg = func.avg(ProductReview.rating).label(None)
    rating_count = func.count(ProductReview.rating).label(None)
    with Session() as s:
        query = (
            select(Product.name, rating_avg, rating_count)
            .join(Product.reviews)
            .group_by(Product.id)
            .order_by(rating_count.desc())
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"Produto {r[0]} {r[1]:.2f} estrelas, avaliado por {r[2]}")


def media_avaliacoes_com_comentarios():
    """
    SELECT p.name, avg(pr.rating)
    FROM products p
    INNER JOIN products_reviews pr ON p.id = pr.product_id
    WHERE pr.comment IS NOT NULL
    GROUP BY p.id;
    """
    rating_avg = func.avg(ProductReview.rating).label(None)
    with Session() as s:
        query = (
            select(Product.name, rating_avg)
            .join(Product.reviews)
            .where(ProductReview.comment.isnot(None))
            .group_by(Product.id)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"Produto {r[0]}: {r[1]:.2f} estrelas ")


def media_avaliacoes_commodore64_por_mes():
    """
    SELECT avg(pr.rating), EXTRACT(month from pr.timestamp)
    FROM products_reviews pr
    INNER JOIN products p ON p.id = pr.product_id
    WHERE p.name = 'Commodore 64' AND pr.timestamp BETWEEN '01-01-2022 00:00:00' AND '12-31-2022 23:59:59'
    GROUP BY EXTRACT(month from pr.timestamp);
    """
    month = func.extract("month", ProductReview.timestamp).label(None)
    rating_avg = func.avg(ProductReview.rating).label(None)
    with Session() as s:
        query = (
            select(rating_avg, month)
            .join(Product.reviews)
            .where(Product.name == "Commodore 64")
            .where(ProductReview.timestamp.between("01-01-2022 00:00:00", "12-31-2022 23:59:59"))
            .group_by(month)
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"Mês {r[1]}: {r[0]:.2f}")


def maior_menor_nota_cliente():
    """
    SELECT c.name, MIN(pr.rating) as "Menor nota", MAX(pr.rating)
    FROM customers c
    INNER JOIN products_reviews pr ON c.id = pr.customer_id
    GROUP BY c.id
    ORDER BY c.name;
    """
    min_rating = func.min(ProductReview.rating).label(None)
    max_rating = func.max(ProductReview.rating).label(None)
    with Session() as s:
        query = (
            select(Customer.name, min_rating, max_rating)
            .join(Customer.reviews)
            .group_by(Customer.id)
            .order_by(Customer.name)
        )
        res = s.execute(query).all()

        for r in res:
            rich.print(f"{r[0]}: menor nota {r[1]}, maior nota {r[2]}")


def media_avaliacao_fabricantes():
    """
    SELECT m.name, m.id, AVG(pr.rating) AS "Média"
    FROM manufacturers m
    INNER JOIN products p ON p.manufacturer_id = m.id
    INNER JOIN products_reviews pr ON pr.product_id = p.id
    GROUP BY m.id, p.id
    ORDER BY AVG(pr.rating) DESC;
    """
    rating_avg = func.avg(ProductReview.rating).label(None)
    with Session() as s:
        query = (
            select(Manufacturer.name, rating_avg)
            .join(Manufacturer.products)
            .join(Product.reviews)
            .group_by(Manufacturer.id, Product.id)
            .order_by(rating_avg.desc())
        )
        res = s.execute(query).all()
        for r in res:
            rich.print(f"{r[0]}: {r[1]:.2f} ⭐")


def media_avaliacao_paises():
    """
    SELECT c.name, AVG(pr.rating) AS "Média de avaliações"
    FROM products_reviews pr
    INNER JOIN products p ON p.id = pr.product_id
    INNER JOIN products_countries pc ON p.id = pc.product_id
    INNER JOIN countries c ON c.id = pc.country_id
    GROUP BY c.id
    ORDER BY  AVG(pr.rating) DESC;
    """
    rating_avg = func.avg(ProductReview.rating).label(None)
    with Session() as s:
        query = (
            select(Country.name, rating_avg)
            .join(Country.products)
            .join(Product.reviews)
            .group_by(Country.id)
            .order_by(rating_avg.desc())
        )
        res = s.execute(query).all()

        for r in res:
            rich.print(f"{r[0]}: {r[1]:.2f} ⭐")


if __name__ == "__main__":
    # pedidos_acima_de_300()
    # pedidos_com_zx81()
    # pedidos_da_marca_amstrad()
    # pedidos_feitos_natal_mais_de_um_produto()
    # clientes_pedidos_mais_novos_mais_antigos()
    # top5_fabricantes_com_mais_vendas()
    # produtos_avaliacoes()
    # media_avaliacoes_com_comentarios()
    # media_avaliacoes_commodore64_por_mes()
    # maior_menor_nota_cliente()
    # media_avaliacao_fabricantes()
    media_avaliacao_paises()
