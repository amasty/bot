import utils

from commands._system import Command
from commands._system import register


@register
class Hello(Command):
    name = 'info'
    keys = ['помощь', 'помоги', 'help']
    description = 'покажу список команд'

    def _do(self):
        """ Показать список комманд

        Returns:
            str: текст сообщения для пользователя

        """
        message = "Вот мои команды:\n{}".format(
            utils.get_commands_list()
        )

        return utils.show_message(message)
