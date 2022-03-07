import json
from socket import *
from common.variables import local_ip, local_port, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT,SENDER, EXIT, DESTINATION
from common.utils import send_message, get_message
import sys
import time
import logging
import logs.client_log_config
from errors import *
from decor import log
import argparse
import threading


client_log = logging.getLogger('app.client')
args = sys.argv

client_log.info("Клиент запущен")


@log
def create_exit_message(acc_name):
    # сообщение словарь для выхода из программы
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: acc_name
    }


@log
def arg_parser():
    # парсер аргументов переданных при запуске
    parser = argparse.ArgumentParser()
    parser.add_argument('address', default=local_ip, nargs='?')
    parser.add_argument('port', default=local_port, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    client_name = namespace.name
    server_port = namespace.port
    client_log.debug("Номер порта %d передан в аргументах при запуске модуля", server_port)
    client_log.debug("Установлен порт %d", server_port)
    server_address = namespace.address
    client_log.debug("Ip аддрес сервера %s передан в аргументах при запуске модуля", server_address)
    if server_port < 1024 or server_port > 65535:
        client_log.critical("Порт %d выходит за рамки допустимого диапазона(от 1024 до 65535)! Завершение работы программы.", server_port)
        sys.exit(1)
    return server_address, server_port, client_name


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
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    client_log.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        client_log.info(f'Отправлено сообщение для пользователя {to_user}')
    except Exception as ex:
        print(ex)
        client_log.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def message_from_server(sock, my_username):
    while True:
        try:
            # обработчик сообщений других пользователей, поступающих с сервера
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                client_log.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[MESSAGE_TEXT]}')
            else:
                client_log.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            client_log.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            client_log.critical(f'Потеряно соединение с сервером.')
            break


@log
def main():
    server_address, server_port, client_name = arg_parser()
    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    client_log.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя клиента: {client_name}')
    # создааем сокет
    socket_init = socket(AF_INET, SOCK_STREAM)
    socket_init.connect((server_address, server_port))
    client_log.info("Создан клиентский сокет, успешно подключен к серверу %s:%d",server_address,server_port)
    send_message(socket_init, create_presence(client_name))
    client_log.debug("Запрос приветствия создан")
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
        # запускаем клиентский процесс приёма сообщений
        receiver = threading.Thread(target=message_from_server, args=(socket_init,client_name))
        receiver.daemon = True
        receiver.start()

        # теперь запустим взаимодейтсвие с пользователем и отправку сообщений
        interface = threading.Thread(target=user_interactive, args=(socket_init, client_name))
        interface.daemon = True
        interface.start()
        client_log.debug("Все процеесы успешно запущены!")

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
                continue
            break


@log
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help(client_name=username)
    while True:
        command = input('Введите команду: ')
        if command == 'm':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            client_log.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


def print_help(client_name):
    """Функция выводящяя справку по использованию"""
    print(f'Привет {client_name}!')
    print('Поддерживаемые команды:')
    print('m - отправить сообщение.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


if __name__ == '__main__':
    main()
