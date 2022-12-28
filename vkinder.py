from vk_bot import vkinder
from work_bd import get_connection
from my_pass import pas
from my_token import TOKEN

conn = get_connection("VKinder", "postgres", pas)

vkinder(217672166, TOKEN, conn)

