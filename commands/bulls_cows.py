import random

import utils

from models.userexpectation import UserExpectation
from commands._system import Command
from commands._system import register


@register
class BullsCows(Command):
    name = 'bulls_cows'
    keys = ['быки и коровы']
    description = 'игра "Быки и Коровы"'

    def _do(self):
        """Игра "Быки и Коровы".

        Notes:
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

        Returns:
            str: текст сообщения для пользователя
            None: пустой аттач

        """
        # пользователь еще не начинал игру, создаем
        if not self.user_expectations:
            return self._create_await()
        # или обрабатываем ход пользователя в уже созданной игре
        return self._process_await()

    def _create_await(self):
        """ От пользователя еще не ожидается попытка хода.
        Создаем ожидание и даем возможность пользователю сделать ход

        Returns:
            str

        """
        UserExpectation.create(user_id=self.data['user_id'], command=self.name, args={'secret': self._make_number()})

        return utils.show_message(
            "Я загадал секретное число, попробуй отдагать его.\n "
            "Если хочешь остановить игру, напиши «стоп».\n "
            "Если хочешь узнать как играть, напиши «правила»."
        )

    def _process_await(self):
        """ Получаем шаг от игрока и обрабатываем его

        Returns:
            str

        """
        # проверяем надо ли остановить игру, показать правила и ход пользователя
        for method in [
            self._stop_maybe,
            self._show_rules_maybe,
            self._check_ask,
        ]:
            message = method()
            if message:
                return utils.show_message(message)

        # серктеное число
        secret = self.user_expectations.args.get('secret')

        # считаем количество быков и коров
        bulls = self._calc_bulls(secret)
        cows = self._calc_cows(secret)

        if bulls == 4:
            # игрок победил, удаляем ожидание, поздравляем
            UserExpectation.delete().where(UserExpectation.id == self.user_expectations.id).execute()
            return utils.show_message("Поздравляю, ты победил, мое секретное число было: {}".format(secret))
        else:
            # игрок еще не победил, формируем ответ
            return utils.show_message(self._format_answer(bulls, cows))

    def _stop_maybe(self):
        """ Проверяем, хочет ли пользователь остановить игру

        Returns
            str

        """
        # проверяем хочет ли игрок прекратить игру
        distance = utils.calc_damerau_levenshtein_distance(self.ask, 'стоп')
        if distance < 1:
            UserExpectation.delete().where(UserExpectation.id == self.user_expectations.id).execute()
            return "Хорошо, мы больше не играем."

    def _show_rules_maybe(self):
        """Показать игроку правила игры

        Returns:
            str

        """
        distance = utils.calc_damerau_levenshtein_distance(self.ask, 'правила')
        if distance < 1:
            return "Я задумываю тайное 4-значное число с неповторяющимися цифрами. " \
                   "Ты делаешь первую попытку отгадать число. Попытка — это 4-значное число с " \
                   "неповторяющимися цифрами, сообщаемое мне. В ответ я сообщаю, сколько цифр угадано " \
                   "без совпадения с их позициями в тайном числе (то есть количество коров) " \
                   "и сколько угадано вплоть до позиции в тайном числе (то есть количество быков). \n\n" \
                   "Например:\nЗадумано тайное число «3219».\nПопытка: «2310».\nРезультат: две «коровы» " \
                   "(две цифры: «2» и «3» — угаданы на неверных позициях) и один «бык» (" \
                   "одна цифра «1» угадана вплоть до позиции)."

    def _make_number(self):
        """ Сделать 4-значное число с неповторяющимися цифрами

        Returns:
            str

        """
        digs = [d for d in range(0, 10)]

        number = []
        for i in range(0, 4):
            d = random.choice(digs)
            digs.remove(d)
            number.append(d)

        return ''.join([str(x) for x in number])

    def _check_ask(self):
        """ Проверить шаг пользователя по правилам игры

        Returns:
            str: сообщение проверки

        """
        msg = None

        if len(self.ask) != 4:
            msg = "Здесь нет 4х цифр."
        elif len(set(self.ask)) != 4:
            msg = "По правилам игры, цифры не могут повторяться."
        for d in self.ask:
            if not d.isdigit():
                msg = "В твоем сообщении не только цифры."
                break
        if msg:
            return "{}\nЕсли хочешь остановить игру, напиши «стоп».\n " \
                   "Если хочешь узнать как играть, напиши «правила».".format(msg)

    def _calc_bulls(self, secret):
        """ Подсчитать сколько быков

        Args:
            secret (str): секретное число

        Returns:
            int: количество быков

        """
        bulls = 0
        for n, l in enumerate(self.ask):
            if secret[n] == l:
                bulls += 1
        return bulls

    def _calc_cows(self, secret):
        """ Подсчитать сколько коров

        Args:
            secret (str): секретное число

        Returns:
            int: количество коров

        """
        cows = 0
        for n, l in enumerate(self.ask):
            if secret[n] != l and l in secret:
                cows += 1
        return cows

    @staticmethod
    def _format_answer(bulls, cows):
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

        return "{} {}, {} {}".format(bulls, bulls_str, cows, cows_str)
