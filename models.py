import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=100)
    joined_on = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ('-joined_on',)

    @classmethod
    def create_user(cls, username, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists")

    def get_journal(self):
        """Get journal entries for a user"""
        return

class BaseModel(UserMixin, Model):
    class Meta:
        database = DATABASE

class BlogEntry(BaseModel):
    pk = PrimaryKeyField()
    title = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    time_spent = CharField()
    learned = TextField()
    resources = TextField()
    tags = CharField(default='')
    user = CharField()
    slug = CharField()

    class Meta:
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, title, date, time_spent, learned,
                     resources, tags, user, slug):
        with DATABASE.transaction():
            cls.create(title=title,
                       date=date,
                       time_spent=time_spent,
                       learned=learned,
                       resources=resources,
                       tags=tags,
                       user=user,
                       slug=slug
                      )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, BlogEntry,], safe=True)
    DATABASE.close()
