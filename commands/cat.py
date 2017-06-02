from api import vk_api
from commands import _command_system


def cat(data):
    # Получаем случайную картинку из пабли
    attachment = vk_api.get_random_wall_picture(-32015300)
    message = "Вот тебе котик :)\nВ следующий раз я пришлю другого котика."

    return message, attachment


cat_command = _command_system.Command()
cat_command.name = 'cat'
cat_command.keys = ['котик', 'кошка', 'кот', 'котенок', 'котяра', 'cat']
cat_command.description = 'пришлю картинку с котиком'
cat_command.process = cat
