import json
from socket import *
from common.variables import local_ip, local_port, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT,SENDER
from common.utils import send_message, get_message
import sys
import time
import logging
import logs.client_log_config
from errors import *
from decor import log
import argparse

client_log = logging.getLogger('app.client')
args = sys.argv

client_log.info("Клиент запущен")


@log
def arg_parser():
    # парсер аргументов переданных при запуске
    parser = argparse.ArgumentParser()
    parser.add_argument('address', default=local_ip, nargs='?')
    parser.add_argument('port', default=local_port, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    client_mode = namespace.mode
    server_port = namespace.port
    client_log.debug("Номер порта %d передан в аргументах при запуске модуля", server_port)
    client_log.debug("Установлен порт %d", server_port)
    server_address = namespace.address
    client_log.debug("Ip аддрес сервера %s передан в аргументах при запуске модуля", server_address)
    if server_port < 1024 or server_port > 65535:
        client_log.critical("Порт %d выходит за рамки допустимого диапазона(от 1024 до 65535)! Завершение работы программы.", server_port)
        sys.exit(1)
    if client_mode not in ('listen', 'send'):
        client_log.critical(f'Указан недопустимый режим работы {client_mode}, '
                    f'допустимые режимы: listen , send')
        sys.exit(1)
    return server_address, server_port, client_mode


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
        elif message[RESPONSE] == 400:
            client_log.debug("Код 400, что-то пошло не так")
            return f'400 : {message[ERROR]}'
    else:
        client_log.error("В аналлизируемом сообщении ошибка значения!")
        raise ReqFieldMissingError(RESPONSE)


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """
    message = input('Введите сообщение для отправки или "exit" для завершения работы: ')
    if message == 'exit':
        sock.close()
        client_log.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    client_log.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def message_from_server(message):
    # обработчик сообщений других пользователей, поступающих с сервера
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TEXT]}')
        client_log.info(f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TEXT]}')
    else:
        client_log.error(f'Получено некорректное сообщение от сервера: {message}')

@log
def main():
    server_address, server_port, client_mode = arg_parser()
    client_log.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_mode}')
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
        sys.exit(1)
    except ConnectionRefusedError:
        client_log.critical(f"Не удалось подключиться к серверу {server_address}:{server_port}, т.к. конечный "
                            f"компьютер отверг запрос на подключение")
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        client_log.error(f'В ответе сервера отсутсвует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ServerError as error:
        client_log.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно,
        # начинаем обмен с ним, согласно требуемому режиму.
        # основной цикл прогрммы:
        while True:
            # режим работы отправка сообщений
            if client_mode == 'send':
                print('Режим работы - отправка сообщений.')
                client_log.debug(f'Режим работы - {client_mode}')
                try:
                    send_message(socket_init,create_message(socket_init))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_log.error(f'Соединение с сервером {server_address}:{server_port} было разорвано.')
                    sys.exit(1)
            # режим работы прием сообщений
            else:
                print('Режим работы - приём сообщений.')
                client_log.debug(f'Режим работы - {client_mode}')
                try:
                    message_from_server(get_message(socket_init))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_log.error(f'Соединение с сервером {server_address}:{server_port} было разорвано.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
