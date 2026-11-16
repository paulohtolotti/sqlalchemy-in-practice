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

import sqlalchemy as sa
import sqlalchemy.orm as so

from src.db import Model

__all__ = ['Country', 'Manufacturer', 'Product']

ProductCountry = sa.Table(
    "products_countries",
    Model.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column("country_id", sa.ForeignKey("countries.id"), primary_key=True)
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
        secondary=ProductCountry, back_populates='products'
    )
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
        cascade="all, delete-orphan", back_populates="manufacturer") # Deleta produtos associados quando o fabricante é removido

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
        secondary=ProductCountry, back_populates='countries'
    )
    def __repr__(self):
        return f"Country({self.id}, {self.name})"
