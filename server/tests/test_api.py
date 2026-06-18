import unittest

from server.app.api import calculate_opening, health, openings_csv
from server.app.schemas import CalculateOpeningRequest, CsvExportRequest


class ApiTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        response = health()

        self.assertEqual(response["status"], "ok")

    def test_calculate_endpoint_returns_weight_and_csv_row(self) -> None:
        request = CalculateOpeningRequest.model_validate(
            {
                "geometry": "rectangular",
                "lengthCm": 20,
                "widthCm": 50,
                "heightCm": 25,
                "quantity": 2,
                "type": "Ceiling",
            }
        )

        response = calculate_opening(request)

        self.assertEqual(response["weightKg"], 22)
        self.assertEqual(response["reviewStatus"], "ready")
        self.assertEqual(response["csvRow"]["Type"], "Ceiling")

    def test_csv_endpoint_returns_csv(self) -> None:
        request = CsvExportRequest.model_validate(
            {
                "openings": [
                    {
                        "geometry": "round",
                        "lengthCm": 15,
                        "widthCm": 15,
                        "heightCm": 30,
                        "quantity": 3,
                    }
                ]
            }
        )

        response = openings_csv(request)
        body = response.body.decode("utf-8")

        self.assertIn("text/csv", response.media_type)
        self.assertTrue(body.startswith("Floor,Construction phase/Plan name"))
        self.assertIn("round", body)


if __name__ == "__main__":
    unittest.main()
