from poke_env import Player
from estimators import *


class NoSwitchDamagePlayer(Player):
    def choose_move(self, battle):
        if battle.available_moves:
            user = battle.all_active_pokemons[0]
            target = battle.all_active_pokemons[1]
            best_move = max(
                battle.available_moves,
                key=lambda move: estimate_damage(
                    user=user, target=target, move=move, battle=battle
                ),
            )
            if battle.can_tera and user.tera_type == best_move.type:
                return self.create_order(best_move, terastallize=True)
            return self.create_order(best_move)
        return self.choose_random_move(battle)
