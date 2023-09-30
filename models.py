import datetime
import os

from dotenv import load_dotenv
from peewee import (CharField, DateTimeField, ForeignKeyField, Model,
                    PostgresqlDatabase, TextField)


load_dotenv()

db = PostgresqlDatabase(
    os.getenv('POSTGRES_DB', 'bot_rates'),
    user=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', 5432),
)


class User(Model):
    username = CharField(
        max_length=32,
    )
    reg_date = DateTimeField(
        default=datetime.datetime.now,
        verbose_name='Дата регистрации',
    )

    class Meta:
        database = db


class Message(Model):
    from_user = ForeignKeyField(
        User,
        on_delete='CASCADE',
        backref='outbox',
        verbose_name='От кого',
    )
    to_user = ForeignKeyField(
        User,
        on_delete='CASCADE',
        backref='inbox',
        verbose_name='Кому',
    )
    text = TextField(
        verbose_name='Текст сообщения',
    )

    class Meta:
        database = db


if __name__ == '__main__':
    db.connect()
    db.create_tables([Message, User])
    User.create(id=0, username='bot')
    User.create(id=1, username='test')
    Message.create(
        from_user=0,
        to_user=1,
        text='Тестируем Большие русские буквы',
    )
    db.close()
