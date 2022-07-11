from ape import chain


# placeholder tests for test mocks
def test_liquid_strategy__with_fee(gov, asset, vault, create_strategy, airdrop_asset):
    strategy = create_strategy(vault)
    amount = 10**18

    airdrop_asset(gov, asset, strategy, amount)

    assert asset.balanceOf(strategy) == amount
    assert strategy.withdrawable() == amount


def test_locked_strategy__with_locked_asset(
    gov, asset, chain, vault, create_locked_strategy, airdrop_asset
):
    strategy = create_locked_strategy(vault)
    amount = 10 * 10**18
    locked_amount = 10**18

    airdrop_asset(gov, asset, strategy, amount)
    assert asset.balanceOf(strategy) == amount
    assert strategy.withdrawable() == amount

    # lock funds for one day
    strategy.setLockedFunds(locked_amount, 3600 * 24, sender=gov)
    unlocked = amount - locked_amount
    assert strategy.withdrawable() == unlocked

    # check lock after half day
    chain.pending_timestamp += 3600 * 12
    strategy.freeLockedFunds(sender=gov)
    assert strategy.withdrawable() == unlocked

    # check lock after full day
    chain.pending_timestamp += 3600 * 12
    strategy.freeLockedFunds(sender=gov)
    assert strategy.withdrawable() == amount

    # test can lock again
    strategy.setLockedFunds(locked_amount, 3600 * 24, sender=gov)
    unlocked = amount - locked_amount
    assert strategy.withdrawable() == unlocked


def test_lossy_strategy__with_multiple_losses(
    gov, fish, asset, vault, create_lossy_strategy, airdrop_asset
):
    strategy = create_lossy_strategy(vault)
    amount = 10 * 10**18
    loss = 10**18

    airdrop_asset(gov, asset, strategy, amount)
    assert asset.balanceOf(strategy) == amount
    assert strategy.withdrawable() == amount

    strategy.setLoss(fish.address, loss, sender=gov)
    initial_loss = amount - loss
    assert asset.balanceOf(strategy) == initial_loss
    assert strategy.withdrawable() == initial_loss

    strategy.setLoss(fish.address, loss, sender=gov)
    secondary_loss = initial_loss - loss
    assert asset.balanceOf(strategy) == secondary_loss
    assert strategy.withdrawable() == secondary_loss
