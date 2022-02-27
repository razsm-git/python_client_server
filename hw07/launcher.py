# Лаунчер для запуска нескольких приложений

import subprocess

process_list = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')
    count_of_clients = 0
    if ACTION == 'q':
        break
    elif ACTION == 's':
        count_of_clients_send = int(input("Введите необходимое кол-во запущенных клиентов на отправку сообщений: "))
        count_of_clients_recive = int(input("Введите необходимое кол-во запущенных клиентов на получение сообщений: "))
        process_list.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(count_of_clients_send):
            process_list.append(subprocess.Popen('python client.py -m send', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(count_of_clients_recive):
            process_list.append(subprocess.Popen('python client.py -m listen', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        for sub in process_list:
            sub.kill()
        process_list.clear()