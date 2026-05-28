"""
File Validator
==============
Low-level file integrity checks: existence, format, size, readability,
header presence, and encoding issues — before the file is loaded.
"""

from pathlib import Path
from typing import Dict, List

import chardet

from config.settings import SUPPORTED_FORMATS
from src.utils.logger import get_logger
from src.utils.console import print_success, print_warning, print_error, print_info

logger = get_logger(__name__)


class FileValidationResult:
    """Container for file validation outcomes."""

    def __init__(self) -> None:
        self.passed: bool = True
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict = {}

    def add_issue(self, msg: str) -> None:
        self.passed = False
        self.issues.append(msg)
        logger.error("File validation issue: %s", msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)
        logger.warning("File validation warning: %s", msg)

    def summary(self) -> Dict:
        return {
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
            "details": self.details,
        }


class FileValidator:
    """
    Validates a list of data files for integrity and readability.
    """

    def __init__(self, files: List[Path]) -> None:
        self.files = files

    def validate_all(self) -> Dict[str, FileValidationResult]:
        """
        Validate every file in *self.files*.

        Returns:
            Dict mapping filename → FileValidationResult.
        """
        results: Dict[str, FileValidationResult] = {}
        for fp in self.files:
            print_info(f"Validating file: {fp.name}")
            result = self._validate_single(fp)
            results[fp.name] = result
            if result.passed:
                print_success(f"{fp.name}: validation passed")
            else:
                print_error(f"{fp.name}: validation FAILED — {result.issues}")
        return results

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    def _validate_single(self, path: Path) -> FileValidationResult:
        result = FileValidationResult()

        # 1. Existence
        if not path.exists():
            result.add_issue(f"File does not exist: {path}")
            return result

        # 2. Format
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            result.add_issue(
                f"Unsupported format '{path.suffix}'. "
                f"Supported: {SUPPORTED_FORMATS}"
            )

        # 3. Size
        size_bytes = path.stat().st_size
        result.details["size_bytes"] = size_bytes
        result.details["size_mb"] = round(size_bytes / 1_048_576, 3)
        if size_bytes == 0:
            result.add_issue("File is empty (0 bytes).")
            return result
        if size_bytes < 10:
            result.add_warning("File is suspiciously small (<10 bytes).")

        # 4. Readability (binary sniff)
        if not self._is_readable(path):
            result.add_issue("File appears corrupted or unreadable.")
            return result

        # 5. Encoding (for text-based formats)
        if path.suffix.lower() in (".csv", ".json"):
            enc_info = self._check_encoding(path)
            result.details["detected_encoding"] = enc_info["encoding"]
            result.details["encoding_confidence"] = enc_info["confidence"]
            if enc_info["confidence"] < 0.6:
                result.add_warning(
                    f"Low encoding confidence ({enc_info['confidence']:.0%}) "
                    f"for detected encoding '{enc_info['encoding']}'."
                )

        # 6. CSV header check
        if path.suffix.lower() == ".csv":
            header_ok = self._has_header(path, enc_info.get("encoding", "utf-8"))
            result.details["has_header"] = header_ok
            if not header_ok:
                result.add_warning("CSV file may be missing column headers.")

        return result

    @staticmethod
    def _is_readable(path: Path) -> bool:
        """Try reading the first 1 KB — returns False if binary garbage."""
        try:
            with open(path, "rb") as fh:
                snippet = fh.read(1024)
            # Heuristic: if >30% of bytes are null, likely corrupt
            null_ratio = snippet.count(b"\x00") / max(len(snippet), 1)
            return null_ratio < 0.30
        except OSError:
            return False

    @staticmethod
    def _check_encoding(path: Path, sample_bytes: int = 50_000) -> Dict:
        with open(path, "rb") as fh:
            raw = fh.read(sample_bytes)
        result = chardet.detect(raw)
        return {
            "encoding": result.get("encoding") or "utf-8",
            "confidence": result.get("confidence") or 0.0,
        }

    @staticmethod
    def _has_header(path: Path, encoding: str) -> bool:
        """
        Heuristic: first row should contain mostly non-numeric tokens
        that look like column names.
        """
        try:
            with open(path, "r", encoding=encoding, errors="replace") as fh:
                first_line = fh.readline().strip()
            if not first_line:
                return False
            tokens = first_line.split(",")
            numeric_count = sum(1 for t in tokens if t.strip().lstrip("-").replace(".", "", 1).isdigit())
            return numeric_count < len(tokens) * 0.5
        except Exception:
            return True  # Assume header present if check fails
