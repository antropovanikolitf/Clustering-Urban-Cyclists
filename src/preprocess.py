"""
Preprocessing and feature engineering for bike-share trip data.

Handles cleaning, feature derivation, scaling, and pipeline creation.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
from typing import Tuple, Optional

from src.paths import get_processed_file, get_artifact_file
from src.diagnostics import calculate_trip_duration, calculate_trip_distance


def clean_trips(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Clean trip data by removing invalid/outlier records.

    Filters applied:
    - Drop rows with missing coordinates
    - Drop rows with missing station names
    - Drop rows with duration < 1 min or > 180 min
    - Drop rows with negative duration (clock skew)
    - Drop rows with distance > 50 km (GPS errors)

    Args:
        df (pd.DataFrame): Raw trip data
        verbose (bool): Print cleaning stats

    Returns:
        pd.DataFrame: Cleaned trip data
    """
    df = df.copy()
    initial_rows = len(df)

    if verbose:
        print("=" * 60)
        print("DATA CLEANING")
        print("=" * 60)
        print(f"Initial rows: {initial_rows:,}\n")

    # Calculate derived features first
    if 'duration_min' not in df.columns:
        df = calculate_trip_duration(df)
    if 'distance_km' not in df.columns:
        df = calculate_trip_distance(df)

    # Filter 1: Missing coordinates
    before = len(df)
    df = df.dropna(subset=['start_lat', 'start_lng', 'end_lat', 'end_lng'])
    if verbose:
        print(f"✓ Dropped {before - len(df):,} rows with missing coordinates")

    # Filter 2: Missing station names
    before = len(df)
    df = df.dropna(subset=['start_station_name', 'end_station_name'])
    if verbose:
        print(f"✓ Dropped {before - len(df):,} rows with missing station names")

    # Filter 3: Invalid duration
    before = len(df)
    df = df[(df['duration_min'] >= 1) & (df['duration_min'] <= 180)]
    if verbose:
        print(f"✓ Dropped {before - len(df):,} rows with duration <1 min or >180 min")

    # Filter 4: Negative duration (clock skew)
    before = len(df)
    df = df[df['started_at'] <= df['ended_at']]
    if verbose:
        print(f"✓ Dropped {before - len(df):,} rows with negative duration (clock skew)")

    # Filter 5: Extreme distance (GPS errors)
    before = len(df)
    df = df[df['distance_km'] <= 50]
    if verbose:
        print(f"✓ Dropped {before - len(df):,} rows with distance >50 km")

    # Cap outliers at 99th percentile
    duration_cap = df['duration_min'].quantile(0.99)
    distance_cap = df['distance_km'].quantile(0.99)

    before_cap = len(df[df['duration_min'] > duration_cap])
    df.loc[df['duration_min'] > duration_cap, 'duration_min'] = duration_cap
    if verbose and before_cap > 0:
        print(f"✓ Capped {before_cap:,} extreme durations at {duration_cap:.1f} min (99th percentile)")

    before_cap = len(df[df['distance_km'] > distance_cap])
    df.loc[df['distance_km'] > distance_cap, 'distance_km'] = distance_cap
    if verbose and before_cap > 0:
        print(f"✓ Capped {before_cap:,} extreme distances at {distance_cap:.2f} km (99th percentile)")

    if verbose:
        print(f"\nFinal rows: {len(df):,}")
        print(f"Data loss: {(1 - len(df)/initial_rows)*100:.1f}%")
        print("=" * 60 + "\n")

    return df


