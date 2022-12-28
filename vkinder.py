from vk_bot import vkinder
from work_bd import get_connection, create_tables
from my_pass import pas
from my_token import TOKEN

conn = get_connection("VKinder", "postgres", pas)
create_tables(conn)



vkinder(217672166, TOKEN, conn)

