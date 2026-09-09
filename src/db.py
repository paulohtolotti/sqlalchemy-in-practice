from dotenv import load_dotenv
from os import environ

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DB_URL = environ['DB_CONN_STRING']

engine: Engine = create_engine(DB_URL, echo=True, echo_pool=True)

class Model(DeclarativeBase):
    pass
