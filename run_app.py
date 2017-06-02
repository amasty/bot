import logging

import settings

from flask import Flask
from flask import json
from flask import request

from handlers import message


logging.basicConfig(level=logging.INFO, format='(%(levelname)s) %(asctime)s: %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello from Flask!'


@app.route('/', methods=['POST'])
def vk_callback():
    data = json.loads(request.data)

    if 'type' not in data.keys():
        return 'who are you?'

    if data['type'] == 'confirmation':
        return settings.confirmation_token

    elif data['type'] == 'message_new':
        message.create_answer(data['object'])

        return 'ok'


@app.before_request
def _db_connect():
    settings.db.connect()


@app.teardown_request
def _db_close(exc):
    if not settings.db.is_closed():
        settings.db.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
