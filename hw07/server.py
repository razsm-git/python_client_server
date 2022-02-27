from socket import *
from common.variables import local_ip, local_port, ACTION, ACCOUNT_NAME, \
    RESPONSE, max_connections, PRESENCE, TIME, USER, ERROR, RESPONDEFAULT_IP_ADDRESS, SENDER, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message
import sys
import json
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
def process_client_message(message, messages_list, client):
    """ Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма."""
    server_log.debug(f"Начат процесс разбора сообщения от клиента {client}")
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        server_log.debug("Сообщение имеет корректный формат")
        send_message(client, {RESPONSE: 200})
        return
    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
        # Иначе отдаём Bad request
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        server_log.warning(f"Клиенту {client} отправлен ответ ERROR: 'Bad Request'")
        return


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
    clients = []
    messages = []
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
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                    server_log.debug(f"Получен ответ от клиента {client_with_message.getpeername()}")
                except:
                    server_log.info(f"Клиент {client_with_message.getpeername()} отключился от сервера")
                    clients.remove(client_with_message)
        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and sent_msg_list:
            message_for_sent = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1],
            }
            del messages[0]
            for waiting_client in sent_msg_list:
                try:
                    send_message(waiting_client, message_for_sent)
                    server_log.debug(f"Отправлен ответ клиенту {waiting_client.getpeername()}")
                except:
                    server_log.info(f"Клиент {waiting_client.getpeername()} отключился от сервера")
                    waiting_client.close()


if __name__ == '__main__':
    main()