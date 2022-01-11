from boa3.boa3 import Boa3

CONTRACT_PATH = '../contract/neo_sandwich.py'


# todo - use click to create CLI


def compile_contract():
    Boa3.compile_and_save(CONTRACT_PATH)


if __name__ == '__main__':
    compile_contract()
