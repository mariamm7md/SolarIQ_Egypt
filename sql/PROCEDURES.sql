-- lOCATION PROCEDURES
-- 1- SELECT 
CREATE PROC LOCATION_SELECT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM Governorate
END;

-- 2- INSERT 
CREATE PROC LOCATION_INSERT
    @Governorate_Name NVARCHAR(100) 
    , @Lat FLOAT 
    , @Long FLOAT
AS 
BEGIN
    SET NOCOUNT ON;
    INSERT INTO Governorate (Governorate_Name , latitude , longitude)
    VALUES 
    (@Governorate_Name , @Lat ,@Long);
END;

-- 3- UPDATE
CREATE PROC LOCATION_UPDATE 
    @Governorate_Name NVARCHAR(100),
    @Lat FLOAT,
    @Long FLOAT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Governorate
    SET
        latitude = @Lat,
        longitude = @Long
    WHERE Governorate_Name = @Governorate_Name;
END;

-- 4- DELETE
CREATE PROC LOCATION_DELETE  
    @Governorate_Name NVARCHAR(100)
AS 
BEGIN
    SET NOCOUNT ON;
    DELETE FROM Governorate 
    WHERE Governorate_Name = @Governorate_Name
END;

--AIR QUALITY PROCEDURES
-- 1- SELECT 
CREATE PROC AIR_QUALITY_SELECT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM Air_quality
END;

-- 2- INSERT
CREATE PROC AIR_QUALITY_INSERT
       @governorate_Name NVARCHAR(100),
       @PM10 FLOAT,
       @PM2_5 FLOAT,
       @Carbon_Monoxide FLOAT,
       @Nitrogen_Dioxide FLOAT,
       @Sulphur_Dioxide FLOAT,
       @AQI_Level INT,
       @DATE DATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO Air_Quality
    (
       governorate_id,
       PM10,
       PM2_5,
       Carbon_Monoxide,
       Nitrogen_Dioxide,
       Sulphur_Dioxide,
       AQI_Level,
       AQI_Label,
       health_alert,
       pm25_exceeds_who,
       pollution_solar_penalty_pct,
       is_dust_storm,
       a_Date
    )
    SELECT 
       G.Governorate_ID,
       @PM10,
       @PM2_5,
       @Carbon_Monoxide,
       @Nitrogen_Dioxide,
       @Sulphur_Dioxide,
       @AQI_Level,
       CASE
            WHEN @AQI_Level = 1 THEN 'Good'
            WHEN @AQI_Level = 2 THEN 'Fair'
            WHEN @AQI_Level = 3 THEN 'Moderate'
            WHEN @AQI_Level = 4 THEN 'Poor'
            ELSE 'Very Poor'
       END,
       CASE WHEN @AQI_Level >= 4 THEN 1 ELSE 0 END,
       CASE WHEN @PM2_5 > 15 THEN 1 ELSE 0 END,
       ROUND(
            CASE
                WHEN ((@PM2_5 / 10.0) * 1.5) > 30 THEN 30
                WHEN ((@PM2_5 / 10.0) * 1.5) < 0 THEN 0
                ELSE ((@PM2_5 / 10.0) * 1.5)
            END
       ,2),
       CASE WHEN @PM10 > 500 THEN 1 ELSE 0 END,
       @DATE
    FROM Governorate G
    WHERE G.Governorate_Name = @governorate_Name;
END;

-- 3- UPDATE 
CREATE PROCEDURE AIR_QUALITY_UPDATE 
       @governorate_Name NVARCHAR(100),
       @PM10 FLOAT,
       @PM2_5 FLOAT,
       @Carbon_Monoxide FLOAT,
       @Nitrogen_Dioxide FLOAT,
       @Sulphur_Dioxide FLOAT,
       @AQI_Level INT,
       @DATE DATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE AQ
    SET
        AQ.governorate_ID = G.governorate_ID,
        AQ.PM10 = @PM10,
        AQ.PM2_5 = @PM2_5,
        AQ.Carbon_Monoxide  = @Carbon_Monoxide,
        AQ.Nitrogen_Dioxide = @Nitrogen_Dioxide,
        AQ.Sulphur_Dioxide = @Sulphur_Dioxide,
        AQ.AQI_Level = @AQI_Level,
        AQ.AQI_Label =
            CASE
                WHEN @AQI_Level = 1 THEN 'Good'
                WHEN @AQI_Level = 2 THEN 'Fair'
                WHEN @AQI_Level = 3 THEN 'Moderate'
                WHEN @AQI_Level = 4 THEN 'Poor'
                ELSE 'Very Poor'
            END,
        AQ.health_alert =
            CASE WHEN @AQI_Level >= 4 THEN 1 ELSE 0 END,
        AQ.pm25_exceeds_who =
            CASE WHEN @PM2_5 > 15 THEN 1 ELSE 0 END,
        AQ.pollution_solar_penalty_pct =
            ROUND(
                CASE
                    WHEN ((@PM2_5 / 10.0) * 1.5) > 30 THEN 30
                    WHEN ((@PM2_5 / 10.0) * 1.5) < 0 THEN 0
                    ELSE ((@PM2_5 / 10.0) * 1.5)
                END
            ,2),
        AQ.is_dust_storm =
            CASE WHEN @PM10 > 500 THEN 1 ELSE 0 END,
        AQ.a_DATE = @DATE
    FROM Air_Quality AQ
    INNER JOIN Governorate G
        ON G.Governorate_Name = @governorate_Name
    WHERE AQ.a_DATE = @DATE;
