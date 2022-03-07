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
        count_of_clients = int(input("Введите необходимое кол-во запущенных клиентов: "))
        process_list.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(1, count_of_clients + 1):
            name = f'test{i}'
            var = subprocess.Popen(f'python client.py -n {name}', creationflags=subprocess.CREATE_NEW_CONSOLE)
            process_list.append(var)
    elif ACTION == 'x':
        for sub in process_list:
            sub.kill()
        process_list.clear()
