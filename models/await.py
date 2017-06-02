import peewee

from models._base import BaseModel
from playhouse.postgres_ext import HStoreField


class Await(BaseModel):
    id = peewee.PrimaryKeyField()
    user_id = peewee.IntegerField(unique=True)
    command = peewee.CharField()
    args = HStoreField(null=True)
    attempts = peewee.IntegerField(default=0)
