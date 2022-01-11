from boa3.boa3 import Boa3

CONTRACT_PATH = '../NeoContracts/wrapped_gas.py'

# todo - use click to create CLI


if __name__ == '__main__':
    Boa3.compile_and_save(CONTRACT_PATH)
