import os

from dotenv import load_dotenv
from peewee import PostgresqlDatabase

from models import Message

load_dotenv()

db = PostgresqlDatabase(
    os.getenv('POSTGRES_DB', 'bot_rates'),
    user=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', 5432),
)

q = Message.select().where(Message.text.contains('тест'))
for i in q:
    print(i.text)
