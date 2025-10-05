# Evaluation Plan — Clustering Urban Bike-Share Users

## Overview
This document defines the metrics, validation strategies, and success criteria for assessing clustering quality. Evaluation combines quantitative metrics (silhouette, Davies-Bouldin) with qualitative interpretability and stakeholder relevance.

---

## Evaluation Metrics

### 1. Silhouette Score
**Definition**: Measures how similar a trip is to its own cluster compared to other clusters.
**Range**: -1 (worst) to +1 (best); 0 = overlapping clusters
**Formula**: For trip i:
```
s(i) = (b(i) - a(i)) / max(a(i), b(i))
```
where:
- `a(i)` = avg distance to trips in same cluster
- `b(i)` = avg distance to trips in nearest other cluster

**Target**: ≥ 0.35 (acceptable separation)
**Interpretation**:
- > 0.5: Strong, well-separated clusters
- 0.25-0.5: Moderate separation (acceptable if interpretable)
- < 0.25: Weak clustering (consider alternative features or algorithms)

**Why This Metric**:
- Widely used in bike-share clustering (Hampshire et al., 2013)
- Penalizes both tight clusters and good separation
- Computed without ground truth labels

---

### 2. Davies-Bouldin Index
**Definition**: Ratio of within-cluster scatter to between-cluster separation (lower is better).
**Range**: 0 (best) to ∞
**Formula**:
```
DB = (1/k) Σ max_j( (σ_i + σ_j) / d(c_i, c_j) )
```
where:
- `σ_i` = avg distance of trips to centroid in cluster i
- `d(c_i, c_j)` = distance between centroids of clusters i and j

**Target**: < 1.5 (tight, well-separated clusters)
**Interpretation**:
- < 1.0: Excellent clustering
- 1.0-2.0: Acceptable
- > 2.0: Poor separation (clusters overlap)

**Why This Metric**:
- Complements silhouette (focuses on centroids vs pairwise distances)
- Favors compact, distinct clusters
- Fast to compute

---

### 3. Calinski-Harabasz Index (Variance Ratio Criterion)
**Definition**: Ratio of between-cluster variance to within-cluster variance (higher is better).
**Range**: 0 to ∞
**Target**: Maximize (no fixed threshold; compare algorithms)

**Why This Metric**:
- Rewards tight clusters with large separation
- Useful for selecting optimal k in K-Means elbow plots
- Less sensitive to noise than silhouette

---

### 4. Interpretability & Domain Alignment
**Definition**: Do clusters match known mobility patterns?
**Validation Criteria**:
- **Commuter cluster**: Weekday AM/PM peaks (7-9 AM, 5-7 PM), short duration (<20 min), high `is_member`
- **Tourist cluster**: Weekend midday (11 AM-3 PM), long duration (30+ min), low `is_member`, round trips
- **Last-mile cluster**: Very short (<10 min), near transit hubs (subway stations)
- **Casual/errand cluster**: Mid-duration (15-30 min), off-peak hours, mixed weekday/weekend

**Method**: Aggregate cluster profiles (mean duration, hour, weekday) and compare to hypotheses.

**Why This Metric**:
- Quantitative metrics alone don't guarantee usefulness
- Stakeholders (city planners) need actionable, understandable segments
- Failed interpretability = reject model even if silhouette is high

---

### 5. Spatial Coverage
**Definition**: Do clusters span diverse geographic regions, or are they concentrated in one area?
**Metric**: Variance of start station lat/lng within and across clusters
**Target**: Clusters should reflect functional zones (e.g., residential, commercial, tourist) rather than arbitrary geography

**Why This Metric**:
- Prevents trivial clustering (e.g., "Manhattan vs Brooklyn")
- Ensures policy recommendations are spatially nuanced

---

### 6. Stability & Robustness
**Definition**: Do results hold across random seeds and data subsets?
**Validation**:
- **K-Means**: Run 20 times with different `random_state`; compute silhouette variance
- **DBSCAN**: Vary `eps` by ±10%; check cluster count stability
- **Subsample test**: Cluster on 80% of data; check if remaining 20% matches cluster assignments

**Target**: Silhouette variance < 0.05; cluster labels agree ≥90% across runs

**Why This Metric**:
- Unstable clusters = unreliable policy recommendations
- Critical for reproducibility and stakeholder trust

