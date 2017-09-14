import random

import utils

from models.await import Await
from commands._system import Command
from commands._system import register


@register
class BullsCows(Command):
    name = 'bulls_cows'
    keys = ['быки и коровы']
    description = 'игра "Быки и Коровы"'
    await = 'bulls_cows'

    def do(self, data, await=None):
        """Игра "Быки и Коровы".

        В классическом варианте игра рассчитана на двух игроков. Каждый из игроков задумывает
        и записывает тайное 4-значное число с неповторяющимися цифрами.

        Игрок, который начинает игру по жребию, делает первую попытку отгадать число.
        Попытка — это 4-значное число с неповторяющимися цифрами, сообщаемое противнику.
        Противник сообщает в ответ, сколько цифр угадано без совпадения с их позициями в тайном
        числе (то есть количество коров) и сколько угадано вплоть до позиции в тайном
        числе (то есть количество быков).

        Например:
        Задумано тайное число «3219».
        Попытка: «2310».
        Результат: две «коровы» (две цифры: «2» и «3» — угаданы на неверных позициях)
        и один «бык» (одна цифра «1» угадана вплоть до позиции).

        Игроки делают попытки угадать по очереди. Побеждает тот, кто угадает
        число первым, при условии, что он не начинал игру. Если же
        отгадавший начинал игру — его противнику предоставляется последний
        шанс угадать последовательность.
        При игре против компьютера игрок вводит комбинации одну за другой,
        пока не отгадает всю последовательность.


        Args:
            data (dict): данные входящего сообщения от пользователя
            await (obj): ожидания от пользователя

        Returns:
            str: текст сообщения для пользователя
            None: пустой аттач

        """
        if not await:
            return self._create_await(data), None

        if self._is_need_rules(data):
            return 'Я задумываю тайное 4-значное число с неповторяющимися цифрами. ' \
                   'Ты делаешь первую попытку отгадать число. Попытка — это 4-значное число с ' \
                   'неповторяющимися цифрами, сообщаемое мне. В ответ я сообщаю, сколько цифр угадано ' \
                   'без совпадения с их позициями в тайном числе (то есть количество коров) ' \
                   'и сколько угадано вплоть до позиции в тайном числе (то есть количество быков). \n\n' \
                   'Например:\nЗадумано тайное число «3219».\nПопытка: «2310».\nРезультат: две «коровы» ' \
                   '(две цифры: «2» и «3» — угаданы на неверных позициях) и один «бык» (' \
                   'одна цифра «1» угадана вплоть до позиции).', None

        return self._process_await(data, await), None

    def _create_await(self, data):
        """ От пользователя еще не ожидается попытка хода.
        Создаем ожидание и даем возможность пользователю сделать ход

        Args:
            data (dict): данные входящего сообщения от пользователя

        Returns:
            str: сообщение для пользователя

        """
        Await.create(user_id=data['user_id'], command=self.await, args={'secret': self._make_number()})
        return 'Я загадал секретное число, попробуй отдагать его.\n' \
               'Если хочешь остановить игру, напиши "стоп".\n' \
               'Если хочешь узнать как играть, напиши "правила".'

    def _process_await(self, data, await):
        """ Получаем шаг от игрока и обрабатываем его

        Args:
            data (dict): данные от пользователя
            await (object): ожидания от пользователя

        Returns:
            str: сообщение пользователю
            str: аттач пользователю

        """
        # проверяем хочет ли игрок прекратить игру
        if self._is_need_stop(data):
            Await.delete().where(Await.id == await.id).execute()
            return "Хорошо, мы больше не играем.", None

        secret = await.args.get('secret')
        ask = data['body'].strip()

        # проверяем сообщение от игрока по правилам игры
        check, msg = self._check_ask(ask)
        if not check:
            return '{}\nЕсли хочешь остановить игру, напиши "стоп".\n' \
                   'Если хочешь узнать как играть, напиши "правила".'.format(msg)

        # считаем количество быков и коров
        bulls = self._calc_bulls(secret, ask)
        cows = self._calc_cows(secret, ask)

        # игрок еще не победил, формируем ответ
        if bulls != 4:
            return self._formate_answer(bulls, cows)
        # игрок победил, удаляем ожидание, поздравляем
        else:
            Await.delete().where(Await.id == await.id).execute()
            return "Поздравляю, ты победил, мое секретное число было: {}".format(secret)

    def _is_need_stop(self, data):
        """ Проверяем, надо ли нам прекратить игру

        Args:
            data (dict): данные от пользователя

        Returns:
            bool: прекратить

        """
        msg = data['body'].strip().lower()

        distance = utils.calc_damerau_levenshtein_distance(msg, 'стоп')
        if distance < 1:
            return True

        return False

    def _is_need_rules(self, data):
        """ Проверяем, надо ли отправить игроку правила игры

        Args:
            data (dict): данные от пользователя

        Returns:
            bool: отправить

        """
        msg = data['body'].strip().lower()

        distance = utils.calc_damerau_levenshtein_distance(msg, 'правила')
        if distance < 1:
            return True

        return False

    def _make_number(self):
        """ Сделать 4-значное число с неповторяющимися цифрами

        Returns:
            str: число
        """
        digs = [d for d in range(0, 10)]

        number = []
        for i in range(0, 4):
            d = random.choice(digs)
            digs.remove(d)
            number.append(d)

        return ''.join([str(x) for x in number])

    def _check_ask(self, ask):
        """ Проверить шаг пользователя по правилам игры

        Args:
            ask (str): шаг пользователя

        Returns:
            bool: результат проверки
            str: сообщение проверки
        """
        if len(ask) != 4:
            return False, "Здесь нет 4х цифр."

        for d in ask:
            if not d.isdigit():
                return False, "В твоем сообщении не только цифры."

        if len(set(ask)) != 4:
            return False, "По правилам игры, цифры не могут повторяться."

        return True, None

    def _calc_bulls(self, secret, ask):
        """ Подсчитать сколько быков

        Args:
            secret (str): секретное число
            ask (str): шаг пользователя

        Returns:
            int: количество быков

        """
        bulls = 0
        for n, l in enumerate(ask):
            if secret[n] == l:
                bulls += 1

        return bulls

    def _calc_cows(self, secret, ask):
        """ Подсчитать сколько коров

        Args:
            secret (str): секретное число
            ask (str): шаг пользователя

        Returns:
            int: количество коров

        """
        cows = 0
        for n, l in enumerate(ask):
            if secret[n] != l and l in secret:
                cows += 1

        return cows

    def _formate_answer(self, bulls, cows):
        """ Сформировать ответ игроку на основе количества быков и коров

        Args:
            bulls (int): количество быков
            cows (int): количество коров

        Returns:
            str: ответ игроку
        """
        if bulls == 0:
            bulls_str = 'быков'
        elif bulls == 1:
            bulls_str = 'бык'
        else:
            bulls_str = 'быка'

        if cows == 0:
            cows_str = 'коров'
        elif cows == 1:
            cows_str = 'корова'
        else:
            cows_str = 'коровы'

        return '{} {}, {} {}'.format(bulls, bulls_str, cows, cows_str)
