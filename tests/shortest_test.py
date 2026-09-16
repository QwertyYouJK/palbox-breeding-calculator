from palbox_breeding_calculator.shortest import create_chain, pairs_dict
import unittest
from pathlib import Path


class TestChain(unittest.TestCase):
    def get_pairs_dict(self):
        project_root = Path(__file__).resolve().parent.parent
        pairs_path = project_root / "assets" / "pairs.json"
        return pairs_dict(pairs_path)

    def check_chain_usable(self, palbox, recipes, chain):
        available = palbox.copy()
        breed_count = 0
        for p1, p2, child in chain:
            self.assertIn(p1, available, "Parent 1 must be in available")
            self.assertIn(p2, available, "Parent 2 must be in available")

            key = tuple(sorted([p1, p2]))
            self.assertEqual(child, recipes[key], "Child must match recipe")

            available.append(child)
            breed_count += 1

        return available, breed_count

    def test_already_owned(self):
        palbox = ["116.0", "114.0"]
        target = "116.0"

        self.assertIsNone(create_chain(palbox, target, {}))

    def test_direct_breeding(self):
        palbox = ["139.0", "195.0"]  # anubis + bellanoir = silvegis
        target = "160.0"
        recipes = self.get_pairs_dict()

        result = create_chain(palbox, target, recipes)

        available, breed_count = self.check_chain_usable(palbox, recipes, result)

        self.assertIn(target, available, "Target should be in available list")
        self.assertEqual(breed_count, 1, "Breed count should be 1")

    def test_two_operations(self):
        # amione + katress = elphidran
        # amione + elphidran = dazzi
        palbox = ["47.0", "79.0"]
        target = "92.0"
        recipes = self.get_pairs_dict()

        result = create_chain(palbox, target, recipes)
        available, breed_count = self.check_chain_usable(palbox, recipes, result)

        self.assertIn(target, available, "Target should be in available list")
        self.assertEqual(breed_count, 2, "Breed count should be 2")

    def test_shared_intermediate(self):
        palbox = ["96.0", "112.0"]
        target = "141.0"
        recipes = self.get_pairs_dict()

        result = create_chain(palbox, target, recipes)
        available, breed_count = self.check_chain_usable(palbox, recipes, result)

        self.assertIn(target, available, "Target should be in available list")
        self.assertEqual(breed_count, 4, "Breed count should be 4")

    def test_unreachable_target(self):
        palbox = ["116.0", "114.0"]
        target = "202.0"
        recipes = self.get_pairs_dict()

        result = create_chain(palbox, target, recipes)
        self.assertIsNone(result)

    def test_input_unchanged(self):
        palbox = ["96.0", "112.0"]
        palbox_copy = palbox.copy()
        target = "141.0"
        recipes = self.get_pairs_dict()

        create_chain(palbox, target, recipes)
        self.assertEqual(palbox, palbox_copy, "Should not change palbox")

    def test_search_continues_with_other_queued_collections(self):
        palbox = ["A", "B", "C"]
        recipes = {
            ("A", "B"): "D",
            ("A", "C"): "E",
            ("B", "C"): "F",
            ("D", "E"): "Target",
        }

        result = create_chain(palbox, "Target", recipes)
        available, breed_count = self.check_chain_usable(palbox, recipes, result)

        self.assertIn("Target", available)
        self.assertEqual(breed_count, 3)

    def test_chain_preserves_dependency_order(self):
        palbox = ["133.0", "106.0"]
        target = "118.1"
        recipes = self.get_pairs_dict()

        result = create_chain(palbox, target, recipes)
        available, breed_count = self.check_chain_usable(palbox, recipes, result)

        self.assertIn(target, available)
        self.assertEqual(breed_count, 4)

    def test_chain_preserves_shortest_shared_route(self):
        palbox = ["109.0", "108.1"]
        target = "91.0"
        recipes = self.get_pairs_dict()

        result = create_chain(palbox, target, recipes)
        available, breed_count = self.check_chain_usable(palbox, recipes, result)

        self.assertIn(target, available)
        self.assertEqual(breed_count, 4)

    def test_empty_palbox(self):
        recipes = {("A", "B"): "Target"}

        self.assertIsNone(create_chain([], "Target", recipes))


if __name__ == "__main__":
    unittest.main()
