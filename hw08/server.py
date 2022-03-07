from socket import *
from common.variables import local_ip, local_port, ACTION, ACCOUNT_NAME, \
    RESPONSE, max_connections, PRESENCE, TIME, USER, ERROR, RESPONDEFAULT_IP_ADDRESS, SENDER, MESSAGE, MESSAGE_TEXT, RESPONSE_200, RESPONSE_400, DESTINATION, SENDER, EXIT
from common.utils import get_message, send_message
import sys
import logging
import logs.server_log_config
from errors import *
from decor import log
import argparse
import select
import time

server_log = logging.getLogger('app.server')
args = sys.argv


@log
def arg_parser():
    # парсер аргументов переданных при запуске
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=local_port, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        listen_port = namespace.p
        server_log.debug("Номер порта %d передан в аргументах при запуске модуля", listen_port)
        server_log.debug("Установлен порт по умолчанию %d", listen_port)
        listen_address = namespace.a
        server_log.debug("Ip аддрес %s передан в аргументах при запуске модуля", listen_address)
        if listen_address == '':
            server_log.debug("По умолчанию будут прослушиваться все ip адреса на интерфейсах")
        else:
            server_log.debug(f"Будет прослушиваться ip адрес {listen_address}")
        if listen_port < 1024 or listen_port > 65535:
            server_log.critical("Порт %d выходит за рамки допустимого диапазона(от 1024 до 65535)! Завершение работы программы.", listen_port)
            sys.exit(1)
    except ValueError:
        server_log.critical("Порт %d должен быть целым числом в рамках допустимого диапазона(от 1024 до 65535)!", listen_port)
        sys.exit(1)
    return listen_address, listen_port


@log
def process_client_message(message, messages_list, client, clients, names):
    """ Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма."""
    server_log.debug(f"Начат процесс разбора сообщения от клиента {client}")
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
            server_log.debug("Сообщение имеет корректный формат")
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.

    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message and DESTINATION in message and SENDER in message:
        messages_list.append(message)
        return
    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return

    # Иначе отдаём Bad request
    else:
        send_message(client, RESPONSE_400)
        server_log.warning(f"Клиенту {client} отправлен ответ {RESPONSE_400}")
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает."""
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        server_log.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        server_log.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


@log
def main():
    server_log.info("Начало работы мудуля сервер")
    listen_address, listen_port = arg_parser()
    # запускаем сокет

    socket_init = socket(AF_INET, SOCK_STREAM)
    socket_init.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socket_init.bind((listen_address, listen_port))
    socket_init.listen(max_connections)
    socket_init.settimeout(0.5)
    print(f'Сервер запущен и слущает запросы на {listen_address}:{listen_port}')
    server_log.info("Сервер запущен и слущает запросы на %s:%d",listen_address,listen_port)
    # список клиентов и сообщений
    clients = []
    messages = []
    # словарь с именами пользователей и принадлежащим им сокетами
    names = dict()

    while True:
        # ждём покдключения до истечения тайм-аута
        try:
            client, client_address = socket_init.accept()
        except OSError as err:
            # возвращает None по таймауту
            # print(err.errno)
            pass
        else:
            server_log.debug("Установили соединение от клиента с адреса %s", client_address)
            clients.append(client)

        recive_msg_list = []
        sent_msg_list = []
        errors_msg_list = []
        # проверим на наличие ждущих клиентов
        try:
            if clients:
                recive_msg_list, sent_msg_list, errors_msg_list = select.select(clients, clients, [], 0)
        except OSError:
            pass
        # принимаем сообщения и если там есть сообщения, кладём в словарь, если ошибка, исключаем клиента.
        if recive_msg_list:
            for client_with_message in recive_msg_list:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message, clients, names)
                    server_log.debug(f"Получен ответ от клиента {client_with_message.getpeername()}")
                except:
                    server_log.info(f"Клиент {client_with_message.getpeername()} отключился от сервера")
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки, отправляем им сообщение.
        for i in messages:
            try:
                process_message(i,names,sent_msg_list)
            except Exception:
                server_log.info(f"Связь с клиентом {i[DESTINATION]} была потеряна")
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()