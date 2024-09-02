from poke_env.environment.pokemon import Pokemon
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.battle import Battle
from poke_env.environment.status import Status
from poke_env.data.gen_data import GenData
from estimators import *
from help_functions import *
from copy import deepcopy
import json
from typing import Union


# ------------------------------------------------BATTLE-EVALUATORS--------------------------------------------------


"""
-----------UNUSED-/-TO-DO-------------
def evaluate_battle_score(battle: Battle, user: Pokemon, target: Pokemon) -> float:
    score = 0.0

    # Weather Evaluation
    # Terrain (Fields) Evaluation
    # Side Conditions
    
    return score

"""

# ------------------------------------------------STATUS-EVALUATORS--------------------------------------------------


def evaluate_boosts(
    battle: Battle, user: Pokemon, target: Pokemon, boost: dict[str, int]
):
    """evaluates boost dictionary, roughly in range (-1, 1), more beneficial the boost higher the score"""
    score = 0

    # Check Speed Boost
    if boost.get("spe", 0) != 0:
        current_speed = user.stats["spe"]
        target_speed = estimate_non_hp_stat(target, "spe")
        new_speed_multiplier = calculate_boost_change(
            user=user, stat_name="spe", stat_change=boost["spe"]
        )
        new_speed = current_speed * new_speed_multiplier
        if boost.get("spe", 0) > 0:
            if current_speed <= target_speed < new_speed:
                score += 0.35  # Boost will allow outspeeding the target
            elif current_speed <= target_speed:
                score += 0.17  # Boost may not make a difference in outspeeding, but still helpful
            else:
                score += 0.1  # Already outspeeding, but boost solidifies position
        elif boost.get("spe", 0) < 0:
            if current_speed > target_speed >= new_speed:
                score -= 0.35  # Speed drop allows the target to outspeed
            elif new_speed > target_speed:
                score -= 0.17  # Speed drop won't cause underspeeding, but still a negative impact
            else:
                score -= 0.1  # Already underspeeding, speed drop doesn't change the situation significantly

    # Check Attack Boost
    if boost.get("atk", 0) != 0:
        score += (
            sign(boost["atk"])
            * 0.3
            * (0.6 ** max(user.boosts.get("atk", 0), 0))
            * is_physical_attacker(user)
            * stat_boost_geom(abs(boost["atk"]))
        )  # Adds points for attack boosts with geometric series for multiple boost

    # Check Special Attack Boost
    if boost.get("spa", 0) != 0:
        score += (
            sign(boost["spa"])
            * 0.3
            * (0.6 ** max(user.boosts.get("spa", 0), 0))
            * is_special_attacker(user)
            * stat_boost_geom(abs(boost["spa"]))
        )  # Adds points for special attack boosts with geometric series for multiple boost

    # Check Defense Boost
    if boost.get("def", 0) != 0:
        if is_physical_attacker(target) >= 0.5:  # Target is likely a physical attacker
            # Adds points for defense boosts (geometric series)
            score += (
                (0.6 ** max(user.boosts.get("def", 0), 0))
                * sign(boost["def"])
                * 0.3
                * stat_boost_geom(abs(boost["def"]))
            )  # Adds more points if target is physical attacker
        else:
            score += (
                (0.6 ** max(user.boosts.get("def", 0), 0))
                * sign(boost["def"])
                * 0.15
                * stat_boost_geom(abs(boost["def"]))
            )  # Adds less points if target is physical attacker

    # Check Special Defense Boost
    if boost.get("spd", 0) != 0:
        if is_special_attacker(target) >= 0.5:  # Target is a special attacker
            # Adds points for special defense boosts (geometric series)
            score += (
                (0.6 ** max(user.boosts.get("spd", 0), 0))
                * sign(boost["spd"])
                * 0.3
                * stat_boost_geom(abs(boost["spd"]))
            )  # Adds more points if target is special attacker
        else:
            score += (
                (0.6 ** max(user.boosts.get("spd", 0), 0))
                * sign(boost["spd"])
                * 0.15
                * stat_boost_geom(abs(boost["spd"]))
            )  # Adds less points if target is special attacker

    return score


def evaluate_status_move(battle: Battle, user: Pokemon, target: Pokemon, move: Move):
    """gives a score in range (0, 1) to a status move"""
    if move.category != MoveCategory.STATUS:
        return 0
    score = 0

    # status !!!
    if move.status != None:
        score += evaluate_pseudo_target_status(target, move.status)

    # move.boosts !!
    if move.boosts != None:
        score += evaluate_boosts(battle, user, target, move.boosts)

    # weather !
    # terrain !
    if move.weather != None:
        pass

    # sleep_usable
    if move.id == "sleeptalk" and user.status == Status.SLP and user.status_counter < 2:
        score += 1

    # heal !
    score += min(move.heal, 1 - user.current_hp_fraction)

    # hazards + weather + terrain :(
    return score


