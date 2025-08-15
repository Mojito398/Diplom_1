from tests.support.api import perform_request_and_validate

COLLECTION_UID = "26206594-ee8e2256-4f05-45bd-a42e-f590eaa2c0d6"


def test_financial_service_filters() -> None:
    perform_request_and_validate(COLLECTION_UID, "Фильтры для навигатора по финсервисам")


def test_financial_service_information_main_page() -> None:
    perform_request_and_validate(COLLECTION_UID, "Получение информации для главной страницы")


def test_financial_service_getting_list() -> None:
    perform_request_and_validate(COLLECTION_UID, "Получение main сервисов")


def test_financial_service_additional_list() -> None:
    perform_request_and_validate(COLLECTION_UID, "Получение additional сервисов")