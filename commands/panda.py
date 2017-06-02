from api import vk_api
from commands import _command_system


def panda(data):
    # Получаем случайную картинку из пабли
    attachment = vk_api.get_random_wall_picture(-36259673)
    message = "Вот тебе панда :3\nВ следующий раз я пришлю другую панду"

    return message, attachment


panda_command = _command_system.Command()
panda_command.name = 'panda'
panda_command.keys = ['панда', 'панды', 'panda']
panda_command.description = 'пришлю картинку с пандой'
panda_command.process = panda
