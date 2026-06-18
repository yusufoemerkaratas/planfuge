import tempfile
import unittest
from pathlib import Path

from server.app.services.plan_discovery import discover_plans


class PlanDiscoveryTests(unittest.TestCase):
    def test_discover_empty_directory_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            # data/pages doesn't even exist yet
            result = discover_plans(root)
            self.assertEqual(result, [])

            # directory exists but empty
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)
            result = discover_plans(root)
            self.assertEqual(result, [])

    def test_discover_extracts_and_sorts_plan_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pages_dir = root / "data" / "pages"
            pages_dir.mkdir(parents=True)
            
            # Create dummy files
            (pages_dir / "SP_U1_0004.png").touch()
            (pages_dir / "SP_U1_0003.png").touch()
            (pages_dir / "SP_U1_0005.jpg").touch() # Should be ignored (not .png)
            (pages_dir / "random.txt").touch() # Should be ignored
            
            result = discover_plans(root)
            
            self.assertEqual(len(result), 2)
            # Should be sorted
            self.assertEqual(result[0], "SP_U1_0003")
            self.assertEqual(result[1], "SP_U1_0004")


if __name__ == "__main__":
    unittest.main()
