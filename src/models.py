"""
O mapeamento objeto-relacional é feito usando type hints, com a classe so.Mapped[t], sendo t um tipo Python.
Para configurações adicionais, usamos o construtor so.mapped_column.

# Relacionamentos
Diferentemente do Java, que estabelecemos o relacionamento usando uma coleção ou atributo do tipo do objeto,
no SQLAlchemy criamos manualmente a coluna que será FK da outra tabela, usando a classe ForeignKey.

"""

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import ForeignKey

from src.db import Model


class Product(Model):
    __tablename__ = "products"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    year: so.Mapped[int] = so.mapped_column(index=True)
    country: so.Mapped[str | None] = so.mapped_column(sa.String(32))
    cpu: so.Mapped[str | None] = so.mapped_column(sa.String(32))

    # FKs
    manufacturer_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("manufacturers.id"), index=True
    )

    # Atributo virtual para facilitar a navegação
    manufacturer: so.Mapped["Manufacturer"] = so.relationship(back_populates="products")

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
    products: so.Mapped[list["Product"]] = so.relationship(back_populates="manufacturer")

    def __repr__(self):
        return f"Manufacturer ({self.id}, {self.name})"

    def add_product(self, product: Product) -> None:
        self.products.append(product)


class Country(Model):
    __tablename__ = "countries"
    id: so.Mapped[int] = so.mapped_column(primary_key=True, index=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True)

    def __repr__(self):
        return f"Country({self.id}, {self.name})"
