from poke_env.environment.pokemon import Pokemon
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.battle import Battle
from poke_env.environment.status import Status

from help_functions import *

EV_TOTAL = 510
EV_AVG = EV_TOTAL / 6
IV_MAX = 31
RANDOM_FACTOR = 0.85
GEN = 9


def estimate_damage_range(user: Pokemon, target: Pokemon, move: Move, battle: Battle):
    """returns a tuple of least damage and most damage user can hit on a target"""
    max_damage = estimate_damage_no_accuracy(
        user=user, target=target, move=move, battle=battle
    )
    return (RANDOM_FACTOR * max_damage, max_damage)


def estimate_hp_stat(user):
    """estimates hp of user"""
    base_stat = user.base_stats["hp"]
    level = user.level
    return int((2 * base_stat + IV_MAX + EV_AVG / 4) * level / 100) + level + 10


def estimate_non_hp_stat(user, stat_name):
    """estimates non hp stat of user"""
    base_stat = user.base_stats[stat_name]
    level = user.level
    return int(
        (int((2 * base_stat + IV_MAX + EV_AVG / 4) * level / 100) + 5)
        * calculate_boost_change(user, stat_name, user.boosts.get(stat_name, 0))
    )


def is_slower(user, target):
    """returns true if user is slower, false otherwise"""
    return estimate_non_hp_stat(user, "spe") < estimate_non_hp_stat(target, "spe")
    # return user.base_stats["spe"] < target.base_stats["spe"]


def estimate_damage_no_accuracy(
    battle: Battle, user: Pokemon, target: Pokemon, move: Move
):
    """estimates maximum damage user can hit on a target without checking accuracy and number of expected hits"""
    if move.category == MoveCategory.STATUS:  # Status move
        return 0
    chosen_attack_stat = estimate_non_hp_stat(user, "atk")
    chosen_defense_stat = estimate_non_hp_stat(target, "def")

    if move.category == MoveCategory.SPECIAL:  # if move is Special instead of Physical
        chosen_attack_stat = estimate_non_hp_stat(user, "spa")
        chosen_defense_stat = estimate_non_hp_stat(target, "spd")

    no_multipliers_damage = (
        (2 * user.level / 5 + 2)
        * move.base_power
        * chosen_attack_stat
        / chosen_defense_stat
    ) / 50 + 2

    weather_multiplier = calculate_weather_multiplier(move, battle)

    stab_multiplier = 1.5 if user.type_1 == move.type or user.type_2 == move.type else 1

    type_effectiveness_multiplier = calculate_effectiveness_multiplier(
        move=move, target=target
    )

    burn_multiplier = (
        0.5
        if move.category == MoveCategory.PHYSICAL
        and user.status == Status.BRN
        and user.ability != "guts"
        else 1
    )

    multipliers = (
        weather_multiplier
        * stab_multiplier
        * type_effectiveness_multiplier
        * burn_multiplier
    )

    return no_multipliers_damage * multipliers


def estimate_damage(user: Pokemon, target: Pokemon, move: Move, battle: Battle):
    """estimates maximum damage user can hit on a target (multiplied by accuracy)"""
    return (
        estimate_damage_no_accuracy(user=user, target=target, move=move, battle=battle)
        * move.accuracy
        * move.expected_hits
    )


def estimate_outspeed_ko_chance(
    user: Pokemon, target: Pokemon, move: Move, battle: Battle
):
    """estimates a chances to outspeed and KO the target"""
    user_speed = user.stats["spe"]
    target_speed = estimate_non_hp_stat(target, "spe")

    if target_speed > user_speed:
        return 0

    min_damage, max_damage = estimate_damage_range(
        user=user, target=target, move=move, battle=battle
    )
    # hp
    target_hp_left = round(target.current_hp_fraction * estimate_hp_stat(user))

    if max_damage < target_hp_left:
        return 0
    if min_damage >= target_hp_left:
        return move.accuracy
    return (max_damage - target_hp_left) / (max_damage - min_damage) * move.accuracy
