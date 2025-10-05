# Data Sources — Clustering Urban Bike-Share Users

## Overview
This document describes the datasets used in this project, their provenance, access methods, and fitness for clustering bike-share trip behavior.

---

## Primary Dataset: CitiBike Trip Data (NYC)

### Source
- **Provider**: Lyft (CitiBike operator)
- **URL**: [https://citibikenyc.com/system-data](https://citibikenyc.com/system-data)
- **License**: Open Data (publicly available under NYC Open Data terms)

### Description
Monthly CSV files containing individual bike-share trip records from New York City's CitiBike system.
Typical timespan: 2013–present (updated monthly).

### File Format
- **Type**: CSV (gzip compressed)
- **Size**: ~100–500 MB per month (uncompressed); ~2–5 million trips/month
- **Naming Convention**: `YYYYMM-citibike-tripdata.csv.zip` (e.g., `202309-citibike-tripdata.csv.zip`)

### Expected Schema

| Column Name | Type | Description | Example |
|-------------|------|-------------|---------|
| `ride_id` | String | Unique trip identifier | `A1B2C3D4E5F6` |
| `rideable_type` | String | Bike type | `classic_bike`, `electric_bike`, `docked_bike` |
| `started_at` | Datetime | Trip start timestamp (UTC or local) | `2023-09-15 08:23:45` |
| `ended_at` | Datetime | Trip end timestamp | `2023-09-15 08:38:12` |
| `start_station_name` | String | Starting station name | `Broadway & W 58 St` |
| `start_station_id` | String | Starting station ID | `4567.08` |
| `end_station_name` | String | Ending station name | `Central Park S & 6 Ave` |
| `end_station_id` | String | Ending station ID | `5678.09` |
| `start_lat` | Float | Start latitude | `40.7661` |
| `start_lng` | Float | Start longitude | `-73.9817` |
| `end_lat` | Float | End latitude | `40.7659` |
| `end_lng` | Float | End longitude | `-73.9764` |
| `member_casual` | String | User type | `member` (subscriber), `casual` (pay-per-ride) |

### Data Collection Period (Planned)
- **Timeframe**: 4 months (March–June 2025 for spring/summer season)
- **Rationale**: Balances sample size (~10M+ trips) with computational feasibility; captures transition from spring to peak summer usage
- **Limitation**: Spring/summer bias (see DATA_FITNESS_ASSESSMENT.md)

---

## Alternative / Supplementary Datasets

### 1. Capital Bikeshare (Washington DC)
- **URL**: [https://capitalbikeshare.com/system-data](https://capitalbikeshare.com/system-data)
- **Why**: Similar schema to CitiBike; useful for cross-city validation
- **Status**: Optional (if time permits in Capstone 5)

### 2. Divvy Bikes (Chicago)
- **URL**: [https://divvybikes.com/system-data](https://divvybikes.com/system-data)
- **Why**: Colder climate; tests generalizability of clusters
- **Status**: Out of scope for now

### 3. Weather Data (NOAA)
- **URL**: [https://www.ncdc.noaa.gov/cdo-web/](https://www.ncdc.noaa.gov/cdo-web/)
- **Why**: Control for rain/snow effects on trip patterns
- **Status**: Excluded (scope constraint); noted as future work

---

## Data Access & Storage

### Download Instructions
1. Visit [CitiBike System Data](https://citibikenyc.com/system-data)
2. Download monthly CSV.zip files for desired timeframe (e.g., March–June 2025)
3. Extract CSVs to `data/raw/bikeshare/` folder
4. Verify schema matches expected columns (run diagnostics in Capstone 2)

### Local Storage Structure
```
data/
├── raw/
│   └── bikeshare/
│       ├── 202503-citibike-tripdata.csv  # March 2025
│       ├── 202504-citibike-tripdata.csv  # April 2025
│       ├── 202505-citibike-tripdata.csv  # May 2025
│       └── 202506-citibike-tripdata.csv  # June 2025
├── interim/                              # (Placeholder for partially cleaned data)
└── processed/
    └── trips_clean.csv                   # Final cleaned dataset (from Capstone 2)
```

### Data Exclusions
- **Pre-2020 data**: Schema changed (older files use `tripduration` column instead of `started_at`/`ended_at`)
- **Bikes removed for service**: Some trips have missing station names → dropped in cleaning
- **Test trips**: Duration < 1 min or > 3 hours → flagged as outliers

---

## Data Privacy & Ethics

### Personal Identifiable Information (PII)
- **None**: Dataset contains no user IDs, names, emails, or payment info
- **Membership status**: `member_casual` is anonymized (cannot link to individual accounts)
- **Geographic precision**: Station locations are public infrastructure (no home addresses)

### Ethical Considerations
- **Aggregation**: All analysis at trip level (no user profiling)
- **Equity**: Spatial clustering may reveal underserved neighborhoods → recommendations must avoid reinforcing biases
- **Transparency**: Open data license allows public scrutiny and replication

---

## Data Provenance

| Attribute | Value |
|-----------|-------|
| **Original Collector** | Lyft (CitiBike operator) |
| **Collection Method** | Automated logging (bike GPS + docking station sensors) |
| **Update Frequency** | Monthly (published ~2 weeks after month end) |
| **Historical Availability** | 2013–present |
| **Quality Assurance** | Lyft performs basic validation (timestamp consistency, GPS bounds) |
| **Known Issues** | Occasional missing station names, GPS drift, test trips |

---

## Data Fitness Summary

| Fitness Criterion | Assessment | Evidence |
|-------------------|------------|----------|
| **Relevance** | ✅ High | Directly captures bike-share trip behavior |
| **Coverage** | ✅ High | Millions of trips; spans entire NYC bike network |
| **Accuracy** | ⚠️ Moderate | GPS drift (~10m); occasional missing stations |
| **Completeness** | ⚠️ Moderate | ~5% missing `start_station_name` (dropped in cleaning) |
| **Timeliness** | ✅ High | 2023 data reflects current usage patterns |
| **Consistency** | ⚠️ Moderate | Schema changed in 2020 (old vs new format) |

**Overall Verdict**: Fit for purpose (see detailed assessment in DATA_FITNESS_ASSESSMENT.md).

---

## Data Update Plan

### If More Data Needed
- Download additional months (e.g., extend to Sept–Nov for seasonal comparison)
- Merge CSVs using `src/loaders.py` (handles schema variations)
- Re-run pipeline from Capstone 2 onward

### Version Control
- **Current Version**: Spring/Summer 2025 (March–June)
- **Logged in**: `data/README.md` (includes download date, file hashes for reproducibility)

---

**Last Updated:** 2025-10-04
**Next Step:** Document data quality findings in DATA_FITNESS_ASSESSMENT.md (Capstone 2).
