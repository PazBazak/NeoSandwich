from boa3_test.tests.test_classes.TestExecutionException import TestExecutionException
from utils.base_test import BaseTest

TOKEN_SYMBOL = "sNEO"

DECIMALS = 8
DECIMALS_MULTIPLIER = 100_000_000


class TestSandwichAsNEP17(BaseTest):
    """
    Testing suite for neo_sandwich.py contracts, validating it's behavior as NEP17 token.
    """
    OTHER_ACCOUNT_1 = bytes(range(20))

    def test_deploy(self):
        """
        Verify the contracts is deployable when OWNER is signing!
        """
        self.assertEqual(True, self.deploy(signer=self.OWNER_SCRIPT_HASH))

    def test_symbol(self):
        """
        Verify the token symbol is 'sNEO'
        """
        self.assertEqual(TOKEN_SYMBOL, self.call_method("symbol"))

    def test_decimals(self):
        """
        Verify the token decimals is 8
        """
        self.assertEqual(DECIMALS, self.call_method("decimals"))

    def test_verify(self):
        """
        Verify that 'verify' method should only return True when the owner has signed the transaction.
        """
        # should fail without signature
        self.assertEqual(False, self.call_method("verify"))

        # should fail if not signed by the owner
        self.assertEqual(False, self.call_method("verify", signer_accounts=[self.OTHER_ACCOUNT_1]))

        # should pass, because owner signed
        self.assertEqual(True, self.call_method("verify", signer_accounts=[self.OWNER_SCRIPT_HASH]))

    def test_validate_balance_of_input(self):
        """
        Verify balanceOf method validates addresses length
        """
        with self.assertRaises(TestExecutionException):
            self.call_method("balanceOf", bytes(19))

        with self.assertRaises(TestExecutionException):
            self.call_method("balanceOf", bytes(21))

    def test_validate_transfer_input(self):
        """
        todo
        """

    def test_cannot_deploy_by_other_account(self):
        """
        Verify that accounts other than OWNER cannot deploy the contracts
        """
        self.assertEqual(False, self.deploy(signer=self.OTHER_ACCOUNT_1))

    def test_transfer(self):
        """
        todo
        """
        # transferred_amount = 10 * DECIMALS_MULTIPLIER  # 10 tokens
        #
        # output, manifest = self.compile_and_save(self.contract_path)
        # wrapped_gas_address = hash160(output)
        #
        # # should fail before running deploy
        # result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                                  self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_1, transferred_amount, "",
        #                                  expected_result_type=bool)
        # self.assertEqual(False, result)
        #
        # result = self.run_smart_contract(self.engine, self.contract_path, 'deploy',
        #                                  signer_accounts=[self.OWNER_SCRIPT_HASH],
        #                                  expected_result_type=bool)
        # self.assertEqual(True, result)
        # # when deploying, the contracts will mint tokens to the owner
        # transfer_events = self.engine.get_events('Transfer', origin=wrapped_gas_address)
        # self.assertEqual(1, len(transfer_events))
        # self.assertEqual(3, len(transfer_events[0].arguments))
        #
        # sender, receiver, amount = transfer_events[0].arguments
        # if isinstance(sender, str):
        #     sender = String(sender).to_bytes()
        # if isinstance(receiver, str):
        #     receiver = String(receiver).to_bytes()
        # self.assertEqual(None, sender)
        # self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        # self.assertEqual(10_000_000 * 100_000_000, amount)
        #
        # # should fail if the sender doesn't sign
        # result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                                  self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_1, transferred_amount, "",
        #                                  expected_result_type=bool)
        # self.assertEqual(False, result)
        #
        # # should fail if the sender doesn't have enough balance
        # result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                                  self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, transferred_amount, "",
        #                                  signer_accounts=[self.OTHER_ACCOUNT_1],
        #                                  expected_result_type=bool)
        # self.assertEqual(False, result)
        #
        # # should fail when any of the scripts' length is not 20
        # with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
        #     self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                             self.OWNER_SCRIPT_HASH, bytes(10), transferred_amount, "")
        # with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
        #     self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                             bytes(10), self.OTHER_ACCOUNT_1, transferred_amount, "")
        #
        # # should fail when the amount is less than 0
        # with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
        #     self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                             self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, -10, "")
        #
        # # fire the transfer event when transferring to yourself
        # balance_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', self.OWNER_SCRIPT_HASH)
        # result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                                  self.OWNER_SCRIPT_HASH, self.OWNER_SCRIPT_HASH, transferred_amount, "",
        #                                  signer_accounts=[self.OWNER_SCRIPT_HASH],
        #                                  expected_result_type=bool)
        # self.assertEqual(True, result)
        # transfer_events = self.engine.get_events('Transfer', origin=wrapped_gas_address)
        # self.assertEqual(2, len(transfer_events))
        # self.assertEqual(3, len(transfer_events[1].arguments))
        #
        # sender, receiver, amount = transfer_events[1].arguments
        # if isinstance(sender, str):
        #     sender = String(sender).to_bytes()
        # if isinstance(receiver, str):
        #     receiver = String(receiver).to_bytes()
        # self.assertEqual(self.OWNER_SCRIPT_HASH, sender)
        # self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        # self.assertEqual(transferred_amount, amount)
        #
        # # transferring to yourself doesn't change the balance
        # balance_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', self.OWNER_SCRIPT_HASH)
        # self.assertEqual(balance_before, balance_after)
        #
        # # does fire the transfer event when transferring to someone other than yourself
        # balance_sender_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
        #                                                 self.OWNER_SCRIPT_HASH)
        # balance_receiver_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
        #                                                   self.OTHER_ACCOUNT_1)
        # result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
        #                                  self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_1, transferred_amount, "",
        #                                  signer_accounts=[self.OWNER_SCRIPT_HASH],
        #                                  expected_result_type=bool)
        # self.assertEqual(True, result)
        # transfer_events = self.engine.get_events('Transfer')
        # self.assertEqual(3, len(transfer_events))
        # self.assertEqual(3, len(transfer_events[2].arguments))
        #
        # sender, receiver, amount = transfer_events[2].arguments
        # if isinstance(sender, str):
        #     sender = String(sender).to_bytes()
        # if isinstance(receiver, str):
        #     receiver = String(receiver).to_bytes()
        # self.assertEqual(self.OWNER_SCRIPT_HASH, sender)
        # self.assertEqual(self.OTHER_ACCOUNT_1, receiver)
        # self.assertEqual(transferred_amount, amount)
        #
        # # transferring to someone other than yourself does change the balance
        # balance_sender_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
        #                                                self.OWNER_SCRIPT_HASH)
        # balance_receiver_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
        #                                                  self.OTHER_ACCOUNT_1)
        # self.assertEqual(balance_sender_before - transferred_amount, balance_sender_after)
        # self.assertEqual(balance_receiver_before + transferred_amount, balance_receiver_after)

