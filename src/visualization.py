"""
Advanced visualization utilities for cluster evaluation.

Provides PCA/t-SNE projections, spatial maps, and characteristic tables.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from typing import Optional, Tuple
import warnings

from src.paths import get_figure_file


def plot_pca_projection(X: pd.DataFrame,
                       labels: np.ndarray,
                       cluster_names: dict = None,
                       save: bool = True) -> Tuple[np.ndarray, PCA]:
    """
    Project data to 2D using PCA and plot clusters.

    Args:
        X (pd.DataFrame): Scaled feature matrix
        labels (np.ndarray): Cluster labels
        cluster_names (dict, optional): {cluster_id: name} for legend
        save (bool): Save figure

    Returns:
        Tuple[np.ndarray, PCA]: (projected_data, pca_model)
    """
    print("Performing PCA projection to 2D...")

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X)

    # Filter out noise if present
    mask = labels >= 0
    X_plot = X_pca[mask]
    labels_plot = labels[mask]

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))

    unique_labels = np.unique(labels_plot)
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))

    for idx, label in enumerate(unique_labels):
        cluster_mask = labels_plot == label
        label_text = cluster_names.get(label, f'Cluster {label}') if cluster_names else f'Cluster {label}'

        ax.scatter(X_plot[cluster_mask, 0],
                  X_plot[cluster_mask, 1],
                  c=[colors[idx]],
                  label=label_text,
                  alpha=0.6,
                  s=20,
                  edgecolors='black',
                  linewidth=0.3)

    # Add noise points if any
    if np.sum(~mask) > 0:
        X_noise = X_pca[~mask]
        ax.scatter(X_noise[:, 0], X_noise[:, 1],
                  c='gray', label='Noise',
                  alpha=0.3, s=10, marker='x')

    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
    ax.set_title(f'PCA Projection of Clusters (Total variance: {pca.explained_variance_ratio_.sum()*100:.1f}%)')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(alpha=0.3)

    plt.tight_layout()

    if save:
        filepath = get_figure_file('pca_clusters_2d.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()

    print(f"✓ PCA complete: {pca.explained_variance_ratio_[0]*100:.1f}% + {pca.explained_variance_ratio_[1]*100:.1f}% = {pca.explained_variance_ratio_.sum()*100:.1f}% variance explained")

    return X_pca, pca


def plot_tsne_projection(X: pd.DataFrame,
                        labels: np.ndarray,
                        cluster_names: dict = None,
                        perplexity: int = 30,
                        n_iter: int = 1000,
                        save: bool = True) -> np.ndarray:
    """
    Project data to 2D using t-SNE and plot clusters (optional).

    Args:
        X (pd.DataFrame): Scaled feature matrix
        labels (np.ndarray): Cluster labels
        cluster_names (dict, optional): {cluster_id: name}
        perplexity (int): t-SNE perplexity parameter
        n_iter (int): Number of iterations
        save (bool): Save figure

    Returns:
        np.ndarray: t-SNE projected data
    """
    print(f"Performing t-SNE projection to 2D (perplexity={perplexity}, n_iter={n_iter})...")
    print("  (This may take a few minutes for large datasets...)")

    # Sample if dataset is very large (t-SNE is O(n²))
    if len(X) > 50000:
        print(f"  Dataset large ({len(X):,} points), sampling 50,000 for t-SNE...")
        sample_idx = np.random.choice(len(X), 50000, replace=False)
        X_sample = X.iloc[sample_idx].values
        labels_sample = labels[sample_idx]
    else:
        X_sample = X.values
        labels_sample = labels
        sample_idx = None

    tsne = TSNE(n_components=2, perplexity=perplexity, n_iter=n_iter, random_state=42, verbose=0)
    X_tsne = tsne.fit_transform(X_sample)

    # Filter out noise if present
    mask = labels_sample >= 0
    X_plot = X_tsne[mask]
    labels_plot = labels_sample[mask]

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))

    unique_labels = np.unique(labels_plot)
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))

    for idx, label in enumerate(unique_labels):
        cluster_mask = labels_plot == label
        label_text = cluster_names.get(label, f'Cluster {label}') if cluster_names else f'Cluster {label}'

        ax.scatter(X_plot[cluster_mask, 0],
                  X_plot[cluster_mask, 1],
                  c=[colors[idx]],
                  label=label_text,
                  alpha=0.6,
                  s=20,
                  edgecolors='black',
                  linewidth=0.3)

    # Add noise points if any
    if np.sum(~mask) > 0:
        X_noise = X_tsne[~mask]
        ax.scatter(X_noise[:, 0], X_noise[:, 1],
                  c='gray', label='Noise',
                  alpha=0.3, s=10, marker='x')

    ax.set_xlabel('t-SNE Dimension 1')
    ax.set_ylabel('t-SNE Dimension 2')
    ax.set_title('t-SNE Projection of Clusters')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(alpha=0.3)

    plt.tight_layout()

    if save:
        filepath = get_figure_file('tsne_clusters_2d.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()

    print("✓ t-SNE complete")

    # Return full t-SNE if not sampled, else return sample
    if sample_idx is not None:
        print("  Note: Plot shows 50,000 sampled points")

    return X_tsne


def create_characteristics_table(df: pd.DataFrame,
                                 labels: np.ndarray,
                                 interpretations: dict = None,
                                 save: bool = True) -> pd.DataFrame:
    """
    Create comprehensive cluster characteristics summary table.

    Args:
        df (pd.DataFrame): Data with all features
        labels (np.ndarray): Cluster labels
        interpretations (dict, optional): {cluster_id: interpretation}
        save (bool): Save as CSV

    Returns:
        pd.DataFrame: Characteristics table
    """
    df_temp = df.copy()
    df_temp['cluster'] = labels

    # Filter out noise
    df_temp = df_temp[df_temp['cluster'] >= 0]

    characteristics = []

    for cluster_id in sorted(df_temp['cluster'].unique()):
        cluster_data = df_temp[df_temp['cluster'] == cluster_id]

        char = {
            'Cluster': cluster_id,
            'Interpretation': interpretations.get(cluster_id, 'Unknown') if interpretations else f'Cluster {cluster_id}',
            'Size': len(cluster_data),
            'Pct_of_Total': f"{len(cluster_data) / len(df_temp) * 100:.1f}%",
            'Avg_Duration_Min': f"{cluster_data['duration_min'].mean():.1f}",
            'Avg_Distance_Km': f"{cluster_data['distance_km'].mean():.2f}",
            'Avg_Start_Hour': f"{cluster_data['start_hour'].mean():.1f}",
            'Pct_Weekend': f"{cluster_data['is_weekend'].mean() * 100:.1f}%",
            'Pct_Member': f"{cluster_data['is_member'].mean() * 100:.1f}%",
            'Pct_Round_Trip': f"{cluster_data['is_round_trip'].mean() * 100:.1f}%",
            'Top_Start_Station': cluster_data['start_station_name'].mode()[0] if len(cluster_data) > 0 else 'N/A',
            'Top_End_Station': cluster_data['end_station_name'].mode()[0] if len(cluster_data) > 0 else 'N/A'
        }

        characteristics.append(char)

    char_df = pd.DataFrame(characteristics)

    print("="*80)
    print("CLUSTER CHARACTERISTICS TABLE")
    print("="*80)
    print(char_df.to_string(index=False))
    print("="*80 + "\n")

    if save:
        from src.paths import REPORTS_DIR
        filepath = REPORTS_DIR / 'cluster_characteristics_table.csv'
        char_df.to_csv(filepath, index=False)
        print(f"✓ Saved: {filepath}\n")

    return char_df


def plot_feature_importance_pca(pca: PCA,
                                feature_names: list,
                                save: bool = True) -> None:
    """
    Plot feature contributions to PC1 and PC2.

    Args:
        pca (PCA): Fitted PCA model
        feature_names (list): Original feature names
        save (bool): Save figure
    """
    components = pca.components_[:2]  # First 2 PCs

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for idx, (ax, pc) in enumerate(zip(axes, components)):
        # Sort by absolute contribution
        sorted_idx = np.argsort(np.abs(pc))[::-1]

        ax.barh(range(len(feature_names)), pc[sorted_idx])
        ax.set_yticks(range(len(feature_names)))
        ax.set_yticklabels([feature_names[i] for i in sorted_idx])
        ax.set_xlabel('Contribution')
        ax.set_title(f'PC{idx+1} Feature Contributions ({pca.explained_variance_ratio_[idx]*100:.1f}% var)')
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(alpha=0.3, axis='x')

    plt.tight_layout()

    if save:
        filepath = get_figure_file('pca_feature_importance.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_explained_variance(pca: PCA, save: bool = True) -> None:
    """
    Plot explained variance by principal component.

    Args:
        pca (PCA): Fitted PCA model
        save (bool): Save figure
    """
    n_components = len(pca.explained_variance_ratio_)
    cumulative_var = np.cumsum(pca.explained_variance_ratio_)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(range(1, n_components + 1), pca.explained_variance_ratio_,
           alpha=0.7, label='Individual', color='steelblue')
    ax.plot(range(1, n_components + 1), cumulative_var,
            'ro-', linewidth=2, label='Cumulative')

    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Explained Variance Ratio')
    ax.set_title('PCA Explained Variance')
    ax.legend()
    ax.grid(alpha=0.3)

    # Annotate cumulative values
    for i, val in enumerate(cumulative_var):
        ax.text(i + 1, val + 0.02, f'{val*100:.1f}%', ha='center', fontsize=9)

    plt.tight_layout()

    if save:
        filepath = get_figure_file('pca_explained_variance.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


def plot_cluster_size_distribution(labels: np.ndarray,
                                   cluster_names: dict = None,
                                   save: bool = True) -> None:
    """
    Plot cluster size distribution (bar chart).

    Args:
        labels (np.ndarray): Cluster labels
        cluster_names (dict, optional): {cluster_id: name}
        save (bool): Save figure
    """
    # Filter out noise
    labels_clean = labels[labels >= 0]

    unique, counts = np.unique(labels_clean, return_counts=True)
    percentages = counts / len(labels_clean) * 100

    fig, ax = plt.subplots(figsize=(10, 6))

    x_labels = [cluster_names.get(c, f'C{c}') if cluster_names else f'C{c}' for c in unique]
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique)))

    bars = ax.bar(x_labels, counts, color=colors, edgecolor='black', alpha=0.7)

    # Add percentage labels
    for bar, pct, count in zip(bars, percentages, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
               f'{pct:.1f}%\n({count:,})',
               ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('Number of Trips')
    ax.set_xlabel('Cluster')
    ax.set_title('Cluster Size Distribution')
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()

    if save:
        filepath = get_figure_file('cluster_size_distribution.png')
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")

    plt.close()


if __name__ == "__main__":
    from src.loaders import load_all_trips
    from src.preprocess import clean_trips, engineer_features, prepare_clustering_features, create_preprocessing_pipeline
    from src.clustering import run_kmeans

    print("="*60)
    print("TESTING VISUALIZATION MODULE")
    print("="*60 + "\n")

    # Load and prepare data (10% sample)
    df = load_all_trips(sample_frac=0.1)
    df = clean_trips(df, verbose=False)
    df = engineer_features(df, verbose=False)
    X = prepare_clustering_features(df)
    X_scaled, _ = create_preprocessing_pipeline(X, apply_pca=False, verbose=False)

    # Run clustering
    labels, _ = run_kmeans(X_scaled, k=5, verbose=False)

    # Test visualizations
    print("\n1. PCA Projection...")
    X_pca, pca_model = plot_pca_projection(X_scaled, labels, save=True)

    print("\n2. Feature Importance...")
    plot_feature_importance_pca(pca_model, X.columns.tolist(), save=True)

    print("\n3. Explained Variance...")
    plot_explained_variance(pca_model, save=True)

    print("\n4. Cluster Size Distribution...")
    plot_cluster_size_distribution(labels, save=True)

    print("\n5. Characteristics Table...")
    interpretations = {0: 'Commuters', 1: 'Tourists', 2: 'Last-Mile', 3: 'Casual', 4: 'Mixed'}
    char_table = create_characteristics_table(df, labels, interpretations, save=True)

    print("\n6. t-SNE Projection (optional, may take time)...")
    # X_tsne = plot_tsne_projection(X_scaled, labels, save=True)

    print("\n✓ Visualization module test complete!")
