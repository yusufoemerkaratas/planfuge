import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.image.red_annotation_detector import detect_red_regions, save_red_debug_mask


class RedAnnotationDetectorTest(unittest.TestCase):
    def test_detects_red_region_bbox(self):
        image = Image.new("RGB", (120, 100), "white")
        for x in range(20, 61):
            for y in range(30, 71):
                image.putpixel((x, y), (230, 20, 20))

        regions, mask = detect_red_regions(image, min_area_px=100)

        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0]["region_id"], "RED-001")
        self.assertEqual(regions[0]["bbox_image"], [20, 30, 41, 41])
        self.assertGreaterEqual(regions[0]["area_px"], 1600)
        self.assertEqual(regions[0]["source"], "red_annotation")
        self.assertEqual(mask.size, image.size)

    def test_filters_small_red_noise(self):
        image = Image.new("RGB", (50, 50), "white")
        image.putpixel((10, 10), (255, 0, 0))

        regions, _ = detect_red_regions(image, min_area_px=10)

        self.assertEqual(regions, [])

    def test_returns_empty_for_no_red_region(self):
        image = Image.new("RGB", (50, 50), "white")

        regions, _ = detect_red_regions(image, min_area_px=10)

        self.assertEqual(regions, [])

    def test_saves_debug_mask(self):
        image = Image.new("RGB", (20, 20), "white")
        image.putpixel((5, 5), (255, 0, 0))
        _, mask = detect_red_regions(image, min_area_px=1)

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "mask.png"
            save_red_debug_mask(mask, output_path)

            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
