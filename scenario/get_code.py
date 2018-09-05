from eth_keys import keys
from eth_utils import (
    encode_hex,
    decode_hex,
)
from eth_typing import Address

from eth.consensus.pow import mine_pow_nonce
from eth import constants, chains
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.backends.memory import MemoryDB
from eth_hash.auto import (
    keccak,
)
from eth_abi import(
    encode_single,
)

from scripts.benchmark.utils.compile import (
    get_compiled_contract
)
from web3 import (
    Web3
)
import pathlib
from scripts.benchmark.utils.tx import (
    new_transaction,
)
from eth.constants import (
    CREATE_CONTRACT_ADDRESS
)
from eth.vm.stamina import(
    getDelegate
)

GENESIS_PARAMS = {
    'parent_hash': constants.GENESIS_PARENT_HASH,
    'uncles_hash': constants.EMPTY_UNCLE_HASH,
    'coinbase': constants.ZERO_ADDRESS,
    'transaction_root': constants.BLANK_ROOT_HASH,
    'receipt_root': constants.BLANK_ROOT_HASH,
    'difficulty': 1,
    'block_number': constants.GENESIS_BLOCK_NUMBER,
    'gas_limit': constants.GENESIS_GAS_LIMIT,
    'timestamp': 1514764800,
    'extra_data': constants.GENESIS_EXTRA_DATA,
    'nonce': constants.GENESIS_NONCE
}

ADDRESS_1_PRIVATE_KEY = keys.PrivateKey(
    decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
)
ADDRESS_2_PRIVATE_KEY = keys.PrivateKey(
    decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d0')
)

ADDRESS_1 = Address(ADDRESS_1_PRIVATE_KEY.public_key.to_canonical_address())
ADDRESS_2 = Address(ADDRESS_2_PRIVATE_KEY.public_key.to_canonical_address())

BLOCKCHAIN = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x0a')
STAMINA =  Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

# deploy contract

FIRST_TX_GAS_LIMIT = 2800000

CONTRACT_FILE = 'scripts/benchmark/contract_data/stamina.sol'
CONTRACT_NAME = 'Stamina'

W3_TX_DEFAULTS = {'gas': 0, 'gasPrice': 0}

contract_interface = get_compiled_contract(
    pathlib.Path(CONTRACT_FILE),
    CONTRACT_NAME
)

w3 = Web3()
addr1 = Web3.toChecksumAddress(ADDRESS_1)
addr2 = Web3.toChecksumAddress(ADDRESS_2)

GENESIS_STATE = {
    ADDRESS_1: {
        "balance" : 10**19,
        "nonce" : 0,
        "code" : b"",
        "storage" : {}
    },
    ADDRESS_2: {
        "balance" : 10**19,
        "nonce" : 0,
        "code" : b"",
        "storage" : {}
    },
    STAMINA: {
        "balance" : 10**19,
        "nonce" : 0,
        "code" : b'',
        "storage" : {}
    }
}

klass = chains.base.MiningChain.configure(
    __name__='TestChain',
    vm_configuration=(
        (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM),
    ))

chain = klass.from_genesis(MemoryDB(), GENESIS_PARAMS, GENESIS_STATE)

# Instantiate the contract

vm = chain.get_vm()

Stamina = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
)
# Build transaction to deploy the contract
w3_tx = Stamina.constructor().buildTransaction(W3_TX_DEFAULTS)
tx = new_transaction(
    vm=chain.get_vm(),
    private_key=ADDRESS_1_PRIVATE_KEY,
    from_=ADDRESS_1,
    to=CREATE_CONTRACT_ADDRESS,
    amount=0,
    gas=FIRST_TX_GAS_LIMIT,
    data=decode_hex(w3_tx['data']),
)

block, receipt, computation = chain.apply_transaction(tx)

# Keep track of deployed contract address
deployed_contract_address = computation.msg.storage_address

assert computation.is_success
# Keep track of simple_token object
stamina = w3.eth.contract(
    address=Web3.toChecksumAddress(encode_hex(deployed_contract_address)),
    abi=contract_interface['abi'],
)

block = chain.get_vm().finalize_block(chain.get_block())

# based on mining_hash, block number and difficulty we can perform
# the actual Proof of Work (PoW) mechanism to mine the correct
# nonce and mix_hash for this block
nonce, mix_hash = mine_pow_nonce(
    block.number,
    block.header.mining_hash,
    block.header.difficulty)

block = chain.mine_block(mix_hash=mix_hash, nonce=nonce)
vm = chain.get_vm()

#print("BLOCK0 CONTRACT_CODE : {}".format(encode_hex(vm.state.account_db.get_code(deployed_contract_address))))

w3_tx2 = stamina.functions.init(
    10000,100,1000
).buildTransaction(W3_TX_DEFAULTS)

tx2 = new_transaction(
    vm=vm,
    private_key=ADDRESS_1_PRIVATE_KEY,
    from_=ADDRESS_1,
    to=deployed_contract_address,
    amount=0,
    gas=FIRST_TX_GAS_LIMIT,
    data=decode_hex(w3_tx2['data']),
)

