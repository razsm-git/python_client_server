from socket import *
from common.variables import local_ip, local_port, max_connections, ACTION, ACCOUNT_NAME, \
    RESPONSE, max_connections, PRESENCE, TIME, USER, ERROR, RESPONDEFAULT_IP_ADDRESS
from common.utils import get_message, send_message
import sys
import json

args = sys.argv


def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad  Requests'
    }


def main():
    try:
        if '-p' in args:
            listen_port = int(args[sys.argv.index('-p') + 1])
        else:
            listen_port = local_port
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print("Отсутсвует номер порта после параметра '-p'")
        sys.exit(1)
    except ValueError:
        print('Номер порта должен быть целым числом в диапазоне от 1024 до 65535')
        sys.exit(1)

    try:
        if '-a' in args:
            listen_address = args[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print('Не указан адрес, на котором будет слушать сервер')
        sys.exit(1)


    # запускаем сокет

    socket_init = socket(AF_INET, SOCK_STREAM)
    socket_init.bind((listen_address, listen_port))
    socket_init.listen(max_connections)

    while True:
        client, client_address = socket_init.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print("Некорректное сообщение от клиента")
            client.close()


if __name__ == '__main__':
    main()