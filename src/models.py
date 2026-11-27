"""
O mapeamento objeto-relacional é feito usando type hints, com a classe so.Mapped[t], sendo t um tipo Python.
Para configurações adicionais, usamos o construtor so.mapped_column.

# Relacionamentos
Diferentemente do Java, que estabelecemos o relacionamento usando uma coleção ou atributo do tipo do objeto,
no SQLAlchemy criamos manualmente a coluna que será FK da outra tabela, usando a classe ForeignKey.

# A 1 - B N
O lado 1 recebe um atributo virtual do tipo do objeto do lado N.
O back populates serve para sincronizar os dois lados do relacionamento, portanto,
os nomes são inversos.
O lado N recebe um atributo indicando a FK diretamente, que é um mapped_column,
e um atributo virtual do tipo classe.
Lado 1
    Mapped[list[B]] = relationship(back_populates="nome do attr do lado N", cascade="comportamento no delete")
Lado N
    a_id: Mapped[UUID] = mapped_column(ForeignKey="tabela_a.id")
    a: Mapped[A] = relationship(back_populates="b"

# A N - B N
Criamos uma tabela associativa usando o sqlalchemy core.
O mapeamento entre A e B é feito somente via entidades e usando o atributo secondary.
"""

import datetime
import decimal
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.types import DateTime

from src.db import Model

__all__ = ["Country", "Customer", "Manufacturer", "Order", "OrderItem", "Product"]

ProductCountry = sa.Table(
    "products_countries",
    Model.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column("country_id", sa.ForeignKey("countries.id"), primary_key=True),
)


class Product(Model):
    __tablename__ = "products"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    year: so.Mapped[int] = so.mapped_column(index=True)
    cpu: so.Mapped[str | None] = so.mapped_column(sa.String(32))

    # FKs
    manufacturer_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("manufacturers.id"), index=True
    )

    # Atributo virtual para facilitar a navegação
    manufacturer: so.Mapped[Manufacturer] = so.relationship(back_populates="products")
    countries: so.Mapped[list[Country]] = so.relationship(
        secondary=ProductCountry, back_populates="products"
    )
    order_items: so.WriteOnlyMapped[OrderItem] = so.relationship(back_populates="product")
    reviews: so.WriteOnlyMapped[ProductReview] = so.relationship(back_populates="product")
    articles: so.WriteOnlyMapped[BlogArticle] = so.relationship(back_populates="product")

    @classmethod
    def from_dto(cls):
        """Cria um Produto a partir de um DTO. Exemplo de um construtor alternativo"""
        return Product()

    def __repr__(self):
        return f"Product({self.id}, {self.name})"


class Manufacturer(Model):
    __tablename__ = "manufacturers"
    id: so.Mapped[int] = so.mapped_column(primary_key=True, index=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)

    # Atributo virtual para facilitar a navegação
    products: so.Mapped[list[Product]] = so.relationship(
        cascade="all, delete-orphan", back_populates="manufacturer"
    )  # Deleta produtos associados quando o fabricante é removido

    def __repr__(self):
        return f"Manufacturer ({self.id}, {self.name})"

    def add_product(self, product: Product) -> None:
        self.products.append(product)


class Country(Model):
    __tablename__ = "countries"
    id: so.Mapped[int] = so.mapped_column(primary_key=True, index=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True)

    # Atributos virtuais
    products: so.Mapped[list[Product]] = so.relationship(
        secondary=ProductCountry, back_populates="countries"
    )

    def __repr__(self):
        return f"Country({self.id}, {self.name})"


class Customer(Model):
    __tablename__ = "customers"
    id: so.Mapped[uuid.UUID] = so.mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), index=True)
    address: so.Mapped[str] = so.mapped_column(sa.String)
    phone: so.Mapped[str] = so.mapped_column(sa.String(20), unique=True)

    orders: so.WriteOnlyMapped[Order] = so.relationship(back_populates="customer")
    reviews: so.WriteOnlyMapped[ProductReview] = so.relationship(back_populates="customer")
    blog_users: so.WriteOnlyMapped[BlogUser] = so.relationship(back_populates="customer")
    
    def __repr__(self):
        return f'Customer({self.id.hex}, "{self.name}")'


