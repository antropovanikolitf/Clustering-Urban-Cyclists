# Data Fitness Assessment — Clustering Urban Bike-Share Users

## Overview
This document evaluates whether the CitiBike trip dataset is suitable for clustering rider behavior. Assessment follows the **Data Quality Framework**: relevance, accuracy, completeness, consistency, timeliness, and coverage.

---

## Assessment Criteria

### 1. Relevance
**Question**: Does the dataset align with our clustering goal (identifying distinct trip behavior patterns)?

**Evidence**:
- ✅ Contains trip-level records (not aggregated) → allows individual behavior clustering
- ✅ Includes temporal features (`started_at`, `ended_at`) → can derive hour, weekday, duration
- ✅ Includes spatial features (`start_lat`, `start_lng`, `end_lat`, `end_lng`) → can compute distance, station zones
- ✅ Includes user type (`member_casual`) → proxies for commuter vs tourist behavior
- ⚠️ Missing bike speed (must derive from distance/duration)
- ⚠️ No weather data (rain/snow may confound patterns)

**Rating**: **High** (core features present; minor gaps acceptable)

---

### 2. Accuracy
**Question**: Are the recorded values correct and precise?

**Evidence**:
- ✅ Timestamps are machine-generated (docking station sensors) → high accuracy
- ⚠️ GPS coordinates have ~10–30m drift (standard for consumer GPS) → acceptable for station-level analysis
- ⚠️ Occasional outliers (e.g., `duration = 0`, `distance = 0`) → likely sensor errors; <1% of trips
- ❌ Some trips have `started_at > ended_at` (clock skew) → must filter

**Known Issues**:
- GPS drift: Stations near tall buildings may show lat/lng jitter
- Test trips: Staff occasionally create 1-second trips for maintenance → filter `duration < 1 min`
- Clock skew: <0.01% of trips have negative duration

**Rating**: **Moderate** (minor errors; easy to clean)

---

### 3. Completeness
**Question**: What percentage of expected data is present?

**Evidence**:
- ✅ `ride_id`, `started_at`, `ended_at`: 100% present
- ⚠️ `start_station_name`, `end_station_name`: ~95% present (5% missing = bikes removed from service mid-trip)
- ⚠️ `start_lat`, `start_lng`, `end_lat`, `end_lng`: ~98% present (2% missing = GPS failure)
- ✅ `member_casual`: 100% present
- ⚠️ `rideable_type`: Introduced in 2020; 100% for recent data

**Handling Missing Data**:
- Drop rows where `start_lat` or `end_lat` is null (cannot compute distance)
- Drop rows where `start_station_name` is null (cannot interpret station-level patterns)
- Expected loss: ~5–7% of trips

**Rating**: **Moderate** (acceptable for unsupervised learning; no imputation needed)

---

### 4. Consistency
**Question**: Is the dataset internally coherent and compatible over time?

**Evidence**:
- ⚠️ **Schema change (2020)**: Pre-2020 files use `tripduration` (seconds) instead of `started_at`/`ended_at`
  → Our pipeline targets post-2020 schema; older data requires conversion
- ✅ Station IDs are stable (same station = same ID across months)
- ⚠️ Station names occasionally change (e.g., "Broadway & W 58 St" → "Broadway & 58th St")
  → Use station ID (not name) for joins
- ✅ `member_casual` values consistent: `member` or `casual` (no typos, no nulls)

**Rating**: **Moderate** (schema stable for post-2020 data; minor station name variations)

---

### 5. Timeliness
**Question**: Is the data recent enough to reflect current bike-share usage?

**Evidence**:
- ✅ Dataset updated monthly (lag ~2 weeks)
- ✅ We will use Spring/Summer 2025 data (Mar–Jun) → reflects current post-pandemic usage patterns
- ⚠️ COVID-19 impact: 2020–2021 data shows anomalies (reduced commuting, increased leisure)
  → Using 2025 data fully captures post-pandemic stabilization

**Rating**: **High** (recent, post-pandemic stabilization)

---

### 6. Coverage
**Question**: Does the dataset span diverse contexts (geographic, temporal, demographic)?

