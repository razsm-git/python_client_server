import sys
import unittest
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from server import process_client_message
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR,\
    RESPONDEFAULT_IP_ADDRESS


class TestServer(unittest.TestCase):
    # Тестирование функции из модуля server

    ok_dict = {RESPONSE: 200}

    error_dict = {RESPONSE: 400, ERROR: 'Bad Requests'}


    def test_request(self):
        "Верный запрос"
        self.assertEqual(process_client_message({ACTION: PRESENCE,
            TIME: 1.2, USER: {ACCOUNT_NAME: 'Guest'}}),self.ok_dict)

    def test_no_action(self):
        "Если не указано действие"
        self.assertEqual(process_client_message(
            {TIME: 1.2, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_dict)

    def test_wrong_action(self):
        "Если указано не верное действие"
        self.assertEqual(process_client_message(
            {ACTION: "Hello", TIME: 1.2, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_dict)

    def test_no_time(self):
        "Если не указано время"
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_dict)

    def test_no_user(self):
        "Если не указан пользователь"
        self.assertEqual(process_client_message(
            {ACTION: "Hello", TIME: 1.2}), self.error_dict)

    def test_wrong_user(self):
        "Если указан не верный пользователь"
        self.assertEqual(process_client_message(
            {ACTION: "Hello", TIME: 1.2б {ACCOUNT_NAME: 'User'}}), self.error_dict)

if __name__ == '__main__':
    unittest.main()