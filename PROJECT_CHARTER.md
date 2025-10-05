# Project Charter — Clustering Urban Bike-Share Users

## Project Name
Clustering Urban Bike-Share Trip Behavior for Sustainable Mobility Planning

## Problem Statement
Urban bike-share systems generate millions of trip records, but rider behavior remains heterogeneous and poorly understood. Without clear segmentation, cities struggle to:
- Allocate infrastructure investments efficiently
- Tailor pricing and service offerings
- Measure sustainability impact across user groups

This project applies unsupervised clustering to reveal distinct trip behavior patterns, enabling data-driven decisions for sustainable urban transport.

---

## Stakeholders

### Primary Beneficiaries
1. **City Planners & Transport Agencies**
   Use clusters to optimize station placement, bike redistribution, and infrastructure (bike lanes, docking capacity).

2. **Bike-Share Operators**
   Inform pricing strategies, membership tiers, and marketing campaigns targeting specific user segments.

3. **Sustainability Advocates & NGOs**
   Quantify bike-share's role in reducing car trips and emissions; advocate for policy support.

4. **Urban Commuters**
   Benefit indirectly from improved service reliability and network expansion driven by insights.

### Secondary Stakeholders
5. **Researchers & Data Scientists**
   Methodology and findings contribute to urban mobility literature.

6. **Policy Makers**
   Evidence-based rationale for green transport funding and regulation.

---

## SMART Goal

**S**pecific: Cluster bike-share trip records into 4-6 interpretable segments (e.g., commuters, tourists, casual, last-mile).

**M**easurable:
- Achieve silhouette score ≥ 0.35 (indicating reasonable cluster separation)
- Davies-Bouldin index < 1.5 (tight, well-separated clusters)
- Qualitative validation: clusters align with known mobility patterns (e.g., weekday morning peaks for commuters)

**A**chievable: Real-world bike-share datasets (CitiBike, Capital Bikeshare) are publicly available; clustering is well-suited for unsupervised pattern discovery.

**R**elevant: Aligns with global sustainability goals (SDG 11: Sustainable Cities) and local urban planning priorities.

**T**ime-bound: Deliver all 5 capstones by end of semester (12 weeks).

---

## Success Criteria

### Technical
- Reproducible pipeline: data cleaning → feature engineering → clustering → evaluation
- Champion algorithm selected via rigorous comparison (KMeans, DBSCAN, Agglomerative)
- Clusters are statistically distinct (p < 0.05 for key features like trip duration, start hour)

### Impact
- Actionable insights delivered in plain-language reports for non-technical stakeholders
- At least 3 concrete policy or operational recommendations per cluster
- Visualizations (PCA maps, heatmaps, profiles) suitable for presentations to city councils or transport agencies

---

## Scope

### In Scope
- Trip-level clustering (aggregated, anonymized data)
- Features: duration, distance, start/end time, weekday, user type (member vs casual), station geography
- Algorithms: KMeans, Agglomerative Hierarchical, DBSCAN
- Evaluation: silhouette, Davies-Bouldin, interpretability, spatial coverage

### Out of Scope
- Real-time prediction or forecasting
- Individual user tracking (privacy preserved)
- Integration with external datasets (weather, events) unless trivial to add
- Deployment to production systems

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Seasonal bias** (data from summer only) | High | Document limitation; recommend collecting multi-season data |
| **Sparse rural stations** skew clusters | Medium | Filter or weight by trip volume; focus on urban core |
| **Overfitting to local city** | Medium | Validate generalizability in Related Work; note transferability limits |
| **Poor silhouette score** | High | Try alternative algorithms, feature sets, or accept and explain |

---

## Ethical Considerations
- **Privacy**: All data is aggregated and anonymized (no user IDs or personal info).
- **Equity**: Clusters may reveal underserved neighborhoods; recommendations must avoid reinforcing biases (e.g., prioritizing affluent areas).
- **Transparency**: Decision log and open methodology allow scrutiny and replication.

---

## Timeline (High-Level)

| Week | Capstone | Deliverable |
|------|----------|-------------|
| 1-2  | 1        | Framing docs + notebook |
| 3-4  | 2        | Data prep pipeline + cleaned dataset |
| 5-7  | 3        | Clustering experiments + champion model |
| 8-9  | 4        | Evaluation + visualizations |
| 10-12| 5        | Impact reports + executive summary |

---

**Approved by:** Nicoli Antropova
**Date:** 2025-10-04
**Version:** 1.0
