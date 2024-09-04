import asyncio
from poke_env.player.random_player import RandomPlayer
from no_switch_damage_player import NoSwitchDamagePlayer
from evaluate_order_player import EvaluateOrderPlayer
from poke_env.player.baselines import SimpleHeuristicsPlayer
from poke_env.player import RandomPlayer
from poke_env import cross_evaluate
from tabulate import tabulate


sh_player = SimpleHeuristicsPlayer()
eo_player = EvaluateOrderPlayer()
random_player = RandomPlayer()
nsd_player = NoSwitchDamagePlayer()
players = [sh_player, eo_player, nsd_player]


async def cross_evaluation_function():
    return await cross_evaluate(players, n_challenges=400)


cross_evaluation = asyncio.run(cross_evaluation_function())

table = [["-"] + [p.username for p in players]]
for p_1, results in cross_evaluation.items():
    table.append([p_1] + [cross_evaluation[p_1][p_2] for p_2 in results])

print(tabulate(table))

"""

------------------  ------------------  ------------------  ------------------
-                   SimpleHeuristics 1  EvaluateOrderPla 1  NoSwitchDamagePl 1
SimpleHeuristics 1                      0.3875              0.655
EvaluateOrderPla 1  0.6125                                  0.7225
NoSwitchDamagePl 1  0.345               0.2775
------------------  ------------------  ------------------  ------------------

Table above was printed after each pair of bots played 400 battles
"""


"""
async def go():
    await first_player.battle_against(second_player, n_battles=1)

asyncio.run(go())

print(
    f"Player {first_player.username} won {first_player.n_won_battles} out of {first_player.n_finished_battles} played against {second_player.username}"
)
"""
