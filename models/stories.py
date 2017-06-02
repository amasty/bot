import peewee

from models._base import BaseModel


class Stories(BaseModel):
    id = peewee.PrimaryKeyField()
    state = peewee.IntegerField()


class StoriesText(BaseModel):
    story = peewee.ForeignKeyField(Stories)
    user_id = peewee.IntegerField()
    text = peewee.TextField()
