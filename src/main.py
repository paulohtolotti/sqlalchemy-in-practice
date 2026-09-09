from dotenv import load_dotenv
from os import environ

load_dotenv()

print(f"DB conn string: {environ['DB_CONN_STRING']}")
