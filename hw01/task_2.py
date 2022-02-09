source = ['class', 'function', 'method']


def info(some_list):
    for i in some_list:
        i = eval(f"b'{i}'")
        print(f"Значение: {i}, тип данных: {type(i)}, длина: {len(i)}")


info(source)
