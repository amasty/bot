import vk
import random
import requests

import settings

session = vk.Session()
api = vk.API(session, v=5.0)


def get_random_wall_picture(group_id):
    """ Получение случайного фото со стены паблика

    Args:
        group_id: id палбика

    Returns:
        str: attachment
    """
    max_num = api.photos.get(owner_id=group_id, album_id='wall', count=0)['count']
    num = random.randint(1, max_num)

    photo = api.photos.get(owner_id=str(group_id), album_id='wall', count=1, offset=num)['items'][0]['id']

    return 'photo{}_{}'.format(group_id, photo)


def send_message(user_id, message, attachment=''):
    """ Отправить личное сообщение пользователю

    Args:
        user_id (str): id юзера вк
        message (str): текст сообщения
        attachment (str): вк аттач
    """
    api.messages.send(access_token=settings.token, user_id=str(user_id), message=message, attachment=attachment)


def upload_attach2message(photo):
    """ Загружает фото в аттач для использования в личных сообщения

    Args:
        photo (bytearray): фото для загрузки

    Returns:
        str: вк аттач для использования в личных сообщениях
    """
    data = api.photos.getMessagesUploadServer(access_token=settings.token)
    upload_url = data['upload_url']

    r = requests.post(upload_url, files={'photo': photo})
    if r.status_code == requests.codes.ok:
        data = r.json()

        photo = api.photos.saveMessagesPhoto(
            access_token=settings.token, server=data['server'], photo=data['photo'], hash=data['hash']
        )

        return 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])
