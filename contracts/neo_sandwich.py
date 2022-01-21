from typing import Any, Union

from boa3.builtin import NeoMetadata, metadata, public
from boa3.builtin.contract import Nep17TransferEvent, abort
from boa3.builtin.interop.blockchain import get_contract
from boa3.builtin.interop.contract import call_contract, GAS
from boa3.builtin.interop.runtime import calling_script_hash, check_witness, executing_script_hash, get_notifications, \
    time
from boa3.builtin.interop.storage import delete, get, put
from boa3.builtin.type import UInt160


# todo - add option to update the contracts itself (saw some snippet, check it out)

# todo - should claim & swap be on the same call (may be problematic if the claimed amount gets large)

# todo - best way to automate the process of claiming & swapping


@metadata
def manifest_metadata() -> NeoMetadata:
    """
    Defines this smart contracts's metadata information
    """
    meta = NeoMetadata()
    meta.supported_standards = ["NEP-17"]
    meta.author = "Neo Sandwich"
    meta.description = "Savings protocol for bNEO, deposit bNEO & earn bNEO."
    meta.email = ""
    return meta


# bNEO contracts script hash & address
bNEO = UInt160(0x48C40D4666F93408BE1BEF038B6722404D9A4C2A)
bNEO_ADDRESS = b"NPmdLGJN47EddqYcxixdGMhtkr7Z5w4Aos"

# flamingo swap router contracts script hash
FLAMINGO_SWAP_ROUTER = UInt160(0xc4b74578540abd0197391867dd18d60762a4d7bd)  # fixme - this is a test net value!

# script hash of the contracts owner
OWNER = UInt160()  # todo - fill

# total supply storage key
SUPPLY_KEY = "totalSupply"

# total bNEO supply storage key
BURGER_SUPPLY_KEY = "burgerSupply"

# token symbol
TOKEN_SYMBOL = "sNEO"

# number of decimal places
TOKEN_DECIMALS = 8


@public
def deploy() -> bool:
    """
    Initializes the storage when the smart contracts is deployed.
    :return: whether the deploy was successful.

    NOTE - This method must return True only during the smart contracts's deploy.
    """
    # todo - how to block re-deployment until funds are deposited?
    #  - save is_deployed flag
    #  - add 1 to supply (negligible amount)
    if not check_witness(OWNER):
        return False

    if get(SUPPLY_KEY).to_int() > 0:
        return False

    put(SUPPLY_KEY, 0)
    Nep17TransferEvent(None, OWNER, 0)

    return True


@public
def symbol() -> str:
    """
    Gets the symbols of the contracts.
    :return: always return 'sNEO'
    """
    return TOKEN_SYMBOL


@public
def decimals() -> int:
    """
    Gets the decimal places of the contracts
    E.g. 8, means to divide the token amount by 100,000,000 (10 ^ 8) to get its user representation.
    :return: always return 8
    """
    return TOKEN_DECIMALS


@public
def totalSupply() -> int:
    """
    Gets the total sNEO token supply.
    :return: the total token supply deployed in the system
    """
    return get(SUPPLY_KEY).to_int()


@public
def burgerSupply() -> int:
    """
    Gets the total bNEO token supply held by the contracts
    :return: the total bNEO tokens the contracts has
    """
    return get(BURGER_SUPPLY_KEY).to_int()


@public
def balanceOf(account: UInt160) -> int:
    """
    Get the current balance of an address
    The parameter account must be a 20-byte address represented by a UInt160
    :param account: the account address to retrieve the balance for
    :type account: UInt160
    """
    assert len(account) == 20
    return get(account).to_int()


@public
def verify() -> bool:
    """
    When this contracts address is included in the transaction signature,
    this method will be triggered as a VerificationTrigger to verify that the signature is correct.
    For example, this method needs to be called when withdrawing token from the contracts.

    :return: whether the transaction signature is correct
    """
    return check_witness(OWNER)


@public
def transfer(from_address: UInt160, to_address: UInt160, amount: int, data: Any) -> bool:
    """
    Transfers an amount of sNEO tokens from one account to another.

    If the method succeeds, it must fire the `Transfer` event and must return true, even if the amount is 0,
    or from and to are the same address.
    :param from_address: the address to transfer from
    :type from_address: UInt160
    :param to_address: the address to transfer to
    :type to_address: UInt160
    :param amount: the amount of sNEO tokens to transfer
    :type amount: int
    :param data: whatever data is pertinent to the onPayment method
    :type data: Any
    :return: whether the transfer was successful
    :raise AssertionError: raised if `from_address` or `to_address` length is not 20 or if `amount` is less than zero.
    """
    assert len(from_address) == 20 and len(to_address) == 20
    assert amount >= 0

    # The function MUST return false if the from account balance does not have enough tokens to spend.
    from_balance = get(from_address).to_int()
    if from_balance < amount:
        return False

    if from_address != calling_script_hash:
        if not check_witness(from_address):
            return False

    if from_address != to_address and amount != 0:
        if from_balance == amount:
            delete(from_address)
        else:
            put(from_address, from_balance - amount)

        to_balance = get(to_address).to_int()
        put(to_address, to_balance + amount)

    # if the method succeeds, it must fire the transfer event
    Nep17TransferEvent(from_address, to_address, amount)
    # if the to_address is a smart contracts, it must call the contracts onPayment
    post_transfer(from_address, to_address, amount, data, True)

    return True


