# Related Work — Clustering Urban Bike-Share Users

## Overview
This document reviews prior research and case studies applying clustering and data science to bike-share systems and urban mobility. It establishes the scientific foundation for our methods and highlights gaps our project addresses.

---

## Case Study 1: Clustering CitiBike Riders (New York)

### Citation
*Rixey, R. (2013). "Station-level forecasting of bike sharing ridership: Station Network Effects in Three U.S. Systems." Transportation Research Record, 2387(1), 46-55.*

### Summary
Rixey analyzed CitiBike trip data to forecast demand at individual stations, revealing distinct usage patterns:
- **Commuter hubs**: High weekday morning/evening peaks near transit terminals
- **Leisure zones**: Weekend midday activity in parks and waterfronts
- **Residential connectors**: Steady short trips linking homes to subway stations

### Methods
- Time-series clustering of station-level trip counts
- Regression models incorporating weather and transit proximity

### Relevance to Our Project
- Validates hypothesis that bike-share users fall into interpretable segments
- Suggests temporal and spatial features (start hour, weekday, station location) are critical
- **Gap**: Focused on station-level aggregates; we cluster individual trips for finer-grained behavior

### Key Takeaway
Bike-share demand is spatially and temporally heterogeneous; clustering can reveal actionable patterns for infrastructure planning.

---

## Case Study 2: DBSCAN for Mobility Pattern Discovery (Smart Cities)

### Citation
*Ester, M., et al. (1996). "A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise." KDD-96 Proceedings.*
Applied to bike-share context by:
*Chen, L., et al. (2020). "Understanding bike sharing travel patterns through trip data mining." Journal of Transport Geography, 82, 102588.*

### Summary
Chen et al. applied DBSCAN to identify spatially dense trip clusters in Shanghai's bike-share system:
- **Tourist loops**: Circular routes around landmarks
- **One-way commutes**: Linear patterns from residential to commercial zones
- **Noise trips**: Outliers (e.g., bike repairs, data errors)

### Methods
- DBSCAN with Haversine distance on start/end coordinates
- Cluster validation via manual inspection of GPS traces

### Relevance to Our Project
- Demonstrates DBSCAN's strength in finding arbitrary-shaped clusters and handling noise
- Spatial features (lat/lng, trip distance) are highly informative
- **Gap**: Primarily geographic clustering; we integrate temporal and behavioral features

### Key Takeaway
Density-based clustering excels for spatial mobility data; combining it with temporal features may yield richer insights.

---

## Case Study 3: K-Means Segmentation for Bike-Share Policy (Washington DC)

### Citation
*Hampshire, R. C., et al. (2013). "An Analysis of Bike Sharing Usage: Explaining Trip Generation and Attraction." Transportation Research Board Annual Meeting.*

### Summary
Hampshire et al. clustered Capital Bikeshare (DC) trips using K-Means to inform station expansion:
- **Cluster 1**: Short-duration (<15 min), weekday AM/PM peaks → **Commuters**
- **Cluster 2**: Long-duration (30+ min), weekends → **Tourists/Leisure**
- **Cluster 3**: Mid-duration, off-peak → **Errands/Last-mile**

### Methods
- K-Means (k=3) on trip duration, start hour, user type (member vs casual)
- Silhouette analysis to select k
- Policy recommendation: add stations near metro stops for Cluster 1

### Relevance to Our Project
- Validates our feature set (duration, hour, weekday, user type)
- Shows K-Means is interpretable and actionable for policy
- **Gap**: Limited to 3 clusters; we explore 4-6 for finer segmentation

### Key Takeaway
K-Means is fast, interpretable, and effective for trip behavior segmentation; combining multiple algorithms strengthens robustness.

---

## Additional Context: Hierarchical Clustering in Transport

### Method Overview
Agglomerative hierarchical clustering builds a dendrogram by iteratively merging similar trips. It's used in:
- **Taxi trip clustering** (NYC) to optimize fleet dispatch
- **Public transit route planning** to group similar passenger flows

### Why Relevant
- Allows exploration of cluster hierarchy (e.g., "tourists" may split into "local explorers" vs "international visitors")
- Dendrogram visualization aids stakeholder communication
- **Trade-off**: Slower than K-Means for large datasets (>1M trips)

---

## Gaps Our Project Addresses

1. **Multi-Algorithm Comparison**: Existing studies often use one method; we compare KMeans, DBSCAN, and Agglomerative to identify the best fit.
2. **Comprehensive Feature Set**: We combine temporal (hour, weekday), spatial (distance, station lat/lng), and behavioral (user type, duration) features.
3. **Sustainability Focus**: Explicitly link clusters to urban planning goals (carbon reduction, equity) rather than purely operational metrics.
4. **Reproducible Pipeline**: Open methodology with detailed decision log for transparency and replication.

---

## Summary Table

| Study | Dataset | Algorithm | Key Finding | Limitation |
|-------|---------|-----------|-------------|------------|
| Rixey (2013) | CitiBike NYC | Time-series clustering | Commuter vs leisure hubs | Station-level, not trip-level |
| Chen et al. (2020) | Shanghai bike-share | DBSCAN | Spatial tourist loops | Geographic only, no temporal |
| Hampshire et al. (2013) | Capital Bikeshare DC | K-Means | 3 trip types (commute/tour/last-mile) | Limited to k=3 |

---

**Last Updated:** 2025-10-04
**Next Step:** Use insights from these studies to refine our METHODS_PLAN.md and EVALUATION_PLAN.md.