def evaluate_user_status(user: Pokemon):
    """gives higher score to more beneficial status, range (-0.7, 0.7)"""
    if user.status == None:
        return 0

    # guts ability!
    guts_flag = user.ability == "guts" or (
        user.ability == None and "guts" in user.possible_abilities
    )
    if guts_flag and user.status == Status.BRN:
        return 0.7
    if guts_flag and user.status == Status.PSN:
        return 0.6
    if guts_flag and user.status == Status.TOX:
        return 0.5
    if guts_flag and user.status == Status.PAR:
        # assuming slowest pokemon has speed around 100 and fastest around 300
        # returns 0 for fastest, returns 0.4 for slowest, linearly in between for others
        return 0.4 * (300 - estimate_non_hp_stat(user, "spe")) / 200

    # BRN - physical/ special split
    # number of special moves/ total number of attacking moves - 0.5
    # returns 0.5 for total special attacker, -0.5 for total physical attacker, linearly in between for others
    if user.status == Status.BRN:
        return is_special_attacker(user=user) - 0.5

    # FRZ
    if user.status == Status.FRZ:
        return -0.7

    # PAR - slow/fast split
    if user.status == Status.PAR:
        # assuming slowest pokemon has speed around 100 and fastest around 300
        # returns -0.2 for slowest, returns -0.6 for fastest, linearly in between for others
        return 0.6 * (-estimate_non_hp_stat(user, "spe")) / 300
    # PSN
    if user.status == Status.PSN:
        return -0.2
    # SLP
    if user.status == Status.SLP:
        return -0.6
    # TOX
    if user.status == Status.TOX:
        return -0.3

    return 0


def evaluate_pseudo_target_status(target: Pokemon, pseudo_status: Status):
    """gives higher score to more disadvantageous status for target, range (-0.7, 0.7)"""
    if target.status != None:
        return 0.0
    pseudo_target = deepcopy(target)
    pseudo_target.status = pseudo_status
    return -evaluate_user_status(pseudo_target)


# ---------------------------------------------------SWITCH-EVALUATORS--------------------------------------------------


"""
-----------UNUSED-----------

def evaluate_switch_chance(battle: Battle, user: Pokemon, target: Pokemon):
    # range (0, 1)
    # check (estimate_outspeed_ko_chance with ___) and then how bad is the matchup
    pass
    

"""


def evaluate_defense_score(attack_multiplier):
    """gives higher score for more beneficial attack_multiplier(type effectiveness against user), range (-2, 0.5)"""
    eps = 0.01
    if abs(attack_multiplier - 0) < eps:
        return 0.5
    if abs(attack_multiplier - 0.25) < eps:
        return 0.3
    if abs(attack_multiplier - 0.5) < eps:
        return 0.1
    if abs(attack_multiplier - 1) < eps:
        return -0.4
    if abs(attack_multiplier - 2) < eps:
        return -1
    if abs(attack_multiplier - 4) < eps:
        return -2
    return 0


def evaluate_switch(user: Pokemon, switch: Pokemon, target: Pokemon, battle: Battle):
    """gives higher score to better switches, range roughly (0, 1)"""
    # check (each) type effectiveness of target against switch, targets known moves,
    # check switch moves effectiveness

    max_switch_damage_move = max(
        switch.moves.values(),
        key=lambda move: estimate_damage(
            user=switch, target=target, move=move, battle=battle
        ),
    )

    # score representing how well potential switch can hit target, range (0, 1)
    attack_score = estimate_damage(
        user=switch, target=target, move=max_switch_damage_move, battle=battle
    ) / estimate_hp_stat(target)

    # score representing how well potential switch can defend against target, range roughly (, )
    defense_score = 0
    target_type1_attack_multiplier = target.type_1.damage_multiplier(
        type_1=switch.type_1,
        type_2=switch.type_2,
        type_chart=GenData.from_gen(GEN).type_chart,
    )
    defense_score += evaluate_defense_score(target_type1_attack_multiplier)
    if target.type_2 != None:
        target_type2_attack_multiplier = target.type_2.damage_multiplier(
            type_1=switch.type_1,
            type_2=switch.type_2,
            type_chart=GenData.from_gen(GEN).type_chart,
        )
        defense_score += evaluate_defense_score(target_type2_attack_multiplier)
        defense_score *= 0.9  # to make more comparable to one type targets

    # evaluates target known moves and updates defense_score
    if target.moves:
        max_target_damage_move = max(
            target.moves.values(),
            key=lambda move: estimate_damage(
                user=target, target=switch, move=move, battle=battle
            ),
        )
        known_moves_score = -estimate_damage(
            user=target, target=switch, move=max_target_damage_move, battle=battle
        ) / (2 * switch.max_hp)
        defense_score += known_moves_score
    else:
        known_moves_score = -0.15
        defense_score += known_moves_score

    # evaluates target possible moves and updates defense_score
    possible_moves = []
    #./pokemon-showdown/data/random-battles/gen9/
    pokemon_sets_file_path = "sets.json"
    with open(pokemon_sets_file_path, "r") as file:
        data = json.load(file)
        for possible_set in data.get(target.base_species, {}).get("sets", []):
            possible_moves.extend(
                map(
                    lambda move_name: Move(json_convert_name(move_name), gen=GEN),
                    possible_set["movepool"],
                )
            )
    if possible_moves:
        max_possible_target_damage_move = max(
            possible_moves,
            key=lambda move: estimate_damage(
                user=target, target=switch, move=move, battle=battle
            ),
        )
        defense_score -= estimate_damage(
            user=target,
            target=switch,
            move=max_possible_target_damage_move,
            battle=battle,
        ) / (2 * switch.max_hp)
    else:
        defense_score += known_moves_score

    # score representing if potential switch outspeeds target
    speed_score = (
        0.5 if switch.stats["spe"] > estimate_non_hp_stat(target, "spe") else -0.5
    )

    # score representing boosts that will be lost if we chose to switch
    # negative when user has positive boosts, positive when has negative boosts, range rougly (-1, 1)
    pseudo_no_boosts_user = deepcopy(user)
    pseudo_no_boosts_user.boosts = {}
    boosts_score = -evaluate_boosts(battle, pseudo_no_boosts_user, target, user.boosts)

    # score representing if we want to sacrifice user (lower the score less likely to switch), range (-1, 0)
    # 0 for users with hp >= 50%, -1 when hp is close to 0%, linearly in between for others
    sacrifice_score = min(2 * user.current_hp_fraction - 1.0, 0.0)

    return (
        attack_score
        + defense_score
        + sacrifice_score
        + switch.current_hp_fraction
        + evaluate_user_status(switch)
        + speed_score
        + boosts_score
    ) / 3


