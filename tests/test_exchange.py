import pytest
import ape
import random

SAMPLES = 20

i_min = 0
i_max = 2

j_min = 0
j_max = 2

amount_min = 10**6
amount_max = 2 * 10**6 * 10**18


def test_exchange(initial_prices, crypto_swap_with_deposit, token, coins, coins_underlying, accounts):
    for sample in range(SAMPLES):
        amount = random.randint(amount_min, amount_max)

        for i in range(i_min, i_max + 1):
            for j in range(j_min, j_max + 1):

                user = accounts[1]

                if i == j or i > 1 or j > 1:
                    with ape.reverts():
                        crypto_swap_with_deposit.get_dy(i, j, 10**6)
                    with ape.reverts():
                        crypto_swap_with_deposit.exchange(i, j, 10**6, 0, sender=user)

                else:
                    prices = [10**18] + initial_prices
                    amount = amount * 10**18 // prices[i]
                    coins_underlying[i]._mint_for_testing(user, amount, sender=accounts[0])
                    coins_underlying[i].approve(coins[i], 2**256 - 1, sender=user)
                    coins[i].deposit(amount, sender=user)

                    calculated = crypto_swap_with_deposit.get_dy(i, j, amount)
                    measured_i = coins[i].balanceOf(user)
                    measured_j = coins[j].balanceOf(user)
                    d_balance_i = crypto_swap_with_deposit.balances(i)
                    d_balance_j = crypto_swap_with_deposit.balances(j)

                    crypto_swap_with_deposit.exchange(
                        i, j, amount, int(0.999 * calculated), sender=user
                    )

                    measured_i -= coins[i].balanceOf(user)
                    measured_j = coins[j].balanceOf(user) - measured_j
                    d_balance_i = crypto_swap_with_deposit.balances(i) - d_balance_i
                    d_balance_j = crypto_swap_with_deposit.balances(j) - d_balance_j

                    assert amount == measured_i
                    assert calculated == measured_j

                    assert d_balance_i == amount
                    assert -d_balance_j == measured_j
