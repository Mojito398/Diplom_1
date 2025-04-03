class Bun:
    """
    Модель булочки для бургера.
    Булочке можно дать название и назначить цену.
    """

    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
#Получить Имя
    def get_name(self) -> str:
        return self.name
#Получить цену
    def get_price(self) -> float:
        return self.price
