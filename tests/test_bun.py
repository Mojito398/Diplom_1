from conftest import *
import allure


class TestBun:

    @allure.title('Тестирование метода get_name, который возвращает название булки.')
    def test_successful_bun_name_retrieval(self, mock_bun):
        assert mock_bun.get_name() == Data1.bun_name

    @allure.title('Тестирование метода get_price, который определяет стоимость булки.')
    def test_successful_bun_price_retrieval(self, mock_bun_2):
        assert mock_bun_2.get_price() == Data2.bun_price