import unittest

from src.candidates.opening_label_parser import parse_opening_label


class OpeningLabelParserTest(unittest.TestCase):
    def test_parse_wdb_dimensions_and_ok_reference(self):
        parsed = parse_opening_label("WDB 70/20 OK -60 UKRD")

        self.assertEqual(
            parsed,
            {
                "label_type": "WDB",
                "width_mm": 700,
                "height_mm": 200,
                "diameter_mm": None,
                "ra_value": None,
                "ok_value": -60,
                "reference": "UKRD",
            },
        )

    def test_parse_compact_ddb_dimensions(self):
        parsed = parse_opening_label("DDB130/140")

        self.assertEqual(parsed["label_type"], "DDB")
        self.assertEqual(parsed["width_mm"], 1300)
        self.assertEqual(parsed["height_mm"], 1400)
        self.assertIsNone(parsed["diameter_mm"])

    def test_parse_diameter_symbol(self):
        parsed = parse_opening_label("DDP Ø150 RA -45 UKRD")

        self.assertEqual(parsed["label_type"], "DDP")
        self.assertEqual(parsed["diameter_mm"], 150)
        self.assertEqual(parsed["ra_value"], -45)
        self.assertIsNone(parsed["ok_value"])
        self.assertEqual(parsed["reference"], "UKRD")

    def test_parse_short_diameter_as_centimeters(self):
        parsed = parse_opening_label("WDB Ø15 RA -80 UKRD")

        self.assertEqual(parsed["label_type"], "WDB")
        self.assertEqual(parsed["diameter_mm"], 150)
        self.assertEqual(parsed["ra_value"], -80)
        self.assertEqual(parsed["reference"], "UKRD")

    def test_parse_ddp_hsi_diameter(self):
        parsed = parse_opening_label("DDP HSI150 RA -50 UKRD")

        self.assertEqual(parsed["label_type"], "DDP")
        self.assertEqual(parsed["diameter_mm"], 150)
        self.assertEqual(parsed["ra_value"], -50)
        self.assertEqual(parsed["reference"], "UKRD")

    def test_parse_hsi_diameter(self):
        parsed = parse_opening_label("HSI150 OK 0 UKRD")

        self.assertEqual(parsed["label_type"], "HSI")
        self.assertEqual(parsed["diameter_mm"], 150)
        self.assertEqual(parsed["ok_value"], 0)
        self.assertEqual(parsed["reference"], "UKRD")

    def test_parse_non_candidate_returns_none(self):
        self.assertIsNone(parse_opening_label("Scale 1:50 UKRD"))

    def test_parse_other_reference_values(self):
        self.assertEqual(parse_opening_label("WDB 20/30 OKRB")["reference"], "OKRB")
        self.assertEqual(parse_opening_label("WDB 20/30 UKRB")["reference"], "UKRB")


if __name__ == "__main__":
    unittest.main()
