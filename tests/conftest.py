import pytest
import requests_mock


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m
