from eth_keys import keys
from eth_utils import decode_hex
from eth_typing import Address

from eth.consensus.pow import mine_pow_nonce
from eth import constants, chains
from eth.vm.forks.byzantium import ByzantiumVM
from eth.db.backends.memory import MemoryDB


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

SENDER_PRIVATE_KEY = keys.PrivateKey(
  decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
)

SENDER = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

GENESIS_STATE = {
    SENDER: {
        "balance" : 10**20,
        "nonce" : 0,
        "code" : b"",
        "storage" : {}
    }
}

klass = chains.base.MiningChain.configure(
    __name__='TestChain',
    vm_configuration=(
        (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM),
    ))

chain = klass.from_genesis(MemoryDB(), GENESIS_PARAMS, GENESIS_STATE)
vm = chain.get_vm()

# nonce = vm.get_transaction_nonce(SENDER)
nonce = vm.state.account_db.get_nonce(SENDER)


tx = vm.create_unsigned_transaction(
    nonce=nonce,
    gas_price=0,
    gas=100000,
    to=RECEIVER,
    value=10 ** 18,
    data=b'',
)

signed_tx = tx.as_signed_transaction(SENDER_PRIVATE_KEY)

chain.apply_transaction(signed_tx)

# We have to finalize the block first in order to be able read the
# attributes that are important for the PoW algorithm
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

print("SENDER BALANCE : {}".format(vm.state.account_db.get_balance(SENDER)))
print("RECEIVER BALANCE : {}".format(vm.state.account_db.get_balance(RECEIVER)))
