"""
Kaggle Analytics Pipeline — Main Orchestrator
=============================================
Entry point for the end-to-end automated data analytics pipeline.

Usage:
    python -m src.main --url "https://www.kaggle.com/datasets/<owner>/<dataset>"

Or run interactively:
    python -m src.main
"""

import argparse
import sys
import traceback
from pathlib import Path

# ── Ensure project root is on sys.path ────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Pipeline imports ──────────────────────────────────────────────────────────
from config.settings import DATA_DIR, REPORTS_DIR, VISUALIZATIONS_DIR
from src.ingestion.kaggle_downloader import KaggleDownloader
from src.ingestion.data_loader import DataLoader
from src.ingestion.domain_classifier import DomainClassifier
from src.validation.file_validator import FileValidator
from src.validation.data_quality import DataQualityValidator
from src.preprocessing.data_processor import DataProcessor
from src.visualization.plot_engine import PlotEngine
from src.insights.insight_generator import InsightGenerator
from src.insights.report_generator import ReportGenerator
from src.utils.logger import get_logger
from src.utils.console import (
    print_banner, print_section, print_success, print_error,
    print_info, print_kv, print_step, print_warning
)

logger = get_logger(__name__)

TOTAL_STEPS = 10


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Automated Kaggle Dataset Analytics Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main --url "https://www.kaggle.com/datasets/uciml/iris"
  python -m src.main --url "https://www.kaggle.com/datasets/shivamb/netflix-shows"
  python -m src.main  # interactive prompt
        """,
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Full Kaggle dataset URL (e.g. https://www.kaggle.com/datasets/owner/name)",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        default=False,
        help="Skip download if dataset already exists locally.",
    )
    return parser.parse_args()


def prompt_for_url() -> str:
    """Interactively request a Kaggle URL from the user."""
    print_info("No URL provided via --url flag.")
    url = input(
        "\n  Enter Kaggle dataset URL\n"
        "  (e.g. https://www.kaggle.com/datasets/uciml/iris)\n"
        "  > "
    ).strip()
    if not url:
        print_error("No URL entered. Exiting.")
        sys.exit(1)
    return url


def run_pipeline(kaggle_url: str) -> None:
    """
    Execute the full end-to-end analytics pipeline.

    Args:
        kaggle_url: Kaggle dataset URL to process.
    """
    print_banner(
        "KAGGLE AUTOMATED ANALYTICS PIPELINE",
        "End-to-End Data Science | Production Grade",
    )
    logger.info("Pipeline started. URL: %s", kaggle_url)

    # ── STEP 1: Download dataset ───────────────────────────────────────────
    print_step(1, TOTAL_STEPS, "Downloading Kaggle dataset")
    try:
        downloader = KaggleDownloader(kaggle_url, DATA_DIR)
        dataset_dir = downloader.download()
    except Exception as exc:
        print_error(f"Download failed: {exc}")
        logger.exception("Download error")
        sys.exit(1)

    # ── STEP 2: Discover & validate files ─────────────────────────────────
    print_step(2, TOTAL_STEPS, "Discovering and validating files")
    loader = DataLoader(dataset_dir)
    files = loader.discover_files()

    if not files:
        print_error("No supported data files found in the downloaded dataset.")
        sys.exit(1)

    validator = FileValidator(files)
    validation_results = validator.validate_all()

    valid_files = [
        fp for fp in files
        if validation_results.get(fp.name, None) and
           validation_results[fp.name].passed
    ]
    if not valid_files:
        print_error("All discovered files failed validation. Cannot proceed.")
        sys.exit(1)

    # ── STEP 3: Load primary file ──────────────────────────────────────────
    print_step(3, TOTAL_STEPS, "Loading dataset into memory")
    primary_file = loader.select_primary_file(valid_files)
    print_info(f"Selected primary file: {primary_file.name}")

    try:
        raw_df, metadata = loader.load(primary_file)
    except Exception as exc:
        print_error(f"Could not load file: {exc}")
        logger.exception("Load error")
        sys.exit(1)

    # ── STEP 4: Domain classification ─────────────────────────────────────
    print_step(4, TOTAL_STEPS, "Classifying dataset domain")
    classifier = DomainClassifier(raw_df)
    domain, domain_scores = classifier.classify()
    print_kv("Top domain scores", str(dict(list(domain_scores.items())[:4])))

    # ── STEP 5: Data quality validation ───────────────────────────────────
    print_step(5, TOTAL_STEPS, "Running data quality assessment")
    quality_validator = DataQualityValidator(raw_df)
    quality_report = quality_validator.run()
    quality_dict = quality_report.to_dict()

    # ── STEP 6: Visualisations BEFORE processing ───────────────────────────
    print_step(6, TOTAL_STEPS, "Generating pre-processing visualisations")
    plot_engine_before = PlotEngine(raw_df, stage="before", domain=domain)
    plots_before = plot_engine_before.generate_all()

    # ── STEP 7: Preprocessing ─────────────────────────────────────────────
    print_step(7, TOTAL_STEPS, "Running advanced data preprocessing")
    processor = DataProcessor(raw_df, quality_report)
    processed_df = processor.process()
    processing_log = processor.get_processing_log()

    # ── Save cleaned dataset ───────────────────────────────────────────────
    cleaned_path = DATA_DIR / "cleaned_dataset.csv"
    try:
        processed_df.to_csv(cleaned_path, index=False)
        print_success(f"Cleaned dataset saved: {cleaned_path}")
    except Exception as exc:
        print_warning(f"Could not save cleaned dataset: {exc}")

    # ── STEP 8: Visualisations AFTER processing ────────────────────────────
    print_step(8, TOTAL_STEPS, "Generating post-processing visualisations")
    plot_engine_after = PlotEngine(processed_df, stage="after", domain=domain)
    plots_after = plot_engine_after.generate_all()

    # ── STEP 9: Business insight generation ───────────────────────────────
    print_step(9, TOTAL_STEPS, "Generating business insights and conclusions")
    insight_gen = InsightGenerator(
        raw_df=raw_df,
        processed_df=processed_df,
        domain=domain,
        quality_report_dict=quality_dict,
        metadata=metadata,
    )
    insights = insight_gen.generate()

    # ── STEP 10: Report generation ─────────────────────────────────────────
    print_step(10, TOTAL_STEPS, "Generating final analytical report")
    report_gen = ReportGenerator(
        insights=insights,
        quality_report=quality_dict,
        metadata=metadata,
        plot_paths_before=plots_before,
        plot_paths_after=plots_after,
        processing_log=processing_log,
    )
    report_paths = report_gen.generate()

    # ── Pipeline completion summary ────────────────────────────────────────
    _print_summary(
        domain=domain,
        metadata=metadata,
        quality_dict=quality_dict,
        report_paths=report_paths,
        cleaned_path=cleaned_path,
        n_plots=len(plots_before) + len(plots_after),
    )


def _print_summary(
    domain: str,
    metadata: dict,
    quality_dict: dict,
    report_paths: dict,
    cleaned_path: Path,
    n_plots: int,
) -> None:
    """Print a final pipeline completion summary."""
    print_section("PIPELINE COMPLETE — OUTPUT SUMMARY")
    print_kv("Domain Detected",          domain)
    print_kv("Rows Processed",           f"{metadata.get('rows', 0):,}")
    print_kv("Columns (original)",       str(metadata.get('columns', 0)))
    print_kv("Quality Score",            f"{quality_dict.get('overall_quality_score', 'N/A')}/100")
    print_kv("Charts Generated",         str(n_plots))
    print_kv("Cleaned Dataset",          str(cleaned_path))
    print_kv("HTML Report",              str(report_paths.get("html", "N/A")))
    print_kv("TXT Report",               str(report_paths.get("txt", "N/A")))
    print_kv("JSON Report",              str(report_paths.get("json", "N/A")))
    print_kv("Visualisations Directory", str(VISUALIZATIONS_DIR))
    print()
    print_success(
        "All outputs saved successfully. Open the HTML report in a browser for the full dashboard."
    )
    logger.info("Pipeline completed successfully.")


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    kaggle_url = args.url or prompt_for_url()

    try:
        run_pipeline(kaggle_url)
    except KeyboardInterrupt:
        print_error("\nPipeline interrupted by user.")
        sys.exit(130)
    except Exception as exc:
        print_error(f"Unexpected pipeline error: {exc}")
        traceback.print_exc()
        logger.exception("Unhandled pipeline exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
