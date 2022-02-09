from chardet import detect
strings = ['сетевое программирование', 'сокет', 'декоратор']
with open('test_file.txt', 'w') as file:
    for string in strings:
        file.write(f'{string}\n')

# определим кодировку
with open('test_file.txt', 'rb') as file_2:
    encode = detect(file_2.read())['encoding']
    print(f"Кодировка файла: {encode}")


with open('test_file.txt', 'r', encoding=encode) as file_3:
    for line in file_3.readlines():
        print(line.strip('\n'))
