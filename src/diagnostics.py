"""
Data diagnostics and quality checks for bike-share trip data.

Provides functions for EDA, missingness analysis, outlier detection,
and visualization.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional
from pathlib import Path

from src.paths import get_figure_file


def calculate_trip_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trip duration in minutes.

    Args:
        df (pd.DataFrame): Trip data with started_at, ended_at

    Returns:
        pd.DataFrame: Data with duration_min column added
    """
    df = df.copy()
    df['duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
    return df


def calculate_trip_distance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate trip distance using Haversine formula.

    Args:
        df (pd.DataFrame): Trip data with start/end lat/lng

    Returns:
        pd.DataFrame: Data with distance_km column added
    """
    df = df.copy()

    # Haversine formula
    lat1 = np.radians(df['start_lat'])
    lon1 = np.radians(df['start_lng'])
    lat2 = np.radians(df['end_lat'])
    lon2 = np.radians(df['end_lng'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # Earth radius in km
    r = 6371

    df['distance_km'] = c * r

    return df


def check_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze missing data patterns.

    Args:
        df (pd.DataFrame): Trip data

    Returns:
        pd.DataFrame: Missing data summary
    """
    missing = pd.DataFrame({
        'column': df.columns,
        'missing_count': df.isna().sum().values,
        'missing_pct': (df.isna().sum().values / len(df) * 100).round(2)
    })

    missing = missing[missing['missing_count'] > 0].sort_values('missing_count', ascending=False)

    return missing


def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
    """
    Detect outliers in a numeric column.

    Args:
        df (pd.DataFrame): Data
        column (str): Column to check
        method (str): 'iqr' or 'zscore'

    Returns:
        pd.Series: Boolean mask of outliers
    """
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return (df[column] < lower) | (df[column] > upper)

    elif method == 'zscore':
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        return z_scores > 3

    else:
        raise ValueError(f"Unknown method: {method}")


def plot_duration_distribution(df: pd.DataFrame, save: bool = True) -> None:
    """
    Plot trip duration distribution.

    Args:
        df (pd.DataFrame): Trip data with duration_min
        save (bool): Save figure to reports/figures/
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(df['duration_min'].dropna(), bins=100, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Duration (minutes)')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Trip Duration Distribution (All Data)')
    axes[0].axvline(df['duration_min'].median(), color='red', linestyle='--',
                    label=f'Median: {df["duration_min"].median():.1f} min')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Filtered histogram (reasonable range)
    reasonable = df[(df['duration_min'] >= 1) & (df['duration_min'] <= 60)]
    axes[1].hist(reasonable['duration_min'], bins=60, edgecolor='black', alpha=0.7, color='green')
    axes[1].set_xlabel('Duration (minutes)')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Trip Duration Distribution (1-60 min)')
    axes[1].axvline(reasonable['duration_min'].median(), color='red', linestyle='--',
                    label=f'Median: {reasonable["duration_min"].median():.1f} min')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()

    if save:
        filepath = get_figure_file('duration_histogram.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_hourly_distribution(df: pd.DataFrame, save: bool = True) -> None:
    """
    Plot trip distribution by hour of day.

    Args:
        df (pd.DataFrame): Trip data with started_at
        save (bool): Save figure to reports/figures/
    """
    df = df.copy()
    df['start_hour'] = df['started_at'].dt.hour

    hourly_counts = df['start_hour'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(hourly_counts.index, hourly_counts.values, edgecolor='black', alpha=0.7, color='steelblue')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Number of Trips')
    ax.set_title('Trip Distribution by Hour of Day')
    ax.set_xticks(range(24))
    ax.grid(alpha=0.3, axis='y')

    # Highlight peak hours
    ax.axvspan(7, 9, alpha=0.2, color='orange', label='AM Peak (7-9)')
    ax.axvspan(17, 19, alpha=0.2, color='red', label='PM Peak (17-19)')
    ax.legend()

    plt.tight_layout()

    if save:
        filepath = get_figure_file('hourly_distribution.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_weekday_distribution(df: pd.DataFrame, save: bool = True) -> None:
    """
    Plot trip distribution by day of week.

    Args:
        df (pd.DataFrame): Trip data with started_at
        save (bool): Save figure to reports/figures/
    """
    df = df.copy()
    df['weekday'] = df['started_at'].dt.day_name()

    # Order days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_counts = df['weekday'].value_counts().reindex(day_order)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['steelblue']*5 + ['lightcoral']*2  # Weekdays blue, weekends red
    ax.bar(weekday_counts.index, weekday_counts.values, edgecolor='black', alpha=0.7, color=colors)
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Number of Trips')
    ax.set_title('Trip Distribution by Day of Week')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()

    if save:
        filepath = get_figure_file('weekday_distribution.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_distance_distribution(df: pd.DataFrame, save: bool = True) -> None:
    """
    Plot trip distance distribution.

    Args:
        df (pd.DataFrame): Trip data with distance_km
        save (bool): Save figure to reports/figures/
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram (all data)
    axes[0].hist(df['distance_km'].dropna(), bins=100, edgecolor='black', alpha=0.7, color='purple')
    axes[0].set_xlabel('Distance (km)')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Trip Distance Distribution (All Data)')
    axes[0].axvline(df['distance_km'].median(), color='red', linestyle='--',
                    label=f'Median: {df["distance_km"].median():.2f} km')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Filtered histogram (reasonable range)
    reasonable = df[(df['distance_km'] >= 0.1) & (df['distance_km'] <= 10)]
    axes[1].hist(reasonable['distance_km'], bins=50, edgecolor='black', alpha=0.7, color='teal')
    axes[1].set_xlabel('Distance (km)')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Trip Distance Distribution (0.1-10 km)')
    axes[1].axvline(reasonable['distance_km'].median(), color='red', linestyle='--',
                    label=f'Median: {reasonable["distance_km"].median():.2f} km')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()

    if save:
        filepath = get_figure_file('distance_histogram.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def generate_data_quality_report(df: pd.DataFrame) -> dict:
    """
    Generate comprehensive data quality report.

    Args:
        df (pd.DataFrame): Trip data

    Returns:
        dict: Quality metrics
    """
    report = {}

    # Basic stats
    report['total_rows'] = len(df)
    report['total_columns'] = len(df.columns)
    report['date_range'] = (df['started_at'].min(), df['started_at'].max())

    # Missing data
    missing = check_missing_data(df)
    report['missing_summary'] = missing.to_dict('records') if len(missing) > 0 else []

    # Duration issues
    if 'duration_min' in df.columns:
        report['negative_duration'] = (df['duration_min'] < 0).sum()
        report['zero_duration'] = (df['duration_min'] == 0).sum()
        report['extreme_duration'] = (df['duration_min'] > 180).sum()  # >3 hours

    # Coordinate issues
    report['missing_coords'] = df[['start_lat', 'start_lng', 'end_lat', 'end_lng']].isna().any(axis=1).sum()

    # User type distribution
    report['member_casual_counts'] = df['member_casual'].value_counts().to_dict()

    return report


if __name__ == "__main__":
    from src.loaders import load_all_trips

    print("=" * 60)
    print("TESTING DIAGNOSTICS MODULE")
    print("=" * 60 + "\n")

    # Load sample data
    df = load_all_trips(sample_frac=0.1)

    # Add derived features
    print("\nCalculating derived features...")
    df = calculate_trip_duration(df)
    df = calculate_trip_distance(df)
    print("✓ Added: duration_min, distance_km")

    # Quality report
    print("\n" + "=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)
    report = generate_data_quality_report(df)
    for key, value in report.items():
        print(f"  {key}: {value}")

    # Generate plots
    print("\n" + "=" * 60)
    print("GENERATING DIAGNOSTIC PLOTS")
    print("=" * 60)
    plot_duration_distribution(df, save=True)
    plot_hourly_distribution(df, save=True)
    plot_weekday_distribution(df, save=True)
    plot_distance_distribution(df, save=True)
    print("\n✓ All plots saved to reports/figures/")
