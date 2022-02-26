from socket import *
from common.variables import local_ip, local_port, ACTION, ACCOUNT_NAME, \
    RESPONSE, max_connections, PRESENCE, TIME, USER, ERROR, RESPONDEFAULT_IP_ADDRESS
from common.utils import get_message, send_message
import sys
import json
import logging
import logs.server_log_config
from errors import *
from decor import log

server_log = logging.getLogger('app.server')
args = sys.argv


@log
def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        server_log.debug("Сообщение имеет корректный формат")
        return {RESPONSE: 200}
    server_log.error("Сообщение имеет не корректный формат")
    return {
        RESPONSE: 400,
        ERROR: 'Bad Requests'
    }


@log
def main():
    server_log.info("Начало работы мудуля сервер")
    try:
        if '-p' in args:
            listen_port = int(args[sys.argv.index('-p') + 1])
            server_log.debug("Номер порта %d передан в аргументах при запуске модуля", listen_port)
        else:
            listen_port = local_port
            server_log.debug("Установлен порт по умолчанию %d", listen_port)
        if listen_port < 1024 or listen_port > 65535:
            server_log.critical("Порт %d выходит за рамки допустимого диапазона(от 1024 до 65535)!", listen_port)
            raise ValueError
    except IndexError:
        server_log.critical("Не указан номер порта")
        sys.exit(1)
    except ValueError:
        server_log.critical("Порт %d должен быть целым числом в рамках допустимого диапазона(от 1024 до 65535)!", listen_port)
        sys.exit(1)

    try:
        if '-a' in args:
            listen_address = args[sys.argv.index('-a') + 1]
            server_log.debug("Ip аддрес %s передан в аргументах при запуске модуля", listen_address)
        else:
            listen_address = ''
            server_log.debug("По умолчанию будут прослушиваться все ip адреса на интерфейсах")
    except IndexError:
        server_log.critical("Не указан Ip адресс, который необходимо слушать")
        sys.exit(1)


    # запускаем сокет

    socket_init = socket(AF_INET, SOCK_STREAM)
    socket_init.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socket_init.bind((listen_address, listen_port))
    socket_init.listen(max_connections)
    server_log.info("Сервер запущен и слущает запросы на %s:%d",listen_address,listen_port)
    while True:
        client, client_address = socket_init.accept()
        server_log.debug("Приняли сообщение от клиента с адреса %s", client_address)
        try:
            message_from_client = get_message(client)
            server_log.debug("Полученое сообщение от клиента: %s", message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            server_log.debug("Отправлен ответ клиенту: %s", response)
            client.close()
            server_log.info("Сокет %s закрыт", client)
        except json.JSONDecodeError:
            server_log.error(f"Ошибка декодировки JSON строки, полученной от клиента {client_address}. Соединение закрывается")
            client.close()
        except IncorrectDataRecivedError:
            server_log.warning(f"Некорректное сообщение от клиента {client_address}. Соединение закрывается")
            client.close()


if __name__ == '__main__':
    main()