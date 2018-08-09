from eth_typing import Address
STAMINA =  Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')
BLOCKCHAIN = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x0a')

from eth_abi import(
    encode_single,
)
from eth_hash.auto import (
    keccak,
)
from eth.vm.message import (
    Message,
)

def execute_bytecode(state,
                     origin,
                     gas_price,
                     gas,
                     to,
                     sender,
                     value,
                     data,
                     code,
                     code_address=None,
                     ):
    """
    Execute raw bytecode in the context of the current state of
    the virtual machine.
    """
    if origin is None:
        origin = sender

    # Construct a message
    message = Message(
        gas=gas,
        to=to,
        sender=sender,
        value=value,
        data=data,
        code=code,
        code_address=code_address,
    )

    # Construction a tx context
    transaction_context = state.get_transaction_context_class()(
        gas_price=gas_price,
        origin=origin,
    )

    # Execute it in the VM
    return state.get_computation(message, transaction_context).apply_computation(
        state,
        message,
        transaction_context,
    )

def getDelegate(state, delegator) :
    fdata = keccak("getDelegate(address)".encode())
    fnsig = fdata[0:4]
    adata = encode_single('address', delegator)
    data = fnsig + adata
    vm_state = state
    code = vm_state.account_db.get_code(STAMINA)

    # params: (state, origin, gas_price, gas, to, sender, value, data, code, code_address=None)
    computation = execute_bytecode(state, None, 100, 100, STAMINA, BLOCKCHAIN, 0, data, code, None)

    assert(computation.is_success)

    addr = computation._memory._bytes
    return addr

def getStamina(state, delegate) :
    fdata = keccak("getStamina(address)".encode())
    fnsig = fdata[0:4]
    adata = encode_single('address', delegate)
    data = fnsig + adata
    vm_state = state
    code = vm_state.account_db.get_code(STAMINA)

    # params: (state, origin, gas_price, gas, to, sender, value, data, code, code_address=None)
    computation = execute_bytecode(state, None, 100, 100, STAMINA, BLOCKCHAIN, 0, data, code, None)

    assert(computation.is_success)

    ret = computation.output
    return ret

def addStamina(state, delegate, val) :
    fdata = keccak("addStamina(address,uint256)".encode())
    fnsig = fdata[0:4]
    adata = encode_single('(address,uint256)', [delegate,val])
    data = fnsig + adata
    vm_state = state
    code = vm_state.account_db.get_code(STAMINA)

    # params: (state, origin, gas_price, gas, to, sender, value, data, code, code_address=None)
    computation = execute_bytecode(state, None, 100, 100, STAMINA, BLOCKCHAIN, 0, data, code, None)

    assert(computation.is_success)

def subtractStamina(state, delegate, val) :
    fdata = keccak("subtractStamina(address,uint256)".encode())
    fnsig = fdata[0:4]
    adata = encode_single('(address,uint256)', [delegate,val])
    data = fnsig + adata
    vm_state = state
    code = vm_state.account_db.get_code(STAMINA)

    # params: (state, origin, gas_price, gas, to, sender, value, data, code, code_address=None)
    computation = execute_bytecode(state, None, 100, 100, STAMINA, BLOCKCHAIN, 0, data, code, None)

    assert(computation.is_success)
