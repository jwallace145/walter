import pytest

from src.api.add_stock import AddStock
from src.api.methods import Status, HTTPStatus
from src.aws.cloudwatch.client import WalterCloudWatchClient
from src.aws.secretsmanager.client import WalterSecretsManagerClient
from src.database.client import WalterDB
from src.stocks.client import WalterStocksAPI
from tst.api.utils import get_add_stock_event, get_expected_response


@pytest.fixture
def add_stock_api(
    walter_cw: WalterCloudWatchClient,
    walter_db: WalterDB,
    walter_stocks_api: WalterStocksAPI,
    walter_sm: WalterSecretsManagerClient,
) -> AddStock:
    return AddStock(walter_cw, walter_db, walter_stocks_api, walter_sm)


def test_add_stock(add_stock_api: AddStock, jwt_walter: str) -> None:
    event = get_add_stock_event(
        email="walter@gmail.com", stock="ABNB", quantity=100.0, token=jwt_walter
    )
    expected_response = get_expected_response(
        api_name=add_stock_api.API_NAME,
        status_code=HTTPStatus.CREATED,
        status=Status.SUCCESS,
        message="Stock added!",
    )
    assert expected_response == add_stock_api.invoke(event)


def test_add_stock_failure_stock_does_not_exist(
    add_stock_api: AddStock, jwt_walter: str
) -> None:
    event = get_add_stock_event(
        email="walter@gmail.com", stock="INVALID", quantity=100.0, token=jwt_walter
    )
    expected_response = get_expected_response(
        api_name=add_stock_api.API_NAME,
        status_code=HTTPStatus.OK,
        status=Status.FAILURE,
        message="Stock does not exist!",
    )
    assert expected_response == add_stock_api.invoke(event)
