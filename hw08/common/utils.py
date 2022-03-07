import json
import sys
import os
sys.path.append(os.path.join(os.getcwd(),'..'))
from common.variables import max_package_length, encoding
from decor import log
from errors import IncorrectDataRecivedError


@log
def get_message(client):
    # функция для приёма сообщений в байтах
    encode_response = client.recv(max_package_length)
    if isinstance(encode_response, bytes):
        json_response = encode_response.decode(encoding=encoding)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError


@log
def send_message(sock, message):
    # функция для отправки сообщения в байтах

    if not isinstance(message, dict):
        raise TypeError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(encoding)
    sock.send(encoded_message)