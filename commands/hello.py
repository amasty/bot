import utils
from commands import _command_system


def hello(data):
    message = "Привет, друг!\nЯ чат-бот, вот мои команды:\n{}".format(
        utils.get_commands_list()
    )

    return message, None


hello_command = _command_system.Command()
hello_command.name = 'hello'
hello_command.keys = ['привет', 'hello', 'дратути', 'здравствуй', 'здравствуйте']
hello_command.description = 'поприветствую тебя'
hello_command.process = hello
