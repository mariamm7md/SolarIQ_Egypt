-- 1. CREATE DATABASE
CREATE DATABASE SolarIQ_DW;
GO

USE SolarIQ_DW;
GO

-- 2. CREATE Dim Date
CREATE TABLE Dim_Date (
    Date_ID INT PRIMARY KEY, 
    Date DATE,
    Year INT,
    Month INT,
    Month_Name NVARCHAR(20),
    Quarter NVARCHAR(5), 
    Day INT,
    Day_of_Week INT,
    Day_Name NVARCHAR(20),
    Week_of_Year INT,
    Season NVARCHAR(50),
    Decade INT,         
    Period NVARCHAR(50)
);
GO
/*
-- INSERT INTO Dim Date
INSERT INTO Dim_Date (
    Date_ID, Date, Year, Month, Month_Name, Quarter, Day, 
    Day_of_Week, Day_Name, Week_of_Year, Season, Decade, Period
) 
SELECT DISTINCT 
    CAST(FORMAT(Date, 'yyyyMMdd') AS INT) AS [Date_ID], -- EX: 20260518
    Date AS [Date],
    YEAR(Date) AS [Year],
    MONTH(Date) AS [Month],
    FORMAT(Date, 'MMMM') AS [Month_Name],
    'Q' + CAST(DATEPART(QUARTER, Date) AS NCHAR(1)) AS [Quarter],
    DAY(Date) AS [Day],
    DATEPART(WEEKDAY, Date) AS [Day_of_Week],
    FORMAT(Date, 'dddd') AS [Day_Name],
    DATEPART(WEEK, Date) AS [Week_of_Year],
    CASE 
        WHEN MONTH(Date) IN (12, 1, 2) THEN 'Winter'
        WHEN MONTH(Date) IN (3, 4, 5)  THEN 'Spring'
        WHEN MONTH(Date) IN (6, 7, 8)  THEN 'Summer'
        WHEN MONTH(Date) IN (9, 10, 11) THEN 'Autumn'
    END AS [Season],
    ((YEAR(Date) / 10) * 10) AS [Decade],
    CASE 
        WHEN YEAR(Date) < 2000 THEN '1981–1999'
        WHEN YEAR(Date) < 2010 THEN '2000–2009'
        WHEN YEAR(Date) < 2020 THEN '2010–2019'
        ELSE '2020+'
    END AS [Period]
FROM 
    Results; 

*/
-- 2. CREATE Dim Governorate
CREATE TABLE Dim_Governorate(
    Governorate_ID INT IDENTITY(1,1) PRIMARY KEY,
    Governorate_Name NVARCHAR(100),
    Region NVARCHAR(50),
    Latitude FLOAT,
    Longitude FLOAT

);

--Add Region
UPDATE Dim_Governorate 
SET Region = 

    CASE 
        WHEN Governorate_Name IN ('Cairo', 'Giza', 'Qalyubia') THEN 'Greatest Cairo'
        
        WHEN Governorate_Name IN ('Dakahlia', 'Damietta', 'Gharbia', 'Kafr El Sheikh', 'Monufia', 'Sharqia', 'Beheira', 'Ismailia', 'Port Said', 'Suez') THEN 'Delta and Canal'
        
        WHEN Governorate_Name IN ('Aswan', 'Asyut', 'Beni Suef', 'Fayoum', 'Luxor', 'Minya', 'Qena', 'Sohag') THEN 'Upper Egypt'
        
        WHEN Governorate_Name IN ('Matrouh', 'New Valley', 'North Sinai', 'South Sinai', 'Red Sea') THEN 'Frontier Governorates'
        
        WHEN Governorate_Name IN ('Alexandria') THEN 'Alxendaria and North Coast'
        
        ELSE 'Other'
        END;
 
-- 3. CREATE FACT WEATHER

create TABLE Fact_Weather (
    Weather_ID INT IDENTITY(1,1) PRIMARY KEY,

    Governorate_Name nvarchar(100),
    Date date,
    Governorate_ID INT,
    Date_ID INT,

    T2M FLOAT,
    T2M_MAX FLOAT,
    T2M_MIN FLOAT,

    RH2M FLOAT,
    PRECTOTCORR FLOAT,

    WS2M FLOAT,
    WD2M FLOAT,

    CLRSKY_SFC_SW_DWN FLOAT,
    ALLSKY_SFC_SW_DWN FLOAT,

    clearness_index FLOAT,
    peak_sun_hours FLOAT,

    temp_penalty_pct FLOAT,
    temp_range FLOAT,
    cloud_impact FLOAT,

    is_hot_day INT,
    is_extreme_precip INT


);
GO