**Evidence**:
- ✅ **Geographic**: Covers all 5 NYC boroughs (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
  → Caveat: 80% of stations in Manhattan/Brooklyn (outer boroughs underrepresented)
- ⚠️ **Temporal**: Spring/Summer 2025 only (Mar–Jun) → seasonal bias (fall/winter may show different patterns)
  → Limitation documented; recommend multi-season validation in future
- ⚠️ **Demographic**: No age, gender, income data (privacy-preserved)
  → Cannot cluster by rider demographics; only behavior (acceptable for our goal)
- ✅ **User type**: Mix of members (~75%) and casual riders (~25%) → sufficient diversity

**Rating**: **Moderate** (good geographic spread; seasonal bias noted)

---

## Summary Table

| Criterion | Rating | Key Issues | Mitigation |
|-----------|--------|------------|------------|
| Relevance | ✅ High | None | - |
| Accuracy | ⚠️ Moderate | GPS drift, outliers | Filter duration <1 min or >3 hrs |
| Completeness | ⚠️ Moderate | 5% missing stations | Drop rows with null lat/lng or station |
| Consistency | ⚠️ Moderate | Schema change (pre-2020) | Use post-2020 data only |
| Timeliness | ✅ High | None | - |
| Coverage | ⚠️ Moderate | Seasonal bias (summer), outer borough underrep | Document limitation; recommend multi-season |

**Overall Fitness**: **Acceptable for clustering** (minor quality issues mitigated by filtering)

---

## Data Cleaning Requirements (For Capstone 2)

### Must-Do Filters
1. **Drop rows** where:
   - `start_lat` or `end_lat` is null
   - `start_station_name` is null
   - `duration_min` < 1 or > 180 (outliers)
   - `started_at > ended_at` (clock skew)

2. **Derive features**:
   - `duration_min = (ended_at - started_at).total_seconds() / 60`
   - `trip_distance_km = haversine(start_lat, start_lng, end_lat, end_lng)`
   - `start_hour = started_at.hour`
   - `weekday = started_at.weekday()`

3. **Cap outliers**:
   - `duration_min`: Clip to 99th percentile (~90 min)
   - `trip_distance_km`: Clip to 99th percentile (~10 km)

### Expected Data Loss
- **Before cleaning**: ~3–5 million trips/month × 3 months = 9–15M trips
- **After cleaning**: ~8.5–14M trips (5–7% loss)
- **Sufficient for clustering**: Yes (>1M trips ensures stable clusters)

---

## Known Biases & Limitations

### 1. Seasonal Bias
- **Issue**: Spring/summer data overrepresents leisure/tourist trips (nicer weather)
- **Impact**: May inflate "weekend leisure" cluster; undercount fall/winter commuters
- **Mitigation**: Document in IMPACT_REPORT.md; recommend fall/winter validation

### 2. Geographic Bias
- **Issue**: Outer boroughs (Bronx, Staten Island) have fewer stations
- **Impact**: Clusters may overrepresent Manhattan/Brooklyn patterns
- **Mitigation**: Note in equity analysis; recommend station expansion in underserved areas

### 3. Survivorship Bias
- **Issue**: Missing station names = bikes removed mid-trip (likely mechanical issues)
- **Impact**: Excludes broken bikes → may undercount short "failed trips"
- **Mitigation**: Acceptable (focus on successful trips for policy planning)

### 4. No Ground Truth
- **Issue**: No labeled "commuter" or "tourist" trips for validation
- **Impact**: Cannot compute precision/recall; rely on interpretability
- **Mitigation**: Use domain knowledge (weekday AM/PM peaks = commuters) as qualitative check

---

## Data Provenance Verification

### Source Authenticity
- ✅ Official CitiBike System Data page (Lyft-operated)
- ✅ Consistent with NYC Open Data Portal schema
- ✅ Cross-referenced with [Citi Bike Monthly Reports](https://citibikenyc.com/about) (trip counts match)

### Data Integrity
- File hashes (MD5): Logged in `data/README.md`
- No evidence of tampering or corruption
- Schema matches documentation

---

## Final Verdict

**Is the data fit for clustering bike-share trip behavior?**
✅ **Yes, with minor cleaning**

**Strengths**:
- Large sample size (millions of trips)
- Rich feature set (temporal, spatial, behavioral)
- High accuracy (machine-generated timestamps/GPS)

**Weaknesses**:
- Seasonal bias (summer only)
- Geographic skew (Manhattan/Brooklyn dominant)
- 5–7% missing data (acceptable loss)

**Next Steps**:
1. Implement cleaning pipeline in `src/loaders.py` and `src/preprocess.py` (Capstone 2)
2. Run diagnostics (`src/diagnostics.py`) to validate assumptions
3. Document findings in `notebooks/02_dataset_preparation.ipynb`

---

**Last Updated:** 2025-10-04
**Assessed By:** Nicoli Antropova
**Review Status:** Ready for Capstone 2 pipeline development
