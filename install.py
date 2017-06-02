from settings import db
from models.await import Await
from models.stories import Stories
from models.stories import StoriesText

db.drop_tables([Stories, StoriesText, Await], cascade=True)
db.create_tables([Stories, StoriesText, Await], safe=True)
