from data import TestDataBase
from conftest import db
import pytest
import allure


class TestDB:
    @allure.title('Тестирование метода available_buns, который извлекает список доступных булочек из базы данных.')
    @allure.description('Используя параметризацию, мы выполняем три теста. В ходе каждого теста мы проверяем имя и стоимость каждой булки по отдельности.')
    @pytest.mark.parametrize('index_bun, bun_name, bun_price', TestDataBase.test_data_base_buns)
    def test_available_buns_db_success(self, db, index_bun, bun_name, bun_price):
        data_buns = db.available_buns()
        assert data_buns[index_bun].get_name() == bun_name and data_buns[index_bun].get_price() == bun_price

    @allure.title('Тестирование метода available_ingredients, который извлекает список доступных ингредиентов из базы данных.')
    @allure.description('С помощью параметризации мы выполняем шесть тестов, проверяя по очереди название, тип и стоимость каждого ингредиента.')
    @pytest.mark.parametrize('index_i, type_ingredient, name_ingredient, price_ingredient',
                             TestDataBase.test_data_base_ingredients)
    def test_available_ingredients_db_success(self, db, index_i, type_ingredient, name_ingredient, price_ingredient):
        data_ingredients = db.available_ingredients()
        assert (data_ingredients[index_i].get_name() == name_ingredient and
                data_ingredients[index_i].get_type() == type_ingredient and
                data_ingredients[index_i].get_price() == price_ingredient)