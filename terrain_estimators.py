"""
-----------UNUSED-----------


from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.weather import Weather

weather_associated_function = {
    Weather.RAINDANCE: is_water_associated,
    Weather.SUNNYDAY: is_fire_associated,
    Weather.
}



def is_type_associated(user: Pokemon, type_needed: PokemonType):
    #help function for checking whether user is aligned with given type
    score = 0.0

    # Increase score if the Pokémon is type_needed
    if type_needed in user.types:
        score += 0.3

    # Increase score based on type_needed moves
    stab_moves = [move for move in user.moves.values() if move.type == type_needed]
    if stab_moves:
        score += 0.3

    return score


def is_ability_type_associated(user: Pokemon, abilities: dict[str]):
    #help function for checking whether user's ability is type-associated ability
    return 0.4 if user.ability in abilities else 0


def is_important_move_type_associated(user: Pokemon, important_moves: dict[str]):
    #help function for checking whether user has one of important moves associated with given type
    for move in user.moves:
        if move.id in important_moves:
            return 0.1  # Additional boost for important moves
    return 0


def is_water_associated(user: Pokemon):

    score = is_type_associated(user, PokemonType.WATER)

    # Increase score based on specific abilities associated with Water
    score += is_ability_type_associated(
        user, {"dryskin", "forecast", "hydration", "raindish", "swiftswim"}
    )

    return score


def is_fire_associated(user: Pokemon) -> float:

    score = is_type_associated(user, PokemonType.FIRE)

    # Increase score based on specific abilities associated with Fire
    score += is_ability_type_associated(
        user,
        {
            "chlorophyll",
            "flowergift",
            "forecast",
            "leafguard",
            "solarpower",
            "protosynthesis",
            "orichalcumpulse",
        },
    )

    return score


def is_electric_associated(user: Pokemon):

    score = is_type_associated(user, PokemonType.ELECTRIC)

    # Increase score based on specific Electric-related abilities
    score += is_ability_type_associated(
        user, {"surgesurfer", "quarkdrive", "hadronengine"}
    )

    # Increase score based on the presence of Electric Seed item
    if user.item == "electricseed":
        score += 0.15

    # Increase score based on Electric-related moves like Rising Voltage and Terrain Pulse
    score += is_important_move_type_associated(user, {"risingvoltage", "terrainpulse"})

    return score


def is_grass_associated(user: Pokemon) -> float:
    score = is_type_associated(user, PokemonType.GRASS)

    # Increase score based on specific Electric-related abilities
    score += is_ability_type_associated(user, {"grasspelt"})

    # Increase score based on the presence of Grassy Seed item
    if user.item == "grassyseed":
        score += 0.15

    # Increase score based on important Grass-type moves
    score += is_important_move_type_associated(user, {"grassyglide", "floralhealing"})

    return score


def is_psychic_associated(user: Pokemon) -> float:

    score = is_type_associated(user, PokemonType.PSYCHIC)

    if user.item == "psychicseed":
        score += 0.15

    # Increase score based on important Psychic-type moves
    score += is_important_move_type_associated(user, {"expandingforce", "terrainpulse"})

    return score

"""
