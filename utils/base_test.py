import pytest
from boa3_test.tests.boa_test import BoaTest
from boa3_test.tests.test_classes.testengine import TestEngine
from .consts import NEO_CONTRACTS_DIR_PATH


class BaseTest(BoaTest):
    """
    Base Test for testing smart contracts
    """

    OWNER_SCRIPT_HASH = bytes(20)

    @pytest.fixture(scope='class', autouse=True)
    def setup_class(self, contract):
        cls = type(self)
        cls.contract_path = self.get_contract_path(NEO_CONTRACTS_DIR_PATH, contract)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.engine = TestEngine()

    def deploy(self, signer=OWNER_SCRIPT_HASH):
        """
        Calls 'deploy' method of the given contract.
        :param signer: Account that signed the deployment call
        """
        return self.call_method('deploy', signer_accounts=[signer])

    def call_method(self, method: str, *args, **kwargs):
        """
        Invokes contract method
        :param method: The contract method name
        :return: The returned value from contract.
        """
        return self.run_smart_contract(
            self.engine,
            self.contract_path,
            method,
            *args, **kwargs)
