import os
import pytest
from boa3_test.tests.test_classes.testengine import TestEngine
from utils.consts import CONTRACTS_DIR_PATH


def list_contracts() -> list:
    """
    todo
    """
    return os.listdir(CONTRACTS_DIR_PATH)

def pytest_addoption(parser):
    parser.addoption("--contracts-name", "--cn", action="store", default="neo_sandwich")


@pytest.fixture(autouse=True)
def engine():
    """
    Create new TestEngine instance.
    :return: newly created TestEngine instance
    """
    return TestEngine()


@pytest.fixture(scope="session", autouse=True)
def contract_path(pytestconfig) -> str:
    """
    Returns the path for the tested contracts
    """
    contract_name = pytestconfig.getoption("contracts_name") + '.py'
    available_contracts = list_contracts()

    assert contract_name in available_contracts, f"Contract not in available contracts - {available_contracts}"

    contract_path_ = os.path.join(CONTRACTS_DIR_PATH, contract_name)
    return contract_path_