def best_switch(user: Pokemon, target: Pokemon, battle: Battle):
    """returns best switch for current battle"""
    return max(
        battle.available_switches,
        key=lambda sw: evaluate_switch(user, sw, target, battle),
    )


# ---------------------------------------------------ATTACK-EVALUATORS--------------------------------------------------


def evaluate_attacking_move(battle: Battle, user: Pokemon, target: Pokemon, move: Move):
    """gives higher score for more beneficial attack, range roughly (0, 1)"""

    if move.id == "recharge" or move.id == "focuspunch":
        return 0
    if move.category == MoveCategory.STATUS:
        return 0

    # calculate maximum damage output from all available pokemon
    max_damage_all = max(
        map(
            lambda move: estimate_damage(user, target, move, battle),
            user.moves.values(),
        )
    )

    for sw in battle.available_switches:
        max_damage_sw = max(
            map(
                lambda move: estimate_damage(sw, target, move, battle),
                sw.moves.values(),
            )
        )
        max_damage_all = max(max_damage_all, max_damage_sw)

    # create this variable to avoid situations where user never chooses attacking move because target is too bulky
    # max statement for situations when all moves are non-damage (very rare)
    max_comparable_damage = max(
        min(estimate_hp_stat(target), max_damage_all), estimate_hp_stat(target) / 4
    )

    score = (
        estimate_damage_no_accuracy(battle, user, target, move)
        * move.accuracy
        * move.expected_hits
    ) / max_comparable_damage
    # used to be divided by estimate_hp_stat(target)

    # multiple-hit move
    score += 0.04 if move.expected_hits > 1 else 0

    # secondary_effect
    for secondary_effect in move.secondary:
        if "status" in secondary_effect:
            score += (
                secondary_effect["chance"]
                / 100
                * evaluate_pseudo_target_status(target, secondary_effect["status"])
            )

        if "boosts" in secondary_effect:
            score += (
                secondary_effect["chance"]
                / 100
                * evaluate_boosts(battle, user, target, secondary_effect["boosts"])
            )

    # breaks protect
    score += 0.04 if move.breaks_protect else 0

    # crit ratio / move.crit_ratio is in range [0, 6]
    score += move.crit_ratio / 12

    # fixed damages (like seismic toss)
    if isinstance(move.damage, int):
        score += move.damage / max_comparable_damage
    elif move.damage == "level":
        score += user.level / max_comparable_damage

    switch_moves = ["uturn", "voltswitch", "flipturn", "partingshot", "batonpass"]
    if move in switch_moves:
        score *= (
            evaluate_switch(user, best_switch(user, target, battle), target, battle)
            + 0.3
        ) ** 2

    # priority moves
    if move.priority > 0 and is_slower(user, target):
        score *= 1.5
    elif move.priority > 0:
        score *= 1.15

    # if ko's target
    if estimate_outspeed_ko_chance(user, target, move, battle) >= 0.9:
        score *= 1.7

    # recoil
    score -= score * move.recoil

    return score


# ---------------------------------------------------ORDER-EVALUATORS--------------------------------------------------


def evaluate_order(
    battle: Battle, user: Pokemon, target: Pokemon, order: Union[Move, Pokemon]
):
    """returns a score to the order(either move or switch pokemon), roughly in range (0, 1)"""
    if isinstance(order, Move):
        if order.category == MoveCategory.STATUS:
            return evaluate_status_move(battle, user, target, order)
        else:
            return evaluate_attacking_move(battle, user, target, order)
    if isinstance(order, Pokemon):
        return evaluate_switch(user, order, target, battle)
