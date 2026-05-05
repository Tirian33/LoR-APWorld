import typing
import random
from .options import LOROptions
from .items import LORItem, item_table
from .locations import ALWAYS_ACCESSIBLE_REGIONS, HIGHER_START_ABNOS, LORLocation, location_table, location_regions, location_name_to_data
from .rules import FLOOR_ABNOS, LIBRARIAN_ITEMS, set_rules
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import add_item_rule, set_rule
from BaseClasses import Entrance, ItemClassification, Region, Tutorial, CollectionState

from Utils import visualize_regions

class LORWebWorld(WebWorld):
    theme = "grass"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Library of Ruina with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["fragger"]
    )]

class LORWorld(World):
    game = "Library of Ruina"  # name of the game/world
    options_dataclass = LOROptions  # options the player can set
    options: LOROptions  # typing hints for option results
    topology_present = True  # show path to required location checks in spoiler

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    item_name_groups = { 
        "Floor": {name for name, data in item_table.items() if data.category == "Floor"},
        "AbnoPages": {name for name, data in item_table.items() if data.category == "AbnoPages"},
        "Librarians": {name for name, data in item_table.items() if data.category == "Librarian"},
        "EGOPage": {name for name, data in item_table.items() if data.category == "EGOPage"},
        "Receptions": {name for name, data in item_table.items() if data.category == "Reception"},
        "Progression": {name for name, data in item_table.items() if data.category == "Progression"},
    }
    location_name_to_id = {data.name: data.address for data in location_table}

    def generate_early(self) -> None:
        #Shove 2 copies of each librarian in sphere 1
        for librarian in LIBRARIAN_ITEMS:
            self.multiworld.local_early_items[self.player][librarian] = 2

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        #Build a Region object based on the region division in locations.py
        regions: typing.Dict[str, Region] = {}
        for region_name, loc_names in location_regions.items():
            region = Region(region_name, self.player, self.multiworld)
            for loc_name in loc_names:
                loc_data = location_name_to_data[loc_name]
                region.locations.append(
                    LORLocation(self.player, loc_data.name, loc_data.address, region)
                )
            self.multiworld.regions.append(region)
            regions[region_name] = region

        #Always available encounters
        for region_name in ALWAYS_ACCESSIBLE_REGIONS:
            menu_region.connect(regions[region_name], f"Menu to {region_name}")

        #Starting abno fights that require libs
        for pos, region_name in enumerate(HIGHER_START_ABNOS):
            entrance = menu_region.connect(regions[region_name], f"Menu to {region_name}")
            set_rule(entrance, lambda state, req=LIBRARIAN_ITEMS[pos+4]:
                     state.count(req, self.player) >= 1
                     )

        for val in FLOOR_ABNOS.values():
            for prev, targ, _, _ in val:
                regions[prev].connect(regions[targ], f"{prev} to {targ}")

        #What receptions remain to be unlocked
        reception_region_names = set(location_regions.keys()) - ALWAYS_ACCESSIBLE_REGIONS - {
                region for chain in FLOOR_ABNOS.values()
                for prev, targ, _, _ in chain for region in (prev, targ)
        } - {
            "Reverb Ensemble", "Black Silence Reception", "Distorted Ensemble", "Keter Realization"
        } - {
            f"[Ensemble] {floor_name}" for floor_name in FLOOR_ABNOS
        }
        for region_name in reception_region_names:
            entrance = menu_region.connect(regions[region_name])
            set_rule(entrance, lambda state, rec=region_name: state.has(rec, self.player))
 
        for floor_name, chain in FLOOR_ABNOS.items():
            final_region = chain[-1][1]
            regions[final_region].connect(regions[f"[Ensemble] {floor_name.replace(' Final', '')}"])

        def ensemble_complete_count(state: CollectionState) -> int:
            return sum(
                1 for floor_name in FLOOR_ABNOS
                for loc in regions[f"[Ensemble] {floor_name}"].locations
                if loc.can_reach(state)
            )

        for floor_name in FLOOR_ABNOS:
            ensemble_entrance = regions[f"[Ensemble] {floor_name}"].connect(regions["Black Silence Reception"])
            set_rule(ensemble_entrance, lambda state: ensemble_complete_count(state) >= 2)

        #Reverb Ensemble -> Distorted Ensemble TODO
        regions["Black Silence Reception"].connect(regions["Distorted Ensemble"])
 
        #Black Silence Reception -> Keter Realization TODO
        regions["Black Silence Reception"].connect(regions["Keter Realization"])


    def create_item(self, item: str) -> LORItem:
        data = item_table[item]
        return LORItem(item, data.item_type, self.item_name_to_id[item], self.player)
    
    def create_items(self) -> None:
        itempool: list[str] = []

        #Abno pages
        for name in self.item_name_groups["AbnoPages"]:
            itempool += [name] * 5

        #Librarians (Philosophy gets 3 because 2 start unlocked: locked Binah + another librarian)
        for name in self.item_name_groups["Librarians"]:
            if name == "Floor of Philosophy Librarian":
                itempool += [name] * 3
            else:
                itempool += [name] * 4

        #EGO pages
        for name in self.item_name_groups["EGOPage"]:
            itempool += [name] * 5

        #Receptions
        #TODO: Might need to touch this up with logic.
        for name in self.item_name_groups["Receptions"]:
            itempool.append(name)

        #Mandatory progression items
        itempool += ["Bonus Passive Attribute Point"] * 8
        itempool += ["Binah"]
        itempool += ["Black Silence"]

        #Fill remaining locations with filler.
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        filler_count = total_locations - len(itempool)

        if filler_count < 0:
            raise Exception(
                f"[Library of Ruina] Item pool exceeds available locations by {-filler_count}. "
                f"Items: {len(itempool)}, Locations: {total_locations}"
            )

        itempool += ["Book of Everything"] * filler_count

        self.multiworld.itempool += map(self.create_item, itempool)

    def set_rules(self) -> None:
        set_rules(self) # rules.py, for better organization.

        #TODO - goals?
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Black Silence", self.player) # wire to end_goals?

    def fill_slot_data(self) -> typing.Dict[str, typing.Any]:
        total = 0
        for i in self.multiworld.itempool:
            if i.name == "Book of Everything":
                total += 1

        return {
            # Seed
            "seed": random.randint(0, 2147483647).__str__(),

            # Settings
            "fillers": self.options.fillers.value,
            "traps": self.options.traps.value,
            "traps_difficulty": self.options.traps_difficulty.value,
            "locked_floors": self.options.locked_floors.value,
            "random_first_floor": self.options.random_first_floor.value,
            "end_goals": ",".join(self.options.end_goals.value),
            "ensemble_battles": self.options.ensemble_battles.value,
            "abno_page_balance": self.options.abno_page_balance.value,
            "drop_system": self.options.drop_system.value,
            "randomize_pages": self.options.randomize_pages.value,
            
            # Data
            "books_of_everything": total,
        }