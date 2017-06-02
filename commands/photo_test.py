from api import vk_api
from commands import _command_system


def photo(data):
    attachment = vk_api.upload_attach2message()
    message = "Вот тебе фото"

    return message, attachment


photo_test = _command_system.Command()
photo_test.name = 'photo_test'
photo_test.keys = ['photo', 'фото']
photo_test.description = 'пришлю фото'
photo_test.process = photo
