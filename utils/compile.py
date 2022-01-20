from boa3.boa3 import Boa3

CONTRACT_PATH = "../contracts/neo_sandwich.py"


# todo - create small CLI


def compile_contract():
    Boa3.compile_and_save(CONTRACT_PATH)


if __name__ == "__main__":
    compile_contract()
