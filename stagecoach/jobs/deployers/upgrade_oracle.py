import asyncio
import os

from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract, ContractFunction

admin_contract_address = (
    0x029E7D00D0142EB684D6B010DDFE59348D892E5F8FF94F1B77CD372645DF4B77
)
oracle_proxy_address = (
    0x0346c57f094d641ad94e43468628d8e9c574dcb2803ec372576ccc60a40be2c4
)


async def main():
    admin_private_key = int(os.environ.get("ADMIN_PRIVATE_KEY"), 0)
    gateway = GatewayClient(net="mainnet")
    signer = StarkCurveSigner(
        admin_contract_address,
        KeyPair.from_private_key(admin_private_key),
        StarknetChainId.MAINNET,
    )

    admin = Account(
        address=admin_contract_address,
        client=gateway,
        signer=signer
    )

    declared_contract_class_hash = (
        0x59e0391fb5cacfcc558a7335eb568d44f7ccda472189b6b126f06c17a1dcf40
    )

    if declared_contract_class_hash is None:
        # Declare implementation
        with open("Oracle.json", "r") as f:
            compiled_contract = f.read()

        declare_transaction = await admin.sign_declare_transaction(
            compiled_contract=compiled_contract, max_fee=int(1e16)
        )

        # To declare a contract, send Declare transaction with AccountClient.declare method
        resp = await admin.client.declare(
            transaction=declare_transaction
        )

        print(hex(resp.transaction_hash))

        await admin.client.wait_for_tx(resp.transaction_hash)

        declared_contract_class_hash = resp.class_hash

    # Upgrade Implementation
    contract = await Contract.from_address(provider=admin, address=oracle_proxy_address, proxy_config=True)

    invocation = await contract.functions['upgrade'].invoke(declared_contract_class_hash, max_fee=int(1e16))
    print(invocation.hash)
    await invocation.wait_for_acceptance()

    print(f"Upgraded oracle proxy with class hash: {hex(declared_contract_class_hash)}")


if __name__ == "__main__":
    asyncio.run(main())