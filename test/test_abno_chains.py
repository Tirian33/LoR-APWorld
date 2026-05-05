from . import LORTestBase
from BaseClasses import CollectionState

class TestFloorChains(LORTestBase):

    def collect_one(self, item_name: str):
        item = next(i for i in self.multiworld.itempool if i.name == item_name)
        self.multiworld.state.collect(item)

    def lower_fls_helper(self, floor: str, seq: list[str], is_keter: bool = False):
        lib = f"Floor of {floor} Librarian"
        
        self.assertTrue(self.can_reach_region(seq[0]))
        self.assertTrue(self.can_reach_region(seq[1]))
        self.assertFalse(self.can_reach_region(seq[2]))
        self.assertFalse(self.can_reach_region(seq[3]))
        if not is_keter: self.assertFalse(self.can_reach_region(f"Floor of {floor} Final"))
        #1 lib
        self.collect_one(lib)
        self.assertTrue(self.can_reach_region(seq[2]))
        self.assertFalse(self.can_reach_region(seq[3]))
        if not is_keter: self.assertFalse(self.can_reach_region(f"Floor of {floor} Final"))
        #2 lib
        self.collect_one(lib)
        if not is_keter: self.assertTrue(self.can_reach_region(seq[3]))
        if is_keter:
            self.assertFalse(self.can_reach_region("Keter Realization"))
            self.collect_one(lib)
            self.collect_one(lib)
            self.assertTrue(self.can_reach_region("Keter Realization"))
        else:
            self.assertTrue(self.can_reach_region(f"Floor of {floor} Final"))

    def test_gen_wks(self):
        floor = "General Works"
        seq = ["Bloodbath", "Heart of Aspiration", "Pinocchio", "The Snow Queen"]
        self.lower_fls_helper(floor, seq, True)

    def test_history(self):
        floor = "History"
        seq = ["Scorched Girl", "Happy Teddy Bear", "Fairy Festival", "Queen Bee"]
        self.lower_fls_helper(floor, seq)
    
    def test_tech_sci(self):
        floor = "Technological Sciences"
        seq = ["Forsaken Murderer", "All-Around Helper", "Singing Machine", "The Funeral of the Dead Butterflies"]
        self.lower_fls_helper(floor, seq)
        
    def test_literature(self):
        floor = "Literature"
        seq = ["Today's Shy Look", "The Red Shoes", "Spider Bud", "Laetitia"]
        self.lower_fls_helper(floor, seq)

    def test_art(self):
        floor = "Art"
        seq = ["Fragment of the Universe", "Child of the Galaxy", "Porccubus", "Alriune"]
        self.lower_fls_helper(floor, seq)

    def upper_fls_helper(self, floor: str, seq: list[str], is_philo: bool = False):
        lib = f"Floor of {floor} Librarian"

        self.assertFalse(self.can_reach_region(seq[0]))
        self.assertFalse(self.can_reach_region(seq[1]))
        self.assertFalse(self.can_reach_region(seq[2]))
        if len(seq) > 3: self.assertFalse(self.can_reach_region(seq[3]))
        self.assertFalse(self.can_reach_region("Floor of " + floor + " Final"))
        #1 lib
        self.collect_one(lib)
        self.assertTrue(self.can_reach_region(seq[0]))
        self.assertFalse(self.can_reach_region(seq[1]))
        self.assertFalse(self.can_reach_region(seq[2]))
        if len(seq) > 3: self.assertFalse(self.can_reach_region(seq[3]))
        self.assertFalse(self.can_reach_region("Floor of " + floor + " Final"))
        #2 lib
        self.collect_one(lib)
        self.assertTrue(self.can_reach_region(seq[1]))
        self.assertFalse(self.can_reach_region(seq[2]))
        if len(seq) > 3: self.assertFalse(self.can_reach_region(seq[3]))
        self.assertFalse(self.can_reach_region("Floor of " + floor + " Final"))
        #3 lib
        self.collect_one(lib)
        self.assertTrue(self.can_reach_region(seq[2]))
        if len(seq) > 3: self.assertFalse(self.can_reach_region(seq[3]))
        self.assertFalse(self.can_reach_region("Floor of " + floor + " Final"))
        #4 lib
        self.collect_one(lib)
        if len(seq) > 3: self.assertTrue(self.can_reach_region(seq[3]))

        #Handle Binah
        if is_philo:
            self.assertFalse(self.can_reach_region("Floor of " + floor + " Final"))
            self.collect_by_name("Binah")
            
        self.assertTrue(self.can_reach_region("Floor of " + floor + " Final"))

    def test_nat_sci(self):
        floor = "Natural Sciences"
        seq = ["The Queen of Hatred", "The Knight of Despair", "The King of Greed", "The Servant of Wrath"]
        self.upper_fls_helper(floor, seq)

    def test_language(self):
        floor = "Language"
        seq = ["Little Red Riding Hooded Mercenary", "Big and Will be Bad Wolf", "Mountain of Smiling Bodies", "Nosferatu"]
        self.upper_fls_helper(floor, seq)

    def test_social_sci(self):
        floor = "Social Sciences"
        seq = ["Scarecrow Searching for Wisdom", "Warm-hearted Woodsman", "The Road Home & Scaredy Cat", "Ozma"]
        self.upper_fls_helper(floor, seq)

    def test_philosophy(self):
        floor = "Philosophy"
        seq = ["Big Bird", "Punishing Bird", "Judgement Bird"]
        self.upper_fls_helper(floor, seq, True)

    def test_religion(self):
        floor = "Religion"
        seq = ["The Burrowing Heaven", "The Price of Silence", "Blue Star"]
        self.upper_fls_helper(floor, seq)

