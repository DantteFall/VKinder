import requests
import time
from group_token import gr_token
from random import randrange
version = 5.131


def long_poll_access(group_id):
    '''Подключение к LongPollServer'''
    url = 'https://api.vk.com/method/groups.getLongPollServer'
    params = {
            'access_token': gr_token,
            'v': version,
            'group_id': group_id
        }
    get_access = requests.get(url, params=params)
    massage = get_access.json()
    massage_text = massage['response']
    time.sleep(0.4)
    return massage_text


def long_poll_answer(group_id):
    '''Получение ответа от пользователя'''
    data = long_poll_access(group_id)
    server = data['server']
    key = data['key']
    ts = data['ts']
    answer = requests.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=90')
    answer_aut = answer.json()
    message = answer_aut['updates'][0]['object']['message']
    return message


def write_msg(user_id, text):
    '''Отпарвляет сообщение'''
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'user_id': user_id,
        'access_token': gr_token,
        'v': version,
        'message': text,
        'random_id': randrange(10 ** 7)
    }
    requests.post(url, params=params)


def send_similar_user(self_user_id, text, photos):
    '''Отпарвляет сообщение'''
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'user_id': self_user_id,
        'access_token': gr_token,
        'v': version,
        'message': text,
        'attachment': photos,
        'random_id': randrange(10 ** 7)
    }
    requests.post(url, params=params)


def find_a_couple(new_user, used):
    '''Выдает подходящего пользователя'''
    similar_list = new_user.get_similar_list()
    if similar_list:
        for user in similar_list:
            if user not in used:
                photos = new_user.send_best_photos(user)
                text = f'https://vk.com/id{user}'
                self_id = new_user.id
                send_similar_user(self_id, text, photos)

    else:
        write_msg(new_user.id, 'У нас закончились подходяшие пары попробуйте позже')
        return 0


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute('CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, age INTEGER NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS city(name TEXT NOT NULL PRIMARY KEY);')
        cur.execute('CREATE TABLE IF NOT EXISTS sex(id SERIAL PRIMARY KEY, name TEXT NOT NULL);')
        cur.execute('CREATE TABLE IF NOT EXISTS relation(id SERIAL PRIMARY KEY, name TEXT NOT NULL);')

        cur.execute('CREATE TABLE IF NOT EXISTS photo(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id));')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user_relation(user_id INTEGER REFERENCES users(id), relation_id INTEGER REFERENCES relation(id),CONSTRAINT ur PRIMARY KEY (user_id, relation_id));')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user_sex(user_id INTEGER REFERENCES users(id), sex_id INTEGER REFERENCES sex(id), CONSTRAINT us PRIMARY KEY (user_id, sex_id));')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user_city(user_id INTEGER REFERENCES users(id), city TEXT REFERENCES city(name), CONSTRAINT uc PRIMARY KEY (user_id, city));')
        conn.commit()


def completion_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT id FROM relation;""")
        relation_id = cur.fetchall()
        relation_list_id = [item for sublist in relation_id for item in sublist]
        if 1 not in relation_list_id:
            cur.execute("""
                    INSERT INTO relation(id, name) VALUES
                    (1, 'не замужем/не женат'),
                    (2, 'есть друг/есть подруга'),
                    (3, 'помолвлен/помолвлена'),
                    (4, 'женат/замужем'),
                    (5, 'всё сложно'),
                    (6, 'в активном поиске'),
                    (7, 'влюблён/влюблена'),
                    (8, 'в гражданском браке');
                    """)

        cur.execute("""SELECT id FROM sex;""")
        sex_id = cur.fetchall()
        sex_list_id = [item for sublist in relation_id for item in sublist]
        if 1 not in sex_list_id:
            cur.execute("""
                        INSERT INTO sex(id, name) VALUES
                        (1, 'женский'),
                        (2, 'мужской');
                        """)
        conn.commit()