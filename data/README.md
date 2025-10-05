# Data Directory

## Overview
This directory contains all datasets used in the Clustering Urban Bike-Share Users project.

## Structure

### `raw/`
Original, unmodified bike-share trip CSVs downloaded from CitiBike System Data.
**DO NOT EDIT FILES IN THIS FOLDER.**

**Expected Files** (to be downloaded by user):
- `202306-citibike-tripdata.csv` (June 2023)
- `202307-citibike-tripdata.csv` (July 2023)
- `202308-citibike-tripdata.csv` (August 2023)

**Source**: [https://citibikenyc.com/system-data](https://citibikenyc.com/system-data)
**License**: NYC Open Data (public domain)

### `interim/`
Intermediate datasets created during processing (e.g., partially cleaned data, feature-engineered files).
Used for debugging and iterative development.

### `processed/`
Final cleaned and preprocessed datasets ready for clustering.

**Expected Files** (created by Capstone 2):
- `trips_clean.csv` – Cleaned trip data with derived features (duration, distance, start_hour, weekday, etc.)

---

## Data Provenance

### Download Date
*To be filled after downloading CSVs*

### File Hashes (MD5)
*To be computed and logged after downloading CSVs*

Example:
```
202306-citibike-tripdata.csv: a1b2c3d4e5f6...
202307-citibike-tripdata.csv: f6e5d4c3b2a1...
202308-citibike-tripdata.csv: 123456789abc...
```

Use `md5sum <filename>` (Linux/Mac) or `Get-FileHash <filename> -Algorithm MD5` (Windows) to verify.

---

## Schema (Post-2020 CitiBike Format)

| Column | Type | Description |
|--------|------|-------------|
| `ride_id` | String | Unique trip ID |
| `rideable_type` | String | `classic_bike`, `electric_bike`, `docked_bike` |
| `started_at` | Datetime | Trip start timestamp |
| `ended_at` | Datetime | Trip end timestamp |
| `start_station_name` | String | Starting station name |
| `start_station_id` | String | Starting station ID |
| `end_station_name` | String | Ending station name |
| `end_station_id` | String | Ending station ID |
| `start_lat` | Float | Start latitude |
| `start_lng` | Float | Start longitude |
| `end_lat` | Float | End latitude |
| `end_lng` | Float | End longitude |
| `member_casual` | String | `member` or `casual` |

---

## Data Exclusions

Files in `raw/` are excluded from git via `.gitignore` to avoid repository bloat.
Processed files (`trips_clean.csv`) are also gitignored.
**To reproduce results**: Download raw CSVs from source and re-run Capstone 2 pipeline.

---

**Last Updated:** 2025-10-04
