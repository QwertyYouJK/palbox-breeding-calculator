import unittest
from pathlib import Path

from PIL import Image

from palbox_breeding_calculator.pal_identify import identify_pal, load_references


class TestPalIdentify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).resolve().parent.parent
        cls.references = load_references(cls.project_root / "assets" / "pal_icons")

    def get_crop(self, filename, row, col):
        path = self.project_root / "screenshots" / filename
        if not path.exists():
            self.skipTest("Local screenshot is not available.")
        with Image.open(path) as image:
            return image.crop(((col - 1) * 106, (row - 1) * 106, col * 106, row * 106))

    def test_cattiva_with_circular_border(self):
        crop = self.get_crop("page 2.png", 1, 1)
        result = identify_pal(crop, self.references)

        self.assertEqual(result["id"], "2.0")
        self.assertEqual(result["candidates"][0][0], "2.0")

    def test_celaray_with_lock_badge(self):
        crop = self.get_crop("page 2.png", 1, 2)
        result = identify_pal(crop, self.references)

        self.assertEqual(result["id"], "7.0")

    def test_unsupported_portrait_is_unknown(self):
        crop = self.get_crop("page 1.png", 1, 1)
        result = identify_pal(crop, self.references)

        self.assertIsNone(result["id"])

    def test_empty_slot_is_unknown(self):
        crop = self.get_crop("page 28.png", 5, 6)
        result = identify_pal(crop, self.references)

        self.assertIsNone(result["id"])

    def test_uniform_image_is_unknown(self):
        for colour in ((0, 0, 0), (30, 40, 44), (255, 255, 255)):
            with self.subTest(colour=colour):
                crop = Image.new("RGB", (106, 106), colour)
                self.assertIsNone(identify_pal(crop, self.references)["id"])

    def test_wrong_crop_size_is_rejected(self):
        with self.assertRaises(ValueError):
            identify_pal(Image.new("RGB", (50, 50)), self.references)


if __name__ == "__main__":
    unittest.main()
