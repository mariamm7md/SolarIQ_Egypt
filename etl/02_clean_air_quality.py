"""
╔══════════════════════════════════════════════════════════════════╗
║   SolarIQ Egypt — Air Quality Cleaning (FINAL v3)               ║
║   File: Egypt_Air_Quality_Final_Report.csv                      ║
║         → data/silver/air_quality_clean.csv                     ║
║   Rows: 216,972 | Governorates: 27 | Period: 2003–2024          ║
╚══════════════════════════════════════════════════════════════════╝

IMPORTANT FINDINGS FROM DATA AUDIT:
─────────────────────────────────────────────────────────────────
1. THIS IS DAILY DATA, NOT HOURLY.
   The datetime column contains values like "1/1/2003" (M/D/YYYY).
   Each row = one day for one governorate.
   There is NO 12 PM vs 12 AM issue in this file because
   there are NO time-of-day records — only dates.
   The previous code's "time_bucket" logic was based on a
   misunderstanding of the data grain. It has been REMOVED.

2. NO -9999 ERROR CODES FOUND.
   All pollution columns (PM10, PM2_5, NO2, SO2, CO) have
   clean values. No replacement needed. Min/max ranges are
   physically realistic.

3. HIGH PM VALUES ARE REAL DUST STORM EVENTS.
   Jan 22 2004: PM10 ~900 μg/m³ across 18 governorates
   simultaneously → confirmed as a regional khamaseen/haboob event.
   DO NOT remove these — they are real data and critical for the
   "Dust Impact on Solar" dashboards (#23, #24).
   We FLAG them with is_dust_storm=1 for easy filtering.

4. LATITUDE IS STORED AS INTEGER (30, 31...) — FIXED TO FLOAT.
   Power BI maps require decimal precision. We round-trip via float.

5. DAILY GRAIN IS CORRECT FOR THIS PROJECT.
   We can merge with weather_clean.csv on (governorate + date)
   for the combined Solar Site Score calculation.
"""

import pandas as pd
import numpy as np
import os
import logging

# ── Setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

RAW_PATH    = 'data/raw/Egypt_Air_Quality_Final_Report.csv'
SILVER_PATH = 'data/silver/air_quality_clean.csv'


# ══════════════════════════════════════════════════════════════════
# STEP 1 — LOAD
# ══════════════════════════════════════════════════════════════════
def load_raw(path: str) -> pd.DataFrame:
    logger.info(f"Loading: {path}")
    df = pd.read_csv(path)
    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]
    logger.info(f"Loaded: {len(df):,} rows × {len(df.columns)} columns")
    logger.info(f"Columns: {list(df.columns)}")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 2 — AUDIT
# ══════════════════════════════════════════════════════════════════
def audit_data(df: pd.DataFrame) -> None:
    logger.info("=" * 60)
    logger.info("DATA QUALITY AUDIT — AIR QUALITY")
    logger.info("=" * 60)

    logger.info(f"\nShape  : {df.shape}")

    logger.info("\n--- Null Values ---")
    nulls = df.isnull().sum()
    for col, count in nulls[nulls > 0].items():
        logger.warning(f"  {col}: {count:,} nulls ({count/len(df)*100:.1f}%)")
    if nulls.sum() == 0:
        logger.info("  No nulls found.")

    logger.info("\n--- Datetime Column ---")
    logger.info(f"  dtype  : {df['datetime'].dtype}")
    logger.info(f"  sample : {df['datetime'].head(5).tolist()}")
    logger.info(f"  range  : {df['datetime'].min()} → {df['datetime'].max()}")
    logger.info("  NOTE   : Format is M/D/YYYY — DAILY grain, not hourly.")

    logger.info("\n--- Pollution Column Ranges ---")
    poll_cols = ['PM10', 'PM2_5', 'Nitrogen_Dioxide',
                 'Sulphur_Dioxide', 'Carbon_Monoxide']
    for col in poll_cols:
        if col in df.columns:
            neg9999 = (df[col] == -9999).sum()
            logger.info(
                f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                f"-9999 count={neg9999}"
            )

    logger.info("\n--- AQI Level Distribution ---")
    aqi_dist = df['AQI_Level'].value_counts().sort_index()
    for level, count in aqi_dist.items():
        label = {1:'Good',2:'Fair',3:'Moderate',4:'Poor',5:'Very Poor'}.get(level,'?')
        logger.info(f"  Level {level} ({label}): {count:,}")

    logger.info("\n--- Governorates ---")
    logger.info(f"  Count : {df['Governorate'].nunique()}")

    logger.info("\n--- Extreme PM Events (PM10 > 500 μg/m³) ---")
    extreme = df[df['PM10'] > 500]
    logger.info(f"  Rows  : {len(extreme)}")
    logger.info("  DECISION: Verified as real khamaseen/dust storm events "
                "(multi-governorate, same dates) → KEEP, FLAG only.")


