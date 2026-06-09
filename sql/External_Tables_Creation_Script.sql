-- ==========================================
-- 1. DROP EXISTING EXTERNAL TABLES
-- ==========================================
IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'AirQuality_External') 
    DROP EXTERNAL TABLE [dbo].[AirQuality_External];

IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'Weather_External') 
    DROP EXTERNAL TABLE [dbo].[Weather_External];

IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'SolarSiteScores_External') 
    DROP EXTERNAL TABLE [dbo].[SolarSiteScores_External];

-- ==========================================
-- 2. RECREATE EXTERNAL DATA SOURCES
-- ==========================================
IF EXISTS (SELECT * FROM sys.external_data_sources WHERE name = 'my_blob') 
    DROP EXTERNAL DATA SOURCE my_blob;

CREATE EXTERNAL DATA SOURCE my_blob WITH (
    LOCATION   = 'abs://silver@solarstorage.blob.core.windows.net',
    CREDENTIAL = my_cred
);

IF EXISTS (SELECT * FROM sys.external_data_sources WHERE name = 'gold_blob') 
    DROP EXTERNAL DATA SOURCE gold_blob;

CREATE EXTERNAL DATA SOURCE gold_blob WITH (
    LOCATION   = 'abs://gold@solarstorage.blob.core.windows.net',
    CREDENTIAL = my_cred 
);

-- ==========================================
-- 3. CREATE EXTERNAL TABLES
-- ==========================================

-- --- AIR QUALITY EXTERNAL TABLE ---
CREATE EXTERNAL TABLE [dbo].[AirQuality_External] (
    [datetime]                    DATE, 
    [Governorate]                 NVARCHAR(100), 
    [lat]                         FLOAT, 
    [lon]                         FLOAT, 
    [PM10]                        FLOAT, 
    [PM2_5]                       FLOAT,
    [Nitrogen_Dioxide]            FLOAT, 
    [Sulphur_Dioxide]             FLOAT, 
    [Carbon_Monoxide]             FLOAT, 
    [AQI_Level]                   INT, 
    [date]                        DATE,
    [year]                        INT, 
    [month]                       INT, 
    [month_name]                  NVARCHAR(20), 
    [quarter]                     INT, 
    [day_of_week]                 INT, 
    [is_weekend]                  INT,
    [season]                      NVARCHAR(50), 
    [aqi_label]                   NVARCHAR(50), 
    [health_alert]                INT, 
    [pm25_exceeds_who]            INT,
    [pollution_solar_penalty_pct] FLOAT, 
    [is_dust_storm]               INT
) 
WITH (
    LOCATION    = 'air_quality_clean.csv', 
    DATA_SOURCE = my_blob, 
    FILE_FORMAT = my_csv_format
);

-- --- WEATHER EXTERNAL TABLE ---
CREATE EXTERNAL TABLE [dbo].[Weather_External] (
    [governorate]                 NVARCHAR(100), 
    [date]                        DATE, 
    [lat]                         FLOAT, 
    [lon]                         FLOAT, 
    [T2M]                         FLOAT, 
    [T2M_MAX]                     FLOAT,
    [T2M_MIN]                     FLOAT, 
    [RH2M]                        FLOAT, 
    [PRECTOTCORR]                 FLOAT, 
    [WS2M]                        FLOAT, 
    [WD2M]                        FLOAT, 
    [CLRSKY_SFC_SW_DWN]           FLOAT,
    [ALLSKY_SFC_SW_DWN]           FLOAT, 
    [year]                        INT, 
    [month]                       INT, 
    [month_name]                  NVARCHAR(20), 
    [quarter]                     INT,
    [day_of_year]                 INT, 
    [week_of_year]                INT, 
    [season]                      NVARCHAR(50), 
    [decade]                      NVARCHAR(50), 
    [period]                      NVARCHAR(50),
    [clearness_index]             FLOAT, 
    [peak_sun_hours]              FLOAT, 
    [temp_penalty_pct]            FLOAT, 
    [temp_range]                  FLOAT,
    [cloud_impact]                FLOAT, 
    [is_hot_day]                  INT, 
    [is_extreme_precip]           INT
) 
WITH (
    LOCATION    = 'weather_clean.csv', 
    DATA_SOURCE = my_blob, 
    FILE_FORMAT = my_csv_format
);

-- --- SOLAR SITE SCORES EXTERNAL TABLE ---
CREATE EXTERNAL TABLE [dbo].[SolarSiteScores_External] (
    [Governorate]                 NVARCHAR(100), 
    [avg_solar_radiation]         FLOAT, 
    [avg_peak_sun_hours]          FLOAT, 
    [avg_temp_max]                FLOAT,
    [avg_wind_speed]              FLOAT, 
    [avg_humidity]                FLOAT, 
    [hot_days_pct]                FLOAT, 
    [avg_clearness_index]         FLOAT,
    [avg_temp_penalty]            FLOAT, 
    [avg_aqi]                     FLOAT, 
    [avg_pm25]                    FLOAT, 
    [avg_pm10]                    FLOAT, 
    [dust_storm_days]             INT,
    [avg_pollution_penalty]       FLOAT, 
    [score_ghi]                   FLOAT, 
    [score_clearness]             FLOAT, 
    [score_temp]                  FLOAT,
    [score_wind]                  FLOAT, 
    [score_humidity]              FLOAT, 
    [score_air]                   FLOAT, 
    [solar_site_score]            FLOAT, 
    [rank]                        FLOAT, 
    [grade]                       NVARCHAR(50), 
    [investment_reco]             NVARCHAR(100)
) 
WITH (
    LOCATION    = 'solar_site_scores.csv', 
    DATA_SOURCE = gold_blob, 
    FILE_FORMAT = my_csv_format
);