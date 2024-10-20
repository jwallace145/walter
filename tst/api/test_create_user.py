import json

import pytest

from src.api.create_user import CreateUser
from src.api.models import Status, HTTPStatus
from src.aws.cloudwatch.client import WalterCloudWatchClient
from src.database.client import WalterDB
from tst.api.utils import get_create_user_event


@pytest.fixture
def create_user_api(
    walter_cw: WalterCloudWatchClient, walter_db: WalterDB
) -> CreateUser:
    return CreateUser(walter_cw, walter_db)


def test_create_user(create_user_api: CreateUser) -> None:
    event = get_create_user_event(email="jim@gmail.com", username="jim", password="jim")
    expected_response = get_expected_response(
        status_code=HTTPStatus.OK, status=Status.SUCCESS, message="User created!"
    )
    assert expected_response == create_user_api.invoke(event)


def test_create_user_failure_invalid_email(create_user_api: CreateUser) -> None:
    event = get_create_user_event(email="jim", username="jim", password="jim")
    expected_response = get_expected_response(
        status_code=HTTPStatus.OK, status=Status.FAILURE, message="Invalid email!"
    )
    assert expected_response == create_user_api.invoke(event)


def test_create_user_failure_invalid_username(create_user_api: CreateUser) -> None:
    event = get_create_user_event(
        email="jim@gmail.com", username="jim ", password="jim"
    )
    expected_response = get_expected_response(
        status_code=HTTPStatus.OK, status=Status.FAILURE, message="Invalid username!"
    )
    assert expected_response == create_user_api.invoke(event)


def test_create_user_failure_user_already_exists(create_user_api: CreateUser) -> None:
    event = get_create_user_event(
        email="walter@gmail.com", username="walter", password="walter"
    )
    expected_response = get_expected_response(
        status_code=HTTPStatus.OK, status=Status.FAILURE, message="User already exists!"
    )
    assert expected_response == create_user_api.invoke(event)


def get_expected_response(
    status_code: HTTPStatus, status: Status, message: str
) -> dict:
    return {
        "statusCode": status_code.value,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS,POST",
        },
        "body": json.dumps(
            {
                "API": "CreateUser",
                "Status": status.value,
                "Message": message,
            }
        ),
    }