block, receipt, computation = chain.apply_transaction(tx2)

assert computation.is_success
print(computation.output)

vm = chain.get_vm()

w3_tx3 = stamina.functions.setDelegator(
    addr2
).buildTransaction(W3_TX_DEFAULTS)

tx3 = new_transaction(
    vm=vm,
    private_key=ADDRESS_1_PRIVATE_KEY,
    from_=ADDRESS_1,
    to=deployed_contract_address,
    amount=0,
    gas=FIRST_TX_GAS_LIMIT,
    data=decode_hex(w3_tx3['data']),
)

block, receipt, computation = chain.apply_transaction(tx3)

assert computation.is_success
print(computation.output)

vm = chain.get_vm()

w3_tx4 = stamina.functions.getDelegatee(
    addr2
).buildTransaction(W3_TX_DEFAULTS)

tx4 = new_transaction(
    vm=vm,
    private_key=ADDRESS_1_PRIVATE_KEY,
    from_=ADDRESS_1,
    to=deployed_contract_address,
    amount=0,
    gas=FIRST_TX_GAS_LIMIT,
    data=decode_hex(w3_tx4['data']),
)

block, receipt, computation = chain.apply_transaction(tx4)

assert computation.is_success
print(encode_hex(computation.output))
print(encode_hex(ADDRESS_1))

# ######### TX1 ###########################
# # init
# vm = chain.get_vm()
#
# fdata = keccak("init(uint256,uint256,uin256)".encode())
# fnsig = fdata[0:4]
# adata = encode_single('(uint256,uint256,uint256)', [1000000000000000000,100,1000])
# data = fnsig + adata
# data = data
#
# nonce = vm.state.account_db.get_nonce(ADDRESS_1)
# tx1 = vm.create_unsigned_transaction(
#     nonce=nonce,
#     gas_price=100,
#     gas=100000,
#     to=deployed_contract_address,
#     value=0,
#     data=data,
# )
#
# signed_tx1 = tx1.as_signed_transaction(ADDRESS_1_PRIVATE_KEY)
#
# new_header, receipt, computation = chain.apply_transaction(signed_tx1)
#
# # We have to finalize the block first in order to be able read the
# # attributes that are important for the PoW algorithm
# block = chain.get_vm().finalize_block(chain.get_block())
#
# # based on mining_hash, block number and difficulty we can perform
# # the actual Proof of Work (PoW) mechanism to mine the correct
# # nonce and mix_hash for this block
# nonce, mix_hash = mine_pow_nonce(
#     block.number,
#     block.header.mining_hash,
#     block.header.difficulty)
#
# block = chain.mine_block(mix_hash=mix_hash, nonce=nonce)
# vm = chain.get_vm()
#
# print("BLOCK1 ADDRESS_1 BALANCE : {}".format(vm.state.account_db.get_balance(ADDRESS_1)))
# print("BLOCK1 ADDRESS_2 BALANCE : {}".format(vm.state.account_db.get_balance(ADDRESS_2)))
# print("-----------------------")
#
# ############ TX2 ##################
# # setDelegatee
# vm = chain.get_vm()
#
# fdata = keccak("setDelegator(address)".encode())
# fnsig = fdata[0:4]
# adata = encode_single('address', ADDRESS_2)
# data = fnsig + adata
#
# nonce = vm.state.account_db.get_nonce(ADDRESS_1)
# tx2 = vm.create_unsigned_transaction(
#     nonce=nonce,
#     gas_price=100,
#     gas=100000,
#     to=deployed_contract_address,
#     value=0,
#     data=data,
# )
#
# signed_tx2 = tx2.as_signed_transaction(ADDRESS_1_PRIVATE_KEY)
#
# _, _, computation = chain.apply_transaction(signed_tx2)
#
# # We have to finalize the block first in order to be able read the
# # attributes that are important for the PoW algorithm
# block = chain.get_vm().finalize_block(chain.get_block())
#
# # based on mining_hash, block number and difficulty we can perform
# # the actual Proof of Work (PoW) mechanism to mine the correct
# # nonce and mix_hash for this block
# nonce, mix_hash = mine_pow_nonce(
#     block.number,
#     block.header.mining_hash,
#     block.header.difficulty)
#
# block = chain.mine_block(mix_hash=mix_hash, nonce=nonce)
#
# vm = chain.get_vm()
#
# print("BLOCK2 ADDRESS_1 BALANCE : {}".format(vm.state.account_db.get_balance(ADDRESS_1)))
# print("BLOCK2 ADDRESS_2 BALANCE : {}".format(vm.state.account_db.get_balance(ADDRESS_2)))
# print("-----------------------")
#
# ############ getDelegate ##################
#
# vm = chain.get_vm()
# delegate = getDelegate(vm.state, ADDRESS_2, deployed_contract_address, ADDRESS_1)
#
# print(encode_hex(delegate))
# print(encode_hex(ADDRESS_1))
# print("-----------------------")
