#не уверен в верности решения, т.к. разные онлайн сервисы как то неоднозеначно давали результаты
#например, эти результаты взял из предложенного сервиса из поля utf-16, хотя не должно бы быть такого как я понимаю
#прошу поясните этот момент ,как правильно конвертировать?

source = ['разработка', 'сокет', 'декоратор']
result = ['\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
          '\u0441\u043e\u043a\u0435\u0442',
          '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440']


def info(some_list):
    for i in some_list:
        print(f"Значение: {i}, тип данных: {type(i)}")


info(source)
info(result)
