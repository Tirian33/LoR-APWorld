import typing
from worlds.generic.Rules import set_rule, add_item_rule
from BaseClasses import CollectionState
from .locations import location_regions

#Which floor region maps to which librarian item
LIBRARIAN_ITEMS = [
    "Floor of History Librarian",
    "Floor of Technological Sciences Librarian",
    "Floor of Literature Librarian",
    "Floor of Art Librarian",
    "Floor of Natural Sciences Librarian",
    "Floor of Language Librarian",
    "Floor of Social Sciences Librarian",
    "Floor of Philosophy Librarian",
    "Floor of Religion Librarian"
]

#Progression of floor abno fights & requirements.
FLOOR_ABNOS: typing.Dict[str, list[tuple[str, str, str | None, int | None]]] = {
    "Floor of History": [
        ("Scorched Girl", "Happy Teddy Bear", None, None),
        ("Happy Teddy Bear", "Fairy Festival", "Floor of History Librarian", 1),
        ("Fairy Festival", "Queen Bee", "Floor of History Librarian", 2),
        ("Queen Bee", "Floor of History Final", None, None),
    ],

    "Floor of Technological Sciences": [
        ("Forsaken Murderer", "All-Around Helper", None, None),
        ("All-Around Helper", "Singing Machine", "Floor of Technological Sciences Librarian", 1),
        ("Singing Machine", "The Funeral of the Dead Butterflies", "Floor of Technological Sciences Librarian", 2),
        ("The Funeral of the Dead Butterflies", "Floor of Technological Sciences Final", None, None),
    ],

    "Floor of Literature": [
        ("Today's Shy Look", "The Red Shoes", None, None),
        ("The Red Shoes", "Spider Bud", "Floor of Literature Librarian", 1),
        ("Spider Bud", "Laetitia", "Floor of Literature Librarian", 2),
        ("Laetitia", "Floor of Literature Final", None, None),
    ],

    "Floor of Art": [
        ("Fragment of the Universe", "Child of the Galaxy", None, None),
        ("Child of the Galaxy", "Porccubus", "Floor of Art Librarian", 1),
        ("Porccubus", "Alriune", "Floor of Art Librarian", 2),
        ("Alriune", "Floor of Art Final", None, None),
    ],

    "Floor of Natural Sciences": [
        #("Menu", "The Queen of Hatred", "Floor of Natural Sciences Librarian", 1),
        ("The Queen of Hatred", "The Knight of Despair", "Floor of Natural Sciences Librarian", 2),
        ("The Knight of Despair", "The King of Greed", "Floor of Natural Sciences Librarian", 3),
        ("The King of Greed", "The Servant of Wrath", "Floor of Natural Sciences Librarian", 4),
        ("The Servant of Wrath", "Floor of Natural Sciences Final", None, None),
    ],

    "Floor of Language": [
        #("Menu", "Little Red Riding Hooded Mercenary", "Floor of Language Librarian", 1),
        ("Little Red Riding Hooded Mercenary", "Big and Will be Bad Wolf", "Floor of Language Librarian", 2),
        ("Big and Will be Bad Wolf", "Mountain of Smiling Bodies", "Floor of Language Librarian", 3),
        ("Mountain of Smiling Bodies", "Nosferatu", "Floor of Language Librarian", 4),
        ("Nosferatu", "Floor of Language Final", None, None),
    ],

    "Floor of Social Sciences": [
        #("Menu", "Scarecrow Searching for Wisdom", "Floor of Social Sciences Librarian", 1),
        ("Scarecrow Searching for Wisdom", "Warm-hearted Woodsman", "Floor of Social Sciences Librarian", 2),
        ("Warm-hearted Woodsman", "The Road Home & Scaredy Cat", "Floor of Social Sciences Librarian", 3),
        ("The Road Home & Scaredy Cat", "Ozma", "Floor of Social Sciences Librarian", 4),
        ("Ozma", "Floor of Social Sciences Final", None, None),
    ],

    "Floor of Philosophy": [
        #("Menu", "Big Bird", "Floor of Philosophy Librarian", 1),
        ("Big Bird", "Punishing Bird", "Floor of Philosophy Librarian", 2),
        ("Punishing Bird", "Judgement Bird", "Floor of Philosophy Librarian", 3),
        ("Judgement Bird", "Floor of Philosophy Final", "Binah", 1),
    ],

    "Floor of Religion": [
        #("Menu", "The Burrowing Heaven", "Floor of Religion Librarian", 1),
        ("The Burrowing Heaven", "The Price of Silence", "Floor of Religion Librarian", 2),
        ("The Price of Silence", "Blue Star", "Floor of Religion Librarian", 3),
        ("Blue Star", "Floor of Religion Final", "Floor of Religion Librarian", 4),
    ],

    "Floor of General Works": [
        ("Bloodbath", "Heart of Aspiration", None, None),
        ("Heart of Aspiration", "Pinocchio", "Floor of General Works Librarian", 1),
        ("Pinocchio", "The Snow Queen", "Floor of General Works Librarian", 2),
        ("The Snow Queen", "Keter Realization", "Floor of General Works Librarian", 4),
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

    #Logic chains on entrances
    for floor, abnos in FLOOR_ABNOS.items():
        for prev, targ, req, count in abnos:
            entrance = mw.get_entrance(f"{prev} to {targ}", player)
            prev_region = mw.get_region(prev, player)
            if req:
                set_rule(entrance, lambda state, p=prev_region, req=req, count=count: 
                         p.can_reach(state) and
                         state.count(req, player) >= count
                         )
            else:
                set_rule(entrance, lambda state, p=prev_region: 
                         p.can_reach(state)
                         )

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