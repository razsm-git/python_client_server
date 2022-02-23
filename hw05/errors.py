class IncorrectDataRecivedError(Exception):
    # Некорректные данные от сокета
    def __str__(self):
        return "Принято некорректное сообщение от клиента"


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f"В данных отсутсвует необходимое поле {self.missing_field}"


class ConnectionRefusedError(Exception):
    def __str__(self):
        return "Попытка подключение не увенчалась успехом"

