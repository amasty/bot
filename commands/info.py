import utils
from commands import _command_system


def info(data):
    message = "Вот мои команды:\n{}".format(
        utils.get_commands_list()
    )

    return message, None


info_command = _command_system.Command()
info_command.name = 'info'
info_command.keys = ['помощь', 'помоги', 'help']
info_command.description = 'покажу список команд'
info_command.process = info
