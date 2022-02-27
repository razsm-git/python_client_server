"""  В каждом модуле выполнить настройку соответствующего логгера по следующему алгоритму:
Создание именованного логгера;
Сообщения лога должны иметь следующий формат: "<дата-время> <уровеньважности> <имямодуля> <сообщение>";
Журналирование должно производиться в лог-файл;
На стороне сервера необходимо настроить ежедневную ротацию лог-файлов.
"""
import logging
import logging.handlers
import os

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'client.log')

# создадим регистратор
client_log = logging.getLogger('app.client')
# установим уровень записи в лог
client_log.setLevel(logging.DEBUG)
# опции форматирования сообщения
formats = logging.Formatter("%(asctime)s %(levelname)10s %(module)-20s %(message)10s")
# создандим обработчик
handler = logging.FileHandler(path, encoding='utf-8')
# установим уровень логирования для обработчика
handler.setLevel(logging.DEBUG)
# применим форматирование сообщения к обработчику
handler.setFormatter(formats)
# добавим обработчик к регистратору
client_log.addHandler(handler)

# для теста
if __name__ == '__main__':
    client_log.critical("Critical! Panic on board")