def engineer_features(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Engineer clustering features from trip data.

    Features created:
    - start_hour: Hour of day (0-23)
    - weekday: Day of week (0=Mon, 6=Sun)
    - is_weekend: Binary (1 if Sat/Sun)
    - is_member: Binary (1 if member)
    - is_round_trip: Binary (1 if start == end station)
    - is_electric: Binary (1 if electric_bike, 0 if classic_bike)

    Args:
        df (pd.DataFrame): Cleaned trip data
        verbose (bool): Print feature info

    Returns:
        pd.DataFrame: Data with engineered features
    """
    df = df.copy()

    if verbose:
        print("=" * 60)
        print("FEATURE ENGINEERING")
        print("=" * 60)

    # Temporal features
    df['start_hour'] = df['started_at'].dt.hour
    df['weekday'] = df['started_at'].dt.weekday  # 0=Monday, 6=Sunday
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)

    if verbose:
        print("✓ Added temporal features: start_hour, weekday, is_weekend")

    # User type
    df['is_member'] = (df['member_casual'] == 'member').astype(int)

    if verbose:
        print("✓ Added user type feature: is_member")

    # Trip pattern
    df['is_round_trip'] = (df['start_station_name'] == df['end_station_name']).astype(int)

    if verbose:
        print("✓ Added trip pattern feature: is_round_trip")

    # Bike type (electric vs classic)
    df['is_electric'] = (df['rideable_type'] == 'electric_bike').astype(int)

    if verbose:
        print("✓ Added bike type feature: is_electric")

    if verbose:
        print(f"\nTotal features for clustering: 8")
        print("  - duration_min (numeric)")
        print("  - distance_km (numeric)")
        print("  - start_hour (numeric)")
        print("  - weekday (numeric)")
        print("  - is_weekend (binary)")
        print("  - is_member (binary)")
        print("  - is_round_trip (binary)")
        print("  - is_electric (binary)")
        print("=" * 60 + "\n")

    return df


def prepare_clustering_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and order features for clustering.

    Args:
        df (pd.DataFrame): Data with engineered features

    Returns:
        pd.DataFrame: Features ready for clustering
    """
    feature_cols = [
        'duration_min',
        'distance_km',
        'start_hour',
        'weekday',
        'is_weekend',
        'is_member',
        'is_round_trip',
        'is_electric'
    ]

    return df[feature_cols].copy()


def create_preprocessing_pipeline(df: pd.DataFrame,
                                   apply_pca: bool = False,
                                   n_components: int = 5,
                                   verbose: bool = True) -> Tuple[pd.DataFrame, dict]:
    """
    Create and apply preprocessing pipeline (scaling + optional PCA).

    Args:
        df (pd.DataFrame): Feature data
        apply_pca (bool): Whether to apply PCA
        n_components (int): Number of PCA components (if apply_pca=True)
        verbose (bool): Print pipeline info

    Returns:
        Tuple[pd.DataFrame, dict]: (transformed_data, pipeline_dict)
    """
    if verbose:
        print("=" * 60)
        print("PREPROCESSING PIPELINE")
        print("=" * 60)

    # Initialize scaler
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)

    if verbose:
        print(f"✓ Applied StandardScaler to {df.shape[1]} features")

    pipeline = {'scaler': scaler}

    # Optional PCA
    if apply_pca:
        pca = PCA(n_components=n_components, random_state=42)
        scaled_data = pca.fit_transform(scaled_data)

        if verbose:
            print(f"✓ Applied PCA: {df.shape[1]} → {n_components} components")
            print(f"  Explained variance: {pca.explained_variance_ratio_.sum()*100:.1f}%")

        pipeline['pca'] = pca
        column_names = [f'PC{i+1}' for i in range(n_components)]
    else:
        column_names = df.columns.tolist()

    # Convert to DataFrame
    transformed_df = pd.DataFrame(scaled_data, columns=column_names, index=df.index)

    if verbose:
        print(f"\nFinal feature shape: {transformed_df.shape}")
        print("=" * 60 + "\n")

    return transformed_df, pipeline


def save_preprocessed_data(df: pd.DataFrame, filename: str = "trips_clean.csv", verbose: bool = True):
    """
    Save cleaned and preprocessed data.

    Args:
        df (pd.DataFrame): Cleaned trip data
        filename (str): Output filename
        verbose (bool): Print save info
    """
    filepath = get_processed_file(filename)
    df.to_csv(filepath, index=False)

    if verbose:
        print(f"✓ Saved processed data: {filepath}")
        print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")


def save_pipeline(pipeline: dict, filename: str = "feature_pipeline.joblib", verbose: bool = True):
    """
    Save preprocessing pipeline for reproducibility.

    Args:
        pipeline (dict): Pipeline objects (scaler, pca)
        filename (str): Output filename
        verbose (bool): Print save info
    """
    filepath = get_artifact_file(filename)
    joblib.dump(pipeline, filepath)

    if verbose:
        print(f"✓ Saved preprocessing pipeline: {filepath}")


if __name__ == "__main__":
    from src.loaders import load_all_trips

    print("=" * 60)
    print("TESTING PREPROCESSING MODULE")
    print("=" * 60 + "\n")

    # Load sample data
    df = load_all_trips(sample_frac=0.1)

    # Clean data
    df_clean = clean_trips(df, verbose=True)

    # Engineer features
    df_features = engineer_features(df_clean, verbose=True)

    # Prepare clustering features
    X = prepare_clustering_features(df_features)
    print(f"Clustering features shape: {X.shape}")
    print(f"\nSample features:\n{X.head()}")

    # Create pipeline (without PCA for testing)
    X_scaled, pipeline = create_preprocessing_pipeline(X, apply_pca=False, verbose=True)

    # Save outputs
    save_preprocessed_data(df_features, verbose=True)
    save_pipeline(pipeline, verbose=True)

    print("\n✓ Preprocessing module test complete!")
