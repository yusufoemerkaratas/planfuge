import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.image.crop_regions import crop_red_regions


class CropRegionsTest(unittest.TestCase):
    def test_crops_region_with_padding_and_metadata(self):
        image = Image.new("RGB", (100, 80), "white")
        regions = [
            {
                "region_id": "RED-001",
                "bbox_image": [20, 15, 30, 25],
                "area_px": 750,
                "source": "red_annotation",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            metadata = crop_red_regions(
                image=image,
                regions=regions,
                output_dir=Path(tmp_dir),
                plan_id="SP_U1_0003",
                padding_px=10,
            )

            self.assertEqual(
                metadata,
                [
                    {
                        "region_id": "RED-001",
                        "crop_path": str(Path(tmp_dir) / "SP_U1_0003_RED-001.png"),
                        "bbox_image": [20, 15, 30, 25],
                        "crop_bbox_image": [10, 5, 60, 50],
                    }
                ],
            )
            self.assertTrue(Path(metadata[0]["crop_path"]).exists())
            with Image.open(metadata[0]["crop_path"]) as crop:
                self.assertEqual(crop.size, (50, 45))

    def test_clips_crop_to_image_boundaries(self):
        image = Image.new("RGB", (50, 40), "white")
        regions = [
            {
                "region_id": "RED-001",
                "bbox_image": [0, 0, 15, 12],
                "area_px": 180,
                "source": "red_annotation",
            },
            {
                "region_id": "RED-002",
                "bbox_image": [42, 33, 8, 7],
                "area_px": 56,
                "source": "red_annotation",
            },
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            metadata = crop_red_regions(
                image=image,
                regions=regions,
                output_dir=Path(tmp_dir),
                plan_id="SP_U1_0004",
                padding_px=10,
            )

            self.assertEqual(metadata[0]["crop_bbox_image"], [0, 0, 25, 22])
            self.assertEqual(metadata[1]["crop_bbox_image"], [32, 23, 50, 40])

    def test_returns_empty_metadata_for_no_regions(self):
        image = Image.new("RGB", (50, 40), "white")

        with tempfile.TemporaryDirectory() as tmp_dir:
            metadata = crop_red_regions(
                image=image,
                regions=[],
                output_dir=Path(tmp_dir),
                plan_id="SP_U1_0005",
            )

            self.assertEqual(metadata, [])


if __name__ == "__main__":
    unittest.main()
