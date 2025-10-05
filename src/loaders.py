"""
Data loading utilities for CitiBike trip data.

Handles reading, merging, and validating bike-share CSV files.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional
import warnings

from src.paths import get_raw_csv_files


# Expected schema (post-2020 CitiBike format)
EXPECTED_COLUMNS = {
    'ride_id': 'object',
    'rideable_type': 'object',
    'started_at': 'object',  # Will parse to datetime
    'ended_at': 'object',    # Will parse to datetime
    'start_station_name': 'object',
    'start_station_id': 'object',
    'end_station_name': 'object',
    'end_station_id': 'object',
    'start_lat': 'float64',
    'start_lng': 'float64',
    'end_lat': 'float64',
    'end_lng': 'float64',
    'member_casual': 'object'
}


def load_single_csv(filepath: Path, verbose: bool = True) -> pd.DataFrame:
    """
    Load a single CSV file with error handling.

    Args:
        filepath (Path): Path to CSV file
        verbose (bool): Print loading info

    Returns:
        pd.DataFrame: Loaded data
    """
    if verbose:
        print(f"Loading {filepath.name}...", end=" ")

    try:
        df = pd.read_csv(filepath, low_memory=False)
        if verbose:
            print(f"✓ {len(df):,} rows")
        return df
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def validate_schema(df: pd.DataFrame, filepath: Path) -> pd.DataFrame:
    """
    Validate dataframe has expected columns.

    Args:
        df (pd.DataFrame): Data to validate
        filepath (Path): Source file (for error messages)

    Returns:
        pd.DataFrame: Validated data with selected columns
    """
    missing_cols = set(EXPECTED_COLUMNS.keys()) - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"File {filepath.name} missing columns: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )

    # Select only expected columns (drop any extras)
    df = df[list(EXPECTED_COLUMNS.keys())].copy()

    return df


def parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse timestamp columns to datetime.

    Args:
        df (pd.DataFrame): Data with string timestamps

    Returns:
        pd.DataFrame: Data with parsed datetimes
    """
    df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
    df['ended_at'] = pd.to_datetime(df['ended_at'], errors='coerce')
    return df


def load_all_trips(sample_frac: Optional[float] = None, random_state: int = 42) -> pd.DataFrame:
    """
    Load and merge all CSV files from raw data directory.

    Args:
        sample_frac (float, optional): Fraction of data to sample (0-1).
                                       None = load all data.
        random_state (int): Random seed for sampling

    Returns:
        pd.DataFrame: Merged trip data
    """
    csv_files = get_raw_csv_files()

    # Filter out non-trip data files (provenance, metadata, etc.)
    trip_files = [f for f in csv_files if 'citibike-tripdata' in f.name.lower() or f.name.startswith('202')]

    print(f"Found {len(trip_files)} trip data CSV files to load (skipped {len(csv_files) - len(trip_files)} metadata files)\n")

    dfs = []

    for filepath in trip_files:
        df = load_single_csv(filepath, verbose=True)
        df = validate_schema(df, filepath)
        dfs.append(df)

    # Merge all dataframes
    print(f"\nMerging {len(dfs)} files...")
    merged = pd.concat(dfs, ignore_index=True)
    print(f"✓ Total rows: {len(merged):,}")

    # Parse datetimes
    print("Parsing datetime columns...")
    merged = parse_datetimes(merged)

    # Optional sampling (for faster development)
    if sample_frac is not None:
        original_size = len(merged)
        merged = merged.sample(frac=sample_frac, random_state=random_state)
        print(f"✓ Sampled {sample_frac*100:.1f}% → {len(merged):,} rows ({original_size:,} → {len(merged):,})")

    print(f"\n✓ Loaded dataset: {merged.shape[0]:,} rows × {merged.shape[1]} columns")
    print(f"  Date range: {merged['started_at'].min()} to {merged['started_at'].max()}")

    return merged


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Get summary statistics about the dataset.

    Args:
        df (pd.DataFrame): Trip data

    Returns:
        dict: Summary statistics
    """
    stats = {
        'total_trips': len(df),
        'date_range': (df['started_at'].min(), df['started_at'].max()),
        'unique_start_stations': df['start_station_name'].nunique(),
        'unique_end_stations': df['end_station_name'].nunique(),
        'member_trips': (df['member_casual'] == 'member').sum(),
        'casual_trips': (df['member_casual'] == 'casual').sum(),
        'missing_start_coords': df['start_lat'].isna().sum(),
        'missing_end_coords': df['end_lat'].isna().sum(),
        'missing_start_station': df['start_station_name'].isna().sum(),
    }

    return stats


if __name__ == "__main__":
    # Test loading
    print("=" * 60)
    print("TESTING DATA LOADER")
    print("=" * 60 + "\n")

    # Load data (sample 10% for testing)
    df = load_all_trips(sample_frac=0.1)

    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    stats = get_summary_stats(df)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("SAMPLE DATA")
    print("=" * 60)
    print(df.head(3))
