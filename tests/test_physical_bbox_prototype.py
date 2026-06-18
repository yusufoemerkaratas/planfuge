import unittest

import numpy as np

from src.image.physical_bbox_prototype import refine_bbox_to_nearby_lines


class PhysicalBboxPrototypeTests(unittest.TestCase):
    def test_aligns_ocr_box_to_surrounding_cad_rectangle(self) -> None:
        image = np.full((120, 140), 255, dtype=np.uint8)
        image[20, 20:101] = 0
        image[80, 20:101] = 0
        image[20:81, 20] = 0
        image[20:81, 100] = 0
        image[40:50, 45:75] = 0

        refined = refine_bbox_to_nearby_lines(image, [45, 40, 30, 10], search_radius=40)

        self.assertEqual(refined, [20, 20, 80, 60])

    def test_returns_none_without_complete_surrounding_geometry(self) -> None:
        image = np.full((80, 80), 255, dtype=np.uint8)
        image[10, 10:70] = 0

        refined = refine_bbox_to_nearby_lines(image, [30, 30, 20, 10])

        self.assertIsNone(refined)


if __name__ == "__main__":
    unittest.main()
