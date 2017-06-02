from peewee import Model
from settings import db


class BaseModel(Model):
    class Meta:
        database = db
