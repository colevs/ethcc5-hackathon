import boa
from dataclasses import dataclass


@dataclass
class Info:
    deployer: str
    user: str
    tokens: [str]
    erc20_list: [object]
    erc4626_list: [object]
    pool: object
    lp_token: object


def setup():
    deployer = "0x0000000000000000000000000000000000001234"
    user = "0x0000000000000000000000000000000000001235"

    tokens = ["USDC", "ETH"]
    prepends = ["y", "a"]
    mint_quantity = 10 * 10**6 * 10**18  # 5 million

    initial_prices = [int(0.8 * 10**18)]

    erc20_list = [None] * len(tokens)
    erc4626_list = [None] * len(tokens)

    with boa.env.prank(deployer):
        for i in range(len(tokens)):
            erc20_list[i] = boa.load(
                "contracts/testing/ERC20Mock.vy", tokens[i], tokens[i], 18
            )
            vault_token = prepends[i] + tokens[i]
            erc4626_list[i] = boa.load(
                "contracts/testing/ERC4626Mock.vy",
                erc20_list[i].address,
                vault_token,
                vault_token,
                18,
            )

        for erc20 in erc20_list:
            erc20._mint_for_testing(user, mint_quantity)

    with boa.env.prank(user):
        for i in range(len(erc20_list)):
            erc20_list[i].approve(erc4626_list[i], 2**256 - 1)
            erc4626_list[i].deposit(int(mint_quantity * (3 / 4)))

    with boa.env.prank(deployer):
        lp_token = boa.load("contracts/CurveTokenV5.vy", "Curve EUR-USD", "crvEURUSD")

        pool = boa.load(
            "contracts/CurveCryptoSwap4626.vy",
            deployer,
            deployer,
            90 * 2**2 * 10000,  # A
            int(2.8e-4 * 1e18),  # gamma
            int(5e-4 * 1e10),  # mid_fee
            int(4e-3 * 1e10),  # out_fee
            10**10,  # allowed_extra_profit
            int(0.012 * 1e18),  # fee_gamma
            int(0.55e-5 * 1e18),  # adjustment_step
            0,  # admin_fee
            600,  # ma_half_time
            initial_prices[0],
            lp_token.address,
            [erc4626.address for erc4626 in erc4626_list],
        )

        lp_token.set_minter(pool.address)

    with boa.env.prank(user):
        for i in range(len(erc20_list)):
            erc4626_list[i].approve(pool, 2**256 - 1)
            erc20_list[i].approve(pool, 2**256 - 1)
        quantities = [mint_quantity // 2, mint_quantity // 2 // 5]
        pool.add_liquidity(quantities, 0)

    return Info(deployer, user, tokens, erc20_list, erc4626_list, pool, lp_token)
