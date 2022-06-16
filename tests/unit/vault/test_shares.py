import ape
from utils import actions, checks
from utils.constants import MAX_INT, ZERO_ADDRESS


def test_deposit_with_invalid_recipient(user, asset, create_vault):
    vault = create_vault(asset)
    amount = 0

    with ape.reverts("invalid recipient"):
        vault.deposit(amount, vault, sender=user)
    with ape.reverts("invalid recipient"):
        vault.deposit(amount, ZERO_ADDRESS, sender=user)


def test_deposit_with_zero_funds(user, asset, create_vault):
    vault = create_vault(asset)
    amount = 0

    with ape.reverts("cannot deposit zero"):
        vault.deposit(amount, user, sender=user)


def test_deposit(user, asset, create_vault):
    vault = create_vault(asset)
    amount = 10**18

    balance = asset.balanceOf(user)
    actions.user_deposit(user, vault, asset, amount)

    assert vault.totalIdle() == amount
    assert vault.balanceOf(user) == amount
    assert vault.totalSupply() == amount
    assert asset.balanceOf(user) == (balance - amount)


def test_deposit_all(user, asset, create_vault):
    vault = create_vault(asset)
    balance = asset.balanceOf(user)

    asset.approve(vault, balance, sender=user)
    vault.deposit(MAX_INT, user, sender=user)

    assert vault.totalIdle() == balance
    assert vault.balanceOf(user) == balance
    assert vault.totalSupply() == balance
    assert asset.balanceOf(user) == 0


def test_withdraw(user, asset, create_vault):
    vault = create_vault(asset)
    amount = 10**18
    strategies = []

    balance = asset.balanceOf(user)
    actions.user_deposit(user, vault, asset, amount)

    vault.withdraw(amount, user, strategies, sender=user)
    checks.check_vault_empty(vault)
    assert asset.balanceOf(vault) == 0
    assert asset.balanceOf(user) == balance


def test_withdraw_with_insufficient_shares(user, asset, create_vault):
    vault = create_vault(asset)
    amount = 10**18
    strategies = []
    shares = amount + 1

    actions.user_deposit(user, vault, asset, amount)

    with ape.reverts("insufficient shares to withdraw"):
        vault.withdraw(shares, user, strategies, sender=user)


def test_withdraw_with_no_shares(user, asset, create_vault):
    vault = create_vault(asset)
    shares = 0
    strategies = []

    with ape.reverts("no shares to withdraw"):
        vault.withdraw(shares, user, strategies, sender=user)


def test_withdraw_all(user, asset, create_vault):
    vault = create_vault(asset)
    strategies = []

    balance = asset.balanceOf(user)
    actions.user_deposit(user, vault, asset, balance)

    vault.withdraw(MAX_INT, user, strategies, sender=user)

    checks.check_vault_empty(vault)
    assert asset.balanceOf(vault) == 0
    assert asset.balanceOf(user) == balance


def test_deposit_limit():
    # TODO: deposit limit tests
    pass
