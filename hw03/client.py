import json
from socket import *
from common.variables import local_ip, local_port, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR
from common.utils import send_message, get_message
import sys
import time

args = sys.argv


def create_presence(account_name='Guest'):
    # функция для создания запроса о присутсвии клиента в сети
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


def process_ans(message):
    # анализ ответа сервера
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'


def main():
    try:
        server_address = args[1]
        server_port = int(args[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = local_ip
        server_port = local_port
    except ValueError:
        print('Номер порта должен быть целым числом в диапазоне от 1024 до 65535')
        sys.exit(1)


    # создааем сокет
    socket_init = socket(AF_INET, SOCK_STREAM)
    socket_init.connect((server_address, server_port))
    message = create_presence()
    send_message(socket_init, message)
    try:
        answer = process_ans(get_message(socket_init))
        print(answer)
    except (ValueError,json.JSONDecodeError):
        print('Декодировка сообщения не выполнена')


if __name__ == '__main__':
    main()
