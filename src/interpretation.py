"""
Cluster interpretation and visualization utilities.

Functions for analyzing cluster characteristics and generating
interpretable visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional

from src.paths import get_figure_file


def describe_clusters(df: pd.DataFrame,
                      labels: np.ndarray,
                      feature_cols: List[str] = None,
                      verbose: bool = True) -> pd.DataFrame:
    """
    Compute cluster statistics (mean values per cluster).

    Args:
        df (pd.DataFrame): Data with features
        labels (np.ndarray): Cluster labels
        feature_cols (List[str], optional): Columns to analyze. If None, use all numeric.
        verbose (bool): Print summary

    Returns:
        pd.DataFrame: Cluster profiles (mean values)
    """
    df_temp = df.copy()
    df_temp['cluster'] = labels

    if feature_cols is None:
        feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Compute means per cluster
    cluster_profiles = df_temp.groupby('cluster')[feature_cols].mean()

    # Add cluster sizes
    cluster_profiles['size'] = df_temp['cluster'].value_counts().sort_index()
    cluster_profiles['pct'] = (cluster_profiles['size'] / len(df) * 100).round(1)

    if verbose:
        print("="*60)
        print("CLUSTER PROFILES")
        print("="*60)
        print(cluster_profiles)
        print("="*60 + "\n")

    return cluster_profiles


def plot_cluster_profiles(df: pd.DataFrame,
                          labels: np.ndarray,
                          feature_cols: List[str] = None,
                          save: bool = True) -> None:
    """
    Plot heatmap of cluster profiles.

    Args:
        df (pd.DataFrame): Data with features
        labels (np.ndarray): Cluster labels
        feature_cols (List[str], optional): Features to plot
        save (bool): Save figure
    """
    profiles = describe_clusters(df, labels, feature_cols, verbose=False)

    # Drop size/pct for heatmap
    heatmap_data = profiles.drop(columns=['size', 'pct'], errors='ignore')

    # Normalize for heatmap (z-score)
    heatmap_normalized = (heatmap_data - heatmap_data.mean()) / heatmap_data.std()

    # Create figure with custom settings (no seaborn to match requirements)
    fig, ax = plt.subplots(figsize=(12, 6))

    # Manual heatmap
    im = ax.imshow(heatmap_normalized.values, aspect='auto', cmap='RdBu_r', vmin=-2, vmax=2)

    # Set ticks
    ax.set_xticks(np.arange(len(heatmap_normalized.columns)))
    ax.set_yticks(np.arange(len(heatmap_normalized.index)))
    ax.set_xticklabels(heatmap_normalized.columns, rotation=45, ha='right')
    ax.set_yticklabels([f'Cluster {i}' for i in heatmap_normalized.index])

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Normalized Value (z-score)', rotation=270, labelpad=20)

    # Add values as text
    for i in range(len(heatmap_normalized.index)):
        for j in range(len(heatmap_normalized.columns)):
            text = ax.text(j, i, f'{heatmap_normalized.values[i, j]:.1f}',
                          ha="center", va="center", color="black", fontsize=9)

    ax.set_title('Cluster Profiles Heatmap (Normalized Features)', fontsize=14, pad=10)
    plt.tight_layout()

    if save:
        filepath = get_figure_file('cluster_profile_heatmap.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_cluster_distributions(df: pd.DataFrame,
                               labels: np.ndarray,
                               feature: str = 'duration_min',
                               save: bool = True) -> None:
    """
    Plot boxplot of feature distribution per cluster.

    Args:
        df (pd.DataFrame): Data with features
        labels (np.ndarray): Cluster labels
        feature (str): Feature to plot
        save (bool): Save figure
    """
    df_temp = df.copy()
    df_temp['cluster'] = labels

    # Filter out noise if present
    df_temp = df_temp[df_temp['cluster'] >= 0]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create boxplot data
    cluster_ids = sorted(df_temp['cluster'].unique())
    data_by_cluster = [df_temp[df_temp['cluster'] == c][feature].values for c in cluster_ids]

    bp = ax.boxplot(data_by_cluster, labels=[f'C{c}' for c in cluster_ids],
                    patch_artist=True, showmeans=True)

    # Color boxes
    colors = plt.cm.Set3(np.linspace(0, 1, len(cluster_ids)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    ax.set_xlabel('Cluster')
    ax.set_ylabel(feature.replace('_', ' ').title())
    ax.set_title(f'{feature.replace("_", " ").title()} Distribution by Cluster')
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()

    if save:
        filepath = get_figure_file(f'cluster_distribution_{feature}.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_hourly_weekday_heatmap(df: pd.DataFrame,
                                labels: np.ndarray,
                                cluster_id: int,
                                save: bool = True) -> None:
    """
    Plot hour × weekday heatmap for a specific cluster.

    Args:
        df (pd.DataFrame): Data with start_hour and weekday features
        labels (np.ndarray): Cluster labels
        cluster_id (int): Cluster to visualize
        save (bool): Save figure
    """
    df_temp = df.copy()
    df_temp['cluster'] = labels

    # Filter to cluster
    cluster_data = df_temp[df_temp['cluster'] == cluster_id]

    # Create hour × weekday matrix
    heatmap_data = cluster_data.groupby(['weekday', 'start_hour']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 6))

    im = ax.imshow(heatmap_data.values, aspect='auto', cmap='YlOrRd', interpolation='nearest')

    # Set ticks
    ax.set_xticks(np.arange(24))
    ax.set_yticks(np.arange(7))
    ax.set_xticklabels(range(24))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Day of Week')
    ax.set_title(f'Cluster {cluster_id}: Trip Frequency by Hour × Weekday')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Trip Count', rotation=270, labelpad=20)

    plt.tight_layout()

    if save:
        filepath = get_figure_file(f'cluster_{cluster_id}_hourly_weekday.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def interpret_clusters(profiles: pd.DataFrame,
                       verbose: bool = True) -> Dict[int, str]:
    """
    Automatically interpret cluster behavior based on profiles.

    Args:
        profiles (pd.DataFrame): Cluster profiles from describe_clusters()
        verbose (bool): Print interpretations

    Returns:
        Dict[int, str]: Cluster ID → interpretation
    """
    interpretations = {}

    for cluster_id in profiles.index:
        row = profiles.loc[cluster_id]

        # Extract key features
        duration = row.get('duration_min', 0)
        distance = row.get('distance_km', 0)
        hour = row.get('start_hour', 12)
        is_weekend = row.get('is_weekend', 0)
        is_member = row.get('is_member', 0.5)
        is_round_trip = row.get('is_round_trip', 0)

        # Interpretation logic
        if is_member > 0.7 and is_weekend < 0.3 and (7 <= hour <= 9 or 17 <= hour <= 19):
            interpretation = "Weekday Commuters (AM/PM peaks, members, short trips)"
        elif is_weekend > 0.5 and duration > 25 and is_member < 0.5:
            interpretation = "Weekend Leisure/Tourists (long trips, casual users)"
        elif duration < 10 and distance < 2:
            interpretation = "Last-Mile Connectors (very short, near transit)"
        elif is_round_trip > 0.3:
            interpretation = "Leisure Loops (round trips, parks/attractions)"
        elif is_member > 0.6 and is_weekend < 0.5:
            interpretation = "Regular Users/Off-Peak Commuters"
        else:
            interpretation = "Mixed/Casual Riders"

        interpretations[cluster_id] = interpretation

    if verbose:
        print("="*60)
        print("CLUSTER INTERPRETATIONS")
        print("="*60)
        for cluster_id, interp in interpretations.items():
            size = profiles.loc[cluster_id, 'size']
            pct = profiles.loc[cluster_id, 'pct']
            print(f"Cluster {cluster_id} ({int(size):,} trips, {pct}%): {interp}")
        print("="*60 + "\n")

    return interpretations


def plot_cluster_comparison_table(results_dict: Dict[str, Dict],
                                  save: bool = True) -> pd.DataFrame:
    """
    Create comparison table of algorithm results.

    Args:
        results_dict (Dict[str, Dict]): {algorithm_name: {k, silhouette, db, ch, runtime}}
        save (bool): Save as CSV

    Returns:
        pd.DataFrame: Comparison table
    """
    rows = []

    for algo_name, metrics in results_dict.items():
        rows.append({
            'Algorithm': algo_name,
            'k': metrics.get('k', metrics.get('n_clusters', '?')),
            'Silhouette': f"{metrics.get('silhouette', np.nan):.4f}",
            'DB Index': f"{metrics.get('davies_bouldin', np.nan):.4f}",
            'CH Index': f"{metrics.get('calinski_harabasz', np.nan):.1f}",
            'Runtime (s)': f"{metrics.get('runtime', 0):.2f}"
        })

    comparison_df = pd.DataFrame(rows)

    print("="*60)
    print("ALGORITHM COMPARISON")
    print("="*60)
    print(comparison_df.to_string(index=False))
    print("="*60 + "\n")

    if save:
        from src.paths import REPORTS_DIR
        filepath = REPORTS_DIR / 'cluster_comparison_table.csv'
        comparison_df.to_csv(filepath, index=False)
        print(f"✓ Saved: {filepath}\n")

    return comparison_df


if __name__ == "__main__":
    from src.loaders import load_all_trips
    from src.preprocess import clean_trips, engineer_features, prepare_clustering_features, create_preprocessing_pipeline
    from src.clustering import run_kmeans

    print("="*60)
    print("TESTING INTERPRETATION MODULE")
    print("="*60 + "\n")

    # Load and prepare data (10% sample)
    df = load_all_trips(sample_frac=0.1)
    df = clean_trips(df, verbose=False)
    df = engineer_features(df, verbose=False)
    X = prepare_clustering_features(df)
    X_scaled, _ = create_preprocessing_pipeline(X, apply_pca=False, verbose=False)

    # Run clustering
    labels, _ = run_kmeans(X_scaled, k=5, verbose=False)

    # Describe clusters
    profiles = describe_clusters(df, labels)

    # Interpret
    interpretations = interpret_clusters(profiles)

    # Visualizations
    plot_cluster_profiles(df, labels, save=True)
    plot_cluster_distributions(df, labels, feature='duration_min', save=True)
    plot_cluster_distributions(df, labels, feature='distance_km', save=True)
    plot_hourly_weekday_heatmap(df, labels, cluster_id=0, save=True)

    print("\n✓ Interpretation module test complete!")
