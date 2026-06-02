/* SolarIQ Egypt - Final Deployment Script 
   Layers: Silver (Air Quality, Weather) & Gold (Solar Site Scores)
*/

-- 1. «·≈⁄œ«œ«  «·√„‰Ì… ( ‰›– „—… Ê«Õœ…)
IF NOT EXISTS (SELECT * FROM sys.symmetric_keys WHERE name LIKE '%MS_DatabaseMasterKey%')
BEGIN
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'Project123';
END

IF NOT EXISTS (SELECT * FROM sys.database_scoped_credentials WHERE name = 'my_cred')
BEGIN 
    CREATE DATABASE SCOPED CREDENTIAL my_cred
    WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
    SECRET = 'sv=2025-11-05&ss=bfqt&srt=sco&sp=rwdlacupyx&se=2026-06-05T22:56:23Z&st=2026-05-07T14:41:23Z&spr=https&sig=yrf7NwcysT0T8Pq82fLepBc1RN3pujPmkwdgilzj6HE%3D';
END

-- 2.  ⁄—Ì› „’«œ— «·»Ì«‰«  (Data Sources) »’Ì€… abs:// «·„œ⁄Ê„…
IF EXISTS (SELECT * FROM sys.external_data_sources WHERE name = 'my_blob') DROP EXTERNAL DATA SOURCE my_blob;
CREATE EXTERNAL DATA SOURCE my_blob
WITH (
    LOCATION = 'abs://silver@solariqstorage.blob.core.windows.net', 
    CREDENTIAL = my_cred
);

IF EXISTS (SELECT * FROM sys.external_data_sources WHERE name = 'gold_blob') DROP EXTERNAL DATA SOURCE gold_blob;
CREATE EXTERNAL DATA SOURCE gold_blob
WITH (
    LOCATION = 'abs://gold@solariqstorage.blob.core.windows.net', 
    CREDENTIAL = my_cred 
);

-- 3.  ⁄—Ì›  ‰”Ìﬁ «·„·› (File Format)
IF EXISTS (SELECT * FROM sys.external_file_formats WHERE name = 'my_csv_format') DROP EXTERNAL FILE FORMAT my_csv_format;
CREATE EXTERNAL FILE FORMAT my_csv_format
WITH (
    FORMAT_TYPE = DELIMITEDTEXT,
    FORMAT_OPTIONS (
        FIELD_TERMINATOR = ',',
        STRING_DELIMITER = '"',
        FIRST_ROW = 2
    )
);

-- 4. ≈‰‘«¡ Ãœ«Ê· «·ÿ»ﬁ… «·›÷Ì… (Silver Layer)
IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'AirQuality_External') DROP EXTERNAL TABLE [dbo].[AirQuality_External];
CREATE EXTERNAL TABLE [dbo].[AirQuality_External] (
    [datetime] DATE,
    [Governorate] NVARCHAR(100),
    [lat] FLOAT,
    [lon] FLOAT,
    [PM10] FLOAT,
    [PM2_5] FLOAT,
    [Nitrogen_Dioxide] FLOAT,
    [Sulphur_Dioxide] FLOAT,
    [Carbon_Monoxide] FLOAT,
    [AQI_Level] INT,
    [date] DATE,
    [year] INT,
    [month] INT,
    [month_name] NVARCHAR(20),
    [quarter] INT,
    [day_of_week] INT,
    [is_weekend] INT,
    [season] NVARCHAR(50),
    [aqi_label] NVARCHAR(50),
    [health_alert] INT,
    [pm25_exceeds_who] INT,
    [pollution_solar_penalty_pct] FLOAT,
    [is_dust_storm] INT
)
WITH (
    LOCATION = 'air_quality_clean.csv', 
    DATA_SOURCE = my_blob,
    FILE_FORMAT = my_csv_format
);

IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'Weather_External') DROP EXTERNAL TABLE [dbo].[Weather_External];
CREATE EXTERNAL TABLE [dbo].[Weather_External] (
    [governorate] NVARCHAR(100),
    [date] DATE,
    [lat] FLOAT,
    [lon] FLOAT,
    [T2M] FLOAT,
    [T2M_MAX] FLOAT,
    [T2M_MIN] FLOAT,
    [RH2M] FLOAT,
    [PRECTOTCORR] FLOAT,
    [WS2M] FLOAT,
    [WD2M] FLOAT,
    [CLRSKY_SFC_SW_DWN] FLOAT,
    [ALLSKY_SFC_SW_DWN] FLOAT,
    [year] INT,
    [month] INT,
    [month_name] NVARCHAR(20),
    [quarter] INT,
    [day_of_year] INT,
    [week_of_year] INT,
    [season] NVARCHAR(50),
    [decade] NVARCHAR(50),
    [period] NVARCHAR(50),
    [clearness_index] FLOAT,
    [peak_sun_hours] FLOAT,
    [temp_penalty_pct] FLOAT,
    [temp_range] FLOAT,
    [cloud_impact] FLOAT,
    [is_hot_day] INT,
    [is_extreme_precip] INT
)
WITH (
    LOCATION = 'weather_clean.csv', 
    DATA_SOURCE = my_blob,
    FILE_FORMAT = my_csv_format
);

-- 5. ≈‰‘«¡ ÃœÊ· «·ÿ»ﬁ… «·–Â»Ì… (Gold Layer) 
IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'SolarSiteScores_External') DROP EXTERNAL TABLE [dbo].[SolarSiteScores_External];
CREATE EXTERNAL TABLE [dbo].[SolarSiteScores_External] (
    [Governorate] NVARCHAR(100),
    [avg_solar_radiation] FLOAT,
    [avg_peak_sun_hours] FLOAT,
    [avg_temp_max] FLOAT,
    [avg_wind_speed] FLOAT,
    [avg_humidity] FLOAT,
    [hot_days_pct] FLOAT, 
    [avg_clearness_index] FLOAT,
    [avg_temp_penalty] FLOAT,
    [avg_aqi] FLOAT,
    [avg_pm25] FLOAT,
    [avg_pm10] FLOAT,
    [dust_storm_days] INT,
    [avg_pollution_penalty] FLOAT,
    [score_ghi] FLOAT,
    [score_clearness] FLOAT,
    [score_temp] FLOAT,
    [score_wind] FLOAT,
    [score_humidity] FLOAT,
    [score_air] FLOAT,
    [solar_site_score] FLOAT,
    [rank] FLOAT, 
    [grade] NVARCHAR(50) ,
    [investment_reco] NVARCHAR(100)   
)
WITH (
    LOCATION = 'solar_site_scores.csv', 
    DATA_SOURCE = gold_blob, 
    FILE_FORMAT = my_csv_format
);



-- 6 Test Tables
SELECT 'Air Quality' as TableName, COUNT(*) as RowsCount FROM [AirQuality_External]
UNION ALL
SELECT 'Weather', COUNT(*) FROM [Weather_External]
UNION ALL
SELECT 'Gold Scores', COUNT(*) FROM [SolarSiteScores_External];

SELECT TOP(10) * FROM [dbo].[SolarSiteScores_External] ORDER BY [rank] ASC;