END;

-- 4- DELETE 
CREATE PROC AIR_QUALITY_DELETE
    @governorate_Name NVARCHAR(100),
    @DATE DATE
AS 
BEGIN
    SET NOCOUNT ON;
    DELETE AQ
    FROM Air_Quality AQ
    INNER JOIN Governorate G
        ON G.Governorate_ID = AQ.Governorate_ID
    WHERE G.Governorate_Name = @governorate_Name
      AND AQ.a_Date = @DATE;
END;

--WEATHER PROCEDURES

-- 1- SELECT
CREATE PROC WEATHER_SELECT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT *
    FROM WEATHER;
END;

-- 2- INSERT
CREATE PROC WEATHER_INSERT
       @governorate_name NVARCHAR(100),
       @T2M FLOAT,
       @T2M_MAX FLOAT,
       @T2M_MIN FLOAT,
       @RH2M FLOAT,
       @PRECTOTCORR FLOAT,
       @WS2M FLOAT,
       @WD2M FLOAT,
       @CLRSKY_SFC_SW_DWN FLOAT,
       @ALLSKY_SFC_SW_DWN FLOAT,
       @DATE DATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO WEATHER
    (
       governorate_ID,
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
       is_extreme_precip,
       w_date
    )
    SELECT
       G.Governorate_ID,
       @T2M,
       @T2M_MAX,
       @T2M_MIN,
       @RH2M,
       @PRECTOTCORR,
       @WS2M,
       @WD2M,
       @CLRSKY_SFC_SW_DWN,
       @ALLSKY_SFC_SW_DWN,
       CASE
            WHEN @CLRSKY_SFC_SW_DWN = 0 THEN NULL
            WHEN (@ALLSKY_SFC_SW_DWN / @CLRSKY_SFC_SW_DWN) > 1 THEN 1
            WHEN (@ALLSKY_SFC_SW_DWN / @CLRSKY_SFC_SW_DWN) < 0 THEN 0
            ELSE ROUND(@ALLSKY_SFC_SW_DWN / @CLRSKY_SFC_SW_DWN, 4)
       END,
       @ALLSKY_SFC_SW_DWN,
       ROUND(
            CASE WHEN (@T2M_MAX - 25) < 0 THEN 0
                 ELSE (@T2M_MAX - 25) * 0.4
            END, 2),
       ROUND(@T2M_MAX - @T2M_MIN, 2),
       ROUND(
            CASE
                WHEN (@CLRSKY_SFC_SW_DWN - @ALLSKY_SFC_SW_DWN) < 0 THEN 0
                ELSE (@CLRSKY_SFC_SW_DWN - @ALLSKY_SFC_SW_DWN)
            END, 4),
       CASE WHEN @T2M_MAX >= 40 THEN 1 ELSE 0 END,
       CASE WHEN @PRECTOTCORR >= 50 THEN 1 ELSE 0 END,
       @DATE
    FROM Governorate G
    WHERE G.Governorate_Name = @governorate_name;
END;

