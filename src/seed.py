"""
Realiza o seed do banco de dados a partir de um CSV (/data/products.csv)
"""

import csv
import logging

from src.db import Model, Session, engine_all_access
from src.models import Country, Manufacturer, Product


logger = logging.getLogger(__name__)

def initial_seed():
    with open("./data/products.csv", "r", encoding="utf-8") as file:
        # Realiza a leitura dos dados como um dicionário. Usa a primeira linha como referência
        reader = csv.DictReader(file)
        products = set()
        all_countries: dict[str, Country] = {}
        manufacturers: dict[str, Manufacturer] = {}

        with Session() as session, session.begin():
            for row in reader:
                row["year"] = int(row["year"])
                manufacturer_name = row.pop("manufacturer")
                countries = row.pop("country").split("/")
                product: Product = Product(**row)

                if manufacturer_name not in manufacturers:
                    manufacturer = Manufacturer(name=manufacturer_name)
                    session.add(manufacturer)
                    manufacturers[manufacturer_name] = manufacturer


                for c in countries:
                    if c not in all_countries:
                        logger.info("Criando %s", c)
                        country = Country(name=c)
                        session.add(country)
                        all_countries[c] = country # "USA": <__main__.Country object at 0x000001D2CE37F8C0>
                    logger.info("Associando %s ao produto %s", c, product.name)
                    all_countries[c].products.append(product)

                # Automaticamente inclue no banco devido ao relacionamento
                manufacturers[manufacturer_name].add_product(product)

            session.add_all(products)


def clean_database():
    Model.metadata.drop_all(engine_all_access)
    Model.metadata.create_all(engine_all_access)


if __name__ == "__main__":
    clean_database()
    initial_seed()
