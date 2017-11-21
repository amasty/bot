import utils

from api import vk_api
from commands._system import Command
from commands._system import register


@register
class Cat(Command):
    name = 'cat'
    keys = ['котик', 'кошка', 'кот', 'котенок', 'котяра', 'cat']
    description = 'пришлю картинку с котиком'

    def _do(self):
        """ Получаем случайное фото кота с паблика

        Returns:
            str: текст сообщения для пользователя
            str: аттач в виде фото кота

        """
        attachment = vk_api.get_random_wall_picture(-32015300)
        message = "Вот тебе котик :)\nВ следующий раз я пришлю другого котика."

        return utils.show_message(message, attachment=attachment)
