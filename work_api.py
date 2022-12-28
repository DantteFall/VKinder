import requests
import time
from group_token import gr_token
from random import randrange
import datetime
from work_bd import get_all_users, add_user_search


def get_info(id, token):
    '''Возвращает основные параметры пользователя'''
    url = 'https://api.vk.com/method/users.get'
    params = {
        'user_ids': id,
        'access_token': token,
        'v': 5.131,
        'fields': 'bdate, age, sex, city, relation'
    }
    get_test = requests.get(url, params=params)
    info = get_test.json()
    if 'response' in info.keys():
        parametrs = info['response']
        params_dict = {}
        for n in parametrs:
            for m, p in n.items():
                params_dict[m] = p
        return params_dict
    else:
        write_msg(id, 'Ошибка сервера попробуйте позже')


def get_city(id, group_id, token):
    '''Возвращает город'''
    info_dict = get_info(id, token)
    if 'city' in info_dict.keys():
        city = info_dict['city']
        time.sleep(0.1)
        return city['title'].lower()
    else:
        write_msg(id, 'Недостаточно данных: укажите город')
        time.sleep(1)
        city = long_poll_answer(group_id)
        if 'text' in city.keys():
            return city['text'].lower()
        else:
            write_msg(id, 'Ошибка сервера попробуйте позже')


def get_age(id, group_id, token):
    '''Возвращает возраст'''
    info_dict = get_info(id, token)
    if 'bdate' in info_dict.keys():
        bdate = info_dict['bdate']
        now = datetime.datetime.now()
        age = int(now.year) - int(bdate[-4:])
        return age
    else:
        write_msg(id, 'Недостаточно данных: укажите возраст')
        age = long_poll_answer(group_id)
        if type(age) is int:
            return age
        else:
            while type(age) is not int:
                write_msg(id, 'Укажите возраст ввиде числа')
                age = long_poll_answer(group_id)
            return age


def get_sex(id, group_id, token):
    '''Возвращает пол'''
    info_dict = get_info(id, token)
    sex = info_dict['sex']
    time.sleep(0.1)
    if sex != 0:
        return sex
    else:
        write_msg(id, 'Недостаточно данных: укажите пол')
        time.sleep(1)
        sex = long_poll_answer(group_id)['text']
        male = ['м', 'муж', 'мужской']
        female = ['ж', 'жен', 'женский']
        if sex.lower() == male or female:
            if sex.lower() in male:
                return 2
            else:
                return 1
        else:
            while sex.lower() not in male or female:
                write_msg(id, 'Эта программа для бинарных личностей, указанный вами пол не привильный попробуйте ещё')
                time.sleep(1)
                sex = long_poll_answer(group_id)['text']
            if sex.lower() in male:
                return 2
            else:
                return 1


def get_relation(id, group_id, token):
    '''Возращает семейное положение'''
    info_dict = get_info(id, token)
    relation = info_dict['relation']
    if relation != 0:
        return relation
    else:
        write_msg(id, 'Недостаточно данных: укажите семейное положение')
        time.sleep(1)
        response = long_poll_answer(group_id)['text']
        relation_dict = {
            1: 'не замужем/не женат',
            2: 'есть друг/есть подруга',
            3: 'помолвлен/помолвлена',
            4: 'женат/замужем',
            5: 'всё сложно',
            6: 'в активном поиске',
            7: 'влюблён/влюблена',
            8: 'в гражданском браке'
        }
        if 'text' in response.keys():
            relation = response['text'].lower()
            for key, value in relation_dict:
                if relation == value:
                    return key
            while relation not in relation_dict.values():
                write_msg(id, 'Семейное положение указано не верно, попробуйте снова')
                time.sleep(1)
                response = long_poll_answer(group_id)['text']
                relation = response['text'].lower()
                for key, value in relation_dict:
                    if relation == value:
                        return key
        else:
            write_msg(id, 'Ошибка сервера попробуйте позже')


def get_profile_photo(id, token):
    '''список фото с информацией о них'''
    url = f'https://api.vk.com/method/photos.getProfile'
    params_photo = {
        'owner_id': id,
        'access_token': token,
        'v': 5.131,
        'extended': 1
    }
    all_photo = requests.get(url, params=params_photo)
    photos = all_photo.json()
    time.sleep(0.1)
    if 'response' in photos.keys():
        return photos['response']
    else:
        return {'eror': 'Ошибка сервера попробуйте позже'}


def photo_list(id, token):
    '''список id фото'''
    list_photo = {}
    pars_photo = get_profile_photo(id, token)
    if 'items' in pars_photo.keys():
        photo_info = pars_photo['items']
        for photo in photo_info:
            list_photo[photo['id']] = photo['likes']['count'] + photo['comments']['count']
        return list_photo
    else:
        return pars_photo['eror']


def best_photo(id, token):
    '''Возвращает список из 3 лучших фото'''
    photo = photo_list(id, token)
    sorted_dict = {}
    sorted_keys = sorted(photo, key=photo.get)
    for photo in sorted_keys:
        sorted_dict[photo] = photo_list[photo]
    best = list(sorted_dict.keys())
    time.sleep(0.1)
    return best[-3:]


