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
path = os.path.join(path, 'server.log')

# создадим регистратор
server_log = logging.getLogger('app.server')
# установим уровень записи в лог
server_log.setLevel(logging.DEBUG)
# опции форматирования сообщения
formats = logging.Formatter("%(asctime)s %(levelname)10s %(module)-20s %(message)10s")
# создандим обработчик
handler = logging.handlers.TimedRotatingFileHandler(path,when='midnight',interval=1, backupCount=3,
                                                                encoding='utf-8')
# установим уровень логирования для обработчика
handler.setLevel(logging.DEBUG)
# применим форматирование сообщения к обработчику
handler.setFormatter(formats)
# добавим обработчик к регистратору
server_log.addHandler(handler)

# для теста
if __name__ == '__main__':
    server_log.critical("Critical! Panic on board")


