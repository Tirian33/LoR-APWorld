import typing
from worlds.generic.Rules import set_rule, add_item_rule
from BaseClasses import CollectionState
from .locations import location_regions

#Which floor region maps to which librarian item
LIBRARIAN_ITEMS = {
    "Floor of History Librarian",
    "Floor of Technological Sciences Librarian",
    "Floor of Literature Librarian",
    "Floor of Art Librarian",
    "Floor of Natural Sciences Librarian",
    "Floor of Language Librarian",
    "Floor of Social Sciences Librarian",
    "Floor of Philosophy Librarian",
    "Floor of Religion Librarian"
}

#Progression of floor abno fights & requirements.
FLOOR_ABNOS: typing.Dict[str, list[tuple[str, str, str | None]]] = {
    "Floor of History": [
        ("Scorched Girl", "Happy Teddy Bear", None),
        ("Happy Teddy Bear", "Fairy Festival", None),
        ("Fairy Festival", "Queen Bee", "Floor of History Librarian"),
        ("Queen Bee", "Floor of History Final", None),
    ],

    "Floor of Technological Sciences": [
        ("Forsaken Murderer", "All-Around Helper", None),
        ("All-Around Helper", "Singing Machine", None),
        ("Singing Machine", "The Funeral of the Dead Butterflies", "Floor of Technological Sciences Librarian"),
        ("The Funeral of the Dead Butterflies", "Floor of Technological Sciences Final", None),
    ],

    "Floor of Literature": [
        ("Today's Shy Look", "The Red Shoes", None),
        ("The Red Shoes", "Spider Bud", None),
        ("Spider Bud", "Laetitia", "Floor of Literature Librarian"),
        ("Laetitia", "Floor of Literature Final", None),
    ],

    "Floor of Art": [
        ("Fragment of the Universe", "Child of the Galaxy", None),
        ("Child of the Galaxy", "Porccubus", None),
        ("Porccubus", "Alriune", "Floor of Art Librarian"),
        ("Alriune", "Floor of Art Final", None),
    ],

    "Floor of Natural Sciences": [
        ("The Queen of Hatred", "The Knight of Despair", None),
        ("The Knight of Despair", "The King of Greed", None),
        ("The King of Greed", "The Servant of Wrath", "Floor of Natural Sciences Librarian"),
        ("The Servant of Wrath", "Floor of Natural Sciences Final", None),
    ],

    "Floor of Language": [
        ("Little Red Riding Hooded Mercenary", "Big and Will be Bad Wolf", None),
        ("Big and Will be Bad Wolf", "Mountain of Smiling Bodies", None),
        ("Mountain of Smiling Bodies", "Nosferatu", "Floor of Language Librarian"),
        ("Nosferatu", "Floor of Language Final", None),
    ],

    "Floor of Social Sciences": [
        ("Scarecrow Searching for Wisdom", "Warm-hearted Woodsman", None),
        ("Warm-hearted Woodsman", "The Road Home & Scaredy Cat", None),
        ("The Road Home & Scaredy Cat", "Ozma", "Floor of Social Sciences Librarian"),
        ("Ozma", "Floor of Social Sciences Final", None),
    ],

    "Floor of Philosophy": [
        ("Big Bird", "Punishing Bird", "Floor of Philosophy Librarian"),
        ("Punishing Bird", "Judgement Bird", None),
        ("Judgement Bird", "Floor of Philosophy Final", "Binah"),
    ],

    "Floor of Religion": [
        ("The Burrowing Heaven", "The Price of Silence", None),
        ("The Price of Silence", "Blue Star", "Floor of Religion Librarian"),
        ("Blue Star", "Floor of Religion Final", None),
    ],

    "Floor of General Works": [
        ("Bloodbath", "Heart of Aspiration", None),
        ("Heart of Aspiration", "Pinocchio", None),
        ("Pinocchio", "The Snow Queen", None),
        ("The Snow Queen", "Keter Realization", "Floor of General Works Librarian"),
    ],
}

#Floors that need a special item in addition to librarian count
SPECIAL_FLOOR_ITEM: typing.Dict[str, str] = {
    "Floor of Philosophy Final": "Binah"
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

def set_rules(world) -> None:
    player = world.player
    mw = world.multiworld
    all_locations = {loc.name: loc for loc in mw.get_locations(player)}

    #Local helper to mark prereqs
    def region_complete(state: CollectionState, region_name: str) -> bool:
        return all(
            loc.can_reach(state) and loc.item and state.has(loc.item.name, player) 
            for loc in mw.get_region(region_name, player).locations
        )
    
    #Logic chains on entrances
    for floor, abnos in FLOOR_ABNOS.items():
        for prev, targ, req in abnos:
            entrance = mw.get_entrance(f"{prev} -> {targ}", player)
            if req == "Binah":
                set_rule(entrance, lambda state, p=prev, req=req: 
                         region_complete(state, p) and
                         state.count(req, player) >= 1)
            elif req:
                set_rule(entrance, lambda state, p=prev, req=req: 
                         region_complete(state, p) and
                         state.count(req, player) >= 2)
            else:
                set_rule(entrance, lambda state, p=prev: region_complete(state, p))

    #Local helper to count completed realizations. Ensures all checks are done to handle cheat console 
    def floor_realizations_complete(state: CollectionState, floor: str) -> bool:
        return all(
            all_locations[loc_name].can_reach(state)
            for loc_name in location_regions[floor]
            if "Realization" in loc_name
        )

    #Ensemble in logic if floor realized; can be considered yellow otherwise. Some fights are possible with just the patron so...
    for floor_name, chain in FLOOR_ABNOS.items():
        final_region = chain[-1][1]
        ensemble_region = f"[Ensemble] {floor_name.replace(' Final', '')}"
        for loc_name in location_regions[ensemble_region]:
            set_rule(
                all_locations[loc_name],
                lambda state, f=final_region: floor_realizations_complete(state, f)
            )

    
    #Local helper to count completed ensembles
    def ensemble_complete_count(state: CollectionState) -> int:
        return sum(
            1 for ensemble_name in FLOOR_ABNOS
             for loc_name in location_regions[f"[Ensemble] {ensemble_name}"]
            if all_locations[loc_name].can_reach(state)
        )

    for loc_name in location_regions["Black Silence Reception"]:
        set_rule(
            all_locations[loc_name],
            lambda state: ensemble_complete_count(state) >= 2
        )