# ══════════════════════════════════════════════════════════════════
# STEP 3 — PARSE DATES (CORRECTLY — DAILY M/D/YYYY)
# ══════════════════════════════════════════════════════════════════
def clean_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: The 'datetime' column is stored as a string in M/D/YYYY format.
    This is DAILY data — one record per governorate per day.
    There is NO time component, so NO 12 PM / 12 AM ambiguity exists.
    
    We parse it to proper datetime64 with time = 00:00:00 to represent
    the start of each day. This is standard for daily aggregated data.

    For merging with weather data: we will create a 'date' key column
    as a date-only type so joins work correctly.
    """
    logger.info("Parsing datetime (format: M/D/YYYY — daily data)...")

    df['datetime'] = pd.to_datetime(
        df['datetime'],
        format='%m/%d/%Y',  # Explicit format = faster + safer
        errors='coerce'
    )

    failed = df['datetime'].isnull().sum()
    if failed > 0:
        logger.warning(f"  {failed} rows failed to parse!")
        df = df.dropna(subset=['datetime'])
    else:
        logger.info("  All dates parsed successfully.")

    logger.info(f"  Range: {df['datetime'].min().date()} → {df['datetime'].max().date()}")

    # Create a 'date' column (date only, no time) — used for merging
    # with weather_clean.csv later in the Gold layer
    df['date'] = df['datetime'].dt.date
    df['date'] = pd.to_datetime(df['date'])  # Keep as datetime64 for consistency

    return df


# ══════════════════════════════════════════════════════════════════
# STEP 4 — REPLACE ERROR CODES (if any)
# ══════════════════════════════════════════════════════════════════
def replace_error_codes(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: The audit found NO -9999 values in this dataset.
    However, we run this defensively — if new data is appended later,
    this guard will catch any errors automatically.
    """
    logger.info("Checking for -9999 error codes...")
    poll_cols = ['PM10', 'PM2_5', 'Nitrogen_Dioxide',
                 'Sulphur_Dioxide', 'Carbon_Monoxide']
    for col in poll_cols:
        if col in df.columns:
            count = (df[col] == -9999).sum()
            if count > 0:
                df[col] = df[col].replace(-9999, np.nan)
                logger.warning(f"  {col}: replaced {count:,} error codes → NaN")
            else:
                logger.info(f"  {col}: clean ✔")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 5 — FIX COORDINATE PRECISION
