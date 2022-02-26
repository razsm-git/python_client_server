import json
from socket import *
from common.variables import local_ip, local_port, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR
from common.utils import send_message, get_message
import sys
import time
import logging
import logs.client_log_config
from errors import *
from decor import log

client_log = logging.getLogger('app.client')
args = sys.argv

client_log.info("Клиент запущен")


@log
def create_presence(account_name='Guest'):
    # функция для создания запроса о присутсвии клиента в сети
    client_log.debug("Начат процесс созадния запроса")
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    client_log.debug("Запрос %s создан", out)
    return out


@log
def process_ans(message):
    # анализ ответа сервера
    client_log.debug("Запущен процесс анализа полученного сообщения %s", message)
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            client_log.debug("Код 200, всё хорошо")
            return '200 : OK'
        client_log.debug("Код 400, что-то пошло не так")
        return f'400 : {message[ERROR]}'
    else:
        client_log.error("В аналлизируемом сообщении ошибка значения!")
        raise ValueError


@log
def main():
    try:
        server_address = args[1]
        client_log.info("Ip адресс сервера %s", server_address)
        server_port = int(args[2])
        client_log.info("Ip порт сервера %d", server_port)
        if server_port < 1024 or server_port > 65535:
            client_log.critical("Порт %d выходит за рамки допустимого диапазона(от 1024 до 65535)!", server_port)
            raise ValueError
    except IndexError:
        server_address = local_ip
        server_port = local_port
        client_log.debug("Установлены адрес и порт сервера по умолчанию %s:%d", server_address,server_port)
    except ValueError:
        client_log.critical("Порт %d должен быть целым числом в рамках допустимого диапазона(от 1024 до 65535)!", server_port)
        sys.exit(1)


    # создааем сокет
    socket_init = socket(AF_INET, SOCK_STREAM)
    socket_init.connect((server_address, server_port))
    client_log.info("Создан клиентский сокет, успешно подключен к серверу %s:%d",server_address,server_port)
    message = create_presence()
    client_log.debug("Запрос приветствия создан")
    send_message(socket_init, message)
    client_log.debug("Отправляем сообщение на сервер %s:%d",server_address,server_port)
    try:
        client_log.debug("Попытка аналлиза ответного сообщения...")
        answer = process_ans(get_message(socket_init))
        client_log.debug("Сообщение проаналлизировано")
    except json.JSONDecodeError:
        client_log.error(f"Ошибка декодировки полученной JSON строки")
    except ConnectionRefusedError:
        client_log.critical(f"Не удалось подключиться к серверу {server_address}:{server_port}, т.к. конечный "
                            f"компьютер отверг запрос на подключение")
    except ReqFieldMissingError as missing_error:
        client_log.error(f'В ответе сервера отсутсвует необходимое поле {missing_error.missing_field}')


if __name__ == '__main__':
    main()
