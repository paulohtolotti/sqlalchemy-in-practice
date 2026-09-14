"""
O mapeamento objeto-relacional é feito usando type hints, com a classe Mapped[t], sendo t um tipo Python.
Para configurações adicionais, usamos o construtor mapped_column.
"""
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Model, engine_all_access


class Product(Model):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    manufacturer: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(index=True)
    country: Mapped[Optional[str]] = mapped_column(String(32))
    cpu: Mapped[Optional[str]] = mapped_column(String(32))

    @classmethod
    def from_dto(cls):
        """Cria um Produto a partir de um DTO. Exemplo de um construtor alternativo"""
        return Product()

    def __repr__(self):
        return f"Product({self.id}, {self.name})"
