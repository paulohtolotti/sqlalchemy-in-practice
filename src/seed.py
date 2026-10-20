"""
Realiza o seed do banco de dados a partir de um CSV (/data/products.csv)
"""
import csv

from src.db import Model, Session, engine_all_access
from src.models import Manufacturer, Product


def initial_seed():
    with open('./data/products.csv', 'r', encoding='utf-8') as file:
        # Realiza a leitura dos dados como um dicionário. Usa a primeira linha como referência
        reader = csv.DictReader(file)
        products = set()
        manufacturers: dict[str, Manufacturer] = {}

        with Session() as session, session.begin():
            for row in reader:
                row['year'] = int(row['year'])
                manufacturer_name = row.pop('manufacturer')
                product: Product = Product(**row)

                if manufacturer_name not in manufacturers:
                    manufacturer = Manufacturer(name=manufacturer_name)
                    session.add(manufacturer)
                    manufacturers[manufacturer_name] = manufacturer

                # Automaticamente inclue no banco devido ao relacionamento
                manufacturers[manufacturer_name].add_product(product)

            session.add_all(products)


def clean_database():
    Model.metadata.drop_all(engine_all_access)
    Model.metadata.create_all(engine_all_access)

if __name__ == "__main__":
    clean_database()
    initial_seed()