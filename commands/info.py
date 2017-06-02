import utils

from commands._system import Command
from commands._system import register


@register
class Hello(Command):
    name = 'info'
    keys = ['помощь', 'помоги', 'help']
    description = 'покажу список команд'

    def do(self, data):
        """ Показать список комманд

        Args:
            data (dict): данные входящего сообщения от пользователя

        Returns:
            str: текст сообщения для пользователя
            None: пустой аттач
        """
        message = "Вот мои команды:\n{}".format(
            utils.get_commands_list()
        )

        return message, None
