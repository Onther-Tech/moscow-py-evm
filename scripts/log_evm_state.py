import pathlib

from scripts.benchmark.utils.chain_plumbing import (
    get_chain,
)

from scripts.benchmark.utils.chain_plumbing import (
    FUNDED_ADDRESS,
    FUNDED_ADDRESS_PRIVATE_KEY,
    SECOND_ADDRESS,
)

from scripts.benchmark.utils.compile import (
    get_compiled_contract
)

from scripts.benchmark.utils.tx import (
    new_transaction,
)

from web3 import (
    Web3
)

from eth.chains.base import (
    MiningChain,
)

from eth.vm.forks.byzantium import (
    ByzantiumVM,
)

from eth.constants import (
    CREATE_CONTRACT_ADDRESS
)

from eth_utils import (
    encode_hex,
    decode_hex,
    to_int
)

CONTRACT_FILE = 'scripts/benchmark/contract_data/erc20.sol'
CONTRACT_NAME = 'SimpleToken'

W3_TX_DEFAULTS = {'gas': 0, 'gasPrice': 0}
DEFAULT_GAS_LIMIT = 3144659

w3 = Web3()

contract_interface = get_compiled_contract(
    pathlib.Path(CONTRACT_FILE),
    CONTRACT_NAME
)

def run() -> None:
    # get Byzantium VM
    chain = get_chain(ByzantiumVM)
    transfer(deploy(chain), chain)

def deploy(chain: MiningChain) -> str:
    return _deploy_simple_token(chain)

def transfer(ca, chain: MiningChain) -> None:
    _erc20_transfer(ca, chain)

def _deploy_simple_token(chain: MiningChain) -> None:
    # Instantiate the contract
    SimpleToken = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    # Build transaction to deploy the contract
    w3_tx = SimpleToken.constructor().buildTransaction(W3_TX_DEFAULTS)
    tx = new_transaction(
        vm=chain.get_vm(),
        private_key=FUNDED_ADDRESS_PRIVATE_KEY,
        from_=FUNDED_ADDRESS,
        to=CREATE_CONTRACT_ADDRESS,
        amount=0,
        gas=DEFAULT_GAS_LIMIT,
        data=decode_hex(w3_tx['data']),
    )

    block, receipt, computation = chain.apply_transaction(tx)
    # Keep track of deployed contract address
    deployed_contract_address = computation.msg.storage_address

    assert computation.is_success

    # Keep track of simple_token object
    simple_token = w3.eth.contract(
        address=Web3.toChecksumAddress(encode_hex(deployed_contract_address)),
        abi=contract_interface['abi'],
    )

    return deployed_contract_address

def _erc20_transfer(ca, chain: MiningChain) -> None:

    simple_token = w3.eth.contract(
        address=Web3.toChecksumAddress(encode_hex(ca)),
        abi=contract_interface['abi'],
    )

    w3_tx = simple_token.functions.transfer(
        SECOND_ADDRESS,
        1000,
    ).buildTransaction(W3_TX_DEFAULTS)

    tx = new_transaction(
        vm=chain.get_vm(),
        private_key=FUNDED_ADDRESS_PRIVATE_KEY,
        from_=FUNDED_ADDRESS,
        to=ca,
        amount=0,
        gas=DEFAULT_GAS_LIMIT,
        data=decode_hex(w3_tx['data']),
    )

    block, receipt, computation = chain.apply_transaction(tx)

    assert computation.is_success
    assert to_int(computation.output) == 1

    # _get_balance(chain, ca, SECOND_ADDRESS)

def _get_balance(chain, ca, adr) -> None:

    simple_token = w3.eth.contract(
        address=Web3.toChecksumAddress(encode_hex(ca)),
        abi=contract_interface['abi'],
    )

    w3_tx = simple_token.functions.balanceOf(
        SECOND_ADDRESS
    ).buildTransaction(W3_TX_DEFAULTS)

    tx = new_transaction(
        vm=chain.get_vm(),
        private_key=FUNDED_ADDRESS_PRIVATE_KEY,
        from_=FUNDED_ADDRESS,
        to=ca,
        amount=0,
        gas=DEFAULT_GAS_LIMIT,
        data=decode_hex(w3_tx['data']),
    )

    block, receipt, computation = chain.apply_transaction(tx)

if __name__ == '__main__':
    run()
