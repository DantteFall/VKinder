import psycopg2


def get_connection(database, user, password):
    '''Создание соединения с базой данных'''
    conn = psycopg2.connect(database=database, user=user, password=password)
    return conn


def create_tables(conn):
    '''Создание таблиц'''
    with conn.cursor() as cur:
        cur.execute('CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY);')
        cur.execute('CREATE TABLE IF NOT EXISTS user_seaarch(user_id INTEGER REFERENCES users(id), search INTEGER REFERENCES users(id), CONSTRAINT us PRIMARY KEY (user_id, search));')
        conn.commit()


def get_all_users(conn):
    '''Возвращает список id пользователей в базе'''
    with conn.cursor() as cur:
        cur.execute("""SELECT id FROM users;""")
        users_id = cur.fetchall()
        list_id = [item for sublist in users_id for item in sublist]
        return list_id


def add_user_id(id, conn):
    '''Добаваляет id пользователя в базу если его еще там нет'''
    with conn.cursor() as cur:
        if id not in get_all_users(conn):
            cur.execute(f"""INSERT INTO users(id) VALUES ({id});""")


def add_user_search(id, search_id, conn):
    '''Добаваляет id пользователя в базу если его еще там нет'''
    with conn.cursor() as cur:
        if id not in get_all_users(conn):
            cur.execute("""DELETE FROM user_search WHERE id=%s, search_id=%s;""", (id, search_id))
            cur.execute(f"""INSERT INTO user_search VALUES ({id}, {search_id});""")


def get_search_list(id, conn):
    '''Выдает список уже показанных пользователю анкет'''
    with conn.cursor() as cur:
        cur.execute("""SELECT search_id FROM user_search WHERE id=%s;""", id)
        users_id = cur.fetchall()
        list_id = [item for sublist in users_id for item in sublist]
        return list_id
