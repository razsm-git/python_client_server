import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json', 'r', encoding='utf-8') as file_1:
        data = json.load(file_1)

    with open('orders.json', 'w', encoding='utf-8') as file_2:
        orders_list = data['orders']
        order = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }
        orders_list.append(order)
        json.dump(data, file_2, indent=4)


write_order_to_json('mobile phone', '4', '15200', 'Tom', '12.01.2021')
write_order_to_json('Ноутбук HP', '1', '65350', 'Екатерина', '02.02.2022')
write_order_to_json('TV', '2', '40150', 'Nick', '25.08.2018')