def post_transfer(
        from_address: Union[UInt160, None], to_address: Union[UInt160, None], amount: int, data: Any,
        call_onPayment: bool
):
    """
    Checks if the one receiving NEP17 tokens is a smart contracts and if it's one the onPayment method will be called.

    :param from_address: the address of the sender
    :type from_address: UInt160
    :param to_address: the address of the receiver
    :type to_address: UInt160
    :param amount: the amount of cryptocurrency that is being sent
    :type amount: int
    :param data: any pertinent data that might validate the transaction
    :type data: Any
    :param call_onPayment: whether onPayment should be called or not
    :type call_onPayment: bool
    """
    if call_onPayment:
        if not isinstance(to_address, None):  # TODO: change to 'is not None' when `is` semantic is implemented
            contract = get_contract(to_address)
            if not isinstance(contract, None):  # TODO: change to 'is not None' when `is` semantic is implemented
                call_contract(to_address, "onNEP17Payment", [from_address, amount, data])


def mint(account: UInt160, amount: int):
    """
    Mints new sNEO tokens.

    :param account: the address of the account that is sending cryptocurrency to this contracts
    :type account: UInt160
    :param amount: the amount of gas to be refunded
    :type amount: int
    :raise AssertionError: raised if amount is less than than 0
    """
    assert amount > 0

    current_total_supply = totalSupply()
    account_balance = balanceOf(account)

    put(SUPPLY_KEY, current_total_supply + amount)
    put(account, account_balance + amount)

    Nep17TransferEvent(None, account, amount)
    post_transfer(None, account, amount, None, True)


@public
def burn(account: UInt160, amount: int):
    """
    Burns sNEO tokens.

    :param account: the address of the account that is pulling out cryptocurrency of this contracts
    :type account: UInt160
    :param amount: the amount of bNEO to be refunded
    :type amount: int
    :raise AssertionError: raised if `account` length is not 20, amount is less than than 0 or the account doesn't have
    enough sNEO to burn
    """
    assert len(account) == 20
    assert amount > 0

    if check_witness(account):
        initial_total_supply = totalSupply()
        account_balance = balanceOf(account)

        assert account_balance >= amount

        put(SUPPLY_KEY, initial_total_supply - amount)

        if account_balance == amount:
            delete(account)
        else:
            put(account, account_balance - amount)

        Nep17TransferEvent(account, None, amount)

        burgers_to_transfer = amount * burgerSupply() // initial_total_supply

        call_contract(bNEO, "transfer", [executing_script_hash, account, burgers_to_transfer, None])


@public
def claim_gas():
    """
    Claims GAS from the bNEO tokens that held in the smart contracts.
    """
    call_contract(bNEO, "transfer", [executing_script_hash, bNEO_ADDRESS, 0, None])


# todo - convert_gas cannot be compiled
# @public
# def convert_gas(amount: int):
#     """
#     Converts amount of GAS to bNEO from the contracts GAS balance using FlamingoFinance.
#
#     NOTE - This is the method that causes the ratio to increase!
#     """
#     if not check_witness(OWNER):
#         abort()
#
#     # todo - is there a way to make it replaceable in-case of Flamingo changing contracts?
#     reserves = call_contract(FLAMINGO_SWAP_ROUTER, "GetReserves", [bNEO, GAS])
#
#     burger_price = (reserves[0] // 100_000_000) // (reserves[1] // 100_000_000)
#     amount_out_min = amount * burger_price * 0.995
#
#     deadline = time + 300  # 5 minutes
#
#     # todo - transfer GAS?
#
#     call_contract(
#         FLAMINGO_SWAP_ROUTER,
#         "SwapTokenInForTokenOut",
#         [executing_script_hash, amount, amount_out_min, [bNEO, GAS], deadline],
#     )
#
#     events = get_notifications(FLAMINGO_SWAP_ROUTER)
#     swap_event = events[-1]  # todo - verify correct index/method & verify.
#
#     # todo - fetch the event to know how many bNEO were claimed
#
#     # todo - update the total bNEO supply (increase it with the fetched amount)


@public
def onNEP17Payment(from_address: UInt160, amount: int, data: Any):
    """
    When this smart contracts receives bNEO, it will mint sNEO using the current ratio.
    Other assets than bNEO will revert the transaction

    :param from_address: the address of the one who is trying to send cryptocurrency to this smart contracts
    :type from_address: UInt160
    :param amount: the amount of cryptocurrency that is being sent to the this smart contracts
    :type amount: int
    :param data: any pertinent data that might validate the transaction
    :type data: Any
    """
    if calling_script_hash == bNEO:
        if get(SUPPLY_KEY).to_int() > 0:
            sandwiches_to_mint = amount * totalSupply() // burgerSupply()
            mint(from_address, sandwiches_to_mint)
        else:
            mint(from_address, amount)
    else:
        abort()
