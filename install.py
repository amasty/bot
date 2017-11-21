from settings import db
from models.userexpectation import UserExpectation
from models.stories import Stories
from models.stories import StoriesText

db.drop_tables([Stories, StoriesText, UserExpectation], cascade=True)
db.create_tables([Stories, StoriesText, UserExpectation], safe=True)
