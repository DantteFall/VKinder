import requests
import time
import datetime
import psycopg2
from my_pass import pas

from bot_methods import write_msg, long_poll_answer
conn = psycopg2.connect(database="VKinder", user="postgres", password=pas)


class User:
    def __init__(self, id, group_id, TOKEN):
        self.acsess_token = TOKEN
        self.adress_api = 'https://api.vk.com/method/'
        self.get_method = 'users.get'
        self.post_method = 'users.post'
        self.get_profile_photo_method = 'photos.getProfile'
        self.group_id = group_id
        self.version = 5.131
        self.id = id
        self.info = self.get_info()
        self.city = self.get_city()
        self.post_data_base()

    def get_info(self):
        '''Возвращает основные параметры пользователя'''
        url = f'{self.adress_api}{self.get_method}'
        params = {
            'user_ids': self.id,
            'access_token': self.acsess_token,
            'v': self.version,
            'fields': 'bdate, age, sex, city, relation'
        }
        get_test = requests.get(url, params=params)
        info = get_test.json()
        parametrs = info['response']
        params_dict = {}
        for n in parametrs:
            for m, p in n.items():
                params_dict[m] = p
        return params_dict

    def get_age(self):
        '''Возвращает возраст'''
        info_dict = self.info
        if 'bdate' in info_dict.keys():
            bdate = info_dict['bdate']
            now = datetime.datetime.now()
            age = int(now.year) - int(bdate[-4:])
            return age
        else:
            return 0

    def get_sex(self):
        '''Возвращает пол'''
        info_dict = self.info
        sex = info_dict['sex']
        time.sleep(0.1)
        return sex

    def get_city(self):
        '''Возвращает город'''
        info_dict = self.info
        if 'city' in info_dict.keys():
            city = info_dict['city']
            time.sleep(0.1)
            return city['title'].lower()
        else:
            with conn.cursor() as cur:
                write_msg(self.id, 'Недостаточно данных: укажите город')
                time.sleep(1)
                city = long_poll_answer(self.group_id)['text']
                return city.lower()

    def get_relation(self):
        '''Возращает семейное положение'''
        info_dict = self.info
        relation = info_dict['relation']
        time.sleep(0.1)
        return relation

    def get_profile_photo(self):
        '''список фото с информацией о них'''
        params_photo = {
            'owner_id': self.id,
            'access_token': self.acsess_token,
            'v': self.version,
            'extended': 1
        }
        url = f'{self.adress_api}{self.get_profile_photo_method}'
        all_photo = requests.get(url, params=params_photo)
        photos = all_photo.json()
        time.sleep(0.1)
        return photos['response']

    def photo_list(self):
        '''список id фото'''
        list_photo = {}
        pars_photo = self.get_profile_photo()
        photo_info = pars_photo['items']
        for photo in photo_info:
            list_photo[photo['id']] = photo['likes']['count'] + photo['comments']['count']
        return list_photo

    def best_photo(self):
        '''Возвращает список из 3 лучших фото'''
        photo_list = self.photo_list()
        sorted_dict = {}
        sorted_keys = sorted(photo_list, key=photo_list.get)
        for photo in sorted_keys:
            sorted_dict[photo] = photo_list[photo]
        best = list(sorted_dict.keys())
        time.sleep(0.1)
        return best[-3:]

    def get_all_users(self):
        '''Возвращает список id пользователей в базе'''
        with conn.cursor() as cur:
            cur.execute("""SELECT id FROM users;""")
            users_id = cur.fetchall()
            list_id = [item for sublist in users_id for item in sublist]
            return list_id

    def get_all_city(self):
        '''Получение списка городов базе данных'''
        with conn.cursor() as cur:
            cur.execute("""SELECT name FROM city;""")
            get_city = cur.fetchall()
            city_list = [item for sublist in get_city for item in sublist]
            return city_list

    def add_user_id(self):
        '''Добаваляет id пользователя в базу если его еще там нет'''
        with conn.cursor() as cur:
            if self.id not in self.get_all_users():
                if self.get_age() != 0:
                    cur.execute(f"""INSERT INTO users(id, age) VALUES ({self.id}, {self.get_age()});""")
                else:
                    with conn.cursor() as cur:
                        write_msg(self.id, 'Недостаточно данных: укажите возраст')
                        age = long_poll_answer(self.group_id)
                        if type(age) is int:
                            cur.execute(f"""INSERT INTO users(id, age) VALUES ({self.id}, {age});""")
                        else:
                            while type(age) is not int:
                                write_msg(self.id, 'Укажите возраст ввиде числа')
                                age = long_poll_answer(self.group_id)
                            cur.execute(f"""INSERT INTO users(id, age) VALUES ({self.id}, {age});""")

    def add_user_city(self):
        '''Добаваляет город пользователя в базу если его еще там нет'''
        with conn.cursor() as cur:
            if self.city not in self.get_all_city():
                cur.execute(f"""INSERT INTO city(name) VALUES ('{self.city}');""")


    def connection_city(self):
        '''Присваивает пользователю город в связуюшей таблице'''
        with conn.cursor() as cur:
            cur.execute(f"""DELETE FROM user_city WHERE user_id={self.id};""")
            cur.execute(f"""INSERT INTO user_city VALUES ({self.id}, '{self.city}');""")

    def connection_relation(self):
        '''Присваивает пользователю семейное положение в связуюшей таблице'''
        with conn.cursor() as cur:
            if self.get_relation() != 0:
                cur.execute("""DELETE FROM user_relation WHERE user_id=%s;""", (self.id,))
                cur.execute(f"""INSERT INTO user_relation VALUES ({self.id}, {self.get_relation()});""")
            else:
                write_msg(self.id, 'Недостаточно данных: укажите семейное положение')
                time.sleep(1)
                relation = long_poll_answer(self.group_id)['text']
                cur.execute(f"""SELECT id FROM relation WHERE name LIKE '%{relation.lower()}%';""")
                user_relation = cur.fetchone()
                if user_relation is not None:
                    cur.execute("""DELETE FROM user_relation WHERE user_id=%s;""", (self.id,))
                    cur.execute(f"""INSERT INTO user_relation VALUES ({self.id}, {user_relation[0]});""")
                else:
                    while user_relation is None:
                        write_msg(self.id, 'Семейное положение указано не верно попробуйте ещё')
                        relation = long_poll_answer(self.group_id)['text']
                        cur.execute(f"""SELECT id FROM relation WHERE name LIKE '%{relation.lower()}%';""")
                        user_relation = cur.fetchone()
                    cur.execute(f"""INSERT INTO user_relation VALUES ({self.id}, {user_relation});""")

    def connection_sex(self):
        '''Присваивает пользователю пол в связуюшей таблице'''
        with conn.cursor() as cur:
            if self.get_sex() != 0:
                cur.execute("""DELETE FROM user_sex WHERE user_id=%s;""", (self.id,))
                cur.execute(f"""INSERT INTO user_sex VALUES ({self.id}, {self.get_sex()});""")
            else:
                write_msg(self.id, 'Недостаточно данных: укажите пол')
                time.sleep(1)
                sex = long_poll_answer(self.group_id)['text']
                male = ['м', 'муж', 'мужской']
                female = ['ж', 'жен', 'женский']
                if sex.lower() in male or female:
                    if sex.lower() in male:
                        user_sex = 2
                    else:
                        user_sex = 1
                    cur.execute("""DELETE FROM user_sex WHERE user_id=%s;""", (self.id,))
                    cur.execute(f"""INSERT INTO user_sex VALUES ({self.id}, {user_sex});""")
                else:
                    while sex.lower() not in male or female:
                        write_msg(self.id, 'Эта программа для бинарных личностей, указанный вами пол не привильный попробуйте ещё')
                        time.sleep(1)
                        sex = long_poll_answer(self.group_id)['text']
                    if sex.lower() in male:
                        user_sex = 2
                    else:
                        user_sex = 1
                    cur.execute("""DELETE FROM user_sex WHERE user_id=%s;""", (self.id,))
                    cur.execute(f"""INSERT INTO user_sex VALUES ({self.id}, {user_sex});""")

    def add_photos(self):
        '''Добавляет 3 лучших фото в базу'''
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM photo WHERE user_id=%s;""", (self.id,))
            photo_list = self.best_photo()
            for photo in photo_list:
                cur.execute(f"""INSERT INTO photo VALUES ({photo}, {self.id});""")

    def post_data_base(self):
        '''Отправляет данные в базу данных'''
        with conn.cursor() as cur:
            self.add_user_id()
            time.sleep(1)
            self.add_user_city()
            time.sleep(1)
            conn.commit()
            self.connection_city()
            time.sleep(1)
            self.connection_relation()
            time.sleep(1)
            self.connection_sex()
            time.sleep(1)
            self.add_photos()
            conn.commit()

    def get_male(self):
        '''Возвращает список пользователей мужского пола'''
        with conn.cursor() as cur:
            cur.execute("""SELECT user_id FROM user_sex WHERE sex_id=2;""")
            male = cur.fetchall()
            male_list = [item for sublist in male for item in sublist]
            return male_list

    def get_female(self):
        '''Возвращает список пользователей женского пола'''
        with conn.cursor() as cur:
            cur.execute("""SELECT user_id FROM user_sex WHERE sex_id=1;""")
            female = cur.fetchall()
            female_list = [item for sublist in female for item in sublist]
            return female_list

    def get_list_sex(self):
        '''Возвращает список пользователей противоположного пола'''
        if self.get_sex() == 1:
            return self.get_male()
        else:
            return self.get_female()

    def get_list_city(self):
        '''Возвращает список пользователей из того же города, что и пользователь'''
        with conn.cursor() as cur:
            cur.execute(f"""SELECT user_id FROM user_city WHERE city='{self.city}';""")
            list_users_from_city = cur.fetchall()
            users_from_city_list = [item for sublist in list_users_from_city for item in sublist]
            return users_from_city_list

    def get_similar_age(self):
        '''Возвращает список пользователей того же возраста, что и пользователь'''
        with conn.cursor() as cur:
            cur.execute(f"""SELECT id FROM users WHERE age={self.get_age()};""")
            users_with_similar_age = cur.fetchall()
            users_with_similar_age_list = [item for sublist in users_with_similar_age for item in sublist]
            return users_with_similar_age_list

    def get_similar_list(self):
        '''Находит подходящих людей по 3 признакам'''
        sex_list = self.get_list_sex()
        time.sleep(0.1)
        city_list = self.get_list_city()
        time.sleep(0.1)
        sge_list = self.get_similar_age()
        bufer_list = []
        similar_list = []
        for user_sex in sex_list:
            if user_sex in city_list:
                bufer_list.append(user_sex)
        for user_age in sge_list:
            if user_age in bufer_list:
                similar_list.append(user_age)
        return similar_list

    def get_best_photos(self, user_similar_id):
        with conn.cursor() as cur:
            cur.execute(f"""SELECT id FROM photo WHERE user_id={user_similar_id};""")
            photo_of_user = cur.fetchall()
            photo_of_user_list = [item for sublist in photo_of_user for item in sublist]
            return photo_of_user_list

    def send_best_photos(self, user_id):
        '''Создает список фото для отправки в сообщении'''
        list_of_photo_to_send = []
        photos = self.get_best_photos(user_id)
        for photo in photos:
            list_of_photo_to_send.append(f'photo{user_id}_{photo}')
        return list_of_photo_to_send



