"""
Data Loader
===========
Discovers, validates, and loads datasets from a local directory.
Supports CSV, XLSX/XLS, JSON, and Parquet formats.
Memory-efficient loading with encoding auto-detection.
"""

import gc
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chardet
import pandas as pd

from config.settings import (
    SUPPORTED_FORMATS,
    CHUNK_SIZE,
    MAX_ROWS_IN_MEMORY,
)
from src.utils.logger import get_logger
from src.utils.console import print_info, print_success, print_warning, print_error

logger = get_logger(__name__)


class DataLoader:
    """
    Discovers and loads dataset files from a directory.

    Attributes:
        directory (Path): Folder to scan for dataset files.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        logger.info("DataLoader scanning: %s", directory)

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def discover_files(self) -> List[Path]:
        """
        Recursively discover all supported data files in *self.directory*.

        Returns:
            Sorted list of file paths.
        """
        found: List[Path] = []
        for fmt in SUPPORTED_FORMATS:
            found.extend(self.directory.rglob(f"*{fmt}"))

        # Filter out macOS metadata files
        found = [f for f in found if not f.name.startswith("._") and f.stat().st_size > 0]
        found.sort()

        if not found:
            logger.warning("No supported data files found in %s", self.directory)
        else:
            logger.info("Discovered %d file(s): %s", len(found), [f.name for f in found])

        return found

    def select_primary_file(self, files: List[Path]) -> Path:
        """
        Heuristically choose the best candidate file for analysis.
        Preference: largest CSV/Parquet > XLSX > JSON.

        Args:
            files: List of candidate file paths.

        Returns:
            Selected primary file path.
        """
        if len(files) == 1:
            return files[0]

        priority_order = [".csv", ".parquet", ".xlsx", ".xls", ".json"]
        for ext in priority_order:
            candidates = [f for f in files if f.suffix.lower() == ext]
            if candidates:
                # Pick the largest file in this format category
                return max(candidates, key=lambda p: p.stat().st_size)

        return files[0]

    def load(self, file_path: Path) -> Tuple[pd.DataFrame, Dict]:
        """
        Load a dataset file into a DataFrame with metadata.

        Args:
            file_path: Path to the data file.

        Returns:
            Tuple of (DataFrame, metadata_dict).

        Raises:
            ValueError: If the file format is unsupported or unreadable.
        """
        ext = file_path.suffix.lower()
        size_mb = file_path.stat().st_size / 1_048_576
        print_info(f"Loading: {file_path.name}  ({size_mb:.2f} MB)")
        logger.info("Loading file: %s  (%.2f MB)", file_path.name, size_mb)

        if size_mb > 500:
            print_warning(f"Large file ({size_mb:.0f} MB) — using chunked loading.")

        try:
            if ext == ".csv":
                df = self._load_csv(file_path)
            elif ext in (".xlsx", ".xls"):
                df = self._load_excel(file_path)
            elif ext == ".json":
                df = self._load_json(file_path)
            elif ext == ".parquet":
                df = self._load_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: '{ext}'")
        except Exception as exc:
            raise ValueError(f"Failed to load '{file_path.name}': {exc}") from exc

        # Force garbage collection after loading large files
        gc.collect()

        metadata = self._build_metadata(df, file_path, size_mb)
        print_success(
            f"Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns"
        )
        return df, metadata

    # ──────────────────────────────────────────
    # Private loaders
    # ──────────────────────────────────────────

    def _load_csv(self, path: Path) -> pd.DataFrame:
        """Load CSV with auto encoding detection and chunked fallback."""
        encoding = self._detect_encoding(path)
        logger.debug("Detected encoding: %s", encoding)

        try:
            df = pd.read_csv(
                path,
                encoding=encoding,
                low_memory=False,
                on_bad_lines="warn",
            )
        except MemoryError:
            print_warning("MemoryError — falling back to chunked loading.")
            df = self._chunked_csv_load(path, encoding)
        except UnicodeDecodeError:
            print_warning("Encoding error with %s — retrying with latin-1.", encoding)
            df = pd.read_csv(path, encoding="latin-1", low_memory=False, on_bad_lines="warn")

        return df

    def _chunked_csv_load(self, path: Path, encoding: str) -> pd.DataFrame:
        """Load a very large CSV in CHUNK_SIZE-row chunks."""
        chunks = []
        with pd.read_csv(
            path, encoding=encoding, chunksize=CHUNK_SIZE, low_memory=False, on_bad_lines="warn"
        ) as reader:
            for chunk in reader:
                chunks.append(chunk)
                if sum(len(c) for c in chunks) >= MAX_ROWS_IN_MEMORY:
                    print_warning(
                        f"Reached {MAX_ROWS_IN_MEMORY:,} row limit — "
                        "truncating for in-memory analysis."
                    )
                    break
        return pd.concat(chunks, ignore_index=True)

    def _load_excel(self, path: Path) -> pd.DataFrame:
        """Load the first sheet of an Excel file."""
        df = pd.read_excel(path, sheet_name=0, engine="openpyxl")
        return df

    def _load_json(self, path: Path) -> pd.DataFrame:
        """Load JSON — handles both record-oriented and nested structures."""
        try:
            df = pd.read_json(path, orient="records")
        except ValueError:
            # Try line-delimited JSON
            try:
                df = pd.read_json(path, lines=True)
            except ValueError:
                # Last resort: load raw dict and normalise
                with open(path, encoding="utf-8") as fh:
                    raw = json.load(fh)
                if isinstance(raw, list):
                    df = pd.json_normalize(raw)
                elif isinstance(raw, dict):
                    df = pd.json_normalize([raw])
                else:
                    raise ValueError("Unrecognised JSON structure.")
        return df

    def _load_parquet(self, path: Path) -> pd.DataFrame:
        """Load a Parquet file using pyarrow engine."""
        return pd.read_parquet(path, engine="pyarrow")

    # ──────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────

    @staticmethod
    def _detect_encoding(path: Path, sample_bytes: int = 50_000) -> str:
        """
        Use chardet to detect file encoding from a sample.

        Args:
            path: File to inspect.
            sample_bytes: Number of bytes to sample.

        Returns:
            Detected encoding string, defaulting to 'utf-8'.
        """
        with open(path, "rb") as fh:
            raw = fh.read(sample_bytes)
        result = chardet.detect(raw)
        encoding = result.get("encoding") or "utf-8"
        # Normalise common aliases
        encoding = encoding.lower().replace("-", "_")
        return encoding

    @staticmethod
    def _build_metadata(df: pd.DataFrame, path: Path, size_mb: float) -> Dict:
        """Build a metadata dictionary for the loaded DataFrame."""
        return {
            "file_name": path.name,
            "file_path": str(path),
            "file_size_mb": round(size_mb, 3),
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
            "memory_usage_mb": round(
                df.memory_usage(deep=True).sum() / 1_048_576, 3
            ),
        }
