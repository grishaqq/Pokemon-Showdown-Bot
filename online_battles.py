import asyncio
from poke_env import AccountConfiguration, ShowdownServerConfiguration
from evaluate_order_player import EvaluateOrderPlayer

my_account_config = AccountConfiguration("grishaqq_bot", "grishaqq_password")
player = EvaluateOrderPlayer(
    account_configuration=my_account_config,
    server_configuration=ShowdownServerConfiguration,
)


async def play():
    await player.ladder(100)


asyncio.run(play())
