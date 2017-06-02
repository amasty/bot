import utils

from commands._system import Command
from commands._system import register


@register
class Hello(Command):
    name = 'hello'
    keys = ['привет', 'hello', 'дратути', 'здравствуй', 'здравствуйте']
    description = 'поприветствую тебя'

    def do(self, data):
        """ Сказать привет пользователю и показать список комманд

        Args:
            data (dict): данные входящего сообщения от пользователя

        Returns:
            str: текст сообщения для пользователя
            None: пустой аттач
        """
        message = "Привет, друг!\nЯ чат-бот, вот мои команды:\n{}".format(
            utils.get_commands_list()
        )

        return message, None
