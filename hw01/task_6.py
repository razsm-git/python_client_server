import locale

default_coding = locale.getpreferredencoding()
print(f"Кодировка системы по умолчанию: {default_coding}")
strings = ['сетевое программирование', 'сокет', 'декоратор']
with open('test_file.txt', 'w') as file:
    for string in strings:
        file.write(f'{string}\n')


with open('test_file.txt', 'r', encoding=default_coding) as file_2:
    print(f'Кодировка файла: {file_2.encoding}')
    for line in file_2.readlines():
        print(line.strip('\n'))