-- UPDATE COLUMNS DATE ID , Governorate ID
UPDATE W
SET W.Governorate_ID = G.Governorate_ID
FROM Fact_Weather W
INNER JOIN Dim_Governorate G
    ON W.Governorate_Name = G.Governorate_Name;


UPDATE W
SET W.Date_ID = D.Date_ID
FROM Fact_Weather W
INNER JOIN Dim_Date D
    ON W.Date = D.Date;


-- DROP COLUMNS Governorate Name , DATE
ALTER TABLE Fact_Weather 
DROP COLUMN Governorate_Name, [Date];


--INSERT INTO FACT WEATHER

/*
INSERT INTO Fact_Weather (
    Governorate_ID,
    Date_ID,
    T2M,
    T2M_MAX,
    T2M_MIN,
    RH2M,
    PRECTOTCORR,
    WS2M,
    WD2M,
    CLRSKY_SFC_SW_DWN,
    ALLSKY_SFC_SW_DWN,
    clearness_index,
    peak_sun_hours,
    temp_penalty_pct,
    temp_range,
    cloud_impact,
    is_hot_day,
    is_extreme_precip
)

SELECT
    L.Governorate_ID,
    D.Date_ID,

    W.T2M,
    W.T2M_MAX,
    W.T2M_MIN,

    W.RH2M,
    W.PRECTOTCORR,

    W.WS2M,
    W.WD2M,

    W.CLRSKY_SFC_SW_DWN,
    W.ALLSKY_SFC_SW_DWN,

    W.clearness_index,
    W.peak_sun_hours,

    W.temp_penalty_pct,
    W.temp_range,
    W.cloud_impact,

    W.is_hot_day,
    W.is_extreme_precip

FROM Weather W

INNER JOIN Dim_Governorate L
    ON W.governorate = L.Governorate
INNER JOIN Dim_Date D
    ON W.W_Date = D.Date

GO
*/


-- 4. CREATE FACT AIR QUALITY

CREATE TABLE Fact_Air_Quality(
      [Air_Quality_ID] INT IDENTITY(1,1) PRIMARY KEY
      ,[Governorate_Name] nvarchar(100)
      ,[Date] date
      ,Governorate_ID INT
      ,Date_ID INT
      ,[PM10] FLOAT
      ,[PM2_5] FLOAT
      ,[Carbon_Monoxide] FLOAT
      ,[Nitrogen_Dioxide] FLOAT
      ,[Sulphur_Dioxide] FLOAT
      ,[AQI_Level] INT
      ,[AQI_Label] NVARCHAR(50)
      ,[Health_Alert] INT
      ,[PM25_Exceeds_Who] INT
      ,[Pollution_Solar_Penalty_Pct] FLOAT
      ,[Is_Dust_Storm] INT
);

-- UPDATE COLUMNS DATE ID , Governorate ID
UPDATE A
SET A.Governorate_ID = G.Governorate_ID
FROM Fact_Air_Quality A
INNER JOIN Dim_Governorate G
    ON A.Governorate_Name = G.Governorate_Name;


UPDATE A
SET A.Date_ID = D.Date_ID
FROM Fact_Air_Quality A
INNER JOIN Dim_Date D
    ON A.Date = D.Date;



-- DROP COLUMNS Governorate Name , DATE
ALTER TABLE Fact_Air_Quality
DROP COLUMN Governorate_Name, [Date];


/*
--INSERT INTO FACT AIR QUALITY
INSERT INTO Fact_Air_Quality(
       [Governorate_ID]
      ,[Date_ID]
      ,[PM10]
      ,[PM2_5]
      ,[Carbon_Monoxide]
      ,[Nitrogen_Dioxide]
      ,[Sulphur_Dioxide]
      ,[AQI_Level]
      ,[AQI_Label]
      ,[Health_Alert]
      ,[PM25_Exceeds_Who]
      ,[Pollution_Solar_Penalty_Pct]
      ,[Is_Dust_Storm]

)

SELECT d.[Governorate_ID]
      ,D.[Date_ID]
      ,A.[PM10]
      ,A.[PM2_5]
      ,A.[Carbon_Monoxide]
      ,A.[Nitrogen_Dioxide]
      ,A.[Sulphur_Dioxide]
      ,A.[AQI_Level]
      ,A.[AQI_Label]
      ,A.[health_alert]
      ,A.[pm25_exceeds_who]
      ,A.[pollution_solar_penalty_pct]
      ,A.[is_dust_storm]
FROM Air_Quality A
INNER JOIN Dim_Governorate G
ON G.Governorate_ID = A.Governorate_ID
INNER JOIN Dim_Date D
ON D.Date = A.A_Date
*/