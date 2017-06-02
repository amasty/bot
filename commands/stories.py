import random

from api import vk_api
from models.await import Await
from models.stories import Stories
from models.stories import StoriesText
from commands import _command_system


def histories(data, await=None):
    if not await:
        return _create_await(data)

    return _process_await(data, await)


def _create_await(data):
    stories = [
        x for x in Stories.select(Stories, StoriesText).distinct(StoriesText.story)
            .join(StoriesText, on=Stories.id == StoriesText.story)
            .where(Stories.state == 0)
            .order_by(StoriesText.story.desc())
        if x.storiestext.user_id != data['user_id']
    ]

    if not stories:
        user_stories = Stories.select(Stories, StoriesText).distinct(StoriesText.story) \
            .join(StoriesText, on=Stories.id == StoriesText.story) \
            .where(Stories.state == 0, StoriesText.user_id == data['user_id']) \
            .order_by(StoriesText.story.desc()) \
            .count()

        if user_stories > 7:
            message = "Сейчас нет историй, который ты можешь продолжить, " \
                      "подожди пока кто-нибудь продолжит историю после тебя"
        else:
            Await.create(user_id=data['user_id'], command='histories', args={'story_id': None})
            message = "Сейчас нет истории для продолжения, давай начнем новую. Пришли мне начало истории."

    else:
        story = random.choice(stories)
        story_texts = [x for x in StoriesText.select().where(StoriesText.story == story.id)]
        last_part = story_texts[-1]

        Await.create(user_id=data['user_id'], command='histories', args={'story_id': str(story.id)})
        message = "Вот тебе последняя часть из истории.\n\n{}\n\nПродолжи ее".format(last_part.text)

    return message, None


def _process_await(data, await):
    if not _check_story_text(data['body']):
        await.attempts += 1
        if await.attempts > 2:
            Await.delete().where(Await.id == await.id).execute()

            return None, None
        else:
            await.save()
            message = "Это не очень похоже на часть истории. Пришли мне предложение."

            return message, None

    if await.args['story_id'] is None:
        story = Stories.create(state=0)
        StoriesText.create(story_id=story.id, user_id=data['user_id'], text=data['body'])
        Await.delete().where(Await.id == await.id).execute()

        message = "Спасибо за начало истории! Скоро я пришлю тебе всю историю."

    else:
        StoriesText.create(story_id=await.args['story_id'], user_id=data['user_id'], text=data['body'])
        Await.delete().where(Await.id == await.id).execute()

        story_texts = [x for x in StoriesText.select().where(StoriesText.story == await.args['story_id'])]

        if len(story_texts) < 5:
            message = "Спасибо за продолжение истории! Скоро я пришлю тебе всю историю."
        else:
            story = Stories.get(id=await.args['story_id'])
            story.state = 1
            story.save()

            full_text = []
            users = set()
            for st in story_texts:
                if st.user_id != data['user_id']:
                    users.add(st.user_id)
                full_text.append(st.text)

            full_text = ' '.join(full_text)
            message = "Общая история закончена, почитай ее\n\n{}".format(full_text)

            for user in users:
                vk_api.send_message(user, message)

    return message, None


def _check_story_text(text):
    while True:
        if '  ' in text:
            text = text.replace('  ', ' ')
        else:
            break

    if len(text) < 20:
        return False

    words = text.split(' ')
    uniques = set(words)
    if len(uniques) / len(words) < 0.4:
        return False

    return True


histories_command = _command_system.Command()
histories_command.name = 'histories'
histories_command.keys = ['история', 'играть в историю', 'писать историю']
histories_command.description = 'игра в составь историю'
histories_command.await = 'histories'
histories_command.process = histories
