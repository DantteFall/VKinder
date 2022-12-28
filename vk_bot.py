
from work_api import long_poll_answer, write_msg, find_a_couple, goodbye, more


def hello(group_id, user_id):
    write_msg(user_id, 'Вас приветствует бот VKinder')
    write_msg(user_id, 'Если вы хотите воспользоваться ботом для поиска пары введите свой id или свое имя')
    long_poll_answer(group_id)


def search(user_id, group_id, token, conn):
    write_msg(user_id, 'Напишите команду "найти", что бы подобрать пару')
    search_accept = long_poll_answer(group_id)
    if search_accept['text'].lower() == 'найти':
        used = []
        ferst_result = find_a_couple(user_id, used, group_id, token, conn)
        if ferst_result != 0:
            answer = more(user_id, group_id)
            if answer == 'найти':
                while answer == 'найти':
                    search_sim = find_a_couple(user_id, used, group_id, token, conn)
                    if search_sim != 0:
                        answer = more(user_id, group_id)
                        if answer == 'стоп':
                            goodbye(user_id)
                        else:
                            while answer != 'найти' or 'стоп':
                                write_msg(user_id, 'Не верная команда попробуйте еще')
                                answer = long_poll_answer(group_id)['text']
                            if answer == 'найти':
                                while answer == 'найти':
                                    find_a_couple(user_id, used, group_id, token, conn)
                                    answer = more(user_id, group_id)
                            if answer == 'стоп':
                                goodbye(user_id)
                    else:
                        goodbye(user_id)
        else:
            goodbye(user_id)


def vkinder(group_id, token, conn):
    user_id = long_poll_answer(group_id)['from_id']
    hello(group_id, user_id)
    search(user_id, group_id, token, conn)