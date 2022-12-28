from work_api import long_poll_answer, write_msg, find_a_couple, goodbye, more, send_eror
from work_bd import add_user_id, create_tables, get_search_list


def hello(group_id, user_id):
    write_msg(user_id, 'Вас приветствует бот VKinder')
    write_msg(user_id, 'Если вы хотите воспользоваться ботом для поиска пары введите свой id или свое имя')
    long_poll_answer(group_id)


def search(user_id, group_id, token, conn):
    write_msg(user_id, 'Напишите команду "найти", что бы подобрать пару')
    search_accept = long_poll_answer(group_id)
    if search_accept != 'Ошибка сервера попробуйте позже':
        if search_accept['text'].lower() == 'найти':
            used = get_search_list(user_id, conn)
            ferst_result = find_a_couple(user_id, used, group_id, token, conn)
            if ferst_result != 0:
                answer = more(user_id, group_id)
                if answer != 'Ошибка сервера попробуйте позже':
                    if answer == 'найти':
                        while answer == 'найти':
                            search_sim = find_a_couple(user_id, used, group_id, token, conn)
                            if search_sim != 0:
                                answer = more(user_id, group_id)
                                if answer != 'Ошибка сервера попробуйте позже':
                                    if answer == 'стоп':
                                        goodbye(user_id)
                                    else:
                                        while answer != 'найти' or 'стоп':
                                            write_msg(user_id, 'Не верная команда попробуйте еще')
                                            answer = long_poll_answer(group_id)['text']
                                            if answer != 'Ошибка сервера попробуйте позже':
                                                if answer == 'найти':
                                                    while answer == 'найти':
                                                        find_a_couple(user_id, used, group_id, token, conn)
                                                        answer = more(user_id, group_id)
                                                elif answer == 'стоп':
                                                    goodbye(user_id)
                                            else:
                                                send_eror(user_id)
                                else:
                                    send_eror(user_id)
                            else:
                                goodbye(user_id)
                else:
                    send_eror(user_id)
            else:
                goodbye(user_id)
    else:
        send_eror(user_id)


def vkinder(group_id, token, conn):
    create_tables(conn)
    user_id = long_poll_answer(group_id)['from_id']
    hello(group_id, user_id)
    add_user_id(user_id, conn)
    search(user_id, group_id, token, conn)