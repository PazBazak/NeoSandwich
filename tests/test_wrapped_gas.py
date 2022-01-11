from boa3.neo import to_script_hash
from boa3 import constants
from boa3.boa3 import Boa3
from boa3.neo.cryptography import hash160
from boa3.neo.vm.type.String import String
from boa3_test.tests.test_classes.TestExecutionException import TestExecutionException
from boa3_test.tests.test_classes.testengine import TestEngine
from utils.base_test import BaseTest

DECIMALS = 8
DECIMALS_MULTIPLIER = 10 ** DECIMALS

SYMBOL = 'zGAS'
TOTAL_SUPPLY = 10_000_000 * DECIMALS_MULTIPLIER


# todo - add docs

class TestWrappedGas(BaseTest):
    """
    Testing suite for wrapped_gas.py contract.
    """

    OTHER_ACCOUNT_1 = bytes(range(20))
    OTHER_ACCOUNT_2 = to_script_hash(b'N123456789A123456789N123456789')

    def test_compile(self):
        Boa3.compile(self.contract_path)

    def test_symbol(self):
        self.assertEqual(SYMBOL, self.call_method('symbol'))

    def test_decimals(self):
        self.assertEqual(DECIMALS, self.call_method('decimals'))

    def test_deploy_by_other_account(self):
        self.assertEqual(False, self.deploy(signer=self.OTHER_ACCOUNT_1))

    def test_deploy(self):
        # owner is a signer, should return True and deploy the contract
        self.assertEqual(True, self.deploy())

        # must always return False  after first execution
        self.assertEqual(False, self.deploy())

    def test_total_supply(self):
        self.assertEqual(0, self.call_method('totalSupply'))

        self.deploy()

        self.assertEqual(TOTAL_SUPPLY, self.call_method('totalSupply'))

    def test_total_balance_of(self):
        self.assertEqual(0, self.call_method('balanceOf', self.OWNER_SCRIPT_HASH))

        self.deploy()

        self.assertEqual(TOTAL_SUPPLY, self.call_method('balanceOf', self.OWNER_SCRIPT_HASH))

    def test_validate_balance_of_input(self):
        # should fail when the script length is not 20
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.call_method('balanceOf', bytes(19))

        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.call_method('balanceOf', bytes(21))

    def test_wrapped_neo_total_transfer(self):
        transferred_amount = 10 * DECIMALS_MULTIPLIER  # 10 tokens

        output, manifest = self.compile_and_save(self.contract_path)
        wrapped_gas_address = hash160(output)

        # todo - continue
        # should fail before running deploy
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_1, transferred_amount, "",
                                         expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(self.engine, self.contract_path, 'deploy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        # when deploying, the contract will mint tokens to the owner
        transfer_events = self.engine.get_events('Transfer', origin=wrapped_gas_address)
        self.assertEqual(1, len(transfer_events))
        self.assertEqual(3, len(transfer_events[0].arguments))

        sender, receiver, amount = transfer_events[0].arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(None, sender)
        self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        self.assertEqual(10_000_000 * 100_000_000, amount)

        # should fail if the sender doesn't sign
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_1, transferred_amount, "",
                                         expected_result_type=bool)
        self.assertEqual(False, result)

        # should fail if the sender doesn't have enough balance
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, transferred_amount, "",
                                         signer_accounts=[self.OTHER_ACCOUNT_1],
                                         expected_result_type=bool)
        self.assertEqual(False, result)

        # should fail when any of the scripts' length is not 20
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                    self.OWNER_SCRIPT_HASH, bytes(10), transferred_amount, "")
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                    bytes(10), self.OTHER_ACCOUNT_1, transferred_amount, "")

        # should fail when the amount is less than 0
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                    self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, -10, "")

        # fire the transfer event when transferring to yourself
        balance_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', self.OWNER_SCRIPT_HASH)
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, self.OWNER_SCRIPT_HASH, transferred_amount, "",
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        transfer_events = self.engine.get_events('Transfer', origin=wrapped_gas_address)
        self.assertEqual(2, len(transfer_events))
        self.assertEqual(3, len(transfer_events[1].arguments))

        sender, receiver, amount = transfer_events[1].arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(self.OWNER_SCRIPT_HASH, sender)
        self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        self.assertEqual(transferred_amount, amount)

        # transferring to yourself doesn't change the balance
        balance_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', self.OWNER_SCRIPT_HASH)
        self.assertEqual(balance_before, balance_after)

        # does fire the transfer event when transferring to someone other than yourself
        balance_sender_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                        self.OWNER_SCRIPT_HASH)
        balance_receiver_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                          self.OTHER_ACCOUNT_1)
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_1, transferred_amount, "",
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        transfer_events = self.engine.get_events('Transfer')
        self.assertEqual(3, len(transfer_events))
        self.assertEqual(3, len(transfer_events[2].arguments))

        sender, receiver, amount = transfer_events[2].arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(self.OWNER_SCRIPT_HASH, sender)
        self.assertEqual(self.OTHER_ACCOUNT_1, receiver)
        self.assertEqual(transferred_amount, amount)

        # transferring to someone other than yourself does change the balance
        balance_sender_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                       self.OWNER_SCRIPT_HASH)
        balance_receiver_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                         self.OTHER_ACCOUNT_1)
        self.assertEqual(balance_sender_before - transferred_amount, balance_sender_after)
        self.assertEqual(balance_receiver_before + transferred_amount, balance_receiver_after)

    def test_wrapped_neo_verify(self):
        # should fail without signature
        result = self.run_smart_contract(self.engine, self.contract_path, 'verify',
                                         expected_result_type=bool)
        self.assertEqual(False, result)

        # should fail if not signed by the owner
        result = self.run_smart_contract(self.engine, self.contract_path, 'verify',
                                         signer_accounts=[self.OTHER_ACCOUNT_1],
                                         expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(self.engine, self.contract_path, 'verify',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

    def test_wrapped_neo_burn(self):
        output, manifest = self.compile_and_save(self.contract_path)
        wrapped_neo_address = hash160(output)

        self.engine.add_neo(wrapped_neo_address, 10_000_000 * 10 ** 8)
        burned_amount = 100 * 10 ** 8

        # deploying this smart contract will give 10m total supply * 10^8 zNEOs to OWNER
        result = self.run_smart_contract(self.engine, self.contract_path, 'deploy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        # when deploying, the contract will mint tokens to the owner
        transfer_events = self.engine.get_events('Transfer', origin=wrapped_neo_address)
        self.assertEqual(1, len(transfer_events))
        wrapped_token_transfer_event = transfer_events[0]
        self.assertEqual(3, len(wrapped_token_transfer_event.arguments))

        sender, receiver, amount = wrapped_token_transfer_event.arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(None, sender)
        self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        self.assertEqual(10_000_000 * 100_000_000, amount)

        # burning zNEO will end up giving NEO to the one who burned it
        neo_wrapped_before = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf',
                                                     wrapped_neo_address)
        neo_owner_before = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf',
                                                   self.OWNER_SCRIPT_HASH)
        zneo_owner_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                    self.OWNER_SCRIPT_HASH)
        # in this case, NEO will be given to the OWNER_SCRIPT_HASH
        result = self.run_smart_contract(self.engine, self.contract_path, 'burn', self.OWNER_SCRIPT_HASH, burned_amount,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertIsVoid(result)

        transfer_events = self.engine.get_events('Transfer', origin=wrapped_neo_address)
        self.assertGreaterEqual(len(transfer_events), 1)
        wrapped_token_transfer_event = transfer_events[-1]
        self.assertEqual(3, len(wrapped_token_transfer_event.arguments))

        sender, receiver, amount = wrapped_token_transfer_event.arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(self.OWNER_SCRIPT_HASH, sender)
        self.assertEqual(None, receiver)
        self.assertEqual(burned_amount, amount)

        transfer_events = self.engine.get_events('Transfer', origin=constants.NEO_SCRIPT)
        self.assertGreaterEqual(len(transfer_events), 1)
        neo_transfer_event = transfer_events[-1]
        self.assertEqual(3, len(neo_transfer_event.arguments))

        sender, receiver, amount = neo_transfer_event.arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(wrapped_neo_address, sender)
        self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        self.assertEqual(burned_amount, amount)

        # balance after burning
        neo_wrapped_after = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf', wrapped_neo_address)
        neo_owner_after = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf',
                                                  self.OWNER_SCRIPT_HASH)
        zneo_owner_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', self.OWNER_SCRIPT_HASH)
        self.assertEqual(neo_wrapped_before - burned_amount, neo_wrapped_after)
        self.assertEqual(neo_owner_before + burned_amount, neo_owner_after)
        self.assertEqual(zneo_owner_before - burned_amount, zneo_owner_after)

        # should fail when the script length is not 20
        with self.assertRaises(TestExecutionException, msg=self.ABORTED_CONTRACT_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'burn', bytes(15), burned_amount,
                                    signer_accounts=[self.OWNER_SCRIPT_HASH])
        # or amount is less than 0
        with self.assertRaises(TestExecutionException, msg=self.ABORTED_CONTRACT_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'burn', self.OWNER_SCRIPT_HASH, -1,
                                    signer_accounts=[self.OWNER_SCRIPT_HASH])

    def test_wrapped_neo_approve(self):
        # todo
        self.contract_path = self.get_contract_self.contract_path('wrapped_neo.py')
        self.contract_path_aux_contract = self.get_contract_self.contract_path('examples/auxiliary_contracts',
                                                                               'auxiliary_contract.py')
        engine = TestEngine()
        engine.add_contract(self.contract_path.replace('.py', '.nef'))

        output, manifest = self.compile_and_save(self.contract_path)
        wrapped_neo_address = hash160(output)
        output, manifest = self.compile_and_save(self.contract_path_aux_contract)
        aux_contract_address = hash160(output)

        allowed_amount = 10 * 10 ** 8

        # this approve will fail, because aux_contract_address doesn't have enough zNEO
        result = self.run_smart_contract(engine, self.contract_path_aux_contract, 'calling_approve',
                                         wrapped_neo_address, self.OTHER_ACCOUNT_1, allowed_amount,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(False, result)

        # deploying this smart contract will give 10m total supply * 10^8 zNEOs to OWNER
        result = self.run_smart_contract(engine, self.contract_path, 'deploy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # OWNER will give zNEO to aux_contract_address so that it can approve
        result = self.run_smart_contract(engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, aux_contract_address, allowed_amount, None,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # this approve will succeed, because aux_contract_address have enough zNEO
        result = self.run_smart_contract(engine, self.contract_path_aux_contract, 'calling_approve',
                                         wrapped_neo_address, self.OTHER_ACCOUNT_1, allowed_amount,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # approved fired an event
        approval_events = engine.get_events('Approval')
        self.assertEqual(1, len(approval_events))

        owner, spender, amount = approval_events[0].arguments
        if isinstance(owner, str):
            owner = String(owner).to_bytes()
        if isinstance(spender, str):
            spender = String(spender).to_bytes()
        self.assertEqual(aux_contract_address, owner)
        self.assertEqual(self.OTHER_ACCOUNT_1, spender)
        self.assertEqual(allowed_amount, amount)

    def test_wrapped_neo_allowance(self):
        path_aux_contract = self.get_contract_path('examples/auxiliary_contracts', 'auxiliary_contract.py')
        self.engine.add_contract(self.contract_path.replace('.py', '.nef'))

        output, manifest = self.compile_and_save(self.contract_path)
        wrapped_neo_address = hash160(output)
        output, manifest = self.compile_and_save(path_aux_contract)
        aux_contract_address = hash160(output)

        allowed_amount = 10 * 10 ** 8

        # aux_contract_address did not approve OTHER_SCRIPT_HASH
        result = self.run_smart_contract(self.engine, self.contract_path, 'allowance', aux_contract_address,
                                         self.OTHER_ACCOUNT_1,
                                         signer_accounts=[aux_contract_address],
                                         expected_result_type=bool)
        self.assertEqual(0, result)

        # deploying smart contract
        result = self.run_smart_contract(self.engine, self.contract_path, 'deploy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # OWNER will give zNEO to aux_contract_address so that it can approve
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, aux_contract_address, allowed_amount, None,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # this approve will succeed, because aux_contract_address have enough zNEO
        result = self.run_smart_contract(self.engine, path_aux_contract, 'calling_approve',
                                         wrapped_neo_address, self.OTHER_ACCOUNT_1, allowed_amount,
                                         signer_accounts=[aux_contract_address],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # aux_contract_address allowed OTHER_SCRIPT_HASH to spend transferred_amount of zNEO
        result = self.run_smart_contract(self.engine, self.contract_path, 'allowance', aux_contract_address,
                                         self.OTHER_ACCOUNT_1,
                                         signer_accounts=[aux_contract_address])
        self.assertEqual(allowed_amount, result)

    def test_wrapped_neo_transfer_from(self):
        path_aux_contract = self.get_contract_path('examples/auxiliary_contracts', 'auxiliary_contract.py')
        self.engine.add_contract(self.contract_path.replace('.py', '.nef'))

        output, manifest = self.compile_and_save(self.contract_path)
        wrapped_neo_address = hash160(output)
        output, manifest = self.compile_and_save(path_aux_contract)
        aux_contract_address = hash160(output)

        allowed_amount = 10 * 10 ** 8

        # deploying smart contract
        result = self.run_smart_contract(self.engine, self.contract_path, 'deploy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        # when deploying, the contract will mint tokens to the owner
        transfer_events = self.engine.get_events('Transfer')
        self.assertEqual(1, len(transfer_events))
        self.assertEqual(3, len(transfer_events[0].arguments))

        sender, receiver, amount = transfer_events[0].arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(None, sender)
        self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        self.assertEqual(10_000_000 * 100_000_000, amount)

        # OWNER will give zNEO to aux_contract_address so that it can approve another contracts
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer',
                                         self.OWNER_SCRIPT_HASH, aux_contract_address, 10_000_000 * 10 ** 8, None,
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        transfer_events = self.engine.get_events('Transfer')
        self.assertEqual(2, len(transfer_events))
        self.assertEqual(3, len(transfer_events[1].arguments))

        sender, receiver, amount = transfer_events[1].arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(self.OWNER_SCRIPT_HASH, sender)
        self.assertEqual(aux_contract_address, receiver)
        self.assertEqual(10_000_000 * 100_000_000, amount)

        # this approve will succeed, because aux_contract_address have enough zNEO
        result = self.run_smart_contract(self.engine, path_aux_contract, 'calling_approve',
                                         wrapped_neo_address, self.OTHER_ACCOUNT_1, allowed_amount,
                                         signer_accounts=[aux_contract_address],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        transferred_amount = allowed_amount

        # this transfer will fail,
        # because OTHER_SCRIPT_HASH is not allowed to transfer more than aux_contract_address approved
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer_from', self.OTHER_ACCOUNT_1,
                                         aux_contract_address,
                                         self.OTHER_ACCOUNT_2, transferred_amount + 1 * 10 ** 8, None,
                                         signer_accounts=[self.OTHER_ACCOUNT_1],
                                         expected_result_type=bool)
        self.assertEqual(False, result)
        transfer_events = self.engine.get_events('Transfer')
        self.assertEqual(2, len(transfer_events))

        # this transfer will succeed and will fire the Transfer event
        balance_spender_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                         self.OTHER_ACCOUNT_1)
        balance_sender_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                        aux_contract_address)
        balance_receiver_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                          self.OTHER_ACCOUNT_2)
        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer_from', self.OTHER_ACCOUNT_1,
                                         aux_contract_address,
                                         self.OTHER_ACCOUNT_2, transferred_amount, None,
                                         signer_accounts=[self.OTHER_ACCOUNT_1],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        transfer_events = self.engine.get_events('Transfer')
        self.assertEqual(3, len(transfer_events))
        self.assertEqual(3, len(transfer_events[2].arguments))

        sender, receiver, amount = transfer_events[2].arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(aux_contract_address, sender)
        self.assertEqual(self.OTHER_ACCOUNT_2, receiver)
        self.assertEqual(transferred_amount, amount)

        # transferring changed the balance
        balance_spender_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                        self.OTHER_ACCOUNT_1)
        balance_sender_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                       aux_contract_address)
        balance_receiver_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf',
                                                         self.OTHER_ACCOUNT_2)
        self.assertEqual(balance_spender_before, balance_spender_after)
        self.assertEqual(balance_sender_before - transferred_amount, balance_sender_after)
        self.assertEqual(balance_receiver_before + transferred_amount, balance_receiver_after)

        # aux_contract_address and OTHER_SCRIPT_HASH allowance was reduced to 0
        result = self.run_smart_contract(self.engine, self.contract_path, 'allowance', aux_contract_address,
                                         self.OTHER_ACCOUNT_1,
                                         signer_accounts=[aux_contract_address],
                                         expected_result_type=bool)
        self.assertEqual(0, result)

        # this approve will succeed, because aux_contract_address have enough zNEO
        result = self.run_smart_contract(self.engine, path_aux_contract, 'calling_approve',
                                         wrapped_neo_address, self.OTHER_ACCOUNT_1, allowed_amount,
                                         signer_accounts=[aux_contract_address],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        transferred_amount = allowed_amount - 4 * 10 ** 8

        result = self.run_smart_contract(self.engine, self.contract_path, 'transfer_from', self.OTHER_ACCOUNT_1,
                                         aux_contract_address,
                                         self.OTHER_ACCOUNT_2, transferred_amount, None,
                                         signer_accounts=[self.OTHER_ACCOUNT_1],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        # aux_contract_address and OTHER_SCRIPT_HASH allowance was reduced to allowed_amount - transferred_amount
        result = self.run_smart_contract(self.engine, self.contract_path, 'allowance', aux_contract_address,
                                         self.OTHER_ACCOUNT_1,
                                         signer_accounts=[aux_contract_address],
                                         expected_result_type=bool)
        self.assertEqual(allowed_amount - transferred_amount, result)

        # should fail when any of the scripts' length is not 20
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer_from',
                                    self.OWNER_SCRIPT_HASH, bytes(10), self.OTHER_ACCOUNT_1, allowed_amount, None)
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer_from',
                                    bytes(10), self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, allowed_amount, None)
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer_from',
                                    self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, bytes(10), allowed_amount, None)

        # should fail when the amount is less than 0
        with self.assertRaises(TestExecutionException, msg=self.ASSERT_RESULTED_FALSE_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'transfer_from',
                                    self.OTHER_ACCOUNT_1, self.OWNER_SCRIPT_HASH, self.OTHER_ACCOUNT_2, -10, None)

    def test_wrapped_gas_onNEP17Payment(self):
        self.engine.add_contract(self.contract_path.replace('.py', '.nef'))

        aux_path = self.get_contract_path('examples/auxiliary_contracts', 'auxiliary_contract.py')

        output, manifest = self.compile_and_save(self.contract_path)
        wrapped_neo_address = hash160(output)

        output, manifest = self.compile_and_save(aux_path)
        aux_address = hash160(output)

        minted_amount = 10 * 10 ** 8
        # deploying wrapped_neo smart contract
        result = self.run_smart_contract(self.engine, self.contract_path, 'deploy',
                                         signer_accounts=[self.OWNER_SCRIPT_HASH],
                                         expected_result_type=bool)
        self.assertEqual(True, result)
        # when deploying, the contract will mint tokens to the owner
        transfer_events = self.engine.get_events('Transfer', origin=wrapped_neo_address)
        self.assertEqual(1, len(transfer_events))
        wrapped_token_transfer_event = transfer_events[0]
        self.assertEqual(3, len(wrapped_token_transfer_event.arguments))

        sender, receiver, amount = wrapped_token_transfer_event.arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(None, sender)
        self.assertEqual(self.OWNER_SCRIPT_HASH, receiver)
        self.assertEqual(10_000_000 * 100_000_000, amount)

        self.engine.add_neo(aux_address, minted_amount)

        # the smart contract will abort if some address other than NEO calls the onPayment method
        with self.assertRaises(TestExecutionException, msg=self.ABORTED_CONTRACT_MSG):
            self.run_smart_contract(self.engine, self.contract_path, 'onNEP17Payment', aux_address, minted_amount, None,
                                    signer_accounts=[aux_address])

        neo_wrapped_before = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf',
                                                     wrapped_neo_address)
        neo_aux_before = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf', aux_address)
        zneo_aux_before = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', aux_address)
        # transferring NEO to the wrapped_neo_address will mint them
        result = self.run_smart_contract(self.engine, aux_path, 'calling_transfer', constants.NEO_SCRIPT,
                                         aux_address, wrapped_neo_address, minted_amount, None,
                                         signer_accounts=[aux_address],
                                         expected_result_type=bool)
        self.assertEqual(True, result)

        transfer_events = self.engine.get_events('Transfer', origin=constants.NEO_SCRIPT)
        self.assertEqual(1, len(transfer_events))
        neo_transfer_event = transfer_events[0]
        self.assertEqual(3, len(neo_transfer_event.arguments))

        sender, receiver, amount = neo_transfer_event.arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(aux_address, sender)
        self.assertEqual(wrapped_neo_address, receiver)
        self.assertEqual(minted_amount, amount)

        transfer_events = self.engine.get_events('Transfer', origin=wrapped_neo_address)
        self.assertEqual(2, len(transfer_events))
        wrapped_token_transfer_event = transfer_events[1]
        self.assertEqual(3, len(wrapped_token_transfer_event.arguments))

        sender, receiver, amount = wrapped_token_transfer_event.arguments
        if isinstance(sender, str):
            sender = String(sender).to_bytes()
        if isinstance(receiver, str):
            receiver = String(receiver).to_bytes()
        self.assertEqual(None, sender)
        self.assertEqual(aux_address, receiver)
        self.assertEqual(minted_amount, amount)

        # balance after burning
        neo_wrapped_after = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf', wrapped_neo_address)
        neo_aux_after = self.run_smart_contract(self.engine, constants.NEO_SCRIPT, 'balanceOf', aux_address)
        zneo_aux_after = self.run_smart_contract(self.engine, self.contract_path, 'balanceOf', aux_address)
        self.assertEqual(neo_wrapped_before + minted_amount, neo_wrapped_after)
        self.assertEqual(neo_aux_before - minted_amount, neo_aux_after)
        self.assertEqual(zneo_aux_before + minted_amount, zneo_aux_after)
