commands = []


class Command:
    def __init__(self):
        self.name = None
        self.__keys = []
        self.description = None
        self.await = None
        commands.append(self)

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, mas):
        for k in mas:
            self.__keys.append(k.lower())

    def process(self, data):
        raise NotImplementedError
