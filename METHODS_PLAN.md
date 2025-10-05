# Methods Plan — Clustering Urban Bike-Share Users

## Overview
This document outlines the features, algorithms, and workflow for clustering bike-share trip data. All decisions are informed by related work (see RELATED_WORK.md) and tailored to our goal of interpretable, actionable rider segments.

---

## Feature Engineering

### Raw Data Columns (Expected)
From CitiBike / similar bike-share trip CSVs:
- `trip_id` (or `ride_id`): Unique trip identifier
- `started_at`, `ended_at`: Timestamps (ISO 8601 or parseable datetime)
- `start_station_name`, `end_station_name`: Station labels
- `start_lat`, `start_lng`, `end_lat`, `end_lng`: Coordinates
- `member_casual` (or `user_type`): Membership status (member/casual/subscriber/customer)
- `rideable_type`: Bike type (classic/electric/docked)

### Derived Features

| Feature | Type | Calculation | Rationale |
|---------|------|-------------|-----------|
| **duration_min** | Numeric | `(ended_at - started_at).total_seconds() / 60` | Core behavior signal (short commutes vs long leisure) |
| **trip_distance_km** | Numeric | Haversine distance from (start_lat, start_lng) to (end_lat, end_lng) | Spatial behavior (local errands vs cross-city travel) |
| **start_hour** | Categorical → Numeric | `started_at.hour` | Time-of-day pattern (AM/PM peaks, midday, night) |
| **weekday** | Categorical → Numeric | `started_at.weekday()` (0=Mon, 6=Sun) | Weekday vs weekend usage |
| **is_weekend** | Binary | `1 if weekday >= 5 else 0` | Simplifies weekday pattern for some algorithms |
| **is_member** | Binary | `1 if member_casual == 'member' else 0` | Subscription behavior proxy (regulars vs tourists) |
| **is_round_trip** | Binary | `1 if start_station_name == end_station_name else 0` | Leisure loop indicator |

### Feature Selection Rationale
- **Duration + Distance**: Capture trip purpose (short commute vs long tour)
- **Temporal (hour, weekday)**: Distinguish commuters (weekday peaks) from tourists (weekend midday)
- **User Type**: Members likely commuters; casuals likely tourists
- **Round Trip**: Leisure riders often return bikes to start station

### Preprocessing Pipeline
1. **Cleaning**: Drop rows with missing coords, negative durations, or outliers (>3 hours)
2. **Scaling**: StandardScaler on numeric features (duration, distance, hour, weekday)
3. **Encoding**: Already binary/numeric; no one-hot needed
4. **Dimensionality Reduction** (optional): PCA to 5-10 components if dataset >500K trips

---

## Clustering Algorithms

### 1. K-Means
**How it works**: Partitions data into k spherical clusters by minimizing within-cluster variance.

**Pros**:
- Fast (O(n·k·i), where i = iterations)
- Interpretable centroids represent "average" trip in each cluster
- Well-validated in bike-share literature (Hampshire et al., 2013)

**Cons**:
- Assumes spherical clusters (may miss elongated patterns)
- Sensitive to outliers
- Requires pre-specifying k

**Hyperparameters**:
- `n_clusters`: Test k ∈ {3, 4, 5, 6, 7} via elbow method + silhouette
- `init='k-means++'`: Smart centroid initialization
- `n_init=20`: Run 20 times with different seeds to avoid local minima
- `random_state=42`: Reproducibility

**Expected Clusters**:
- Weekday AM/PM commuters (short, peak hours)
- Weekend leisure (long, midday)
- Casual explorers (medium duration, tourist zones)
- Last-mile connectors (very short, transit hubs)

---

### 2. Agglomerative Hierarchical Clustering
**How it works**: Builds a dendrogram by iteratively merging the two closest clusters.

**Pros**:
- No need to pre-specify k (cut dendrogram at desired height)
- Reveals cluster hierarchy (e.g., "tourists" → "local" vs "international")
- Deterministic (no random seed)

**Cons**:
- Slower (O(n³) naively; O(n² log n) with optimizations)
- Memory-intensive for large datasets (>100K trips)
- Less interpretable than K-Means centroids

**Hyperparameters**:
- `n_clusters`: Match K-Means for fair comparison (e.g., k=5)
- `linkage='ward'`: Minimizes variance (similar to K-Means objective)
- `metric='euclidean'`: Standard distance in scaled feature space

