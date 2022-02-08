# не понял , почему нельзя какие то значения запись в байтовом виде? тут получилось
# функцию не стал импортировать из task_2.py, для наглядности

source = ['attribute', 'класс', 'функция', 'type']

def info(some_list):
    for i in some_list:
        i = bytes(i, encoding='utf-8')
        print(f"Значение: {i}, тип данных: {type(i)}, длина: {len(i)}")


info(source)

