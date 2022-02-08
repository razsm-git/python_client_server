source = ['разработка', 'администрирование', 'protocol', 'standard']


def info(some_list):
    for i in some_list:
        i = str(i).encode()
        print(f"Значение в байтовом виде: {i}, тип данных: {type(i)}, длина: {len(i)}")
        i = i.decode()
        print(f"Значение в текстовом виде виде: {i}, тип данных: {type(i)}, длина: {len(i)}")


info(source)
