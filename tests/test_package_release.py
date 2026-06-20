import shutil
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.package_release import (
    get_tracked_files,
    package_frontend_zip,
    package_source_tar_gz,
    package_source_zip,
    sha256_checksum,
    write_checksums,
)


class TestReleasePackager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.test_dir.name).resolve()

        # Initialize Git repo
        subprocess.run(["git", "init", "-q"], cwd=str(self.repo_root), check=True)

        # Configure dummy Git identity
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=str(self.repo_root), check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=str(self.repo_root), check=True
        )

        # Create dummy tracked files
        self.tracked_files = [
            Path("README.md"),
            Path("compose.yaml"),
            Path("server/main.py"),
            Path("client/src/App.tsx"),
        ]

        for file_path in self.tracked_files:
            abs_path = self.repo_root / file_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(f"Content for {file_path}", encoding="utf-8")

        # Stage files in Git
        subprocess.run(["git", "add", "."], cwd=str(self.repo_root), check=True)

        # Create untracked file to verify it's ignored
        untracked = self.repo_root / "untracked_file.txt"
        untracked.write_text("untracked content", encoding="utf-8")

        # Create dummy client/dist folder (untracked/ignored by git)
        self.dist_dir = self.repo_root / "client" / "dist"
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        (self.dist_dir / "index.html").write_text("HTML content", encoding="utf-8")
        (self.dist_dir / "assets").mkdir(parents=True, exist_ok=True)
        (self.dist_dir / "assets" / "index.js").write_text("JS content", encoding="utf-8")

        # Destination directory for packaging
        self.dest_dir = self.repo_root / "dist"
        self.dest_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_get_tracked_files(self):
        files = get_tracked_files(self.repo_root)
        self.assertEqual(len(files), len(self.tracked_files))
        for f in self.tracked_files:
            self.assertIn(f, files)

    def test_package_source_zip(self):
        version = "1.0.2"
        zip_path = package_source_zip(self.repo_root, version, self.tracked_files, self.dest_dir)

        self.assertTrue(zip_path.is_file())
        self.assertEqual(zip_path.name, "planfuge-1.0.2.zip")

        # Verify ZIP contents
        with zipfile.ZipFile(zip_path, "r") as z:
            namelist = z.namelist()
            self.assertEqual(len(namelist), len(self.tracked_files))
            for f in self.tracked_files:
                expected_in_zip = f"planfuge-{version}/{f}"
                self.assertIn(expected_in_zip, namelist)
                self.assertEqual(z.read(expected_in_zip).decode("utf-8"), f"Content for {f}")

    def test_package_source_tar_gz(self):
        version = "1.0.2"
        tar_path = package_source_tar_gz(self.repo_root, version, self.tracked_files, self.dest_dir)

        self.assertTrue(tar_path.is_file())
        self.assertEqual(tar_path.name, "planfuge-1.0.2.tar.gz")

        # Verify TAR.GZ contents
        with tarfile.open(tar_path, "r:gz") as t:
            members = t.getmembers()
            names = [m.name for m in members]
            self.assertEqual(len(names), len(self.tracked_files))
            for f in self.tracked_files:
                expected_in_tar = f"planfuge-{version}/{f}"
                self.assertIn(expected_in_tar, names)

                # Verify contents
                f_member = t.extractfile(expected_in_tar)
                self.assertIsNotNone(f_member)
                self.assertEqual(f_member.read().decode("utf-8"), f"Content for {f}")

    def test_package_frontend_zip(self):
        version = "1.0.2"
        fe_zip_path = package_frontend_zip(self.repo_root, version, self.dest_dir)

        self.assertIsNotNone(fe_zip_path)
        self.assertTrue(fe_zip_path.is_file())
        self.assertEqual(fe_zip_path.name, "planfuge-frontend-1.0.2.zip")

        # Verify ZIP contents (flat relative to client/dist)
        with zipfile.ZipFile(fe_zip_path, "r") as z:
            namelist = z.namelist()
            self.assertEqual(len(namelist), 2)
            self.assertIn("index.html", namelist)
            self.assertIn("assets/index.js", namelist)
            self.assertEqual(z.read("index.html").decode("utf-8"), "HTML content")
            self.assertEqual(z.read("assets/index.js").decode("utf-8"), "JS content")

    def test_package_frontend_zip_missing_dist(self):
        # Delete client/dist and verify it returns None
        shutil.rmtree(self.dist_dir)
        fe_zip_path = package_frontend_zip(self.repo_root, "1.0.2", self.dest_dir)
        self.assertIsNone(fe_zip_path)

    def test_write_checksums_and_sha256(self):
        # Create a dummy file to hash
        dummy_file = self.repo_root / "dummy.txt"
        dummy_file.write_text("hello world", encoding="utf-8")

        expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        self.assertEqual(sha256_checksum(dummy_file), expected_hash)

        # Write checksum file
        checksums_path = write_checksums([dummy_file], self.dest_dir)
        self.assertTrue(checksums_path.is_file())
        self.assertEqual(checksums_path.name, "SHA256SUMS")

        content = checksums_path.read_text(encoding="utf-8")
        self.assertEqual(content, f"{expected_hash}  dummy.txt\n")


if __name__ == "__main__":
    unittest.main()
