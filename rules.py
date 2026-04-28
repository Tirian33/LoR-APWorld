import typing
from worlds.generic.Rules import set_rule, add_item_rule
from BaseClasses import CollectionState
from .locations import location_regions

#Which floor region maps to which librarian item
REGION_LIBRARIAN_LINK: typing.Dict[str, str] = {
    "Floor of History Late":                "Floor of History Librarian",
    "Floor of Technological Sciences Late": "Floor of Technological Sciences Librarian",
    "Floor of Literature Late":             "Floor of Literature Librarian",
    "Floor of Art Late":                    "Floor of Art Librarian",
    "Floor of Natural Sciences Late":       "Floor of Natural Sciences Librarian",
    "Floor of Language Late":               "Floor of Language Librarian",
    "Floor of Social Sciences Late":        "Floor of Social Sciences Librarian",
    "Floor of Philosophy Late":             "Floor of Philosophy Librarian",
    "Floor of Religion":                    "Floor of Religion Librarian"
}

#Floors that need a special item in addition to librarian count
SPECIAL_FLOOR_ITEM: typing.Dict[str, str] = {
    "Floor of Philosophy Late": "Binah"
}

#Which floor region each ensemble check belongs to
ENSEMBLE_FLOOR: typing.Dict[str, str] = {
    "[Ensemble] The Crying Children":       "Floor of History Late",
    "[Ensemble] The Church of Gears":       "Floor of Technological Sciences Late",
    "[Ensemble] The Eighth Chef":           "Floor of Literature Late",
    "[Ensemble] The Musicians of Bremen":   "Floor of Art Late",
    "[Ensemble] The 8 o'Clock Circus":      "Floor of Natural Sciences Late",
    "[Ensemble] L'heure du Loup":           "Floor of Language Late",
    "[Ensemble] The Puppeteer":             "Floor of Social Sciences Late",
    "[Ensemble] The Blood-red Night":       "Floor of Philosophy Late",
    "[Ensemble] Yesterday's Promise":       "Floor of Religion",
    "[Ensemble] The Blue Reverberation":    "Floor of General Works",
}

LIBRARIAN_ITEMS = set(REGION_LIBRARIAN_LINK.values())

def set_rules(world) -> None:
    player = world.player
    mw = world.multiworld
    all_locations = {loc.name: loc for loc in mw.get_locations(player)}

    #Realization location rules - require 2 librarians to be in logic
    for floor, librarian in REGION_LIBRARIAN_LINK.items():
        for loc_name in location_regions[floor]:
            if "Realization" not in loc_name:
                continue
            loc = all_locations[loc_name]
            if floor in SPECIAL_FLOOR_ITEM:
                required_item = SPECIAL_FLOOR_ITEM[floor]
                set_rule(loc, lambda state, item=required_item, lib=librarian:
                    state.has(item, player) and state.count(lib, player) >= 2
                )
            else:
                set_rule(loc, lambda state, lib=librarian:
                    state.count(lib, player) >= 2
                )

    #Local helper to count completed realizations. Ensures all checks are done to handle cheat console 
    def floor_realizations_complete(state: CollectionState, floor: str) -> bool:
        return all(
            all_locations[loc_name].can_reach(state)
            for loc_name in location_regions[floor]
            if "Realization" in loc_name
        )

    #Ensemble in logic if floor realized; can be considered yellow otherwise. Some fights are possible with just the patron so...
    for loc_name in location_regions["Reverb Ensemble"]:
        #rm (N)
        ensemble_base = loc_name.rsplit("(", 1)[0].rstrip()
        if ensemble_base in ENSEMBLE_FLOOR:
            floor = ENSEMBLE_FLOOR[ensemble_base]
            set_rule(
                all_locations[loc_name], lambda state, f=floor: floor_realizations_complete(state, f)
            )

    
    #Local helper to count completed ensembles
    def ensemble_complete_count(state: CollectionState) -> int:
        return sum(
            1 for loc_name in location_regions["Reverb Ensemble"]
            if all_locations[loc_name].can_reach(state)
        )

    #Black Silence requires at least 2 ensemble checks complete. This ensure if player simply won the Keter ensemble fight. Again not needed, but helps discourage bks
    for loc_name in location_regions["Black Silence Reception"]:
        set_rule(
            all_locations[loc_name],lambda state: ensemble_complete_count(state) >= 2
        )