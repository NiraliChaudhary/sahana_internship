"""
Kaggle Dataset Downloader
==========================
Handles parsing Kaggle dataset URLs, downloading via the Kaggle API
or direct fallback, and locating the downloaded files.
"""

import os
import re
import zipfile
from pathlib import Path
from typing import Optional, Tuple

from src.utils.logger import get_logger
from src.utils.console import print_info, print_success, print_warning, print_error

logger = get_logger(__name__)


class KaggleDownloader:
    """
    Downloads and extracts Kaggle datasets given a dataset URL.

    Attributes:
        kaggle_url (str): Full Kaggle dataset URL.
        output_dir (Path): Directory where files will be saved.
        owner (str): Kaggle dataset owner/username.
        dataset_name (str): Kaggle dataset slug.
    """

    KAGGLE_URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?kaggle\.com/(?:datasets?/)?([^/]+)/([^/?#]+)"
    )

    def __init__(self, kaggle_url: str, output_dir: Path) -> None:
        self.kaggle_url = kaggle_url.strip()
        self.output_dir = output_dir
        self.owner, self.dataset_name = self._parse_url()
        logger.info("KaggleDownloader initialised for: %s/%s", self.owner, self.dataset_name)

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def download(self) -> Path:
        """
        Download and extract the Kaggle dataset.

        Returns:
            Path to the directory containing the extracted dataset files.

        Raises:
            RuntimeError: If download or extraction fails.
        """
        dataset_dir = self.output_dir / self.dataset_name
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Skip download if files already exist
        existing = list(dataset_dir.glob("*"))
        non_zip = [f for f in existing if f.suffix != ".zip"]
        if non_zip:
            print_info(f"Dataset already present at: {dataset_dir}")
            logger.info("Skipping download — files already exist.")
            return dataset_dir

        print_info(f"Downloading: {self.owner}/{self.dataset_name} → {dataset_dir}")
        self._download_via_api(dataset_dir)

        # Extract any zip archives produced by the API
        self._extract_zips(dataset_dir)

        print_success(f"Dataset downloaded and extracted to: {dataset_dir}")
        return dataset_dir

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    def _parse_url(self) -> Tuple[str, str]:
        """
        Extract owner and dataset slug from a Kaggle URL.

        Returns:
            Tuple of (owner, dataset_name).

        Raises:
            ValueError: If the URL does not match the expected Kaggle format.
        """
        match = self.KAGGLE_URL_PATTERN.search(self.kaggle_url)
        if not match:
            raise ValueError(
                f"Invalid Kaggle URL: '{self.kaggle_url}'.\n"
                "Expected format: https://www.kaggle.com/datasets/<owner>/<dataset>"
            )
        owner, name = match.group(1), match.group(2)
        # Strip query strings / fragments that may have slipped through
        name = name.split("?")[0].split("#")[0]
        return owner, name

    def _download_via_api(self, destination: Path) -> None:
        """
        Use the official kaggle-python library to download the dataset.

        Args:
            destination: Directory to store downloaded files.

        Raises:
            RuntimeError: If the Kaggle API is not configured or download fails.
        """
        try:
            import kaggle  # noqa: F401 — triggers credential check on import
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()
            logger.info("Kaggle API authenticated successfully.")

            api.dataset_download_files(
                dataset=f"{self.owner}/{self.dataset_name}",
                path=str(destination),
                unzip=False,   # We handle extraction ourselves for better control
                quiet=False,
                force=False,
            )
        except OSError as exc:
            raise RuntimeError(
                "Kaggle API credentials not found.\n"
                "Please place your kaggle.json at ~/.kaggle/kaggle.json "
                "or set KAGGLE_USERNAME and KAGGLE_KEY environment variables.\n"
                f"Original error: {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Kaggle API download failed: {exc}\n"
                "Verify the dataset slug and your internet connection."
            ) from exc

    def _extract_zips(self, directory: Path) -> None:
        """
        Extract all .zip files found in *directory* in-place.

        Args:
            directory: Folder to scan for zip archives.
        """
        zips = list(directory.glob("*.zip"))
        if not zips:
            logger.debug("No zip archives to extract.")
            return

        for zip_path in zips:
            print_info(f"Extracting: {zip_path.name}")
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(directory)
                zip_path.unlink()  # Remove the zip after extraction
                logger.info("Extracted and removed: %s", zip_path.name)
            except zipfile.BadZipFile:
                print_warning(f"Skipping corrupt zip: {zip_path.name}")
                logger.warning("Corrupt zip file ignored: %s", zip_path.name)