class Order(Model):
    __tablename__ = "orders"
    id: so.Mapped[uuid.UUID] = so.mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    timestamp: so.Mapped[datetime.datetime] = so.mapped_column(
        DateTime(timezone=False), default=datetime.datetime.now(tz=datetime.UTC)
    )
    customer_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("customers.id"))

    customer: so.Mapped[Customer] = so.relationship(
        back_populates="orders", lazy="raise", order_by=timestamp.desc()
    )
    order_items: so.Mapped[list[OrderItem]] = so.relationship(back_populates="order")

    def __repr__(self):
        return f"Order({self.id.hex})"


class OrderItem(Model):
    __tablename__ = "orders_items"

    product_id: so.Mapped[uuid.UUID] = so.mapped_column(
        sa.ForeignKey("products.id"), primary_key=True
    )
    order_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("orders.id"), primary_key=True)
    unit_price: so.Mapped[decimal.Decimal] = so.mapped_column(sa.DECIMAL(10, 2))
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer)

    product: so.Mapped[Product] = so.relationship(back_populates="order_items")
    order: so.Mapped[Order] = so.relationship(back_populates="order_items")

    def __repr__(self):
        return f"OrderItem(p_id: {self.product_id}, order_id: {self.order_id})"


class ProductReview(Model):
    __tablename__ = "products_reviews"

    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("products.id"), primary_key=True)
    customer_id: so.Mapped[uuid.UUID] = so.mapped_column(
        sa.ForeignKey("customers.id"), primary_key=True
    )
    timestamp: so.Mapped[datetime.datetime] = so.mapped_column(
        sa.DateTime(timezone=False), default=datetime.datetime.now(tz=datetime.UTC), index=True
    )
    rating: so.Mapped[int] = so.mapped_column(sa.Integer)
    comment: so.Mapped[str | None] = so.mapped_column(sa.Text, nullable=True)
    product: so.Mapped[Product] = so.relationship(back_populates="reviews")
    customer: so.Mapped[Customer] = so.relationship(back_populates="reviews")


class BlogAuthor(Model):
    __tablename__ = "blog_authors"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)

    articles: so.WriteOnlyMapped[BlogArticle] = so.relationship(back_populates="author")

    def __repr__(self):
        return f"BlogAuthor({self.id}, '{self.name}')"


class BlogArticle(Model):
    __tablename__ = "blog_articles"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("blog_authors.id"))
    product_id: so.Mapped[int | None] = so.mapped_column(
        sa.ForeignKey("products.id"), default=None
    )
    timestamp: so.Mapped[datetime.datetime] = so.mapped_column(
        sa.DateTime(timezone=False), default=datetime.datetime.now(tz=datetime.UTC), index=True
    )

    product: so.Mapped[Product | None] = so.relationship(back_populates="articles")
    author: so.Mapped[BlogAuthor] = so.relationship(back_populates="articles")
    views: so.WriteOnlyMapped[BlogView] = so.relationship(back_populates="article")

class BlogUser(Model):
    __tablename__ = "blog_users"
    id: so.Mapped[uuid.UUID] = so.mapped_column(default=uuid.uuid4, primary_key=True)
    customer_id: so.Mapped[uuid.UUID | None] = so.mapped_column(
        sa.ForeignKey("customers.id"), index=True, default=None
    )
    
    customer: so.Mapped[Customer | None] = so.relationship(back_populates="blog_users")
    sessions: so.Mapped[BlogSession] = so.relationship(back_populates="user")
    
    def __repr__(self):
        return f"BlogUser({self.id.hex})"
    
class BlogSession(Model):
    __tablename__ = "blog_sessions"
    id: so.Mapped[uuid.UUID] = so.mapped_column(default=uuid.uuid4, primary_key=True)
    user_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("blog_users.id"), index=True)
    
    user: so.Mapped[BlogUser] = so.relationship(back_populates="sessions")
    views: so.WriteOnlyMapped[BlogView] = so.relationship(back_populates="session")
    def __repr__(self):
        return f"BlogSession({self.id.hex})"

class BlogView(Model):
    __tablename__ = "blog_views"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    article_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("blog_articles.id"))
    session_id: so.Mapped[uuid.UUID] = so.mapped_column(sa.ForeignKey("blog_sessions.id"))

    timestamp: so.Mapped[datetime.datetime] = so.mapped_column(
        sa.DateTime(timezone=False), default=datetime.datetime.now(tz=datetime.UTC), index=True
    )
    session: so.Mapped[BlogSession] = so.relationship(back_populates="views")
    article: so.Mapped[BlogArticle] = so.relationship(back_populates="views")