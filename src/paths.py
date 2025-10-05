"""
Robust path handling for Clustering Urban Bike-Share Users project.

This module provides centralized path management to ensure all scripts
can reliably locate data, artifacts, and output directories regardless
of where they're executed from.
"""

from pathlib import Path

# Project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw" / "bikeshare"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Output directories
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

# Ensure output directories exist
INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def get_raw_csv_files():
    """
    Get list of all CSV files in raw data directory.

    Returns:
        list: Sorted list of Path objects pointing to CSV files
    """
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"Raw data directory not found: {RAW_DATA_DIR}")

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DATA_DIR}")

    return csv_files


def get_processed_file(filename="trips_clean.csv"):
    """
    Get path to processed data file.

    Args:
        filename (str): Name of processed file

    Returns:
        Path: Full path to processed file
    """
    return PROCESSED_DATA_DIR / filename


def get_artifact_file(filename):
    """
    Get path to artifact file (models, pipelines).

    Args:
        filename (str): Name of artifact file

    Returns:
        Path: Full path to artifact file
    """
    return ARTIFACTS_DIR / filename


def get_figure_file(filename):
    """
    Get path to figure file.

    Args:
        filename (str): Name of figure file

    Returns:
        Path: Full path to figure file
    """
    return FIGURES_DIR / filename


if __name__ == "__main__":
    # Test path discovery
    print("Project paths:")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  Raw data: {RAW_DATA_DIR}")
    print(f"  Processed data: {PROCESSED_DATA_DIR}")
    print(f"  Figures: {FIGURES_DIR}")
    print(f"  Artifacts: {ARTIFACTS_DIR}")
    print(f"\nRaw CSV files found: {len(get_raw_csv_files())}")
    for f in get_raw_csv_files()[:3]:
        print(f"  - {f.name}")
    if len(get_raw_csv_files()) > 3:
        print(f"  ... and {len(get_raw_csv_files()) - 3} more")
