import yaml

source_data = {
    'cars': ['bmw', 'audi', 'jeep'],
    'cars_free': 3,
    'price': {
        'bmw': '9500€',
        'audi': '11000€',
        'jeep': '8210€'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as file_1:
    yaml.dump(source_data, file_1, default_flow_style=False, allow_unicode=True)

with open('file.yaml', 'r', encoding='utf-8') as file_2:
    result = yaml.load(file_2, Loader=yaml.SafeLoader)

print(source_data == result)