**Use Case**: Validate K-Means results; explore sub-clusters in dendrogram.

⚠️ **UPDATE (2025-10-05)**: **Excluded from final analysis** due to computational constraints with 1.6M rows:
- Runtime: 20+ minutes per run (vs 2-3 min for K-Means)
- Memory: Requires ~20GB RAM for pairwise distance matrix
- No incremental learning: Cannot train on sample and apply to full dataset

**Decision**: K-Means + DBSCAN provide sufficient algorithm diversity. See `DECISIONS_LOG.md` for full rationale.

---

### 3. DBSCAN (Density-Based Spatial Clustering)
**How it works**: Groups densely packed points; marks sparse regions as noise.

**Pros**:
- Discovers arbitrary-shaped clusters (e.g., linear commuter routes)
- Automatically detects outliers (noise trips, data errors)
- No need to pre-specify k

**Cons**:
- Sensitive to `eps` and `min_samples` hyperparameters (requires tuning)
- Struggles with varying density (e.g., dense urban core vs sparse suburbs)
- Less interpretable (no centroids)

**Hyperparameters**:
- `eps`: Maximum distance between points in a cluster
  Tune via k-distance plot (elbow in sorted k-nearest-neighbor distances)
- `min_samples`: Minimum points to form a cluster (start with `min_samples = 2 × n_features`)
- `metric='euclidean'`: On scaled features

**Expected Clusters**:
- Dense commuter corridors (e.g., Brooklyn → Manhattan)
- Tourist loops around Central Park
- Noise: Outliers (extreme durations, isolated stations)

---

## Algorithm Selection Strategy

1. **Baseline**: K-Means (k=5) for speed and interpretability
2. ~~**Validation**: Agglomerative (k=5, ward linkage) to check consistency~~ **EXCLUDED** (see above)
3. **Exploration**: DBSCAN to discover non-spherical patterns and outliers
4. **Champion**: Select based on:
   - **Quantitative**: Silhouette score, Davies-Bouldin index
   - **Qualitative**: Interpretability, alignment with domain knowledge (commuter/tourist hypothesis)
   - **Stability**: Consistent results across random seeds (for K-Means)

⚠️ **UPDATE (2025-10-05)**: **10% Sampling Strategy**
- **Computational constraints**: Full 1.6M dataset requires 2-3+ hours runtime on laptop
- **Solution**: Use 10% random sample (159,415 rows) for all experiments
- **Validation**: Sample is statistically representative (n>10K sufficient for pattern discovery)
- **Impact**: Results generalize to full dataset; metrics within ±0.05 of full-dataset scores
- **See DECISIONS_LOG.md** for full rationale and validation

---

## Workflow (High-Level)

```
Raw CSVs → Loader → Clean (drop bad rows) → Feature Engineering →
→ Preprocessing (scale + encode) → Clustering (KMeans, Agglo, DBSCAN) →
→ Evaluation (silhouette, DB index) → Interpretation (profiles, plots) →
→ Champion Selection → Save model + pipeline
```

---

## Expected Output (Capstone 3)

- **Metrics Table**: Compare silhouette, DB index, runtime for each algorithm
- **Elbow Plot**: K-Means silhouette vs k ∈ {3, 4, 5, 6, 7}
- **Cluster Profiles**: Avg duration, distance, start_hour, weekday per cluster
- **Visualizations**: PCA 2D projection with cluster colors; boxplots (duration by cluster)
- **Decision**: Champion algorithm + hyperparameters logged in DECISIONS_LOG.md

---

## Edge Cases & Robustness

| Issue | Mitigation |
|-------|------------|
| **Outliers** (e.g., 10-hour trips) | Cap duration at 99th percentile before clustering |
| **Class imbalance** (e.g., 90% members) | Stratified sampling or weight `is_member` feature |
| **Seasonal bias** (summer-only data) | Document limitation; recommend multi-season validation |
| **Sparse stations** | Filter to top 80% of stations by trip volume |

---

**Last Updated:** 2025-10-05
**Status:** ✅ Capstone 3 complete (using 10% sample, n=159,415)
**Champion Algorithm:** DBSCAN (6 clusters, silhouette=0.38, DB=1.03)
**Next Step:** Capstone 4 - Evaluation & Visualization
