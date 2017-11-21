import utils

from commands._system import Command
from commands._system import register


@register
class Hello(Command):
    name = 'hello'
    keys = ['привет', 'hello', 'дратути', 'здравствуй', 'здравствуйте']
    description = 'поприветствую тебя'

    def _do(self):
        """ Сказать привет пользователю и показать список комманд

        Returns:
            str: текст сообщения для пользователя

        """
        message = "Привет, друг!\nЯ чат-бот, вот мои команды:\n{}".format(
            utils.get_commands_list()
        )

        return utils.show_message(message)
