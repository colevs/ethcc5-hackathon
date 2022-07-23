import boa

deployer = "0x0000000000000000000000000000000000001234"
user = "0x0000000000000000000000000000000000001235"

tokens = ["USD", "EUR"]
mint_quantity = 5 * 10**6 * 10**18  # 5 million

erc20_list = [None] * len(tokens)
erc4626_list = [None] * len(tokens)

with boa.env.prank(deployer):
    for i in range(len(tokens)):
        erc20_list[i] = boa.load("contracts/testing/ERC20Mock.vy", tokens[i], tokens[i], 18)
        erc4626_list[i] = boa.load("contracts/testing/ERC4626Mock.vy", erc20_list[i].address)
        
    for erc20 in erc20_list:
        erc20._mint_for_testing(user, mint_quantity)

with boa.env.prank(user):
    for i in range(len(erc20_list)):
        erc20_list[i].approve(erc4626_list[i], 2**256 - 1)
        erc4626_list[i].deposit(mint_quantity)