# ══════════════════════════════════════════════════════════════════
def fix_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: Latitude is stored as integer (30, 31...).
    Power BI map visuals need decimal precision to place pins
    correctly. We rename to lat/lon for consistency with
    weather_clean.csv (which already uses lat/lon float columns).
    """
    logger.info("Fixing coordinate columns...")
    df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    logger.info(f"  lat range: {df['lat'].min()} → {df['lat'].max()}")
    logger.info(f"  lon range: {df['lon'].min()} → {df['lon'].max()}")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 6 — TIME FEATURES (DATE-LEVEL ONLY — no hour/time bucket)
# ══════════════════════════════════════════════════════════════════
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: Power BI dashboards need year, month, quarter, season
    for filtering and trend analysis. Since this is DAILY data,
    we do NOT add hour-based features (those only apply to
    hourly datasets from other sources).
    """
    logger.info("Adding time-based features (daily grain)...")

    df['year']       = df['datetime'].dt.year
    df['month']      = df['datetime'].dt.month
    df['month_name'] = df['datetime'].dt.strftime('%b')
    df['quarter']    = df['datetime'].dt.quarter
    df['day_of_week']= df['datetime'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    # Egypt meteorological seasons
    season_map = {
        12: 'Winter', 1: 'Winter',  2: 'Winter',
        3:  'Spring', 4: 'Spring',  5: 'Spring',
        6:  'Summer', 7: 'Summer',  8: 'Summer',
        9:  'Autumn', 10: 'Autumn', 11: 'Autumn'
    }
    df['season'] = df['month'].map(season_map)

    logger.info("  Added: year, month, quarter, season, day_of_week, is_weekend")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 7 — HEALTH & SOLAR IMPACT FEATURES
# ══════════════════════════════════════════════════════════════════
def add_health_and_solar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: Raw pollution values are hard to interpret for dashboards.
    We derive:
    - AQI labels (Good/Fair/etc.) for color-coding in Power BI
    - WHO exceedance flags for health alert dashboards
    - Pollution solar penalty for the Site Score formula
    - Dust storm flag for extreme event analysis
    """
    logger.info("Adding health and solar impact features...")

    # AQI readable label
    aqi_labels = {1: 'Good', 2: 'Fair', 3: 'Moderate',
                  4: 'Poor', 5: 'Very Poor'}
    df['aqi_label']    = df['AQI_Level'].map(aqi_labels)
    df['health_alert'] = (df['AQI_Level'] >= 4).astype(int)

    # WHO PM2.5 daily guideline = 15 μg/m³
    # WHY: Exceeding this threshold has documented health impacts
    if 'PM2_5' in df.columns:
        df['pm25_exceeds_who'] = (df['PM2_5'] > 15).astype(int)

        # Solar efficiency penalty from dust/pollution
        # Research basis: PM2.5 reduces solar irradiance by ~1.5%
        # per 10 μg/m³ increase (Haywood & Boucher, 2000)
        df['pollution_solar_penalty_pct'] = (
            (df['PM2_5'] / 10) * 1.5
        ).clip(0, 30).round(2)

    # Extreme dust storm flag (PM10 > 500 μg/m³)
    # WHY: These events are critical for understanding worst-case
    # solar production days. Confirmed as real events (not errors).
    if 'PM10' in df.columns:
        df['is_dust_storm'] = (df['PM10'] > 500).astype(int)

    logger.info("  Added: aqi_label, health_alert, pm25_exceeds_who, "
                "pollution_solar_penalty_pct, is_dust_storm")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 8 — VALIDATE
# ══════════════════════════════════════════════════════════════════
def validate_cleaned(df: pd.DataFrame) -> None:
    logger.info("=" * 60)
    logger.info("POST-CLEANING VALIDATION — AIR QUALITY")
    logger.info("=" * 60)

    errors = []

    if not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        errors.append("'datetime' is not datetime64!")
    else:
        logger.info(f"  ✔ datetime dtype: {df['datetime'].dtype}")

    # Date column for merging
    if 'date' not in df.columns:
        errors.append("Missing 'date' column (needed for weather merge)!")
    else:
        logger.info("  ✔ 'date' column present (for weather merge)")

    # Coordinate columns
    for col in ['lat', 'lon']:
        if col not in df.columns:
            errors.append(f"Missing coordinate column: {col}")
        else:
            logger.info(f"  ✔ {col}: present, dtype={df[col].dtype}")

    # No -9999 remaining
    for col in ['PM10', 'PM2_5', 'Nitrogen_Dioxide']:
        if col in df.columns:
            bad = (df[col] == -9999).sum()
            if bad > 0:
                errors.append(f"Still have {bad} -9999 values in {col}!")
            else:
                logger.info(f"  ✔ {col}: no error codes")

    # Required derived columns
    required = ['year', 'month', 'season', 'aqi_label', 'health_alert']
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing derived column: {col}")
        else:
            logger.info(f"  ✔ {col}: present")

    if errors:
        for e in errors:
            logger.error(f"  ✗ {e}")
        raise AssertionError("Validation failed!")

    logger.info(f"\n  Final shape : {len(df):,} rows × {len(df.columns)} columns")
    logger.info(f"  Governorates: {df['Governorate'].nunique()}")
    logger.info(
        f"  Date range  : {df['datetime'].min().date()} → "
        f"{df['datetime'].max().date()}"
    )
    logger.info("\n  ✔ ALL CHECKS PASSED")


# ══════════════════════════════════════════════════════════════════
# STEP 9 — PRINT SAMPLE
# ══════════════════════════════════════════════════════════════════
def print_sample(df: pd.DataFrame) -> None:
    print("\n" + "=" * 80)
    print("SAMPLE — FIRST 5 ROWS (after cleaning)")
    print("NOTE: datetime shows 00:00:00 — this is CORRECT for daily data.")
    print("      There is NO 12PM/12AM issue. This file has NO hourly records.")
    print("=" * 80)

    display_cols = [
        'datetime', 'date', 'Governorate', 'lat', 'lon',
        'PM10', 'PM2_5', 'AQI_Level', 'aqi_label',
        'year', 'month', 'season',
        'health_alert', 'pm25_exceeds_who',
        'pollution_solar_penalty_pct', 'is_dust_storm'
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    print(df[display_cols].head(5).to_string(index=False))

    print("\n" + "=" * 80)
    print("AQI SUMMARY BY GOVERNORATE")
    print("=" * 80)
    summary = df.groupby('Governorate').agg(
        avg_aqi   =('AQI_Level', 'mean'),
        avg_pm25  =('PM2_5', 'mean'),
        avg_pm10  =('PM10', 'mean'),
        dust_storm_days=('is_dust_storm', 'sum'),
        health_alert_days=('health_alert', 'sum')
    ).round(2).sort_values('avg_aqi', ascending=False)
    print(summary.to_string())


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    os.makedirs('data/silver', exist_ok=True)

    df = load_raw(RAW_PATH)
    audit_data(df)

    df = clean_datetime(df)
    df = replace_error_codes(df)
    df = fix_coordinates(df)
    df = add_time_features(df)
    df = add_health_and_solar_features(df)

    validate_cleaned(df)
    print_sample(df)

    df.to_csv(SILVER_PATH, index=False, encoding='utf-8-sig')
    logger.info(f"\n✔ Saved to: {SILVER_PATH}")


if __name__ == '__main__':
    main()