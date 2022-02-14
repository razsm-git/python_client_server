import csv
import re
import os
from chardet import detect


def get_data():
    list_of_files = os.listdir('data')
    main_data = []
    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    for file in list_of_files:
        with open(f"data/{file}", 'rb') as raw_file:
            encode = detect(raw_file.read())['encoding']
        with open(f"data/{file}", 'r', encoding=encode) as raw_file_encode:
            data = raw_file_encode.readlines()

        def re_func(var, row):
            if re.findall(f'({var})', row):
                new_row = re.split(r':', row, maxsplit=1)
                name = new_row[0].strip()
                value = new_row[-1].strip()
                return {name: value}

        for row in data:
            for header in headers:
                result = re_func(header, row)

                try:
                    keys = [key for key in result.keys()]
                    values = [val for val in result.values()]
                    if keys[0] == headers[0]:
                        os_prod_list.append(values[0])
                    elif keys[0] == headers[1]:
                        os_name_list.append(values[0])
                    elif keys[0] == headers[2]:
                        os_code_list.append(values[0])
                    elif keys[0] == headers[3]:
                        os_type_list.append(values[0])
                except Exception as ex:
                    pass
    main_data.append(headers)
    data_for_rows = [os_prod_list, os_name_list, os_code_list, os_type_list]
    for i in range(len(data_for_rows[0])):
        line = [row[i] for row in data_for_rows]
        main_data.append(line)
    return main_data


def write_to_csv(path):
    data = get_data()
    print(data)
    with open(f'{path}', 'w', encoding='utf-8') as file:
        writer = csv.writer(file,)
        for row in data:
            writer.writerow(row)


write_to_csv('result.csv')

