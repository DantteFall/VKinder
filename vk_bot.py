import psycopg2
from my_token import TOKEN
from my_pass import pas
from class_user import User
from bot_methods import long_poll_answer, write_msg, find_a_couple, create_tables, completion_tables

conn = psycopg2.connect(database="VKinder", user="postgres", password=pas)

create_tables(conn)

completion_tables(conn)

group_id = 217672166

user_id = long_poll_answer(group_id)['from_id']
write_msg(user_id, 'Вас приветствует бот VKinder')
write_msg(user_id, 'Если вы хотите воспользоваться ботом для поиска пары введите свой id или свое имя')
response = long_poll_answer(group_id)
new_user = User(user_id, group_id, TOKEN)
write_msg(user_id, 'Напишите команду "найти", что бы подобрать пару')
search = long_poll_answer(group_id)
if search['text'].lower() == 'найти':
    used = []
    ferst_result = find_a_couple(new_user, used)
    if ferst_result != 0:
        write_msg(user_id, 'Если хотите получить другой вариант напишите еще, если хотите завершить поиск напишите стоп')
        answer = long_poll_answer(group_id)['text']
        if answer == 'найти':
            while answer == 'найти':
                search_sim = find_a_couple(new_user, used)
                if search_sim != 0:
                    write_msg(user_id,'Если хотите получить другой вариант напишите еще, если хотите завершить поиск напишите стоп')
                    answer = long_poll_answer(group_id)['text']
                    if answer == 'стоп':
                        write_msg(user_id, 'До новых втреч')
                    else:
                        while answer != 'найти' or 'стоп':
                            write_msg(user_id, 'Не верная команда попробуйте еще')
                            answer = long_poll_answer(group_id)['text']
                        if answer == 'найти':
                            while answer == 'найти':
                                find_a_couple(new_user, used)
                                write_msg(user_id, 'Если хотите получить другой вариант напишите еще, если хотите завершить поиск напишите стоп')
                                answer = long_poll_answer(group_id)['text']
                        if answer == 'стоп':
                            write_msg(user_id, 'До новых втреч')
                else:
                    write_msg(user_id, 'До новых втреч')
    else:
        write_msg(user_id, 'До новых втреч')