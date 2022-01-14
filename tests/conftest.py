import pytest
from boa3_test.tests.test_classes.testengine import TestEngine


@pytest.fixture(autouse=True)
def engine():
    """
    todo
    :return:
    """
    return TestEngine()

