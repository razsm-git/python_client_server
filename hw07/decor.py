import logging
import logs.server_log_config
import logs.client_log_config
import sys
import inspect


if sys.argv[0].find('server.py') != -1:
    logger = logging.getLogger('app.server')
else:
    logger = logging.getLogger('app.client')


def log(some_func):
    # Функция декоратора
    def wrap(*args,**kwargs):
        var = some_func(*args,**kwargs)
        logger.debug(f"Вызвана функция {some_func.__name__} с аргументами args: {args}, kwargs: {kwargs} "
                     f"из модуля: {some_func.__module__}."
                     f"Вызов из функции: {inspect.stack()[1][3]}")
        return var
    return wrap
