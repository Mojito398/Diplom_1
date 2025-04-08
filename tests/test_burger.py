from praktikum.burger import Burger
from conftest import *
import pytest
import allure


class TestBurger:
    @allure.title('Тестирование метода set_buns, который добавляет булочку в бургер.')
    def test_successful_bun_setting(self, mock_bun):
        burger = Burger()
        burger.set_buns(mock_bun)
        assert burger.bun == mock_bun

    @allure.title('Тестирование функционала метода add_ingredient, который позволяет добавлять ингредиенты в бургер.')
    @allure.description('С помощью параметризации мы проводим три теста: по очереди добавляем соус и две различные начинки.')
    @pytest.mark.parametrize('ingredients, added_ingredient', [
        [Data1.sauce_name, Data1.sauce_name],
        [Data1.filling_name, Data1.filling_name],
        [Data2.filling_name, Data2.filling_name]
        ]
    )
    def test_successful_ingredient_addition(self, ingredients, added_ingredient):
        burger = Burger()
        burger.add_ingredient(ingredients)
        assert burger.ingredients == [added_ingredient] and len(burger.ingredients) == 1

    @allure.title('Тестирование работы метода remove_ingredient, который удаляет ингредиент из бургера.')
    @allure.description('С помощью параметризации мы проводим два теста, чтобы убедиться, что соус и начинка удаляются по отдельности.')
    @pytest.mark.parametrize('ingredients, removed_ingredient', [
        [Data1.sauce_name, Data1.sauce_name],
        [Data2.filling_name, Data2.filling_name]
        ]
    )
    def test_successful_ingredient_removal(self, ingredients, removed_ingredient, mock_filling):
        burger = Burger()
        burger.add_ingredient(mock_filling)
        burger.add_ingredient(ingredients)
        burger.remove_ingredient(1)
        assert removed_ingredient not in burger.ingredients and mock_filling in burger.ingredients

    @allure.title('Тестирование метода move_ingredient, отвечающего за перемещение ингредиентов в бургере.')
    def test_successful_ingredient_movement(self, mock_sauce, mock_filling):
        burger = Burger()
        burger.add_ingredient(mock_sauce)
        burger.add_ingredient(mock_filling)
        burger.move_ingredient(0, 1)
        assert len(burger.ingredients) == 2
        assert burger.ingredients[0] == mock_filling and burger.ingredients[1] == mock_sauce

    @allure.title('Тестирование функции get_price, отвечающей за расчет итоговой стоимости бургера.')
    def test_successful_burger_price_retrieval(self, mock_bun_2, mock_sauce_2, mock_filling_2):
        burger = Burger()
        burger.set_buns(mock_bun_2)
        burger.add_ingredient(mock_sauce_2)
        burger.add_ingredient(mock_filling_2)
        assert burger.get_price() == Data2.burger_final_cost

    @allure.title('Тестирование метода get_receipt, который возвращает рецепт приготовленного бургера и его стоимость.')
    def test_successful_receipt_retrieval(self, mock_bun, mock_sauce, mock_filling, mock_filling_2):
        burger = Burger()
        burger.set_buns(mock_bun)
        burger.add_ingredient(mock_sauce)
        burger.add_ingredient(mock_filling)
        burger.add_ingredient(mock_filling_2)
        assert burger.get_receipt() == ('(==== Флюоресцентная булка R2-D3 ====)\n'
                                        '= sauce Соус традиционный галактический =\n'
                                        '= filling Мясо бессмертных моллюсков Protostomia =\n'
                                        '= filling Сыр с астероидной плесенью =\n'
                                        '(==== Флюоресцентная булка R2-D3 ====)\n'
                                        '\n'
                                        f'Price: {burger.get_price()}')