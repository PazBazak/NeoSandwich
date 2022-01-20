import pytest
from boa3.boa3 import Boa3
from boa3_test.tests.boa_test import BoaTest


class BaseTest(BoaTest):
    """
    Base Test for testing smart contracts
    """
    OWNER_SCRIPT_HASH = bytes(20)

    @pytest.fixture(autouse=True)
    def setup(self, engine, contract_path):
        self.engine = engine
        self.contract_path = contract_path

    @pytest.fixture(scope='session', autouse=True)
    def compile_contract(self, contract_path):
        Boa3.compile(contract_path)

    def deploy(self, signer=None):
        """
        Calls 'deploy' method of the given contracts.
        :param signer: Account that signed the deployment call
        """
        signer = signer or self.OWNER_SCRIPT_HASH
        return self.call_method("deploy", signer_accounts=[signer])

    def call_method(self, method: str, *args, **kwargs):
        """
        Invokes a contracts method
        :param method: The contracts method name
        :return: The returned value from contracts.
        """
        return self.run_smart_contract(self.engine, self.contract_path, method, *args, **kwargs)
