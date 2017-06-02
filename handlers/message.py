import logging

import utils
import peewee
import commands.cat
import commands.info
import commands.hello
import commands.panda
import commands.stories

from api import vk_api
from models.await import Await
from commands._system import commands


def get_answer(data):
    """ Получаем ответ для пользователя из модулей бота

    Args:
        data (dict): данные входящего сообщения от пользователя

    Returns:
        str: текст сообщения для пользователя
        str: аттач в сообщении
    """
    body = data['body'].lower()
    message = None
    attachment = None

    try:
        await_command = Await.get(Await.user_id == data['user_id'])
    except peewee.DoesNotExist:
        await_command = None

    probably_key = None
    probably_command = None
    min_distance = len(body)
    for command in commands:
        # если модуль ожиает от пользователя сообщения, сразу передаем управление в модуль
        if await_command and command.await == await_command.command:
            return command.do(data, await=await_command)

        # иначе пытается подобрать модуль на основе комманды
        for key in command.keys:
            distance = utils.calc_damerau_levenshtein_distance(body, key)
            if distance < min_distance:
                min_distance = distance
                probably_command = command
                probably_key = key

                # минимальная дистанция без опечаток
                if min_distance == 0:
                    return command.do(data)

    # выбираем модуль с минимальным расстоянием
    if min_distance < len(body) * 0.4:
        message, attachment = probably_command.do(data)
        message = "Я понял ваш запрос как '{}'\n\n{}".format(probably_key, message)

    return message, attachment


def create_answer(data):
    """ Создаем ответ пользователю

    Args:
        data (dict): данные входящего сообщения от пользователя

    Returns:
        str: текст сообщения для пользователя
        str: аттач в сообщении
    """
    logging.info("Incoming msg {}".format(data))

    message, attachment = get_answer(data)
    if message is None:
        message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"

    logging.info("Outcoming msg to: '{}', msg: '{}', attch: '{}'".format(data['user_id'], message, attachment))
    vk_api.send_message(data['user_id'], message, attachment)
