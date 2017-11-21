commands = []


def register(cls):
    commands.append(cls())


class Command:
    name = None
    keys = None
    description = None

    def __init__(self):
        self.data = None
        self.ask = None
        self.user_expectations = None
        self._check_command()

    def do(self, data, user_expectations=None):
        # данные о пользователе
        self.data = data
        # ожидания от пользователя
        self.user_expectations = user_expectations
        # сообщение пользователя
        self.ask = self.data['body'].strip().lower()

        return self._do()

    def _do(self):
        raise NotImplementedError

    def _check_command(self):
        for a in ['name', 'keys', 'description']:
            if getattr(self, a) is None:
                raise AttributeError
