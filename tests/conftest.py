import pytest
import os
from utils.consts import NEO_CONTRACTS_DIR_PATH


def get_contracts():
    """
    :return: full paths of available contracts for testing
    """
    return os.listdir(NEO_CONTRACTS_DIR_PATH)


def pytest_addoption(parser):
    parser.addoption("--contract", action="store", choices=get_contracts())


@pytest.fixture(scope='session')
def contract(pytestconfig):
    contract = pytestconfig.getoption("contract")
    return contract