-- 3- UPDATE
CREATE PROC WEATHER_UPDATE
       @governorate_name NVARCHAR(100),
       @T2M FLOAT,
       @T2M_MAX FLOAT,
       @T2M_MIN FLOAT,
       @RH2M FLOAT,
       @PRECTOTCORR FLOAT,
       @WS2M FLOAT,
       @WD2M FLOAT,
       @CLRSKY_SFC_SW_DWN FLOAT,
       @ALLSKY_SFC_SW_DWN FLOAT,
       @DATE DATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE W
    SET
        W.governorate_id = G.Governorate_ID,
        W.T2M = @T2M,
        W.T2M_MAX = @T2M_MAX,
        W.T2M_MIN = @T2M_MIN,
        W.RH2M = @RH2M,
        W.PRECTOTCORR = @PRECTOTCORR,
        W.WS2M = @WS2M,
        W.WD2M = @WD2M,
        W.CLRSKY_SFC_SW_DWN = @CLRSKY_SFC_SW_DWN,
        W.ALLSKY_SFC_SW_DWN = @ALLSKY_SFC_SW_DWN,
        W.clearness_index =
            CASE
                WHEN @CLRSKY_SFC_SW_DWN = 0 THEN NULL
                WHEN (@ALLSKY_SFC_SW_DWN / @CLRSKY_SFC_SW_DWN) > 1 THEN 1
                WHEN (@ALLSKY_SFC_SW_DWN / @CLRSKY_SFC_SW_DWN) < 0 THEN 0
                ELSE ROUND(@ALLSKY_SFC_SW_DWN / @CLRSKY_SFC_SW_DWN, 4)
            END,
        W.peak_sun_hours = @ALLSKY_SFC_SW_DWN,
        W.temp_penalty_pct =
            ROUND(
                CASE WHEN (@T2M_MAX - 25) < 0 THEN 0
                     ELSE (@T2M_MAX - 25) * 0.4
                END, 2),
        W.temp_range = ROUND(@T2M_MAX - @T2M_MIN, 2),
        W.cloud_impact =
            ROUND(
                CASE
                    WHEN (@CLRSKY_SFC_SW_DWN - @ALLSKY_SFC_SW_DWN) < 0 THEN 0
                    ELSE (@CLRSKY_SFC_SW_DWN - @ALLSKY_SFC_SW_DWN)
                END, 4),
        W.is_hot_day = CASE WHEN @T2M_MAX >= 40 THEN 1 ELSE 0 END,
        W.is_extreme_precip = CASE WHEN @PRECTOTCORR >= 50 THEN 1 ELSE 0 END,
        W.w_date = @DATE
    FROM WEATHER W
    INNER JOIN Governorate G
        ON G.Governorate_Name = @governorate_name
    WHERE W.w_date = @DATE;
END;

-- 4- DELETE

CREATE PROC WEATHER_DELETE
    @governorate_Name NVARCHAR(100),
    @DATE DATE
AS 
BEGIN
    SET NOCOUNT ON;
    DELETE W
    FROM Weather W
    INNER JOIN Governorate G
        ON G.Governorate_ID = W.Governorate_ID
    WHERE G.Governorate_Name = @governorate_Name
      AND W.W_Date = @DATE;
END;

-- GetAirQualityByGovernorate

/*
تستقبل رقم المحافظة
وترجع بيانات جودة الهواء الخاصة بيها فقط
*/

CREATE PROC GetAirQualityByGovernorate @Governorate NVARCHAR(100) 
AS
BEGIN
	SELECT 
       [air_quality_id]
      ,G.[Governorate_Name]
	  ,[PM10]
      ,[PM2_5]
      ,[AQI_Level]
      ,[AQI_Label]
      ,[health_alert]
      ,[pollution_solar_penalty_pct]
      ,[is_dust_storm]
      ,[a_Date]
	FROM 
		Air_quality A
	INNER JOIN 
        Governorate G
    ON 
        G.governorate_id = A.governorate_id

    WHERE G.[Governorate_Name] = @Governorate
       
END;

EXEC GetAirQualityByGovernorate Cairo




--GetHighPollutionAreas

/*
أكثر المحافظات تلوثًا
*/

CREATE PROC GetHighPollutionAreas 
AS
BEGIN
    SELECT TOP(5)
        G.[Governorate_Name] 
        ,AVG(PM2_5) AS [Average PM2_5]
        ,AVG(PM10) AS [Average PM10]
        ,AVG(Carbon_Monoxide) AS [Average Carbon_Monoxide]
        ,AVG(Nitrogen_Dioxide) AS [Average Nitrogen Dioxide]
        ,AVG(Sulphur_Dioxide)  AS [Average Sulphur Dioxide]
    FROM 
        Air_Quality A
    INNER JOIN  
        Governorate G
    ON 
        G.governorate_id = A.governorate_id

    GROUP BY 
        G.[Governorate_Name]

    ORDER BY 
        [Average PM2_5] DESC

END;
     
EXEC GetHighPollutionAreas


-- GetHottestGovernorates
--أعلى المحافظات حرارة

CREATE PROC GetHottestGovernorates
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP(5)
        G.Governorate_Name,
        AVG(W.T2M_MAX) AS Avg_Max_Temperature,
        AVG(W.T2M) AS Avg_Temperature,
        MAX(W.T2M_MAX) AS Highest_Temperature
    FROM Weather W
    INNER JOIN Governorate G
        ON G.Governorate_ID = W.Governorate_ID

    GROUP BY G.Governorate_Name

    ORDER BY Avg_Max_Temperature DESC;
END;

--GetBestSolarGovernorates
--ترجع أفضل المحافظات المناسبة للطاقة الشمسية

CREATE PROC GetBestSolarGovernorates
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP(5)
        G.Governorate_Name,
        AVG(W.ALLSKY_SFC_SW_DWN) AS Avg_Solar_Radiation,
        AVG(W.clearness_index) AS Avg_Clearness_Index,
        AVG(W.peak_sun_hours) AS Avg_Peak_Sun_Hours
    FROM Weather W
    INNER JOIN Governorate G
        ON G.Governorate_ID = W.Governorate_ID

    GROUP BY G.Governorate_Name

    ORDER BY Avg_Solar_Radiation DESC;
END;