---

## Algorithm Comparison Framework

### Metrics Table (Example Template)

| Algorithm | k | Silhouette | DB Index | CH Index | Runtime (s) | Interpretable? | Notes |
|-----------|---|------------|----------|----------|-------------|----------------|-------|
| K-Means | 4 | 0.38 | 1.4 | 1200 | 12 | ✓ | Clear commuter/tourist split |
| K-Means | 5 | 0.42 | 1.2 | 1450 | 15 | ✓ | Best quantitative + qualitative |
| K-Means | 6 | 0.39 | 1.5 | 1380 | 18 | ~ | One cluster too small (<5%) |
| Agglomerative | 5 | 0.40 | 1.3 | 1420 | 95 | ✓ | Consistent with K-Means |
| DBSCAN | auto | 0.28 | 2.1 | 980 | 45 | ✗ | 30% noise; poor separation |

**Champion Selection**:
- Primary: Silhouette ≥ 0.35 AND DB < 1.5 AND interpretable
- Tiebreaker: Higher CH index, faster runtime, simpler (K-Means > Agglomerative)

---

## Visualization Strategy (Capstone 4)

### Mandatory Plots
1. **Elbow Plot**: Silhouette score vs k (for K-Means)
2. **DB Index vs k**: Select k where DB is minimized
3. **PCA 2D Projection**: Scatter plot of trips colored by cluster (first 2 PCs)
4. **Cluster Profiles**:
   - Bar chart: Avg `duration_min` per cluster
   - Heatmap: Avg `start_hour` × `weekday` per cluster
   - Boxplot: Trip distance distribution per cluster

### Optional Enhancements
5. **t-SNE or UMAP**: Alternative 2D projection (if PCA unclear)
6. **Dendrogram**: For Agglomerative clustering (show hierarchy)
7. **Geographic Map**: Plot start/end stations colored by dominant cluster

---

## Validation Against Baseline

### Baseline (Naïve Clustering)
- **Random assignment**: Assign trips to k clusters uniformly at random
- **Single feature**: Cluster on `is_member` only (binary split)

**Expected Baseline Scores**:
- Random: Silhouette ≈ 0, DB ≈ 3
- Single feature: Silhouette ≈ 0.15, DB ≈ 2

**Success Criterion**: Our models must significantly outperform baseline (p < 0.05 via permutation test).

---

## Failure Modes & Mitigation

| Failure | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| **Poor silhouette (<0.3)** | Overlapping clusters | Features lack discriminative power | Add/remove features; try DBSCAN |
| **High DB index (>2)** | Diffuse, scattered clusters | Too many clusters or noisy data | Reduce k; filter outliers |
| **Uninterpretable clusters** | No clear commuter/tourist pattern | Features don't capture behavior | Re-engineer (e.g., add `trip_speed`, `station_popularity`) |
| **Unstable clusters** | Results vary across seeds | K-Means stuck in local minima | Increase `n_init`; try hierarchical |
| **Excessive noise (DBSCAN)** | >20% trips labeled noise | `eps` too small or `min_samples` too high | Tune hyperparameters via grid search |

---

## Stakeholder Validation (Capstone 5)

### Qualitative Checks
- **Face validity**: Do cluster names (commuter/tourist) resonate with city planners?
- **Actionability**: Can each cluster inform a specific policy (e.g., add stations, adjust pricing)?
- **Equity**: Do clusters avoid biasing against low-income or underserved areas?

### Deliverables
- Cluster summary table (for IMPACT_REPORT.md)
- Top 3 policy recommendations per cluster
- Sensitivity analysis: How do results change if we exclude weekends or tourists?

---

## Summary: Evaluation Checklist

- [ ] Compute silhouette, DB, CH for all algorithms and k values
- [ ] Create elbow plots (silhouette vs k, DB vs k)
- [ ] Validate stability (20 runs, variance < 0.05)
- [ ] Generate PCA projection and cluster profiles
- [ ] Verify interpretability (match commuter/tourist hypotheses)
- [ ] Compare to baseline (random, single-feature)
- [ ] Document champion algorithm in DECISIONS_LOG.md

---

**Last Updated:** 2025-10-04
**Next Step:** Apply this plan in Capstone 4 (notebooks/04_evaluating_visualizing_clusters.ipynb).
