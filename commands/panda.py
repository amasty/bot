import utils

from api import vk_api
from commands._system import Command
from commands._system import register


@register
class Hello(Command):
    name = 'panda'
    keys = ['панда', 'панды', 'panda']
    description = 'пришлю картинку с пандой'

    def _do(self):
        """ Получаем случайное фото панды с паблика

        Returns:
            str: текст сообщения для пользователя
            str: аттач в виде фото панды

        """
        attachment = vk_api.get_random_wall_picture(-36259673)
        message = "Вот тебе панда :3\nВ следующий раз я пришлю другую панду"

        return utils.show_message(message, attachment=attachment)
