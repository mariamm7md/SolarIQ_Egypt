"""
╔══════════════════════════════════════════════════════════════════╗
║   SolarIQ Egypt — Weather Data Cleaning (FINAL v3)              ║
║   File: weather_data.csv → data/silver/weather_clean.csv        ║
║   Rows: ~443,772 | Governorates: 27 | Period: 1981–2025         ║
╚══════════════════════════════════════════════════════════════════╝

KEY DECISIONS (WHY):
─────────────────────────────────────────────────────────────────
1. -999 → NaN  : NASA POWER uses -999 as "no data" flag. Keeping
   it would corrupt ALL averages and charts in Power BI.

2. date integer → datetime  : Power BI cannot filter/group on an
   integer like 19810101. Must be real datetime.

3. PRECTOTCORR > 50 mm  : 30 records across 18 governorates on
   the SAME days match known storm events. These are NOT errors —
   they represent real extreme rain events (mostly coastal).
   We FLAG them but do NOT remove them.

4. clearness_index = ALLSKY / CLRSKY  : Scientific ratio showing
   how much cloud/dust reduces radiation. Value close to 1 = ideal.
   Clipped to [0, 1] because ALLSKY can't exceed CLRSKY physically.

5. temp_penalty_pct  : Solar panels lose ~0.4% efficiency per °C
   above 25°C. This derived column feeds directly into the
   Solar Site Score formula.

6. No GROUP BY in this script  : This file stays at the DAILY
   GRAIN (one row per governorate per day). Aggregation happens
   in the Gold layer ONLY — so your Fact/Dimension model stays
   flexible for any drill-down in Power BI.
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# ── Setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

RAW_PATH    = 'data/raw/weather_data.csv'
SILVER_PATH = 'data/silver/weather_clean.csv'


# ══════════════════════════════════════════════════════════════════
# STEP 1 — LOAD
# ══════════════════════════════════════════════════════════════════
def load_raw(path: str) -> pd.DataFrame:
    logger.info(f"Loading: {path}")
    df = pd.read_csv(path)
    # Normalize column names: strip whitespace, keep original case
    df.columns = [c.strip() for c in df.columns]
    logger.info(f"Loaded: {len(df):,} rows × {len(df.columns)} columns")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 2 — AUDIT (run before any cleaning, print full report)
# ══════════════════════════════════════════════════════════════════
def audit_data(df: pd.DataFrame) -> None:
    logger.info("=" * 60)
    logger.info("DATA QUALITY AUDIT — WEATHER")
    logger.info("=" * 60)

    logger.info(f"\nShape  : {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")

    logger.info("\n--- Null Values ---")
    nulls = df.isnull().sum()
    for col, count in nulls[nulls > 0].items():
        logger.warning(f"  {col}: {count:,} nulls ({count/len(df)*100:.1f}%)")
    if nulls.sum() == 0:
        logger.info("  No nulls found.")

    logger.info("\n--- NASA -999 Error Codes ---")
    for col in ['ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN']:
        if col in df.columns:
            count = (df[col] == -999).sum()
            pct   = count / len(df) * 100
            logger.warning(f"  {col}: {count:,} values = -999 ({pct:.1f}%)")

    logger.info("\n--- Date Column ---")
    logger.info(f"  dtype  : {df['date'].dtype}")
    logger.info(f"  sample : {df['date'].head(3).tolist()}")
    logger.info(f"  range  : {df['date'].min()} → {df['date'].max()}")

    logger.info("\n--- Precipitation Outlier Check ---")
    high_prec = df[df['PRECTOTCORR'] > 50]
    logger.info(f"  Rows with PRECTOTCORR > 50 mm: {len(high_prec)}")
    if len(high_prec) > 0:
        logger.info("  Distribution by governorate:")
        logger.info(high_prec.groupby('governorate').size().to_string())
        logger.info("  DECISION: These match known storm events → KEEP, FLAG only.")

    logger.info("\n--- Governorates ---")
    logger.info(f"  Count : {df['governorate'].nunique()}")
    logger.info(f"  Values: {sorted(df['governorate'].unique())}")


# ══════════════════════════════════════════════════════════════════
# STEP 3 — CLEAN DATES
# ══════════════════════════════════════════════════════════════════
def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: NASA POWER stores dates as integers (e.g. 19810101).
    Power BI treats integers as numbers, not dates — time intelligence
    functions (DATEADD, SAMEPERIODLASTYEAR, etc.) won't work.
    We MUST convert to proper datetime64.
    """
    logger.info("Converting integer dates → datetime64...")
    df['date'] = pd.to_datetime(
        df['date'].astype(str), format='%Y%m%d', errors='coerce'
    )
    bad_dates = df['date'].isnull().sum()
    if bad_dates > 0:
        logger.warning(f"  {bad_dates} dates failed to parse — investigate!")
    else:
        logger.info(f"  All dates converted successfully.")
    logger.info(f"  Range: {df['date'].min().date()} → {df['date'].max().date()}")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 4 — REPLACE ERROR CODES
