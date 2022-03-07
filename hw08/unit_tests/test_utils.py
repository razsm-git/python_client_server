import unittest
import json
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.utils import get_message, send_message
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR, encoding


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_msg = None
        self.recived_msg = None

    def send(self, msg_for_send):
        """ функция для отправки сообщения
        оно будет закодировано и отправлено в сокет """
        msg_json = json.dumps(self.test_dict)
        self.encoded_msg = msg_json.encode(encoding)
        self.recived_msg = msg_for_send

    def recv(self, max_len):
        # функция для получения данных из сокета
        msg_json = json.dumps(self.test_dict)
        return msg_json.encode(encoding)


class TestUtils(unittest.TestCase):
    # Класс для тестирования функций отправки и получения, без создания сокетов
    test_dict_for_send = {
        ACTION: PRESENCE,
        TIME: 1.2,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }
    test_dict_recived_ok = {RESPONSE: 200}
    test_dict_recived_error = {RESPONSE: 400, ERROR: 'Bad requests'}

    def test_send_message(self):
        # создаем тестовый сокет
        test_socket = TestSocket(self.test_dict_for_send)
        send_message(test_socket, self.test_dict_for_send)

        self.assertEqual(test_socket.encoded_msg, test_socket.recived_msg)

    def test_error_type_data(self):
        # проверим, что входные данные это точно словарь
        test_socket = TestSocket(self.test_dict_for_send)
        send_message(test_socket, self.test_dict_for_send)
        self.assertRaises(TypeError, send_message, test_socket,'error data string')

    def test_get_message(self):
        # проверим функцию приема сообщений
        test_socket_ok = TestSocket(self.test_dict_recived_ok)
        self.assertEqual(get_message(test_socket_ok), self.test_dict_recived_ok)

    def test_get_message_error(self):
        test_socket_error = TestSocket(self.test_dict_recived_error)
        self.assertEqual(get_message(test_socket_error), self.test_dict_recived_error)


if __name__ == '__main__':
    unittest.main()
