import datetime
import os

from dotenv import load_dotenv
from peewee import (DateTimeField, ForeignKeyField, Model, PostgresqlDatabase,
                    TextField)


load_dotenv()

db = PostgresqlDatabase(
    os.getenv('POSTGRES_DB', 'bot_rates'),
    user=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', 5432),
)


class User(Model):
    reg_date = DateTimeField(
        default=datetime.datetime.now,
        verbose_name='Дата регистрации',
    )

    class Meta:
        database = db

    def delete_instance(self, *args, **kwargs):
        if self.id == 0:
            raise Exception('Нельзя удалить аккаунт бота')
        return super().delete_instance(*args, **kwargs)


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
    datetime = DateTimeField(
        default=datetime.datetime.now,
        verbose_name='Дата и время',
    )

    class Meta:
        database = db


if __name__ == '__main__':
    db.connect()
    db.create_tables([Message, User])
    User.get_or_create(id=0)
    db.close()
