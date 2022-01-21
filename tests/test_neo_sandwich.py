from boa3.neo import to_script_hash
from boa3 import constants
from boa3.neo.cryptography import hash160
from boa3.neo.vm.type.String import String
from boa3_test.tests.test_classes.TestExecutionException import TestExecutionException
from utils.base_test import BaseTest

DECIMALS_MULTIPLIER = 100_000_000


class TestNeoSandwich(BaseTest):
    """
    Testing suite for neo_sandwich.py contracts.
    """
    OTHER_ACCOUNT_1 = bytes(range(20))
    OTHER_ACCOUNT_2 = to_script_hash(b"N123456789A123456789N123456789")

    def test_onNEP17Payment_no_burgers(self):
        """
        todo
        """
        # output, _ = self.compile_and_save(self.contract_path)
        # neo_sandwich_address = hash160(output)
        #
        # self.deploy()
        #
        # self.engine.add_neo(self.OTHER_ACCOUNT_1, 100 * DECIMALS_MULTIPLIER)
        # self.engine.add_gas(self.OTHER_ACCOUNT_1, 100 * DECIMALS_MULTIPLIER)
        #
        # # the smart contracts will abort if some address other than NEO calls the onPayment method
        # with self.assertRaises(TestExecutionException, msg=self.ABORTED_CONTRACT_MSG):
        #     self.run_smart_contract(
        #         self.engine,
        #         self.contract_path,
        #         "onNEP17Payment",
        #         aux_address,
        #         minted_amount,
        #         None,
        #         signer_accounts=[aux_address],
        #     )
        #
        # neo_wrapped_before = self.run_smart_contract(
        #     self.engine, constants.NEO_SCRIPT, "balanceOf", neo_sandwich_address
        # )
        # neo_aux_before = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, "balanceOf", aux_address)
        # zneo_aux_before = self.run_smart_contract(self.engine, self.contract_path, "balanceOf", aux_address)
        # # transferring NEO to the wrapped_neo_address will mint them
        # result = self.run_smart_contract(
        #     self.engine,
        #     aux_path,
        #     "calling_transfer",
        #     constants.NEO_SCRIPT,
        #     aux_address,
        #     neo_sandwich_address,
        #     minted_amount,
        #     None,
        #     signer_accounts=[aux_address],
        #     expected_result_type=bool,
        # )
        # self.assertEqual(True, result)
        #
        # transfer_events = self.engine.get_events("Transfer", origin=constants.NEO_SCRIPT)
        # self.assertEqual(1, len(transfer_events))
        # neo_transfer_event = transfer_events[0]
        # self.assertEqual(3, len(neo_transfer_event.arguments))
        #
        # sender, receiver, amount = neo_transfer_event.arguments
        # if isinstance(sender, str):
        #     sender = String(sender).to_bytes()
        # if isinstance(receiver, str):
        #     receiver = String(receiver).to_bytes()
        # self.assertEqual(aux_address, sender)
        # self.assertEqual(neo_sandwich_address, receiver)
        # self.assertEqual(minted_amount, amount)
        #
        # transfer_events = self.engine.get_events("Transfer", origin=neo_sandwich_address)
        # self.assertEqual(2, len(transfer_events))
        # wrapped_token_transfer_event = transfer_events[1]
        # self.assertEqual(3, len(wrapped_token_transfer_event.arguments))
        #
        # sender, receiver, amount = wrapped_token_transfer_event.arguments
        # if isinstance(sender, str):
        #     sender = String(sender).to_bytes()
        # if isinstance(receiver, str):
        #     receiver = String(receiver).to_bytes()
        # self.assertEqual(None, sender)
        # self.assertEqual(aux_address, receiver)
        # self.assertEqual(minted_amount, amount)
        #
        # # balance after burning
        # neo_wrapped_after = self.run_smart_contract(
        #     self.engine, constants.NEO_SCRIPT, "balanceOf", neo_sandwich_address
        # )
        # neo_aux_after = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, "balanceOf", aux_address)
        # zneo_aux_after = self.run_smart_contract(self.engine, self.contract_path, "balanceOf", aux_address)
        # self.assertEqual(neo_wrapped_before + minted_amount, neo_wrapped_after)
        # self.assertEqual(neo_aux_before - minted_amount, neo_aux_after)
        # self.assertEqual(zneo_aux_before + minted_amount, zneo_aux_after)