# ══════════════════════════════════════════════════════════════════
def replace_error_codes(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: NASA POWER uses -999 as a sentinel for "measurement not
    available". It is NOT a real physical value. Any average, min,
    max, or chart that includes -999 will be completely wrong.

    APPROACH: Replace with NaN (Not a Number). Power BI and pandas
    both ignore NaN in aggregations, which is exactly what we want.
    We do NOT fill/interpolate — keeping NaN is honest about the gap.
    """
    logger.info("Replacing NASA -999 error codes → NaN...")
    solar_cols = ['ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN']
    for col in solar_cols:
        if col in df.columns:
            count = (df[col] == -999).sum()
            df[col] = df[col].replace(-999, np.nan)
            logger.info(f"  {col}: {count:,} values replaced")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 5 — TIME FEATURES
# ══════════════════════════════════════════════════════════════════
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: Power BI dashboards need to filter/slice by year, month,
    season, decade. We add these here ONCE so every dashboard
    downstream can use them without re-calculating.

    These columns will also feed the DimDate table in your star schema.
    """
    logger.info("Adding time-based features...")

    df['year']         = df['date'].dt.year
    df['month']        = df['date'].dt.month
    df['month_name']   = df['date'].dt.strftime('%b')   # Jan, Feb...
    df['quarter']      = df['date'].dt.quarter
    df['day_of_year']  = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)

    # Egypt meteorological seasons (NOT European calendar)
    season_map = {
        12: 'Winter', 1: 'Winter',  2: 'Winter',
        3:  'Spring', 4: 'Spring',  5: 'Spring',
        6:  'Summer', 7: 'Summer',  8: 'Summer',
        9:  'Autumn', 10: 'Autumn', 11: 'Autumn'
    }
    df['season'] = df['month'].map(season_map)

    # Decade — for long-term climate trend analysis (Dashboard #29)
    df['decade'] = (df['year'] // 10) * 10

    # Period buckets for before/after comparisons
    def get_period(y):
        if y < 2000:  return '1981–1999'
        if y < 2010:  return '2000–2009'
        if y < 2020:  return '2010–2019'
        return '2020+'

    df['period'] = df['year'].apply(get_period)

    logger.info("  Time features added: year, month, quarter, season, decade, period")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 6 — DERIVED SOLAR FEATURES
# ══════════════════════════════════════════════════════════════════
def add_solar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHY: Raw columns alone aren't enough for the Solar Site Score.
    We derive scientific metrics that engineers actually use to
    evaluate solar sites.
    """
    logger.info("Calculating derived solar features...")

    # ── Clearness Index (Kt) ──────────────────────────────────────
    # WHY: Kt = ALLSKY / CLRSKY tells us how much of the available
    # solar energy actually reaches the ground (accounting for cloud,
    # dust, and pollution). Closer to 1.0 = cleaner sky = better site.
    valid_sky = (
        df['CLRSKY_SFC_SW_DWN'].notna() &
        df['ALLSKY_SFC_SW_DWN'].notna() &
        (df['CLRSKY_SFC_SW_DWN'] > 0)
    )
    df['clearness_index'] = np.nan
    df.loc[valid_sky, 'clearness_index'] = (
        df.loc[valid_sky, 'ALLSKY_SFC_SW_DWN'] /
        df.loc[valid_sky, 'CLRSKY_SFC_SW_DWN']
    ).clip(0, 1).round(4)

    # ── Peak Sun Hours ────────────────────────────────────────────
    # WHY: NASA POWER's ALLSKY unit is kWh/m²/day = Peak Sun Hours.
    # This is the standard metric used by solar engineers to size
    # PV systems and estimate annual energy production.
    df['peak_sun_hours'] = df['ALLSKY_SFC_SW_DWN']

    # ── Temperature Penalty ───────────────────────────────────────
    # WHY: Crystalline silicon panels (standard type) lose ~0.4%
    # efficiency for every °C above 25°C (STC standard).
    # Formula: penalty = (T_max - 25) × 0.4%  (clipped at 0)
    df['temp_penalty_pct'] = (
        (df['T2M_MAX'] - 25).clip(lower=0) * 0.4
    ).round(2)

    # ── Temperature Range (Thermal Stress) ───────────────────────
    # WHY: Large daily swings cause thermal expansion/contraction
    # which degrades panel connections over time. High range =
    # higher maintenance cost.
    df['temp_range'] = (df['T2M_MAX'] - df['T2M_MIN']).round(2)

    # ── Cloud/Dust Impact ─────────────────────────────────────────
    # WHY: Difference between what COULD arrive (clear sky) vs what
    # DID arrive. Large gap = lots of cloud or dust → worse site.
    df['cloud_impact'] = (
        df['CLRSKY_SFC_SW_DWN'] - df['ALLSKY_SFC_SW_DWN']
    ).clip(lower=0).round(4)

    # ── Extreme Heat Flag ─────────────────────────────────────────
    # WHY: Days above 40°C significantly reduce panel output and
    # can trigger thermal shutdowns. Used in Dashboard #8 (hot days
    # trend) and in the Site Score penalty calculation.
    df['is_hot_day'] = (df['T2M_MAX'] >= 40).astype(int)

    # ── Extreme Rain Flag (do NOT remove, just flag) ──────────────
    # WHY: Rain > 50mm is physically possible in Egypt during
    # Mediterranean storms (Alex, Matrouh). We confirmed Jan 22 2004
    # was a real regional dust storm + rain event affecting 18
    # governorates simultaneously. Removing it would erase real data.
    # However, we flag it so analysts can filter if needed.
    df['is_extreme_precip'] = (df['PRECTOTCORR'] > 50).astype(int)

    logger.info("  Solar features added: clearness_index, peak_sun_hours, "
                "temp_penalty_pct, temp_range, cloud_impact, is_hot_day, "
                "is_extreme_precip")
    return df


# ══════════════════════════════════════════════════════════════════
# STEP 7 — VALIDATE
# ══════════════════════════════════════════════════════════════════
def validate_cleaned(df: pd.DataFrame) -> None:
    logger.info("=" * 60)
    logger.info("POST-CLEANING VALIDATION — WEATHER")
    logger.info("=" * 60)

    errors = []

    # No more -999 values
    for col in ['ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN']:
        if col in df.columns:
            bad = (df[col] == -999).sum()
            if bad > 0:
                errors.append(f"Still have {bad} -999 in {col}!")
            else:
                logger.info(f"  ✔ {col}: no -999 remaining")

    # Date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        errors.append("'date' column is not datetime64!")
    else:
        logger.info(f"  ✔ date dtype: {df['date'].dtype}")

    # Required derived columns exist
    required_cols = [
        'year', 'month', 'season', 'clearness_index',
        'temp_penalty_pct', 'peak_sun_hours', 'is_hot_day'
    ]
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing column: {col}")
        else:
            logger.info(f"  ✔ {col}: present")

    if errors:
        for e in errors:
            logger.error(f"  ✗ {e}")
        raise AssertionError("Validation failed — see errors above.")

    logger.info(f"\n  Final shape : {len(df):,} rows × {len(df.columns)} columns")
    logger.info(f"  Governorates: {df['governorate'].nunique()}")
    logger.info(
        f"  Date range  : {df['date'].min().date()} → {df['date'].max().date()}"
    )
    logger.info("\n  ✔ ALL CHECKS PASSED")


# ══════════════════════════════════════════════════════════════════
# STEP 8 — PRINT SAMPLE
# ══════════════════════════════════════════════════════════════════
def print_sample(df: pd.DataFrame) -> None:
    print("\n" + "=" * 70)
    print("SAMPLE — FIRST 5 ROWS (after cleaning)")
    print("=" * 70)

    display_cols = [
        'governorate', 'date', 'year', 'month', 'season',
        'T2M', 'T2M_MAX', 'T2M_MIN',
        'ALLSKY_SFC_SW_DWN', 'CLRSKY_SFC_SW_DWN',
        'clearness_index', 'peak_sun_hours',
        'temp_penalty_pct', 'RH2M', 'WS2M', 'is_hot_day'
    ]
    # Filter to only columns that actually exist
    display_cols = [c for c in display_cols if c in df.columns]
    print(df[display_cols].head(5).to_string(index=False))

    print("\n" + "=" * 70)
    print("SOLAR RADIATION — GOVERNORATE AVERAGES (Top 10)")
    print("=" * 70)
    summary = df.groupby('governorate').agg(
        avg_radiation=('ALLSKY_SFC_SW_DWN', 'mean'),
        avg_clearness=('clearness_index', 'mean'),
        avg_psh      =('peak_sun_hours', 'mean'),
        hot_days_pct =('is_hot_day', 'mean')
    ).round(3).sort_values('avg_radiation', ascending=False)
    print(summary.head(10).to_string())


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    os.makedirs('data/silver', exist_ok=True)

    df = load_raw(RAW_PATH)
    audit_data(df)

    df = clean_dates(df)
    df = replace_error_codes(df)
    df = add_time_features(df)
    df = add_solar_features(df)

    validate_cleaned(df)
    print_sample(df)

    df = df[df['date'].dt.year >= 2003]
    df = df[df['date'].dt.year <= 2024]

    # Save — UTF-8 BOM for Arabic compatibility in Excel & Power BI
    df.to_csv(SILVER_PATH, index=False, encoding='utf-8-sig')
    logger.info(f"\n✔ Saved to: {SILVER_PATH}")


if __name__ == '__main__':
    main()