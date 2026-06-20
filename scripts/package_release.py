#!/usr/bin/env python3
"""Deterministic release packager for Planfuge.

Packages Git-tracked files into ZIP and TAR.GZ source archives,
packages compiled frontend assets into a separate ZIP,
and generates SHA256 checksums.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import tarfile
import zipfile
from pathlib import Path


def get_tracked_files(repo_root: Path) -> list[Path]:
    """Get a list of all Git-tracked files relative to repo_root."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(repo_root),
        )
        files = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                path = repo_root / line
                if path.is_file():
                    files.append(Path(line))
        return sorted(files)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to list Git-tracked files: {e.stderr}") from e


def sha256_checksum(file_path: Path) -> str:
    """Calculate the SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def package_source_zip(repo_root: Path, version: str, files: list[Path], dest_dir: Path) -> Path:
    """Create a ZIP archive of all Git-tracked source files under a versioned directory."""
    archive_name = f"planfuge-{version}.zip"
    archive_path = dest_dir / archive_name
    root_dir_name = f"planfuge-{version}"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for rel_path in files:
            abs_path = repo_root / rel_path
            archive_target_path = Path(root_dir_name) / rel_path
            zip_file.write(abs_path, str(archive_target_path))

    return archive_path


def package_source_tar_gz(repo_root: Path, version: str, files: list[Path], dest_dir: Path) -> Path:
    """Create a TAR.GZ archive of all Git-tracked source files under a versioned directory."""
    archive_name = f"planfuge-{version}.tar.gz"
    archive_path = dest_dir / archive_name
    root_dir_name = f"planfuge-{version}"

    with tarfile.open(archive_path, "w:gz") as tar_file:
        for rel_path in files:
            abs_path = repo_root / rel_path
            archive_target_path = Path(root_dir_name) / rel_path
            tar_file.add(abs_path, str(archive_target_path))

    return archive_path


def package_frontend_zip(repo_root: Path, version: str, dest_dir: Path) -> Path | None:
    """Package compiled frontend assets from client/dist into a ZIP archive."""
    dist_dir = repo_root / "client" / "dist"
    if not dist_dir.is_dir():
        print("Warning: client/dist directory not found. Skipping frontend package.")
        return None

    archive_name = f"planfuge-frontend-{version}.zip"
    archive_path = dest_dir / archive_name

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(dist_dir):
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(dist_dir)
                zip_file.write(abs_path, str(rel_path))

    return archive_path


def write_checksums(artifact_paths: list[Path], dest_dir: Path) -> Path:
    """Write the SHA256 checksums file for all artifacts."""
    checksums_path = dest_dir / "SHA256SUMS"
    lines = []
    for path in artifact_paths:
        checksum = sha256_checksum(path)
        lines.append(f"{checksum}  {path.name}\n")

    checksums_path.write_text("".join(lines), encoding="utf-8")
    return checksums_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        required=True,
        help="The release version string (e.g. 1.0.1)",
    )
    parser.add_argument(
        "--out",
        default="dist",
        help="Directory to save generated artifacts (default: dist/)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    dest_dir = repo_root / args.out
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Clean up standard tags prefix if passed (e.g. refs/tags/v1.0.1 -> 1.0.1 or v1.0.1)
    version = args.version.split("/")[-1]
    if version.startswith("v") and len(version) > 1:
        version = version[1:]

    print(f"Packaging Planfuge release v{version}...")
    tracked_files = get_tracked_files(repo_root)
    print(f"Found {len(tracked_files)} Git-tracked files.")

    artifacts = []

    # 1. Source ZIP
    src_zip = package_source_zip(repo_root, version, tracked_files, dest_dir)
    print(f"Created source ZIP: {src_zip.name}")
    artifacts.append(src_zip)

    # 2. Source TAR.GZ
    src_tar = package_source_tar_gz(repo_root, version, tracked_files, dest_dir)
    print(f"Created source TAR.GZ: {src_tar.name}")
    artifacts.append(src_tar)

    # 3. Frontend ZIP
    fe_zip = package_frontend_zip(repo_root, version, dest_dir)
    if fe_zip:
        print(f"Created frontend ZIP: {fe_zip.name}")
        artifacts.append(fe_zip)

    # 4. Checksums
    checksums = write_checksums(artifacts, dest_dir)
    print(f"Generated checksums file: {checksums.name}")

    print("\nRelease packaging completed successfully!")


if __name__ == "__main__":
    main()
