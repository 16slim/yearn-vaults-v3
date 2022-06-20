import pytest
import ape
from ape import chain
from utils import checks
from utils.constants import ZERO_ADDRESS


def test_add_strategy__with_valid_strategy(chain, gov, vault, create_strategy):
    new_strategy = create_strategy(vault)

    snapshot = chain.pending_timestamp
    tx = vault.addStrategy(new_strategy.address, sender=gov)
    event = list(tx.decode_logs(vault.StrategyAdded))

    assert len(event) == 1
    assert event[0].strategy == new_strategy.address

    strategy_params = vault.strategies(new_strategy)
    assert strategy_params.activation == snapshot
    assert strategy_params.currentDebt == 0
    assert strategy_params.maxDebt == 0


def test_add_strategy__with_zero_address__fails_with_error(gov, vault):
    with ape.reverts("strategy cannot be zero address"):
        vault.addStrategy(ZERO_ADDRESS, sender=gov)


def test_add_strategy__with_activation__fails_with_error(gov, vault, strategy):
    with ape.reverts("strategy already active"):
        vault.addStrategy(strategy.address, sender=gov)


def test_add_strategy__with_incorrect_asset__fails_with_error(
    gov, vault, create_strategy, mock_token, create_vault
):
    # create strategy with same vault but diff asset
    other_vault = create_vault(mock_token)
    mock_token_strategy = create_strategy(other_vault)

    with ape.reverts("invalid asset"):
        vault.addStrategy(mock_token_strategy.address, sender=gov)


def test_add_strategy__with_incorrect_vault__fails_with_error(
    gov, vault, asset, create_strategy, create_vault
):
    # create strategy with diff vault but same asset
    other_vault = create_vault(asset)
    strategy = create_strategy(other_vault)

    with ape.reverts("invalid vault"):
        vault.addStrategy(strategy.address, sender=gov)


def test_revoke_strategy__with_existing_strategy(gov, vault, strategy):
    tx = vault.revokeStrategy(strategy.address, sender=gov)
    event = list(tx.decode_logs(vault.StrategyRevoked))

    assert len(event) == 1
    assert event[0].strategy == strategy.address

    strategy_params = vault.strategies(strategy)
    checks.check_revoked_strategy(strategy_params)


def test_revoke_strategy__with_non_zero_debt__fails_with_error():
    # TODO: try to remove a strategy with debt in it
    # implement when we can add debt to strategy
    return


def test_revoke_strategy__with_inactive_strategy__fails_with_error(
    gov, vault, create_strategy
):
    strategy = create_strategy(vault)

    with ape.reverts("strategy not active"):
        vault.revokeStrategy(strategy.address, sender=gov)


def test_migrate_strategy__with_no_debt(chain, gov, vault, strategy, create_strategy):
    new_strategy = create_strategy(vault)
    old_strategy = strategy
    old_strategy_params = vault.strategies(old_strategy)
    old_current_debt = old_strategy_params.currentDebt
    old_max_debt = old_strategy_params.maxDebt

    snapshot = chain.pending_timestamp
    tx = vault.migrateStrategy(new_strategy.address, old_strategy.address, sender=gov)
    event = list(tx.decode_logs(vault.StrategyMigrated))

    assert len(event) == 1
    assert event[0].old_strategy == old_strategy.address
    assert event[0].new_strategy == new_strategy.address

    new_strategy_params = vault.strategies(new_strategy)
    assert new_strategy_params.activation == snapshot
    assert new_strategy_params.currentDebt == old_current_debt
    assert new_strategy_params.maxDebt == old_max_debt

    old_strategy_params = vault.strategies(old_strategy)
    checks.check_revoked_strategy(old_strategy_params)


def test_migrate_strategy__with_existing_debt():
    # TODO: successfully migrate strategy with funds
    # implement when we can add debt to strategy
    return


def test_migrate_strategy__with_inactive_old_strategy__fails_with_error(
    gov, vault, create_strategy
):
    old_strategy = create_strategy(vault)
    new_strategy = create_strategy(vault)

    with ape.reverts("old strategy not active"):
        vault.migrateStrategy(new_strategy.address, old_strategy.address, sender=gov)


def test_migrate_strategy__with_incorrect_vault__fails_with_error(
    gov, asset, vault, strategy, create_strategy, create_vault
):
    old_strategy = strategy
    other_vault = create_vault(asset)
    new_strategy = create_strategy(other_vault)

    with ape.reverts("invalid vault"):
        vault.migrateStrategy(new_strategy.address, old_strategy.address, sender=gov)


def test_migrate_strategy__with_incorrect_asset__fails_with_error(
    gov, vault, strategy, mock_token, create_strategy, create_vault
):
    old_strategy = strategy
    other_vault = create_vault(mock_token)
    new_strategy = create_strategy(other_vault)

    with ape.reverts("invalid asset"):
        vault.migrateStrategy(new_strategy.address, old_strategy.address, sender=gov)


def test_migrate_strategy__with_active_new_strategy__fails_with_error(
    gov, vault, strategy, create_strategy
):
    old_strategy = strategy
    new_strategy = create_strategy(vault)

    # activate strategy
    vault.addStrategy(new_strategy.address, sender=gov)

    with ape.reverts("strategy already active"):
        vault.migrateStrategy(new_strategy.address, old_strategy.address, sender=gov)


def test_migrate_strategy__with_zero_address_new_strategy__fails_with_error(
    gov, vault, strategy
):
    old_strategy = strategy
    new_strategy = ZERO_ADDRESS

    with ape.reverts("strategy cannot be zero address"):
        vault.migrateStrategy(new_strategy, old_strategy.address, sender=gov)


@pytest.mark.parametrize("max_debt", [0, 10**22])
def test_update_max_debt__with_debt_value(gov, vault, strategy, max_debt):
    vault.updateMaxDebtForStrategy(strategy.address, max_debt, sender=gov)

    assert vault.strategies(strategy.address).maxDebt == max_debt
