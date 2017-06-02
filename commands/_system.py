commands = []


def register(cls):
    commands.append(cls())


class Command:
    name = None
    keys = None
    description = None
    await = None

    def __init__(self):
        self._check_command()

    def _check_command(self):
        for a in ['name', 'keys', 'description']:
            if getattr(self, a) is None:
                raise AttributeError

    def do(self, data):
        raise NotImplementedError
