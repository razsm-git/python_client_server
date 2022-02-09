# не понял , почему нельзя какие то значения запись в байтовом виде? тут получилось
# функцию не стал импортировать из task_2.py, для наглядности

source = ['attribute', 'класс', 'функция', 'type']


def info(some_list):
    for i in some_list:
        try:
            bytes(i, encoding='ascii')
        except UnicodeError as ex:
            print(f"Значение '{i}' неевозможно записать в байтовом виде, тип данных: {type(i)}, длина: {len(i)}")


info(source)