def send_best_photos(id, token):
    '''Создает список фото для отправки в сообщении'''
    list_of_photo_to_send = []
    photos = best_photo(id, token)
    for photo in photos:
        list_of_photo_to_send.append(f'photo{id}_{photo}')
    return list_of_photo_to_send


def long_poll_access(group_id):
    '''Подключение к LongPollServer'''
    url = 'https://api.vk.com/method/groups.getLongPollServer'
    params = {
            'access_token': gr_token,
            'v': 5.131,
            'group_id': group_id
        }
    get_access = requests.get(url, params=params)
    massage = get_access.json()
    if 'response' in massage.keys():
        massage_text = massage['response']
        time.sleep(0.4)
        return massage_text
    else:
        return {'eror': 'Ошибка сервера попробуйте позже'}


def long_poll_answer(group_id):
    '''Получение ответа от пользователя'''
    data = long_poll_access(group_id)
    if 'server' in data.keys():
        server = data['server']
        key = data['key']
        ts = data['ts']
        answer = requests.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=90')
        answer_aut = answer.json()
        if 'updates' in answer_aut.keys():
            if 'message' in answer_aut['updates'][0]['object'].keys():
                message = answer_aut['updates'][0]['object']['message']
                return message
            else:
                return 'Ошибка сервера попробуйте позже'
        else:
            return 'Ошибка сервера попробуйте позже'
    else:
        return data['eror']


def write_msg(user_id, text):
    '''Отпарвляет сообщение'''
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'user_id': user_id,
        'access_token': gr_token,
        'v': 5.131,
        'message': text,
        'random_id': randrange(10 ** 7)
    }
    requests.post(url, params=params)


def get_male(group_id, token, conn):
    '''Возвращает список пользователей мужского пола'''
    male_list = []
    all_users = get_all_users(conn)
    for user in all_users:
        user_sex = get_sex(user, group_id, token)
        if user_sex == 2:
            male_list.append(user)

    return male_list


def get_female(group_id, token, conn):
    '''Возвращает список пользователей женского пола'''
    female_list = []
    all_users = get_all_users(conn)
    for user in all_users:
        user_sex = get_sex(user, group_id, token)
        if user_sex == 1:
            female_list.append(user)
    return female_list


def get_list_sex(id, group_id, token, conn):
    '''Возвращает список пользователей противоположного пола'''
    sex = get_sex(id, group_id, token)
    if sex == 1:
        return get_male(group_id, token, conn)
    else:
        return get_female(group_id, token, conn)


def get_list_city(id, group_id, token, conn):
    '''Возвращает список пользователей из того же города, что и пользователь'''
    cimilar_city = []
    self_city = get_city(id, group_id, token)
    all_users = get_all_users(conn)
    for user in all_users:
        user_sity = get_city(user, group_id, token)
        if user_sity == self_city:
            cimilar_city.append(user)
    return cimilar_city


def get_similar_age(id, group_id, token, conn):
    '''Возвращает список пользователей того же возраста, что и пользователь'''
    cimilar_age = []
    self_age = get_age(id, group_id, token)
    all_users = get_all_users(conn)
    for user in all_users:
        user_age = get_city(user, group_id, token)
        if user_age == self_age:
            cimilar_age.append(user)
    return cimilar_age


def get_similar_list(id, group_id, token, conn):
    '''Находит подходящих людей по 3 признакам'''
    sex_list = get_list_sex(id, group_id, token, conn)
    time.sleep(0.1)
    city_list = get_list_city(id, group_id, token, conn)
    time.sleep(0.1)
    sge_list = get_similar_age(id, group_id, token, conn)
    bufer_list = []
    similar_list = []
    for user_sex in sex_list:
        if user_sex in city_list:
            bufer_list.append(user_sex)
    for user_age in sge_list:
        if user_age in bufer_list:
            similar_list.append(user_age)
    return similar_list


def send_similar_user(self_user_id, text, photos):
    '''Отпарвляет сообщение с фото'''
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'user_id': self_user_id,
        'access_token': gr_token,
        'v': 5.131,
        'message': text,
        'attachment': photos,
        'random_id': randrange(10 ** 7)
    }
    requests.post(url, params=params)


def find_a_couple(id, used, group_id, token, conn):
    '''Выдает подходящего пользователя'''
    similar_list = get_similar_list(id, group_id, token, conn)
    if similar_list:
        for user in similar_list:
            if user not in used:
                photos = send_best_photos(user)
                text = f'https://vk.com/id{user}'
                self_id = id
                if photos != 'Ошибка сервера попробуйте позже':
                    send_similar_user(self_id, text, photos)
                    add_user_search(id, user, conn)
                else:
                    write_msg(id, 'Ошибка сервера попробуйте позже')

    else:
        write_msg(id, 'У нас закончились подходяшие пары попробуйте позже')
        return 0


def more(user_id, group_id):
    write_msg(user_id, 'Если хотите получить другой вариант напишите еще, если хотите завершить поиск напишите стоп')
    answer = long_poll_answer(group_id)['text']
    if answer != 'Ошибка сервера попробуйте позже':
        return answer
    else:
        return 'Ошибка сервера попробуйте позже'


def goodbye(user_id):
    write_msg(user_id, 'До новых втреч')
    return


def send_eror(user_id):
    write_msg(user_id, 'Ошибка сервера попробуйте позже')
