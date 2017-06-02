import os
import logging
import importlib

import utils
import peewee

from api import vk_api
from models.await import Await
from commands._command_system import commands


def load_modules():
    files = os.listdir("commands")
    modules = filter(lambda x: x.endswith('.py') and not x.startswith('_'), files)
    for m in modules:
        importlib.import_module("commands." + m[0:-3])


def get_answer(data):
    body = data['body'].lower()
    message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"
    attachment = None
    min_distance = float(len(body))

    try:
        await_command = Await.get(Await.user_id == data['user_id'])
    except peewee.DoesNotExist:
        await_command = None

    probably_key = None
    probably_command = None
    for command in commands:
        # если модуль ожиает от пользователя сообщения, сразу передаем управление в модуль
        if await_command and command.await == await_command.command:
            return command.process(data, await=await_command)

        # иначе пытается подобрать модуль на основе комманды
        for key in command.keys:
            distance = utils.calc_damerau_levenshtein_distance(body, key)
            if distance < min_distance:
                min_distance = distance
                probably_command = command
                probably_key = key

                if min_distance == 0:
                    return command.process(data)

    # не подобрали модуль, пытаемся подобрать с учетом опечаток
    if min_distance < len(body) * 0.4:
        message, attachment = probably_command.process(data)
        message = "Я понял ваш запрос как '{}'\n\n{}".format(probably_key, message)

    return message, attachment


def create_answer(data):
    load_modules()

    logging.info("Incoming msg {}".format(data))
    user_id = data['user_id']

    message, attachment = get_answer(data)
    if message is None:
        message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"

    logging.info("Outcoming msg to: '{}', msg: '{}', attch: '{}'".format(user_id, message, attachment))
    vk_api.send_message(user_id, message, attachment)
