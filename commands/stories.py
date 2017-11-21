import random

import utils

from api import vk_api
from models.userexpectation import UserExpectation
from models.stories import Stories
from models.stories import StoriesText
from commands._system import Command
from commands._system import register


@register
class Histories(Command):
    name = 'histories'
    keys = ['история', 'играть в историю', 'писать историю']
    description = 'игра в составь историю'

    def _do(self):
        """ Игра для пользователей составь историю.
        Пользователь дополняет общую историю. В конце должна получится одна большая история.


        Returns:
            str: сообщение для пользователя

        """
        if not self.user_expectations:
            return self._create_await()

        return self._process_await()

    def _create_await(self):
        """ От пользователя еще не ожидается часть истории.
        Создаем ожидание и даем возможность пользователю либо
        дополнить историю, либо начать новую

        Returns:
            str: сообщение для пользователя

        """
        stories = [
            x for x in Stories.select(Stories, StoriesText).distinct(StoriesText.story)
            .join(StoriesText, on=Stories.id == StoriesText.story)
            .where(Stories.state == 0)
            .order_by(StoriesText.story.desc())
            if x.storiestext.user_id != self.data['user_id']
        ]

        if not stories:
            user_stories = Stories.select(Stories, StoriesText).distinct(StoriesText.story) \
                .join(StoriesText, on=Stories.id == StoriesText.story) \
                .where(Stories.state == 0, StoriesText.user_id == self.data['user_id']) \
                .order_by(StoriesText.story.desc()) \
                .count()
            if user_stories > 7:
                return utils.show_message(
                    "Сейчас нет историй, который ты можешь продолжить, "
                    "подожди немного, пока кто-нибудь не начнет новую"
                )
            else:
                UserExpectation.create(user_id=self.data['user_id'], command=self.name, args={'story_id': None})
                return utils.show_message(
                    "Сейчас нет истории для продолжения, давай начнем новую. Пришли мне начало истории."
                )
        else:
            story = random.choice(stories)
            story_texts = [x for x in StoriesText.select().where(StoriesText.story == story.id)]
            last_part = story_texts[-1]

            UserExpectation.create(user_id=self.data['user_id'], command=self.name, args={'story_id': str(story.id)})
            return utils.show_message(
                "Вот тебе последняя часть из истории.\n\n{}\n\nПродолжи ее".format(last_part.text)
            )

    def _process_await(self):
        """ Мы уже ждем от пользователя часть истории. Дополняем общую историю
        частью от пользователя

        Returns:
            str: сообщение для пользователя

        """
        if not self._validate_story_text(self.data['body']):
            self.user_expectations.attempts += 1
            # Пользователь слишком много присылал сообщений не похожих на историю.
            # Удаляем ожидание от него продолжения истории
            if self.user_expectations.attempts > 3:
                UserExpectation.delete().where(UserExpectation.id == self.user_expectations.id).execute()
                return utils.show_message(
                    "От тебя пришло много сообщений не похожих на продолжение истории, давай я "
                    "больше не буду ждать продолжения."
                )
            else:
                self.user_expectations.save()
                return utils.show_message("Это не очень похоже на часть истории. Пришли мне предложение.")

        if self.user_expectations.args['story_id'] is None:
            story = Stories.create(state=0)
            StoriesText.create(story_id=story.id, user_id=self.data['user_id'], text=self.data['body'])
            UserExpectation.delete().where(UserExpectation.id == self.user_expectations.id).execute()
            return utils.show_message("Спасибо за начало истории! Скоро я пришлю тебе всю историю.")
        else:
            StoriesText.create(
                story_id=self.user_expectations.args['story_id'], user_id=self.data['user_id'], text=self.data['body']
            )
            UserExpectation.delete().where(UserExpectation.id == self.user_expectations.id).execute()

            story_texts = [x for x in StoriesText.select().where(StoriesText.story == self.user_expectations.args['story_id'])]

            if len(story_texts) < 5:
                return utils.show_message("Спасибо за продолжение истории! Скоро я пришлю тебе всю историю.")
            else:
                story = Stories.get(id=self.user_expectations.args['story_id'])
                story.state = 1
                story.save()

                full_text = []
                users = set()
                for st in story_texts:
                    if st.user_id != self.data['user_id']:
                        users.add(st.user_id)
                    full_text.append(st.text)
                full_text = ' '.join(full_text)
                for user in users:
                    vk_api.send_message(user, "Общая история закончена, почитай ее\n\n{}".format(full_text))

    @staticmethod
    def _validate_story_text(text):
        """ Проверяем часть истории на похожесть на текст

        Args:
            text (str): часть истории от пользователя

        Returns:
            bool: True если текст похож на часть истории

        """
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
