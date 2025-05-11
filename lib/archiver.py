# archiver.py
import tarfile
from pathlib import Path
import os

class Archiver:
    def __init__(self, archive_format: str = 'tar.gz'):
        if archive_format not in ['tar.gz', 'zip']:
            raise ValueError("Unsupported archive format. Choose 'tar.gz' or 'zip'.")
        self.archive_format = archive_format

    def compress_files(self, files_to_archive: list[Path], archive_path_output: Path, staging_area: Path):
        """
        Compresses files into an archive.
        :param files_to_archive: List of Paths to individual files (e.g., encrypted copies in staging_area).
        :param archive_path_output: Path to the final archive file.
        :param staging_area: The base directory from which to archive files, to maintain relative paths.
        """
        if self.archive_format == 'tar.gz':
            with tarfile.open(archive_path_output, "w:gz") as tar:
                for file_path in files_to_archive:
                    # arcname should be the path relative to the staging area
                    # or how you want it to appear inside the tarball
                    arcname = file_path.relative_to(staging_area)
                    tar.add(file_path, arcname=arcname)
            print(f"Created tar.gz archive: {archive_path_output}")
        # Add 'zip' support similarly using zipfile module if needed

    def extract_files(self, archive_path_input: Path, destination_path: Path):
        destination_path.mkdir(parents=True, exist_ok=True)
        if self.archive_format == 'tar.gz':
            with tarfile.open(archive_path_input, "r:gz") as tar:
                tar.extractall(path=destination_path)
            print(f"Extracted tar.gz archive to: {destination_path}")
        # Add 'zip' support similarly