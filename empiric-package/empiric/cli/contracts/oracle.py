import configparser
import json
import time
from pathlib import Path
from typing import Optional, Tuple

import typer
from empiric.cli import SUCCESS, config, net
from empiric.cli.contracts.utils import (
    DEFAULT_MAX_FEE,
    _format_currencies,
    _format_pairs,
)
from empiric.cli.utils import coro
from empiric.core.utils import str_to_felt
from starknet_py.contract import Contract
from starknet_py.net.client import Client
from starkware.starknet.compiler.compile import get_selector_from_name

from .utils import declare_contract

app = typer.Typer(help="Deployment commands for Oracle")
ORACLE_CONFIG = typer.Option(
    "",
    "--deploy-config",
    "-d",
    help="configuration for currency and pair deployment",
)


@app.command()
@coro
async def deploy(
    cli_config=config.DEFAULT_CONFIG, deploy_config: Optional[str] = ORACLE_CONFIG
):
    """
    Deploy a new proxied instance of the publisher registry.
    This requires a configuration file for the currencies and pairs that the oracle will support.
    There is a sample config called oracle_constructor_data.json that shows the format.

    """
    config_parser = configparser.ConfigParser()
    config_parser.read(cli_config)

    deploy_config = deploy_config or config_parser["CONFIG"]["oracle-config-path"]

    # TODO (rlkelly): allow setting default path for config lookup in cli config
    deploy_config_path = Path(deploy_config)
    if not deploy_config_path.is_file():
        typer.echo(
            "No valid config path, please provide arg using --deploy_config or create a copy of "
            "cli/sample_config/oracle_constructor_data.json in the current path"
        )
        return 1

    gateway_url, chain_id = config.validate_config(cli_config)
    client = net.init_client(gateway_url, chain_id)
    account_client = net.init_account_client(client, cli_config)

    await deploy_oracle_proxy(account_client, deploy_config_path, cli_config)

    return SUCCESS


@app.command()
@coro
async def publish_entry(entry: str, config_path=config.DEFAULT_CONFIG):
    pair_id, value, timestamp, source, publisher = entry.split(",")
    if timestamp.lower() == "now":
        timestamp = int(time.time())

    await _publish_entry(
        config_path,
        (
            str_to_felt(pair_id.lower()),
            int(value),
            int(timestamp),
            str_to_felt(source),
            str_to_felt(publisher),
        ),
    )

    return SUCCESS


@app.command()
@coro
async def cp(pair_id: str, config_path=config.DEFAULT_CONFIG):
    client = net.init_empiric_client(config_path)
    invocation = await client.oracle.set_checkpoint.invoke(
        str_to_felt(pair_id),
        0,
        max_fee=DEFAULT_MAX_FEE,
    )
    print("invocation:", invocation.hash)

    return SUCCESS


async def deploy_oracle_proxy(
    client: Client, deploy_config_path: Path, config_path: Path
):
    """starknet deploy --contract contracts/build/PublisherRegistry.json --inputs <ADMIN_ADDRESS>"""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)
    compiled_contract_path = Path(
        config_parser["CONFIG"].get("contract-path", config.COMPILED_CONTRACT_PATH)
    )

    deploy_config = json.loads(deploy_config_path.read_text("utf-8"))
    currencies = deploy_config["currencies"]
    pairs = deploy_config["pairs"]

    admin_address = int(config_parser["USER"]["address"])
    publisher_registry_address = int(config_parser["CONTRACTS"]["publisher-registry"])

    declared_oracle_class_hash = await declare_contract(
        client, compiled_contract_path, "Oracle"
    )
    compiled_proxy = (compiled_contract_path / "Proxy.json").read_text("utf-8")

    deployment_result = await Contract.deploy(
        client,
        compiled_contract=compiled_proxy,
        constructor_args=[
            declared_oracle_class_hash,
            get_selector_from_name("initializer"),
            [
                admin_address,
                publisher_registry_address,
                len(currencies),
                *_format_currencies(currencies),
                len(pairs),
                *_format_pairs(pairs),
            ],
        ],
    )
    await deployment_result.wait_for_acceptance()
    typer.echo(f"proxy address: {deployment_result.deployed_contract.address}")

    oracle_proxy_address = deployment_result.deployed_contract.address
    config_parser["CONTRACTS"]["oracle-proxy"] = str(oracle_proxy_address)

    with open(config_path, "w") as f:
        config_parser.write(f)


async def _publish_entry(config_path: Path, entry: Tuple[int, int, int, int, int]):
    client = net.init_empiric_client(config_path)
    invocation = await client.publish_entry(*entry)

    await invocation.wait_for_acceptance()
    typer.echo(f"response hash: {invocation.hash}")


@app.command()
@coro
async def get_value(pair_id: str, config_path: Path = config.DEFAULT_CONFIG):
    client = net.init_empiric_client(config_path)
    entry = await client.oracle.get_value.call(str_to_felt(pair_id), 0)
    typer.echo(f"publishers: {entry}")