from poke_env.environment.pokemon import Pokemon
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.battle import Battle
from poke_env.environment.weather import Weather
from poke_env.data.gen_data import GenData

GEOM_R = 0.4


def count_move_category(user: Pokemon, category_needed: MoveCategory):
    """counts number of moves of certain category"""
    count = 0
    for move in user.moves.values():
        if move.category == category_needed:
            count += 1
    return count


def is_physical_attacker(user: Pokemon):
    """returns value closer to 1 if physical attacker, 0 otherwise"""
    special_move_cnt = count_move_category(
        user=user, category_needed=MoveCategory.SPECIAL
    )
    physical_move_cnt = count_move_category(
        user=user, category_needed=MoveCategory.PHYSICAL
    )
    if special_move_cnt + physical_move_cnt == 0:
        return 1.0 if user.base_stats["atk"] > user.base_stats["spa"] else 0.0
    return physical_move_cnt / (special_move_cnt + physical_move_cnt)


def is_special_attacker(user: Pokemon):
    """returns value closer to 1 if special attacker, 0 otherwise"""
    special_move_cnt = count_move_category(
        user=user, category_needed=MoveCategory.SPECIAL
    )
    physical_move_cnt = count_move_category(
        user=user, category_needed=MoveCategory.PHYSICAL
    )
    if special_move_cnt + physical_move_cnt == 0:
        return 1.0 if user.base_stats["spa"] > user.base_stats["atk"] else 0.0
    return special_move_cnt / (special_move_cnt + physical_move_cnt)


def calculate_weather_multiplier(move: Move, battle: Battle):
    """returns weather damage multiplier for a given move in the battle"""
    if (
        Weather.RAINDANCE in battle.weather.keys() and move.type == PokemonType.WATER
    ) or (
        Weather.SUNNYDAY in battle.weather.keys()
        and (move.type == PokemonType.FIRE or move.id == "hydrosteam")
    ):
        return 1.5
    if (
        Weather.RAINDANCE in battle.weather.keys() and move.type == PokemonType.FIRE
    ) or (Weather.SUNNYDAY in battle.weather.keys() and move.type == PokemonType.WATER):
        return 0.5
    return 1.0


def calculate_effectiveness_multiplier(move: Move, target: Pokemon):
    """returns effectiveness multiplier / build-in method doesn't account for terastallized pokemon"""
    if not target.terastallized:
        return target.damage_multiplier(move)
    return move.type.damage_multiplier(
        type_1=target.tera_type, type_2=None, type_chart=GenData.from_gen(9).type_chart
    )


def calculate_boost_change(user: Pokemon, stat_name: str, stat_change: int):
    """returns by how much stat is changed"""
    stage_before = user.boosts.get(stat_name, 0)
    stage_after = max(min(user.boosts.get(stat_name, 0) + stat_change, 6), -6)
    multiplier_after = (
        (2 + stage_after) / 2 if stage_after >= 0 else 2 / (2 - stage_after)
    )
    multiplier_before = (
        (2 + stage_before) / 2 if stage_before >= 0 else 2 / (2 - stage_before)
    )
    return multiplier_after / multiplier_before


def stat_boost_geom(stat_change):
    """returns multiplier to a boost, using geometric series for multiple stage boost"""
    return (1 - GEOM_R**stat_change) / (1 - GEOM_R)


def sign(x):
    """returns sign of the number, 0 if 0"""
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0


def json_convert_name(s):
    """converts pokemon names from json format to showdown format"""
    return s.lower().replace(" ", "").replace("-", "")
