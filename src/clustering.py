"""
Clustering algorithms for bike-share trip data.

Implements KMeans, Agglomerative Hierarchical, and DBSCAN clustering
with evaluation metrics.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from typing import Tuple, Dict, List
import matplotlib.pyplot as plt

from src.paths import get_figure_file


def run_kmeans(X: pd.DataFrame,
               k: int = 5,
               n_init: int = 20,
               random_state: int = 42,
               verbose: bool = True) -> Tuple[np.ndarray, KMeans]:
    """
    Run K-Means clustering.

    Args:
        X (pd.DataFrame): Scaled feature matrix
        k (int): Number of clusters
        n_init (int): Number of initializations
        random_state (int): Random seed
        verbose (bool): Print progress

    Returns:
        Tuple[np.ndarray, KMeans]: (cluster_labels, fitted_model)
    """
    if verbose:
        print(f"Running K-Means with k={k}...")

    kmeans = KMeans(
        n_clusters=k,
        init='k-means++',
        n_init=n_init,
        random_state=random_state,
        max_iter=300
    )

    labels = kmeans.fit_predict(X)

    if verbose:
        unique_labels = np.unique(labels)
        print(f"✓ Converged in {kmeans.n_iter_} iterations")
        print(f"  Clusters found: {len(unique_labels)}")
        print(f"  Cluster sizes: {np.bincount(labels)}")

    return labels, kmeans


def run_agglomerative(X: pd.DataFrame,
                      k: int = 5,
                      linkage: str = 'ward',
                      verbose: bool = True) -> Tuple[np.ndarray, AgglomerativeClustering]:
    """
    Run Agglomerative Hierarchical clustering.

    Args:
        X (pd.DataFrame): Scaled feature matrix
        k (int): Number of clusters
        linkage (str): Linkage criterion ('ward', 'complete', 'average')
        verbose (bool): Print progress

    Returns:
        Tuple[np.ndarray, AgglomerativeClustering]: (cluster_labels, fitted_model)
    """
    if verbose:
        print(f"Running Agglomerative clustering with k={k}, linkage={linkage}...")

    agg = AgglomerativeClustering(
        n_clusters=k,
        linkage=linkage
    )

    labels = agg.fit_predict(X)

    if verbose:
        unique_labels = np.unique(labels)
        print(f"✓ Complete")
        print(f"  Clusters found: {len(unique_labels)}")
        print(f"  Cluster sizes: {np.bincount(labels)}")

    return labels, agg


def run_dbscan(X: pd.DataFrame,
               eps: float = 0.5,
               min_samples: int = 10,
               verbose: bool = True) -> Tuple[np.ndarray, DBSCAN]:
    """
    Run DBSCAN clustering.

    Args:
        X (pd.DataFrame): Scaled feature matrix
        eps (float): Maximum distance between samples
        min_samples (int): Minimum samples in neighborhood
        verbose (bool): Print progress

    Returns:
        Tuple[np.ndarray, DBSCAN]: (cluster_labels, fitted_model)
    """
    if verbose:
        print(f"Running DBSCAN with eps={eps}, min_samples={min_samples}...")

    dbscan = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        metric='euclidean'
    )

    labels = dbscan.fit_predict(X)

    if verbose:
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels[unique_labels >= 0])  # Exclude noise (-1)
        n_noise = np.sum(labels == -1)

        print(f"✓ Complete")
        print(f"  Clusters found: {n_clusters}")
        print(f"  Noise points: {n_noise} ({n_noise/len(labels)*100:.1f}%)")
        if n_clusters > 0:
            cluster_sizes = np.bincount(labels[labels >= 0])
            print(f"  Cluster sizes: {cluster_sizes}")

    return labels, dbscan


def compute_metrics(X: pd.DataFrame, labels: np.ndarray, verbose: bool = True) -> Dict[str, float]:
    """
    Compute clustering evaluation metrics.

    Args:
        X (pd.DataFrame): Feature matrix
        labels (np.ndarray): Cluster labels
        verbose (bool): Print metrics

    Returns:
        Dict[str, float]: Evaluation metrics
    """
    # Filter out noise points for DBSCAN
    mask = labels >= 0
    X_clean = X[mask]
    labels_clean = labels[mask]

    # Require at least 2 clusters
    n_clusters = len(np.unique(labels_clean))

    if n_clusters < 2:
        if verbose:
            print("⚠️  Warning: Less than 2 clusters, cannot compute metrics")
        return {
            'silhouette': np.nan,
            'davies_bouldin': np.nan,
            'calinski_harabasz': np.nan,
            'n_clusters': n_clusters
        }

    # Compute metrics
    silhouette = silhouette_score(X_clean, labels_clean)
    db_index = davies_bouldin_score(X_clean, labels_clean)
    ch_index = calinski_harabasz_score(X_clean, labels_clean)

    metrics = {
        'silhouette': silhouette,
        'davies_bouldin': db_index,
        'calinski_harabasz': ch_index,
        'n_clusters': n_clusters
    }

    if verbose:
        print("\n" + "="*60)
        print("CLUSTERING METRICS")
        print("="*60)
        print(f"  Silhouette Score: {silhouette:.4f}")
        print(f"  Davies-Bouldin Index: {db_index:.4f}")
        print(f"  Calinski-Harabasz Index: {ch_index:.1f}")
        print(f"  Number of clusters: {n_clusters}")
        print("="*60 + "\n")

    return metrics


def kmeans_elbow_analysis(X: pd.DataFrame,
                          k_range: List[int] = [3, 4, 5, 6, 7],
                          random_state: int = 42,
                          save: bool = True) -> pd.DataFrame:
    """
    Perform elbow analysis for K-Means.

    Args:
        X (pd.DataFrame): Feature matrix
        k_range (List[int]): Range of k values to test
        random_state (int): Random seed
        save (bool): Save plot

    Returns:
        pd.DataFrame: Results table
    """
    print("="*60)
    print("K-MEANS ELBOW ANALYSIS")
    print("="*60 + "\n")

    results = []

    for k in k_range:
        labels, model = run_kmeans(X, k=k, random_state=random_state, verbose=False)
        metrics = compute_metrics(X, labels, verbose=False)

        results.append({
            'k': k,
            'silhouette': metrics['silhouette'],
            'davies_bouldin': metrics['davies_bouldin'],
            'calinski_harabasz': metrics['calinski_harabasz'],
            'inertia': model.inertia_
        })

        print(f"k={k}: silhouette={metrics['silhouette']:.4f}, DB={metrics['davies_bouldin']:.4f}, CH={metrics['calinski_harabasz']:.1f}")

    results_df = pd.DataFrame(results)

    # Plot elbow curves
    if save:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Silhouette
        axes[0, 0].plot(results_df['k'], results_df['silhouette'], 'o-', linewidth=2, markersize=8)
        axes[0, 0].axhline(0.35, color='red', linestyle='--', label='Target (≥0.35)')
        axes[0, 0].set_xlabel('Number of Clusters (k)')
        axes[0, 0].set_ylabel('Silhouette Score')
        axes[0, 0].set_title('Silhouette Score vs k')
        axes[0, 0].grid(alpha=0.3)
        axes[0, 0].legend()

        # Davies-Bouldin
        axes[0, 1].plot(results_df['k'], results_df['davies_bouldin'], 'o-', linewidth=2, markersize=8, color='orange')
        axes[0, 1].axhline(1.5, color='red', linestyle='--', label='Target (<1.5)')
        axes[0, 1].set_xlabel('Number of Clusters (k)')
        axes[0, 1].set_ylabel('Davies-Bouldin Index')
        axes[0, 1].set_title('Davies-Bouldin Index vs k (lower is better)')
        axes[0, 1].grid(alpha=0.3)
        axes[0, 1].legend()

        # Calinski-Harabasz
        axes[1, 0].plot(results_df['k'], results_df['calinski_harabasz'], 'o-', linewidth=2, markersize=8, color='green')
        axes[1, 0].set_xlabel('Number of Clusters (k)')
        axes[1, 0].set_ylabel('Calinski-Harabasz Index')
        axes[1, 0].set_title('Calinski-Harabasz Index vs k (higher is better)')
        axes[1, 0].grid(alpha=0.3)

        # Inertia
        axes[1, 1].plot(results_df['k'], results_df['inertia'], 'o-', linewidth=2, markersize=8, color='purple')
        axes[1, 1].set_xlabel('Number of Clusters (k)')
        axes[1, 1].set_ylabel('Inertia (Within-cluster sum of squares)')
        axes[1, 1].set_title('Inertia vs k (lower is better)')
        axes[1, 1].grid(alpha=0.3)

        plt.tight_layout()

        filepath = get_figure_file('kmeans_elbow_analysis.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"\n✓ Saved elbow plot: {filepath}")
        plt.close()

    return results_df


def stability_check(X: pd.DataFrame,
                   k: int = 5,
                   n_runs: int = 20,
                   verbose: bool = True) -> Dict[str, float]:
    """
    Check clustering stability across multiple runs.

    Args:
        X (pd.DataFrame): Feature matrix
        k (int): Number of clusters
        n_runs (int): Number of runs
        verbose (bool): Print results

    Returns:
        Dict[str, float]: Stability metrics
    """
    if verbose:
        print(f"\nChecking stability over {n_runs} runs (k={k})...")

    silhouettes = []

    for i in range(n_runs):
        labels, _ = run_kmeans(X, k=k, random_state=42+i, verbose=False)
        metrics = compute_metrics(X, labels, verbose=False)
        silhouettes.append(metrics['silhouette'])

    stability = {
        'mean_silhouette': np.mean(silhouettes),
        'std_silhouette': np.std(silhouettes),
        'min_silhouette': np.min(silhouettes),
        'max_silhouette': np.max(silhouettes)
    }

    if verbose:
        print(f"✓ Silhouette mean={stability['mean_silhouette']:.4f}, std={stability['std_silhouette']:.4f}")
        print(f"  Range: [{stability['min_silhouette']:.4f}, {stability['max_silhouette']:.4f}]")

        if stability['std_silhouette'] < 0.05:
            print("  ✓ Stable (std < 0.05)")
        else:
            print("  ⚠️  Unstable (std ≥ 0.05)")

    return stability


if __name__ == "__main__":
    from src.loaders import load_all_trips
    from src.preprocess import clean_trips, engineer_features, prepare_clustering_features, create_preprocessing_pipeline

    print("="*60)
    print("TESTING CLUSTERING MODULE")
    print("="*60 + "\n")

    # Load and prepare data (10% sample)
    df = load_all_trips(sample_frac=0.1)
    df = clean_trips(df, verbose=False)
    df = engineer_features(df, verbose=False)
    X = prepare_clustering_features(df)
    X_scaled, _ = create_preprocessing_pipeline(X, apply_pca=False, verbose=False)

    print(f"Data shape: {X_scaled.shape}\n")

    # Test K-Means
    labels_km, model_km = run_kmeans(X_scaled, k=5)
    metrics_km = compute_metrics(X_scaled, labels_km)

    # Test Agglomerative
    labels_agg, model_agg = run_agglomerative(X_scaled, k=5)
    metrics_agg = compute_metrics(X_scaled, labels_agg)

    # Test DBSCAN
    labels_db, model_db = run_dbscan(X_scaled, eps=0.5, min_samples=50)
    metrics_db = compute_metrics(X_scaled, labels_db)

    # Elbow analysis
    elbow_results = kmeans_elbow_analysis(X_scaled, k_range=[3, 4, 5, 6], save=True)
    print(f"\nElbow results:\n{elbow_results}")

    # Stability check
    stability = stability_check(X_scaled, k=5, n_runs=10)

    print("\n✓ Clustering module test complete!")
