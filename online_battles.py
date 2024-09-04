import asyncio
import sys

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
"""
------------------  ------------------  ------------------  ------------------
-                   SimpleHeuristics 1  EvaluateOrderPla 1  NoSwitchDamagePl 1
SimpleHeuristics 1                      0.4425              0.6575
EvaluateOrderPla 1  0.5575                                  0.6025
NoSwitchDamagePl 1  0.3425              0.3975
------------------  ------------------  ------------------  ------------------
grisha@Skinny-Legend pokemon-bots % 
"""
