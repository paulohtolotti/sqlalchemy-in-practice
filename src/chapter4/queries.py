import logging

from src.db import Session
from src.models import *

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(name)s %(funcName)s %(message)s',
    level=logging.INFO
)


def adding_countries():
    """Para remover ou adicionar entidades, basta acessar o atributo virtual mapeado"""
    with Session() as s, s.begin():
        product = s.get(Product, 20)

        if not product:
            return

        logger.info("Adicionando países para produto %s", product.name)
        country1 = s.get(Country, 1)
        country2 = s.get(Country, 2)

        if country1 and country2:
            product.countries.append(country1)
            product.countries.append(country2)
        

def removing_countries():
    # Removendo os países adicionados anteriormente
    with Session() as s, s.begin():
        product = s.get(Product, 20)

        if not product:
            logger.error("Produto com id 20 não existe")

        # Limpando a associação
        product.countries = [c for c in product.countries if c.id != 2 and c.id != 3]

if __name__ == "__main__":
    removing_countries()