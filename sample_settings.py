from playhouse.postgres_ext import PostgresqlExtDatabase

token = ''
confirmation_token = ''

db = PostgresqlExtDatabase(
    'vk_bot',
    user='vk_bot',
    password='',
    host='localhost',
)

commands_black_list = ['hello', 'info']
