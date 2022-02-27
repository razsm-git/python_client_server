import sys
import unittest
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from client import create_presence, process_ans
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR,\
    RESPONDEFAULT_IP_ADDRESS

class TestServer(unittest.TestCase):
    # Тестирование функции из модуля client
    def test_create_presence(self):
        var = create_presence()
        var[TIME] = 1.2
        self.assertEqual(var, {ACTION: PRESENCE, TIME: 1.2, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_ok_process_ans(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_err_process_ans(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Requests'}), '400 : Bad Requests')

    def test_no_response(self):
        'не передано сообщение в качестве аргумента функции'
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Requests'})


if __name__ == '__main__':
    unittest.main()