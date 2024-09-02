from poke_env.player import Player
from estimators import *
from evaluators import *


class EvaluateOrderPlayer(Player):
    def choose_move(self, battle):
        user = battle.all_active_pokemons[0]
        target = battle.all_active_pokemons[1]
        available_orders = battle.available_moves + battle.available_switches
        if available_orders:
            best_move = max(
                available_orders,
                key=lambda order: evaluate_order(battle, user, target, order),
            )
            """print(f"{user} {target}")
            for order in available_orders:
                print(order, evaluate_order(battle, user, target, order))
            print()"""
            return self.create_order(best_move)
        return self.choose_random_move(battle)
