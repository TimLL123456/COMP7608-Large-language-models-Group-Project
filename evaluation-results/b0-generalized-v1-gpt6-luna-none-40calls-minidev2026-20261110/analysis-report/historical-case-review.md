# 全部107題歷史轉變審閱



66題修正、41題退步；歷史budget、timeout及retry不同，不將SQL變化視為prompt單因果。每題完整頁包含兩輪observable trace、SQL diff及Gold。



<a id="q11"></a>

## [Q11](failure-case-review.md#q11) · 歷史啱→本輪錯 · california_schools

候選關聯：R7／排名／集合。缺少最低起始年級選擇，直接回傳全部合資格學校；另加入 EILName='High School'。

歷史→本輪：model replies 6→8；tool attempts 6→9；SQL attempts 3→5。

Question：Following up on the SAT participation review: among the currently operating high schools in the district with NCES identification number 0613360 that had no SAT test takers, which one begins serving students at the earliest grade? Please give me each such school's name and grade span served. Note that a high school must actually enroll students through grade 12-offering grade 12 without enrollment doesn't count. A school with no SAT record counts as having zero SAT test takers and should be included; only exclude schools with a positive number of SAT test takers. Compare starting grades as school grades-preschool comes before kindergarten, which comes before grade 1-and use the lowest grade the school actually serves, not just what it offers. If several schools tie at the earliest grade, list them all alphabetically by school name.

歷史SQL：
```sql
SELECT s.School AS school_name, s.GSserved AS grade_span_served
FROM schools AS s
LEFT JOIN satscores AS sat ON sat.cds = s.CDSCode
WHERE s.NCESDist = '0613360'
  AND s.StatusType = 'Active'
  AND s.GSserved LIKE '%12%'
  AND (sat.NumTstTakr IS NULL OR sat.NumTstTakr = 0)
  AND CAST(SUBSTR(s.GSserved, 1, INSTR(s.GSserved, '-') - 1) AS INTEGER) = (
      SELECT MIN(CAST(SUBSTR(s2.GSserved, 1, INSTR(s2.GSserved, '-') - 1) AS INTEGER))
      FROM schools AS s2
      LEFT JOIN satscores AS sat2 ON sat2.cds = s2.CDSCode
      WHERE s2.NCESDist = '0613360'
        AND s2.StatusType = 'Active'
        AND s2.GSserved LIKE '%12%'
        AND (sat2.NumTstTakr IS NULL OR sat2.NumTstTakr = 0)
  )
ORDER BY school_name;
```

本輪SQL：
```sql
SELECT s.School, s.GSserved
FROM schools AS s
LEFT JOIN satscores AS ss ON ss.cds = s.CDSCode
WHERE s.NCESDist = '0613360'
  AND s.StatusType = 'Active'
  AND s.EILName = 'High School'
  AND s.GSserved IS NOT NULL
  AND s.GSserved LIKE '%12%'
  AND (ss.NumTstTakr IS NULL OR ss.NumTstTakr = 0)
ORDER BY s.School;
```



<a id="q12"></a>

## [Q12](failure-case-review.md#q12) · 歷史啱→本輪錯 · california_schools

候選關聯：R4／篩選對齊。以 DOC='56'、District 特定名稱及 Active 代替 DOCType='State Board of Education'，候選學校集合不同。

歷史→本輪：model replies 9→6；tool attempts 10→9；SQL attempts 6→6。

Question：I'm profiling schools run directly by the California State Board of Education. Which of those schools has the highest average SAT reading score? If several tie for the highest, give me all of them. For each school, I need its name and its full mailing street address - the complete address, not an abbreviated one. Only include schools the State Board runs directly, and the score must be the school's own result, not a district-wide figure.

歷史SQL：
```sql
SELECT s.School, s.MailStreet
FROM schools AS s
JOIN satscores AS ss ON ss.cds = s.CDSCode
WHERE s.DOCType = 'State Board of Education'
  AND s.School IS NOT NULL
  AND ss.rtype = 'S'
  AND ss.AvgScrRead = (
      SELECT MAX(ss2.AvgScrRead)
      FROM schools AS s2
      JOIN satscores AS ss2 ON ss2.cds = s2.CDSCode
      WHERE s2.DOCType = 'State Board of Education'
        AND s2.School IS NOT NULL
        AND ss2.rtype = 'S'
  );
```

本輪SQL：
```sql
SELECT s.School, s.MailStreet
FROM schools AS s
JOIN satscores AS ss ON ss.cds = s.CDSCode
WHERE s.DOC = '56'
  AND s.District = 'State Board of Education Charter'
  AND s.StatusType = 'Active'
  AND ss.AvgScrRead IS NOT NULL
  AND ss.AvgScrRead = (
      SELECT MAX(ss2.AvgScrRead)
      FROM schools AS s2
      JOIN satscores AS ss2 ON ss2.cds = s2.CDSCode
      WHERE s2.DOC = '56'
        AND s2.District = 'State Board of Education Charter'
        AND s2.StatusType = 'Active'
        AND ss2.AvgScrRead IS NOT NULL
  );
```



<a id="q17"></a>

## [Q17](historical-case-review.md#q17) · 歷史錯→本輪啱 · california_schools

候選關聯：R1／識別碼／篩選。補回CDS前導0並限rtype='S'；兩項同時變更，未分離各自貢獻。

歷史→本輪：model replies 4→6；tool attempts 4→6；SQL attempts 1→3。

Question：I'm looking at SAT participation in Contra Costa County. How many schools in the county had more SAT test takers than the school with CDS code 7618040730051? That school is itself a Contra Costa County school, so I just want the count of schools strictly ahead of it by number of SAT test takers, based on the SAT results snapshot in the data. A single number is all I need.

歷史SQL：
```sql
SELECT COUNT(*) AS schools_ahead
FROM satscores AS s
JOIN schools AS sch ON sch.CDSCode = s.cds
WHERE sch.County = 'Contra Costa'
  AND s.NumTstTakr > (
    SELECT target.NumTstTakr
    FROM satscores AS target
    WHERE target.cds = '7618040730051'
  );
```

本輪SQL：
```sql
SELECT COUNT(*) AS schools_ahead
FROM satscores AS s
JOIN schools AS sc ON sc.CDSCode = s.cds
WHERE sc.County = 'Contra Costa'
  AND s.rtype = 'S'
  AND s.NumTstTakr > (
      SELECT NumTstTakr
      FROM satscores
      WHERE cds = '07618040730051'
        AND rtype = 'S'
  );
```



<a id="q23"></a>

## [Q23](historical-case-review.md#q23) · 歷史錯→本輪啱 · california_schools

候選關聯：R4／學校層篩選。新增rtype='S'並改管理員email fallback，候選SAT集合更貼合學校層。

歷史→本輪：model replies 6→6；tool attempts 7→7；SQL attempts 3→3。

Question：I'm looking at the schools that the State Board of Education directly runs or charters. Which individual school among them had the most students score at least 1500 on the SAT? Please give me that school's name and its administrator's email address. If two schools tie on that count, list both.

歷史SQL：
```sql
SELECT
    COALESCE(s.School, s.District) AS School,
    s.AdmEmail1 AS AdministratorEmail
FROM schools AS s
JOIN satscores AS sat ON sat.cds = s.CDSCode
WHERE s.DOCType = 'State Board of Education'
  AND sat.NumGE1500 = (
      SELECT MAX(sat2.NumGE1500)
      FROM schools AS s2
      JOIN satscores AS sat2 ON sat2.cds = s2.CDSCode
      WHERE s2.DOCType = 'State Board of Education'
  );
```

本輪SQL：
```sql
WITH school_scores AS (
    SELECT
        s.CDSCode,
        s.School,
        s.AdmEmail1,
        s.AdmEmail2,
        s.AdmEmail3,
        ss.NumGE1500
    FROM schools AS s
    JOIN satscores AS ss ON ss.cds = s.CDSCode
    WHERE s.DOCType = 'State Board of Education'
      AND ss.rtype = 'S'
),
top_score AS (
    SELECT MAX(NumGE1500) AS NumGE1500
    FROM school_scores
)
SELECT
    school_scores.School,
    COALESCE(school_scores.AdmEmail1, school_scores.AdmEmail2, school_scores.AdmEmail3) AS AdministratorEmail
FROM school_scores
JOIN top_score ON school_scores.NumGE1500 = top_score.NumGE1500;
```



<a id="q26"></a>

## [Q26](historical-case-review.md#q26) · 歷史錯→本輪啱 · california_schools

候選關聯：R2／百分比尺度。FRPM已存比例乘100，符合percentage尺度；join與count策略亦同時變更。

歷史→本輪：model replies 5→9；tool attempts 7→10；SQL attempts 3→6。

Question：I'm reviewing charter school funding models and want to compare the directly funded and locally funded charters that are currently in operation. For each of the two funding categories, please give me: (1) the number of charter schools currently in operation, counting only schools the directory lists as active (open), not closed or merged; (2) total 2014-2015 K-12 enrollment; (3) the average percentage of students eligible for free or reduced-price meals, on a 0-100 scale, rounded to two decimals; and (4) the average combined SAT score (reading + math + writing) across schools that have reported scores, rounded to two decimals. Note that schools without SAT results should still count in the school count, enrollment total, and meal-eligibility average. Please give me these figures grouped by funding category.

歷史SQL：
```sql
WITH active_charters AS (
    SELECT CDSCode, FundingType
    FROM schools
    WHERE StatusType = 'Active'
      AND Charter = 1
      AND FundingType IN ('Directly funded', 'Locally funded')
),
funding_stats AS (
    SELECT
        ac.FundingType,
        COUNT(*) AS school_count,
        SUM(f.`Enrollment (K-12)`) AS total_enrollment,
        AVG(f.`Percent (%) Eligible FRPM (K-12)`) AS avg_frpm_eligible_pct
    FROM active_charters AS ac
    LEFT JOIN frpm AS f
        ON f.CDSCode = ac.CDSCode
       AND f.`Academic Year` = '2014-2015'
    GROUP BY ac.FundingType
),
sat_stats AS (
    SELECT
        ac.FundingType,
        AVG(s.AvgScrRead + s.AvgScrMath + s.AvgScrWrite) AS avg_combined_sat
    FROM active_charters AS ac
    JOIN satscores AS s
        ON s.cds = ac.CDSCode
    WHERE s.AvgScrRead IS NOT NULL
      AND s.AvgScrMath IS NOT NULL
      AND s.AvgScrWrite IS NOT NULL
    GROUP BY ac.FundingType
)
SELECT
    fs.FundingType,
    fs.school_count,
    fs.total_enrollment,
    ROUND(fs.avg_frpm_eligible_pct, 2) AS avg_frpm_eligible_pct,
    ROUND(ss.avg_combined_sat, 2) AS avg_combined_sat
FROM funding_stats AS fs
LEFT JOIN sat_stats AS ss
    ON ss.FundingType = fs.FundingType
ORDER BY fs.FundingType;
```

本輪SQL：
```sql
SELECT
    s.FundingType,
    COUNT(DISTINCT s.CDSCode) AS charter_school_count,
    SUM(f."Enrollment (K-12)") AS total_2014_2015_k12_enrollment,
    ROUND(AVG(f."Percent (%) Eligible FRPM (K-12)" * 100), 2) AS average_frpm_eligible_percentage,
    ROUND(
        AVG(
            CASE
                WHEN sa.AvgScrRead IS NOT NULL
                 AND sa.AvgScrMath IS NOT NULL
                 AND sa.AvgScrWrite IS NOT NULL
                THEN sa.AvgScrRead + sa.AvgScrMath + sa.AvgScrWrite
            END
        ),
        2
    ) AS average_combined_sat_score
FROM schools AS s
LEFT JOIN frpm AS f
    ON f.CDSCode = s.CDSCode
   AND f."Academic Year" = '2014-2015'
LEFT JOIN satscores AS sa
    ON sa.cds = s.CDSCode
WHERE s.Charter = 1
  AND s.StatusType = 'Active'
  AND s.FundingType IN ('Directly funded', 'Locally funded')
GROUP BY s.FundingType;
```



<a id="q29"></a>

## [Q29](historical-case-review.md#q29) · 歷史錯→本輪啱 · california_schools

候選關聯：R2／欄位來源。funding分組由schools.FundingType改frpm Charter Funding Type。

歷史→本輪：model replies 9→7；tool attempts 9→7；SQL attempts 6→4。

Question：I'm studying charter schools run by county offices of education. Using the K-12 school meal program records, for the charter schools these county offices operate, broken down by charter funding type (directly funded and locally funded only), I'd like to know: how many are currently operating, their total K-12 enrollment, and their total number of FRPM-eligible K-12 students. A school counts as currently operating only if its status is Active. Please give me one row per funding type, with directly funded first.

歷史SQL：
```sql
SELECT
    s.FundingType,
    COUNT(*) AS operating_schools,
    SUM(f.`Enrollment (K-12)`) AS total_k12_enrollment,
    SUM(f.`FRPM Count (K-12)`) AS total_frpm_eligible_k12_students
FROM schools AS s
JOIN frpm AS f
    ON s.CDSCode = f.CDSCode
WHERE s.DOCType = 'County Office of Education (COE)'
  AND s.Charter = 1
  AND s.StatusType = 'Active'
  AND s.FundingType IN ('Directly funded', 'Locally funded')
GROUP BY s.FundingType
ORDER BY CASE s.FundingType
    WHEN 'Directly funded' THEN 1
    WHEN 'Locally funded' THEN 2
END;
```

本輪SQL：
```sql
SELECT
    f.`Charter Funding Type`,
    COUNT(*) AS currently_operating_schools,
    SUM(f.`Enrollment (K-12)`) AS total_k12_enrollment,
    SUM(f.`FRPM Count (K-12)`) AS total_frpm_eligible_k12_students
FROM frpm AS f
JOIN schools AS s
    ON f.CDSCode = s.CDSCode
WHERE s.DOCType = 'County Office of Education (COE)'
  AND s.Charter = 1
  AND s.StatusType = 'Active'
  AND f.`Charter Funding Type` IN ('Directly funded', 'Locally funded')
GROUP BY f.`Charter Funding Type`
ORDER BY CASE f.`Charter Funding Type`
    WHEN 'Directly funded' THEN 1
    WHEN 'Locally funded' THEN 2
END;
```



<a id="q32"></a>

## [Q32](historical-case-review.md#q32) · 歷史錯→本輪啱 · california_schools

候選關聯：R4／取消附加篩選。取消Low Grade/High Grade排P及Enrollment>0等條件。

歷史→本輪：model replies 9→11；tool attempts 10→13；SQL attempts 6→9。

Question：I'm planning a targeted meal-support pilot and want to compare one school against similar schools in our county. The county I mean is the one where Fremont High (CDS code 1612590125716) is located - please identify the county by that CDS code, not by the school name. For that county, please look at all K-12 schools with more than 500 free meals and fewer than 700 FRPM meals, and give me back: the county name; the number of schools; the average free-meal percentage and the average FRPM percentage, both on a 0-100 scale with each school's own percentage rounded to 2 decimals before averaging; the number of charter schools and the number of non-charter schools (charter vs. non-charter per the charter indicator in the frpm data); and the average SAT score, where a school's SAT score is the sum of its three SAT section averages, counted only for schools that actually have SAT records, with no SAT record meaning the school is simply excluded from that average. Please round the reported averages to 2 decimals.

歷史SQL：
```sql
WITH target_county AS (
    SELECT `County Name` AS county_name
    FROM frpm
    WHERE CDSCode = '01612590125716'
),
eligible_schools AS (
    SELECT
        f.CDSCode,
        f.`County Name` AS county_name,
        ROUND(f.`Free Meal Count (K-12)` * 100.0 / f.`Enrollment (K-12)`, 2) AS free_meal_pct,
        ROUND(f.`FRPM Count (K-12)` * 100.0 / f.`Enrollment (K-12)`, 2) AS frpm_pct,
        f.`Charter School (Y/N)` AS charter
    FROM frpm AS f
    WHERE f.`County Name` = (SELECT county_name FROM target_county)
      AND f.`Low Grade` <> 'P'
      AND f.`High Grade` <> 'P'
      AND f.`Free Meal Count (K-12)` > 500
      AND f.`FRPM Count (K-12)` < 700
      AND f.`Enrollment (K-12)` > 0
),
school_sat AS (
    SELECT
        cds,
        AvgScrRead + AvgScrMath + AvgScrWrite AS sat_score
    FROM satscores
    WHERE AvgScrRead IS NOT NULL
      AND AvgScrMath IS NOT NULL
      AND AvgScrWrite IS NOT NULL
)
SELECT
    e.county_name,
    COUNT(*) AS school_count,
    ROUND(AVG(e.free_meal_pct), 2) AS avg_free_meal_percentage,
    ROUND(AVG(e.frpm_pct), 2) AS avg_frpm_percentage,
    SUM(CASE WHEN e.charter = 1 THEN 1 ELSE 0 END) AS charter_school_count,
    SUM(CASE WHEN e.charter = 0 THEN 1 ELSE 0 END) AS non_charter_school_count,
    ROUND(AVG(ss.sat_score), 2) AS avg_sat_score
FROM eligible_schools AS e
LEFT JOIN school_sat AS ss ON ss.cds = e.CDSCode
GROUP BY e.county_name;
```

本輪SQL：
```sql
WITH eligible AS (
    SELECT
        f.CDSCode,
        f.`County Name` AS county,
        f.`Charter School (Y/N)` AS charter,
        ROUND(
            f.`Free Meal Count (K-12)` * 100.0 / f.`Enrollment (K-12)`,
            2
        ) AS free_pct,
        ROUND(
            f.`FRPM Count (K-12)` * 100.0 / f.`Enrollment (K-12)`,
            2
        ) AS frpm_pct
    FROM frpm AS f
    WHERE f.`County Name` = (
        SELECT `County Name`
        FROM frpm
        WHERE CDSCode = '01612590125716'
    )
      AND f.`Free Meal Count (K-12)` > 500
      AND f.`FRPM Count (K-12)` < 700
),
sat AS (
    SELECT
        cds,
        AvgScrRead + AvgScrMath + AvgScrWrite AS total_score
    FROM satscores
    WHERE AvgScrRead IS NOT NULL
      AND AvgScrMath IS NOT NULL
      AND AvgScrWrite IS NOT NULL
)
SELECT
    e.county,
    COUNT(*) AS school_count,
    ROUND(AVG(e.free_pct), 2) AS average_free_meal_percentage,
    ROUND(AVG(e.frpm_pct), 2) AS average_frpm_percentage,
    SUM(CASE WHEN e.charter = 1 THEN 1 ELSE 0 END) AS charter_school_count,
    SUM(CASE WHEN e.charter = 0 THEN 1 ELSE 0 END) AS non_charter_school_count,
    ROUND(AVG(s.total_score), 2) AS average_sat_score
FROM eligible AS e
LEFT JOIN sat AS s
    ON s.cds = e.CDSCode
GROUP BY e.county;
```



<a id="q33"></a>

## [Q33](historical-case-review.md#q33) · 歷史錯→本輪啱 · california_schools

候選關聯：R8／保留一般查詢。原本硬寫519/12，改按County、DOCType及OpenDate動態COUNT/12。

歷史→本輪：model replies 12→7；tool attempts 12→8；SQL attempts 9→4。

Question：I'm studying the 1980 growth of public schooling in San Diego County. What was the average number of schools per month that opened in San Diego County in 1980 under a school district's jurisdiction? I need just that single number. Please average over all 12 months of 1980 (months with no openings count as zero), and give me the exact average without rounding.

歷史SQL：
```sql
SELECT 519.0 / 12;
```

本輪SQL：
```sql
SELECT COUNT(*) / 12.0 AS average_schools_per_month
FROM schools
WHERE County = 'San Diego'
  AND DOCType IN (
    'Elementary School District',
    'High School District',
    'Unified School District'
  )
  AND OpenDate >= '1980-01-01'
  AND OpenDate < '1981-01-01';
```



<a id="q35"></a>

## [Q35](historical-case-review.md#q35) · 歷史錯→本輪啱 · california_schools

候選關聯：R7／型別契約。取消printf文字化比例，保留原生數值。

歷史→本輪：model replies 7→6；tool attempts 8→7；SQL attempts 4→3。

Question：A parent is asking about a school and could only give me the CDS code 1612590137943. Can you look up that school and give me its name, county, district, and city; its K-12 enrollment; the number of K-12 students eligible for free or reduced price meals and the percentage eligible (report the percentage exactly as it appears, without rounding); and the SAT results - number of test takers, average reading score, average math score, average writing score, and the number of test takers whose total score is at least 1500?

歷史SQL：
```sql
SELECT
    s.School AS school_name,
    s.County AS county,
    s.District AS district,
    s.City AS city,
    f."Enrollment (K-12)" AS k12_enrollment,
    f."FRPM Count (K-12)" AS k12_frpm_eligible_count,
    printf('%!.17g', f."Percent (%) Eligible FRPM (K-12)") AS k12_frpm_eligible_percentage,
    t.NumTstTakr AS sat_test_takers,
    t.AvgScrRead AS sat_average_reading_score,
    t.AvgScrMath AS sat_average_math_score,
    t.AvgScrWrite AS sat_average_writing_score,
    t.NumGE1500 AS sat_test_takers_total_score_at_least_1500
FROM schools AS s
LEFT JOIN frpm AS f ON f.CDSCode = s.CDSCode
LEFT JOIN satscores AS t ON t.cds = s.CDSCode
WHERE s.CDSCode = '01612590137943';
```

本輪SQL：
```sql
SELECT
    s.School AS school_name,
    s.County AS county,
    s.District AS district,
    s.City AS city,
    f."Enrollment (K-12)" AS enrollment_k12,
    f."FRPM Count (K-12)" AS frpm_count_k12,
    f."Percent (%) Eligible FRPM (K-12)" AS percent_eligible_frpm_k12,
    t.NumTstTakr AS sat_test_takers,
    t.AvgScrRead AS average_reading_score,
    t.AvgScrMath AS average_math_score,
    t.AvgScrWrite AS average_writing_score,
    t.NumGE1500 AS test_takers_total_score_at_least_1500
FROM schools AS s
LEFT JOIN frpm AS f ON f.CDSCode = s.CDSCode
LEFT JOIN satscores AS t ON t.cds = s.CDSCode
WHERE s.CDSCode = '01612590137943';
```



<a id="q41"></a>

## [Q41](historical-case-review.md#q41) · 歷史錯→本輪啱 · california_schools

候選關聯：R1／有效值域。High Grade由寬鬆CAST改明確K、1至8，避免其他字串CAST為0。

歷史→本輪：model replies 5→6；tool attempts 5→6；SQL attempts 2→3。

Question：I'm auditing FRPM enrollment reporting and need to contact some elementary and middle schools. Please list the name and street address of every named school whose K-12 enrollment exceeds its enrollment of students aged 5-17 by more than 30 students, and whose highest grade of enrollment is grade 8 or below. Kindergarten counts as grade 8 or below. Give me one row per school; any order is fine.

歷史SQL：
```sql
SELECT s.School AS name, s.Street AS street_address
FROM frpm AS f
JOIN schools AS s ON s.CDSCode = f.CDSCode
WHERE s.School IS NOT NULL
  AND TRIM(s.School) <> ''
  AND f."Enrollment (K-12)" - f."Enrollment (Ages 5-17)" > 30
  AND CASE
        WHEN f."High Grade" = 'K' THEN 0
        ELSE CAST(f."High Grade" AS INTEGER)
      END <= 8;
```

本輪SQL：
```sql
SELECT s.School AS name, s.Street AS street_address
FROM frpm AS f
JOIN schools AS s ON s.CDSCode = f.CDSCode
WHERE s.School IS NOT NULL
  AND TRIM(s.School) <> ''
  AND f.`Enrollment (K-12)` - f.`Enrollment (Ages 5-17)` > 30
  AND f.`High Grade` IN ('K', '1', '2', '3', '4', '5', '6', '7', '8');
```



<a id="q44"></a>

## [Q44](historical-case-review.md#q44) · 歷史錯→本輪啱 · california_schools

候選關聯：R1／識別碼。CDS補回前導0。

歷史→本輪：model replies 23→6；tool attempts 23→7；SQL attempts 20→4。

Question：I have a school on file with CDS code 1611430131177. Find the school in the same county as that school whose own SAT record shows the most students scoring at least 1500 (not a district-wide roll-up). If two schools tie on that count, use the one with the smaller CDS code. Send me that school's administrator's first and last name.

歷史SQL：
```sql
SELECT s.AdmFName1, s.AdmLName1
FROM schools AS s
JOIN satscores AS sat ON sat.cds = s.CDSCode
WHERE s.County = (
    SELECT County
    FROM schools
    WHERE CDSCode = '1611430131177'
)
  AND sat.rtype = 'S'
ORDER BY sat.NumGE1500 DESC, s.CDSCode ASC
LIMIT 1;
```

本輪SQL：
```sql
SELECT s.AdmFName1, s.AdmLName1
FROM schools AS s
JOIN satscores AS ss ON ss.cds = s.CDSCode
WHERE s.County = (
    SELECT County
    FROM schools
    WHERE CDSCode = '01611430131177'
)
  AND ss.rtype = 'S'
ORDER BY ss.NumGE1500 DESC, s.CDSCode ASC
LIMIT 1;
```



<a id="q49"></a>

## [Q49](historical-case-review.md#q49) · 歷史錯→本輪啱 · card_games

候選關聯：R2／定義來源。borderless由frameEffects extendedart改borderColor='borderless'；亦納空白IDs。

歷史→本輪：model replies 14→5；tool attempts 13→6；SQL attempts 11→2。

Question：List the IDs of borderless card printings for which Card Kingdom lacks a regular-version listing or a foil-version listing.

歷史SQL：
```sql
SELECT id
FROM cards
WHERE frameEffects LIKE '%extendedart%'
  AND (cardKingdomId IS NULL OR cardKingdomFoilId IS NULL);
```

本輪SQL：
```sql
SELECT id
FROM cards
WHERE borderColor = 'borderless'
  AND (
    cardKingdomId IS NULL OR trim(cardKingdomId) = ''
    OR cardKingdomFoilId IS NULL OR trim(cardKingdomFoilId) = ''
  );
```



<a id="q58"></a>

## [Q58](historical-case-review.md#q58) · 歷史錯→本輪啱 · card_games

候選關聯：R7／輸出契約。取消額外count欄，僅輸出percentage；同時改為DISTINCT uuid。

歷史→本輪：model replies 6→8；tool attempts 5→7；SQL attempts 2→3。

Question：Among card printings with no recorded power value or a variable power expression, what percentage have a French translation? Round to two decimals.

歷史SQL：
```sql
SELECT COUNT(*) AS qualifying_printings,
       SUM(CASE WHEN f.uuid IS NOT NULL THEN 1 ELSE 0 END) AS french_printings,
       ROUND(100.0 * SUM(CASE WHEN f.uuid IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS percentage
FROM cards c
LEFT JOIN (
    SELECT DISTINCT uuid
    FROM foreign_data
    WHERE language = 'French'
) f ON f.uuid = c.uuid
WHERE c.power IS NULL OR c.power = '' OR c.power LIKE '%*%';
```

本輪SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN f.uuid IS NOT NULL THEN c.uuid END)
    / COUNT(DISTINCT c.uuid),
    2
) AS percentage_with_french_translation
FROM cards c
LEFT JOIN foreign_data f
    ON f.uuid = c.uuid
    AND f.language = 'French'
WHERE c.power IS NULL
   OR instr(c.power, '*') > 0;
```



<a id="q70"></a>

## [Q70](historical-case-review.md#q70) · 歷史錯→本輪啱 · card_games

候選關聯：R7／型別契約。frame年份由原文字欄改CAST INTEGER。

歷史→本輪：model replies 5→6；tool attempts 5→6；SQL attempts 2→3。

Question：I'm tracking printings of Tarmogoyf. Of all its printings, which frame version is the newest? Please give me the year that identifies that latest frame version, and the percentage of the card's printings that use it, rounded to two decimal places. The percentage should be over all printings of the card.

歷史SQL：
```sql
SELECT
    frameVersion AS latest_frame_year,
    ROUND(
        100.0 * COUNT(*) / (SELECT COUNT(*) FROM cards WHERE name = 'Tarmogoyf'),
        2
    ) AS percentage_of_printings
FROM cards
WHERE name = 'Tarmogoyf'
  AND frameVersion = (
      SELECT frameVersion
      FROM cards
      WHERE name = 'Tarmogoyf'
        AND frameVersion GLOB '[0-9]*'
      ORDER BY CAST(frameVersion AS INTEGER) DESC
      LIMIT 1
  )
GROUP BY frameVersion;
```

本輪SQL：
```sql
WITH frame_counts AS (
    SELECT frameVersion, COUNT(*) AS printing_count
    FROM cards
    WHERE name = 'Tarmogoyf'
    GROUP BY frameVersion
),
total AS (
    SELECT COUNT(*) AS printing_count
    FROM cards
    WHERE name = 'Tarmogoyf'
),
latest AS (
    SELECT frameVersion
    FROM frame_counts
    ORDER BY CAST(frameVersion AS INTEGER) DESC
    LIMIT 1
)
SELECT
    CAST(latest.frameVersion AS INTEGER) AS year,
    ROUND(100.0 * frame_counts.printing_count / total.printing_count, 2) AS percentage
FROM latest
JOIN frame_counts ON frame_counts.frameVersion = latest.frameVersion
CROSS JOIN total;
```



<a id="q72"></a>

## [Q72](historical-case-review.md#q72) · 歷史錯→本輪啱 · card_games

候選關聯：R1／token匹配。keyword由子字串LIKE改逗號界定Flying/Cycling完整token。

歷史→本輪：model replies 4→6；tool attempts 3→5；SQL attempts 1→3。

Question：I'm brewing and looking for cards that combine two keyword abilities. How many cards in the collection have both Flying and Cycling? Note that each printing counts as its own card, and a card only counts if it has both keywords.

歷史SQL：
```sql
SELECT COUNT(*) AS count_cards
FROM cards
WHERE keywords LIKE '%Flying%'
  AND keywords LIKE '%Cycling%';
```

本輪SQL：
```sql
SELECT COUNT(*) AS card_count
FROM cards
WHERE ',' || keywords || ',' LIKE '%,Flying,%'
  AND ',' || keywords || ',' LIKE '%,Cycling,%';
```



<a id="q73"></a>

## [Q73](historical-case-review.md#q73) · 歷史錯→本輪啱 · card_games

候選關聯：R8／CTE排序範圍。修正chosen UNION中的全域ORDER BY/LIMIT，兩個set分開ROW_NUMBER；另排manaCost空字串。

歷史→本輪：model replies 9→4；tool attempts 10→4；SQL attempts 6→1。

Question：I'm comparing how mana-cheap Magic: The Gathering sets have become over time. For two sets — the set where Abyssal Horror was first printed, and the most recently released set in the database — I want one row per set with the set name and the percentage of that set's cards that have a mana cost whose converted mana cost is 3 or less, rounded to two decimal places. By "first printed", I mean the set with the earliest release date among the sets Abyssal Horror appears in; if several share that earliest date, use the one whose set code comes first alphabetically. For the most recent set, use the latest release date among all sets; if several share that date, again take the one whose set code comes first alphabetically. By "converted mana cost" I mean the card's mana value, and a card counts as having a mana cost only if a mana cost is printed on it.

歷史SQL：
```sql
WITH chosen AS (
    SELECT s.code, s.name
    FROM sets AS s
    WHERE s.code = (
        SELECT c.setCode
        FROM cards AS c
        JOIN sets AS printed_set ON printed_set.code = c.setCode
        WHERE c.name = 'Abyssal Horror'
        ORDER BY printed_set.releaseDate ASC, printed_set.code ASC
        LIMIT 1
    )

    UNION

    SELECT code, name
    FROM sets
    ORDER BY releaseDate DESC, code ASC
    LIMIT 1
)
SELECT
    chosen.name AS set_name,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN cards.manaCost IS NOT NULL
                     AND cards.convertedManaCost <= 3
                THEN 1
                ELSE 0
            END
        ) / COUNT(cards.id),
        2
    ) AS percentage
FROM chosen
JOIN cards ON cards.setCode = chosen.code
GROUP BY chosen.code, chosen.name;
```

本輪SQL：
```sql
WITH abyssal_sets AS (
    SELECT s.code, s.name, s.releaseDate,
           ROW_NUMBER() OVER (ORDER BY s.releaseDate, s.code) AS rn
    FROM sets AS s
    JOIN cards AS c ON c.setCode = s.code
    WHERE c.name = 'Abyssal Horror'
),
latest_set AS (
    SELECT code, name,
           ROW_NUMBER() OVER (ORDER BY releaseDate DESC, code ASC) AS rn
    FROM sets
),
chosen AS (
    SELECT code, name FROM abyssal_sets WHERE rn = 1
    UNION
    SELECT code, name FROM latest_set WHERE rn = 1
)
SELECT chosen.name AS set_name,
       ROUND(
           100.0 * SUM(
               CASE
                   WHEN c.manaCost IS NOT NULL
                    AND TRIM(c.manaCost) <> ''
                    AND c.convertedManaCost <= 3
                   THEN 1 ELSE 0
               END
           ) / COUNT(c.id),
           2
       ) AS percentage
FROM chosen
JOIN cards AS c ON c.setCode = chosen.code
GROUP BY chosen.code, chosen.name
ORDER BY chosen.code;
```



<a id="q81"></a>

## [Q81](failure-case-review.md#q81) · 歷史啱→本輪錯 · card_games

候選關聯：R3／過度去重。先 DISTINCT name,artist，將 printing 計數改為卡名計數，與 Gold COUNT(*) 不同。

歷史→本輪：model replies 6→8；tool attempts 5→7；SQL attempts 3→5。

Question：I'm writing a spotlight piece on card artists, and I need to know: among black-bordered cards that are obtainable on Magic Arena and have a printed power of 10 or greater, which artist illustrated the most of them? Please give me the artist's name and the number of those cards they illustrated. A card counts even if it's also available outside Arena, as long as it can be obtained on Arena. If several artists tie for the most, list every one of them along with that count.

歷史SQL：
```sql
SELECT artist, COUNT(*) AS card_count
FROM cards
WHERE borderColor = 'black'
  AND availability LIKE '%arena%'
  AND power GLOB '[0-9]*'
  AND CAST(power AS INTEGER) >= 10
GROUP BY artist
HAVING COUNT(*) = (
  SELECT MAX(card_count)
  FROM (
    SELECT COUNT(*) AS card_count
    FROM cards
    WHERE borderColor = 'black'
      AND availability LIKE '%arena%'
      AND power GLOB '[0-9]*'
      AND CAST(power AS INTEGER) >= 10
    GROUP BY artist
  )
);
```

本輪SQL：
```sql
WITH eligible AS (
    SELECT DISTINCT name, artist
    FROM cards
    WHERE borderColor = 'black'
      AND availability LIKE '%arena%'
      AND power GLOB '[0-9]*'
      AND CAST(power AS INTEGER) >= 10
),
counts AS (
    SELECT artist, COUNT(*) AS card_count
    FROM eligible
    GROUP BY artist
)
SELECT artist, card_count
FROM counts
WHERE card_count = (SELECT MAX(card_count) FROM counts)
ORDER BY artist;
```



<a id="q83"></a>

## [Q83](historical-case-review.md#q83) · 歷史錯→本輪啱 · card_games

候選關聯：R1／條件計數。只在Japanese非空翻譯時COUNT set，避免LEFT JOIN後計入所有sets。

歷史→本輪：model replies 4→8；tool attempts 4→9；SQL attempts 1→6。

Question：Hi! I'm preparing a licensing brief for our Japanese partner about Magic: The Gathering localization coverage. Could you pull a report of every expansion type (core, expansion, promo, etc.), showing for each one how many sets of that type carry a Japanese name entry? A Japanese name entry means the set's name-translations include a Japanese-language entry giving the set's name in Japanese. Please include every expansion type in the report even if none of its sets have such an entry (show 0 for those), and sort the results alphabetically by expansion type. Nothing else needed - just the expansion type and the count.

歷史SQL：
```sql
SELECT s.type AS expansion_type,
       COUNT(DISTINCT s.id) AS japanese_name_set_count
FROM sets AS s
LEFT JOIN set_translations AS st
  ON st.setCode = s.code
 AND st.language = 'Japanese'
GROUP BY s.type
ORDER BY s.type;
```

本輪SQL：
```sql
SELECT
    s.type,
    COUNT(DISTINCT CASE
        WHEN t.language = 'Japanese'
         AND t.translation IS NOT NULL
         AND TRIM(t.translation) <> ''
        THEN s.id
    END) AS japanese_name_sets
FROM sets AS s
LEFT JOIN set_translations AS t
    ON t.setCode = s.code
GROUP BY s.type
ORDER BY s.type;
```



<a id="q90"></a>

## [Q90](historical-case-review.md#q90) · 歷史錯→本輪啱 · card_games

候選關聯：R1／數值排序。frameVersion由MAX文字改數值年份優先。

歷史→本輪：model replies 4→7；tool attempts 3→6；SQL attempts 1→3。

Question：I'm tracking John Avon's artwork. Among his cards that exist as powerful foils, what is the most recent frame year, and how many of those cards carry it? If several years are tied for most recent, give each year with its own count. Match John Avon on the illustrator's name.

歷史SQL：
```sql
SELECT frameVersion, COUNT(*) AS card_count
FROM cards
WHERE artist = 'John Avon'
  AND cardKingdomId IS NOT NULL AND cardKingdomId <> ''
  AND cardKingdomFoilId IS NOT NULL AND cardKingdomFoilId <> ''
GROUP BY frameVersion
HAVING frameVersion = (
    SELECT MAX(frameVersion)
    FROM cards
    WHERE artist = 'John Avon'
      AND cardKingdomId IS NOT NULL AND cardKingdomId <> ''
      AND cardKingdomFoilId IS NOT NULL AND cardKingdomFoilId <> ''
);
```

本輪SQL：
```sql
SELECT frameVersion, COUNT(*) AS card_count
FROM cards
WHERE artist = 'John Avon'
  AND cardKingdomId IS NOT NULL
  AND cardKingdomId <> ''
  AND cardKingdomFoilId IS NOT NULL
  AND cardKingdomFoilId <> ''
GROUP BY frameVersion
ORDER BY CASE
    WHEN frameVersion GLOB '[0-9]*' THEN CAST(frameVersion AS INTEGER)
    ELSE -1
END DESC
LIMIT 1;
```



<a id="q92"></a>

## [Q92](failure-case-review.md#q92) · 歷史啱→本輪錯 · card_games

候選關聯：R7／排序契約。題目要求 Foil id alphabetical order，Agent 改用 CAST(... AS INTEGER) 排序。

歷史→本輪：model replies 4→4；tool attempts 3→3；SQL attempts 1→1。

Question：I keep a Card Kingdom catalogue and want to list the creature cards that Card Kingdom stocks in both foil and non-foil printings. A card counts as stocked in both printings when both its Card Kingdom Foil id and its Card Kingdom id are present. Please give me one row per card, with each card's Card Kingdom Foil id and Card Kingdom id, and nothing else. I only need the three cards with the lowest Card Kingdom Foil ids in alphabetical order, with ties broken by the Card Kingdom id.

歷史SQL：
```sql
SELECT cardKingdomFoilId, cardKingdomId
FROM cards
WHERE types LIKE '%Creature%'
  AND cardKingdomFoilId IS NOT NULL
  AND cardKingdomId IS NOT NULL
ORDER BY cardKingdomFoilId, cardKingdomId
LIMIT 3;
```

本輪SQL：
```sql
SELECT cardKingdomFoilId, cardKingdomId
FROM cards
WHERE types LIKE '%Creature%'
  AND cardKingdomFoilId IS NOT NULL
  AND cardKingdomFoilId <> ''
  AND cardKingdomId IS NOT NULL
  AND cardKingdomId <> ''
ORDER BY CAST(cardKingdomFoilId AS INTEGER), cardKingdomId
LIMIT 3;
```



<a id="q98"></a>

## [Q98](failure-case-review.md#q98) · 歷史啱→本輪錯 · card_games

候選關聯：R4／條件替換。layout 清單代替 side IS NOT NULL；日期 replace/date 與 Gold substr 年份不同。

歷史→本輪：model replies 7→9；tool attempts 6→9；SQL attempts 3→6。

Question：I'm putting together a retrospective of promotional cards. Can you get me the card name of every promotional card that has multiple faces printed on it (like split, transform, or adventure cards) and was originally released in 2019? By "originally released" I mean the card's own first-release date, not the release date of the set its promotional printing belongs to, and "in 2019" means January 1 through December 31, 2019. If a card has more than one promotional printing from that year, list it just once. I only want the card names, nothing else.

歷史SQL：
```sql
SELECT DISTINCT name
FROM cards
WHERE isPromo = 1
  AND originalReleaseDate >= '2019/01/01'
  AND originalReleaseDate <= '2019/12/31'
  AND otherFaceIds IS NOT NULL
  AND otherFaceIds <> ''
ORDER BY name;
```

本輪SQL：
```sql
SELECT DISTINCT name
FROM cards
WHERE isPromo = 1
  AND layout IN ('split', 'transform', 'adventure', 'modal_dfc', 'aftermath', 'meld', 'flip')
  AND date(replace(originalReleaseDate, '/', '-')) BETWEEN '2019-01-01' AND '2019-12-31'
ORDER BY name;
```



<a id="q100"></a>

## [Q100](historical-case-review.md#q100) · 歷史錯→本輪啱 · card_games

候選關聯：R2／資料來源。French/Italian printings由set_translations改foreign_data。

歷史→本輪：model replies 5→6；tool attempts 6→8；SQL attempts 2→3。

Question：I'm cataloguing European releases of Counterspell. How many of its printings were released with both a French and an Italian localization? I just need the count as a single number.

歷史SQL：
```sql
SELECT COUNT(*) AS count
FROM (
    SELECT c.setCode, c.number
    FROM cards AS c
    JOIN sets AS s ON s.code = c.setCode
    WHERE c.name = 'Counterspell'
      AND EXISTS (
          SELECT 1 FROM set_translations AS f
          WHERE f.setCode = c.setCode AND f.language = 'French'
      )
      AND EXISTS (
          SELECT 1 FROM set_translations AS i
          WHERE i.setCode = c.setCode AND i.language = 'Italian'
      )
    GROUP BY c.setCode, c.number
);
```

本輪SQL：
```sql
SELECT COUNT(*) AS count
FROM (
    SELECT c.setCode, c.number
    FROM cards AS c
    WHERE c.name = 'Counterspell'
      AND EXISTS (
          SELECT 1
          FROM foreign_data AS f
          WHERE f.uuid = c.uuid AND f.language = 'French'
      )
      AND EXISTS (
          SELECT 1
          FROM foreign_data AS i
          WHERE i.uuid = c.uuid AND i.language = 'Italian'
      )
    GROUP BY c.setCode, c.number
);
```



<a id="q102"></a>

## [Q102](failure-case-review.md#q102) · 歷史啱→本輪錯 · card_games

候選關聯：R1／數值／文字排序。MAX(frameVersion) 使用文字排序，Gold 將 frameVersion CAST 為 INTEGER。

歷史→本輪：model replies 11→7；tool attempts 10→7；SQL attempts 7→4。

Question：Which set contains the Aven Mindcensor printing that uses the newest card frame? I want the set's name and its release date. Count every printing, including promotional and online-only ones. If several printings share the newest frame, use the most recently released one; if the release dates tie too, list each such set once. Please give me the set name, not its code.

歷史SQL：
```sql
WITH newest AS (
    SELECT MAX(CAST(frameVersion AS INTEGER)) AS year
    FROM cards
    WHERE name = 'Aven Mindcensor'
      AND frameVersion GLOB '[0-9]*'
),
latest_release AS (
    SELECT MAX(s.releaseDate) AS releaseDate
    FROM cards c
    JOIN sets s ON s.code = c.setCode
    CROSS JOIN newest n
    WHERE c.name = 'Aven Mindcensor'
      AND CAST(c.frameVersion AS INTEGER) = n.year
)
SELECT DISTINCT s.name AS set_name, s.releaseDate
FROM cards c
JOIN sets s ON s.code = c.setCode
CROSS JOIN newest n
CROSS JOIN latest_release lr
WHERE c.name = 'Aven Mindcensor'
  AND CAST(c.frameVersion AS INTEGER) = n.year
  AND s.releaseDate = lr.releaseDate;
```

本輪SQL：
```sql
SELECT s.name, s.releaseDate
FROM cards AS c
JOIN sets AS s ON s.code = c.setCode
WHERE c.name = 'Aven Mindcensor'
  AND c.frameVersion = (
    SELECT MAX(frameVersion)
    FROM cards
    WHERE name = 'Aven Mindcensor'
  )
  AND s.releaseDate = (
    SELECT MAX(s2.releaseDate)
    FROM cards AS c2
    JOIN sets AS s2 ON s2.code = c2.setCode
    WHERE c2.name = 'Aven Mindcensor'
      AND c2.frameVersion = (
        SELECT MAX(frameVersion)
        FROM cards
        WHERE name = 'Aven Mindcensor'
      )
  )
GROUP BY s.name, s.releaseDate;
```



<a id="q103"></a>

## [Q103](failure-case-review.md#q103) · 歷史啱→本輪錯 · card_games

候選關聯：R1／缺失值。NOT EXISTS 未限制 Spanish translation 非空，把只有 NULL 翻譯記錄當已有西班牙名。

歷史→本輪：model replies 4→8；tool attempts 4→7；SQL attempts 1→4。

Question：I'm auditing which recent products were never localized for Spanish-speaking markets. Can you find every set released in calendar year 2020 that has no Spanish name? For each of those, I just need the set code and the set's release date.

歷史SQL：
```sql
SELECT s.code, s.releaseDate
FROM sets AS s
WHERE s.releaseDate >= '2020-01-01'
  AND s.releaseDate < '2021-01-01'
  AND NOT EXISTS (
    SELECT 1
    FROM set_translations AS st
    WHERE st.setCode = s.code
      AND lower(st.language) = 'es'
  )
ORDER BY s.releaseDate, s.code;
```

本輪SQL：
```sql
SELECT s.code, s.releaseDate
FROM sets AS s
WHERE s.releaseDate >= '2020-01-01'
  AND s.releaseDate < '2021-01-01'
  AND NOT EXISTS (
      SELECT 1
      FROM set_translations AS t
      WHERE t.setCode = s.code
        AND t.language = 'Spanish'
  )
ORDER BY s.releaseDate, s.code;
```



<a id="q106"></a>

## [Q106](historical-case-review.md#q106) · 歷史錯→本輪啱 · card_games

候選關聯：R4／計算範圍。SUM baseSetSize限制於有翻譯sets，移除expansion附加限制。

歷史→本輪：model replies 7→5；tool attempts 8→6；SQL attempts 4→2。

Question：For the blocks named exactly "Masques" and "Mirage", how widely were their sets localized? For each of these two blocks, give me one row with the block's name, how many of its sets have an official translated name, and the total number of cards in the base sets of those sets combined. Base set size means the number of cards in the set's base set, not counting supplementary cards. Nothing else, please.

歷史SQL：
```sql
WITH block_stats AS (
    SELECT
        s.block,
        COUNT(DISTINCT CASE
            WHEN EXISTS (
                SELECT 1
                FROM set_translations st
                WHERE st.setCode = s.code
                  AND st.translation IS NOT NULL
                  AND TRIM(st.translation) <> ''
            ) THEN s.code
        END) AS translated_sets,
        SUM(CASE
            WHEN s.type = 'expansion' THEN COALESCE(s.baseSetSize, 0)
            ELSE 0
        END) AS base_set_cards
    FROM sets s
    WHERE s.block IN ('Masques', 'Mirage')
    GROUP BY s.block
)
SELECT block, translated_sets, base_set_cards
FROM block_stats
ORDER BY CASE block WHEN 'Masques' THEN 1 WHEN 'Mirage' THEN 2 END;
```

本輪SQL：
```sql
SELECT
    s.block AS block_name,
    COUNT(DISTINCT s.code) AS sets_with_official_translated_name,
    SUM(s.baseSetSize) AS total_base_set_cards
FROM sets AS s
WHERE s.block IN ('Masques', 'Mirage')
  AND EXISTS (
      SELECT 1
      FROM set_translations AS st
      WHERE st.setCode = s.code
        AND st.translation IS NOT NULL
        AND TRIM(st.translation) <> ''
  )
GROUP BY s.block
ORDER BY s.block;
```



<a id="q107"></a>

## [Q107](historical-case-review.md#q107) · 歷史錯→本輪啱 · card_games

候選關聯：R6／關係範圍。只累加boros且有Japanese entry的qualifying printings，取消按名稱擴展到其他printing。

歷史→本輪：model replies 10→7；tool attempts 11→8；SQL attempts 7→4。

Question：I'm assembling a Japanese-language boros deck and want to check which cards need careful rules review. For every card that has a boros watermark and a Japanese printing, please give me: the Japanese card name, the English card type, and the total number of official rulings recorded for that card. A card is identified by its Japanese name together with its English card type - printings that share both count as one card, and if either differs they should be listed as separate cards. The ruling total should add up all ruling entries across every printing of that card, and if a card has no rulings, list it with a total of 0.

歷史SQL：
```sql
WITH jp_cards AS (
    SELECT DISTINCT c.uuid, f.name AS japanese_name, c.type AS english_type
    FROM cards c
    JOIN foreign_data f ON f.uuid = c.uuid
    WHERE lower(c.watermark) = 'boros'
      AND f.language = 'Japanese'
),
card_printings AS (
    SELECT DISTINCT
        j.japanese_name,
        j.english_type,
        c.uuid
    FROM jp_cards j
    JOIN foreign_data f
      ON f.name = j.japanese_name
     AND f.language = 'Japanese'
    JOIN cards c
      ON c.uuid = f.uuid
     AND c.type = j.english_type
),
ruling_totals AS (
    SELECT
        p.japanese_name,
        p.english_type,
        COUNT(r.id) AS ruling_total
    FROM card_printings p
    LEFT JOIN rulings r ON r.uuid = p.uuid
    GROUP BY p.japanese_name, p.english_type
)
SELECT japanese_name, english_type, ruling_total
FROM ruling_totals
ORDER BY japanese_name, english_type;
```

本輪SQL：
```sql
WITH qualifying AS (
    SELECT DISTINCT
        fd.name AS japanese_name,
        c.type AS english_type,
        c.uuid
    FROM cards AS c
    JOIN foreign_data AS fd
        ON fd.uuid = c.uuid
    WHERE c.watermark = 'boros'
      AND fd.language = 'Japanese'
),
ruling_totals AS (
    SELECT uuid, COUNT(*) AS ruling_count
    FROM rulings
    GROUP BY uuid
)
SELECT
    q.japanese_name,
    q.english_type,
    SUM(COALESCE(rt.ruling_count, 0)) AS total_rulings
FROM qualifying AS q
LEFT JOIN ruling_totals AS rt
    ON rt.uuid = q.uuid
GROUP BY q.japanese_name, q.english_type
ORDER BY q.japanese_name, q.english_type;
```



<a id="q108"></a>

## [Q108](failure-case-review.md#q108) · 歷史啱→本輪錯 · card_games

候選關聯：R6／關係限制。把 set translation 語言集合額外綁定相同 setCode 的 printing，且改 COUNT(*) 為 DISTINCT uuid。

歷史→本輪：model replies 5→6；tool attempts 7→8；SQL attempts 2→3。

Question：I'm putting together a localization coverage report. Among the languages into which the card sets themselves were translated (i.e., have a set translation), which language has the fewest printings whose flavor text was translated into that language? Please give me the language name and the number of such printings. If several languages tie for the fewest, list all of them, ordered alphabetically by language name.

歷史SQL：
```sql
WITH set_languages AS (
  SELECT DISTINCT language
  FROM set_translations
  WHERE language IS NOT NULL
),
translated_printings AS (
  SELECT DISTINCT fd.language, fd.uuid
  FROM foreign_data AS fd
  JOIN set_languages AS sl ON sl.language = fd.language
  WHERE fd.flavorText IS NOT NULL
    AND TRIM(fd.flavorText) <> ''
),
counts AS (
  SELECT sl.language, COUNT(tp.uuid) AS printing_count
  FROM set_languages AS sl
  LEFT JOIN translated_printings AS tp
    ON tp.language = sl.language
  GROUP BY sl.language
)
SELECT language, printing_count
FROM counts
WHERE printing_count = (SELECT MIN(printing_count) FROM counts)
ORDER BY language;
```

本輪SQL：
```sql
WITH counts AS (
    SELECT st.language, COUNT(DISTINCT c.uuid) AS printing_count
    FROM set_translations AS st
    JOIN cards AS c
        ON c.setCode = st.setCode
    JOIN foreign_data AS fd
        ON fd.uuid = c.uuid
       AND fd.language = st.language
    WHERE fd.flavorText IS NOT NULL
      AND TRIM(fd.flavorText) <> ''
    GROUP BY st.language
),
minimum_count AS (
    SELECT MIN(printing_count) AS printing_count
    FROM counts
)
SELECT counts.language, counts.printing_count
FROM counts
JOIN minimum_count
    ON counts.printing_count = minimum_count.printing_count
ORDER BY counts.language;
```



<a id="q109"></a>

## [Q109](historical-case-review.md#q109) · 歷史錯→本輪啱 · card_games

候選關聯：R3／實體粒度。COUNT printing uuid改oracle card ID，並跨同card printings檢查French set。

歷史→本輪：model replies 4→8；tool attempts 5→9；SQL attempts 1→5。

Question：I'm building a French-language cube and want some big finishers for it. How many different creature cards with power 10 or greater have at least one printing in a set whose name has a French translation? Please return just that single number. Note: a set qualifies based on its name having a French translation, no matter when it was released or what type of set it is, and a card counts if any of its printings comes from such a set.

歷史SQL：
```sql
SELECT COUNT(DISTINCT c.uuid) AS creature_card_count
FROM cards c
WHERE c.type LIKE '%Creature%'
  AND c.power GLOB '[0-9]*'
  AND CAST(c.power AS INTEGER) >= 10
  AND EXISTS (
    SELECT 1
    FROM set_translations st
    WHERE st.language = 'French'
      AND instr(',' || c.printings || ',', ',' || st.setCode || ',') > 0
  );
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT c.scryfallOracleId)
FROM cards AS c
WHERE c.scryfallOracleId IS NOT NULL
  AND c.types LIKE '%Creature%'
  AND CAST(c.power AS REAL) >= 10
  AND EXISTS (
      SELECT 1
      FROM cards AS p
      JOIN set_translations AS st ON st.setCode = p.setCode
      WHERE p.scryfallOracleId = c.scryfallOracleId
        AND st.language = 'French'
  );
```



<a id="q115"></a>

## [Q115](historical-case-review.md#q115) · 歷史錯→本輪啱 · card_games

候選關聯：R6／父子集合。卡數納parentCode相關supplemental sets，輸出取消多餘total count欄。

歷史→本輪：model replies 11→13；tool attempts 10→14；SQL attempts 6→10。

Question：Among the Commander-type expansion sets released in calendar year 2020 (1 January 2020 to 31 December 2020), I need the one with the highest total card count, so we can plan translation work. Please send me the set's id from the sets listing, its name, and the number of official languages it was released in. The total card count should include promotional and related supplemental products, but exclude Alchemy modifications. If two sets tie for the highest total card count, list each of them, ordered by set id ascending.

歷史SQL：
```sql
SELECT s.id, s.name,
       (SELECT COUNT(*)
        FROM cards c
        WHERE c.setCode = s.code
          AND COALESCE(c.isOnlineOnly, 0) = 0) AS total_card_count,
       (SELECT COUNT(DISTINCT st.language)
        FROM set_translations st
        WHERE st.setCode = s.code) AS official_language_count
FROM sets s
WHERE s.type = 'commander'
  AND s.releaseDate >= '2020-01-01'
  AND s.releaseDate < '2021-01-01'
ORDER BY total_card_count DESC, s.id ASC
LIMIT 1;
```

本輪SQL：
```sql
WITH commander_sets AS (
    SELECT id, code, name, releaseDate
    FROM sets
    WHERE lower(type) = 'commander'
      AND releaseDate >= '2020-01-01'
      AND releaseDate < '2021-01-01'
),
card_counts AS (
    SELECT s.id,
           s.code,
           s.name,
           COUNT(c.id) AS total_card_count
    FROM commander_sets s
    LEFT JOIN sets related
      ON related.parentCode = s.code
    LEFT JOIN cards c
      ON c.setCode = s.code
      OR c.setCode = related.code
    WHERE c.isOnlineOnly = 0 OR c.id IS NULL
    GROUP BY s.id, s.code, s.name
),
ranked AS (
    SELECT *,
           RANK() OVER (ORDER BY total_card_count DESC) AS card_rank
    FROM card_counts
)
SELECT r.id,
       r.name,
       (SELECT COUNT(DISTINCT language)
        FROM set_translations t
        WHERE t.setCode = r.code) AS official_language_count
FROM ranked r
WHERE r.card_rank = 1
ORDER BY r.id ASC;
```



<a id="q117"></a>

## [Q117](failure-case-review.md#q117) · 歷史啱→本輪錯 · card_games

候選關聯：R3／計數單位。以 printing uuid 去重代替卡名 name 去重。

歷史→本輪：model replies 11→7；tool attempts 10→7；SQL attempts 7→4。

Question：I'm putting together a black artifact flavor-showcase section for a trade binder. How many mono-black Artifact cards have a foreign-language printing that shows flavor text in that language? By mono-black I mean black is the card's only colour, and by Artifact cards I include artifacts combined with another card type, like an Artifact Creature. I'm counting cards, not printings – a card is the same card regardless of set, print run, or language. Just give me one number.

歷史SQL：
```sql
SELECT COUNT(DISTINCT c.name)
FROM cards c
JOIN foreign_data f ON f.uuid = c.uuid
WHERE c.colors = 'B'
  AND instr(',' || c.types || ',', ',Artifact,') > 0
  AND f.language IS NOT NULL
  AND lower(f.language) NOT IN ('english', 'unknown')
  AND f.flavorText IS NOT NULL
  AND trim(f.flavorText) <> '';
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT c.uuid)
FROM cards c
JOIN foreign_data f ON f.uuid = c.uuid
WHERE c.colors = 'B'
  AND c.types LIKE '%Artifact%'
  AND f.language IS NOT NULL
  AND f.flavorText IS NOT NULL
  AND TRIM(f.flavorText) <> '';
```



<a id="q132"></a>

## [Q132](failure-case-review.md#q132) · 歷史啱→本輪錯 · codebase_community

候選關聯：R7／輸出形狀。Gold 單行四個 scalar，Agent 輸出兩個群組行，並額外加入群組名稱欄。

歷史→本輪：model replies 4→7；tool attempts 5→8；SQL attempts 1→4。

Question：I'm putting together the yearly activity report with a Germany-focused breakdown of who did the editing, covering posts created in calendar year 2012. For the 2012 posts whose last editor is a user based in Germany, I need the total score; and for all other posts created in 2012, I need their total score as well. Also, how many Germany-based users were the last editor of at least one 2012 post, and what their combined reputation is, as shown on their profiles. A user based in Germany is one whose profile location is in Germany.

歷史SQL：
```sql
WITH posts_2012 AS (
    SELECT Id, Score, LastEditorUserId
    FROM posts
    WHERE CreaionDate >= '2012-01-01'
      AND CreaionDate < '2013-01-01'
),
germany_editors AS (
    SELECT DISTINCT u.Id, u.Reputation
    FROM posts_2012 AS p
    JOIN users AS u
      ON u.Id = p.LastEditorUserId
    WHERE u.Location LIKE '%Germany%'
)
SELECT
    COALESCE(SUM(
        CASE WHEN u.Location LIKE '%Germany%' THEN p.Score ELSE 0 END
    ), 0) AS germany_last_editor_post_score,
    COALESCE(SUM(
        CASE WHEN u.Id IS NULL OR u.Location IS NULL OR u.Location NOT LIKE '%Germany%'
             THEN p.Score ELSE 0 END
    ), 0) AS other_post_score,
    (SELECT COUNT(*) FROM germany_editors) AS germany_editor_user_count,
    (SELECT COALESCE(SUM(Reputation), 0) FROM germany_editors)
        AS germany_editor_combined_reputation
FROM posts_2012 AS p
LEFT JOIN users AS u
  ON u.Id = p.LastEditorUserId;
```

本輪SQL：
```sql
WITH germany_last_editors AS (
    SELECT DISTINCT u.Id, u.Reputation
    FROM posts p
    JOIN users u ON u.Id = p.LastEditorUserId
    WHERE p.CreaionDate >= '2012-01-01'
      AND p.CreaionDate < '2013-01-01'
      AND u.Location LIKE '%Germany%'
),
post_groups AS (
    SELECT
        CASE
            WHEN u.Id IS NOT NULL AND u.Location LIKE '%Germany%'
                THEN 'Germany-based last editor'
            ELSE 'All other posts'
        END AS post_group,
        SUM(p.Score) AS total_score
    FROM posts p
    LEFT JOIN users u ON u.Id = p.LastEditorUserId
    WHERE p.CreaionDate >= '2012-01-01'
      AND p.CreaionDate < '2013-01-01'
    GROUP BY post_group
),
editor_stats AS (
    SELECT
        COUNT(*) AS editor_count,
        SUM(Reputation) AS combined_reputation
    FROM germany_last_editors
)
SELECT
    pg.post_group,
    pg.total_score,
    es.editor_count AS germany_last_editor_user_count,
    es.combined_reputation AS germany_users_combined_reputation
FROM post_groups pg
CROSS JOIN editor_stats es
ORDER BY CASE pg.post_group
    WHEN 'Germany-based last editor' THEN 1
    ELSE 2
END;
```



<a id="q136"></a>

## [Q136](failure-case-review.md#q136) · 歷史啱→本輪錯 · codebase_community

候選關聯：R1／地點編碼。Location='Germany' 漏掉城市加國家的 location；排名邏輯已處理第二不同值。

歷史→本輪：model replies 4→4；tool attempts 4→4；SQL attempts 1→1。

Question：I'm profiling users by where they say they live. Among the users located in Germany, who has the second most badges of all time? By second most I mean the highest badge total strictly below the top holder's total. If several users tie at that total, include all of them. Please give me each such user's display name and their badge total, ordered by display name.

歷史SQL：
```sql
WITH germany_badges AS (
    SELECT u.Id, u.DisplayName, COUNT(b.Id) AS badge_total
    FROM users AS u
    JOIN badges AS b ON b.UserId = u.Id
    WHERE u.Location LIKE '%Germany%'
    GROUP BY u.Id, u.DisplayName
)
SELECT DisplayName, badge_total
FROM germany_badges
WHERE badge_total = (
    SELECT MAX(badge_total)
    FROM germany_badges
    WHERE badge_total < (SELECT MAX(badge_total) FROM germany_badges)
)
ORDER BY DisplayName;
```

本輪SQL：
```sql
WITH german_user_badge_counts AS (
    SELECT u.Id, u.DisplayName, COUNT(b.Id) AS badge_total
    FROM users AS u
    LEFT JOIN badges AS b ON b.UserId = u.Id
    WHERE u.Location = 'Germany'
    GROUP BY u.Id, u.DisplayName
),
ranked_totals AS (
    SELECT badge_total,
           DENSE_RANK() OVER (ORDER BY badge_total DESC) AS total_rank
    FROM (SELECT DISTINCT badge_total FROM german_user_badge_counts)
)
SELECT g.DisplayName, g.badge_total
FROM german_user_badge_counts AS g
JOIN ranked_totals AS r ON r.badge_total = g.badge_total
WHERE r.total_rank = 2
ORDER BY g.DisplayName;
```



<a id="q137"></a>

## [Q137](failure-case-review.md#q137) · 歷史啱→本輪錯 · codebase_community

候選關聯：R1／地點編碼。LIKE '%CA%' 不是 California／CA token 匹配，會誤配其他字串並漏掉完整 California。

歷史→本輪：model replies 6→6；tool attempts 5→5；SQL attempts 3→3。

Question：I'm planning regional outreach and want to know which California-based account draws the most profile attention. Among users whose stated location shows they are based in California, give me the user id, display name, profile view count, and reputation of the user or users with the most profile views. If several such users tie for the most profile views, list every one of them with those same four values.

歷史SQL：
```sql
SELECT Id, DisplayName, Views, Reputation
FROM users
WHERE Location LIKE '%CA%'
  AND (Location LIKE '%CA,%' OR Location LIKE '%, CA' OR Location LIKE '%, CA,%')
  AND Views = (
    SELECT MAX(Views)
    FROM users
    WHERE Location LIKE '%CA%'
      AND (Location LIKE '%CA,%' OR Location LIKE '%, CA' OR Location LIKE '%, CA,%')
  );
```

本輪SQL：
```sql
SELECT Id, DisplayName, Views, Reputation
FROM users
WHERE Location LIKE '%CA%'
  AND Location NOT LIKE '%Canada%'
  AND Views = (
      SELECT MAX(Views)
      FROM users
      WHERE Location LIKE '%CA%'
        AND Location NOT LIKE '%Canada%'
  );
```



<a id="q141"></a>

## [Q141](historical-case-review.md#q141) · 歷史錯→本輪啱 · codebase_community

候選關聯：R4／link分類。postLinks增加LinkTypeId=1。

歷史→本輪：model replies 4→6；tool attempts 4→6；SQL attempts 1→3。

Question：Among all posts whose title contains the phrase 'principal component scores', which one has the most related posts linked to it? For each such post, give me the post title and the number of related posts. If several posts tie for the most, list every one of them with their counts. The count should cover related posts across the site's entire history.

歷史SQL：
```sql
WITH counts AS (
    SELECT p.Id, p.Title, COUNT(pl.Id) AS related_count
    FROM posts AS p
    LEFT JOIN postLinks AS pl ON pl.PostId = p.Id
    WHERE p.Title LIKE '%principal component scores%'
    GROUP BY p.Id, p.Title
)
SELECT Title, related_count
FROM counts
WHERE related_count = (SELECT MAX(related_count) FROM counts);
```

本輪SQL：
```sql
WITH candidates AS (
    SELECT Id, Title
    FROM posts
    WHERE Title LIKE '%principal component scores%'
),
related_counts AS (
    SELECT c.Id, c.Title, COUNT(pl.Id) AS related_count
    FROM candidates AS c
    LEFT JOIN postLinks AS pl
        ON pl.PostId = c.Id
       AND pl.LinkTypeId = 1
    GROUP BY c.Id, c.Title
)
SELECT Title, related_count
FROM related_counts
WHERE related_count = (SELECT MAX(related_count) FROM related_counts)
ORDER BY Title;
```



<a id="q152"></a>

## [Q152](historical-case-review.md#q152) · 歷史錯→本輪啱 · debit_card_specializing

候選關聯：R4／取消附加篩選。yearmonth existence移除Consumption>0限制。

歷史→本輪：model replies 5→4；tool attempts 7→8；SQL attempts 2→3。

Question：How many customers who pay in EUR and had gas consumption in 2012 also had gas consumption in 2013? I just need a single number: the count of such customers. By 2012 and 2013 I mean those calendar years, and gas consumption in any month of the year counts.

歷史SQL：
```sql
SELECT COUNT(DISTINCT c.CustomerID) AS customer_count
FROM customers AS c
WHERE c.Currency = 'EUR'
  AND EXISTS (
    SELECT 1
    FROM yearmonth AS y
    WHERE y.CustomerID = c.CustomerID
      AND y.Date LIKE '2012%'
      AND y.Consumption > 0
  )
  AND EXISTS (
    SELECT 1
    FROM yearmonth AS y
    WHERE y.CustomerID = c.CustomerID
      AND y.Date LIKE '2013%'
      AND y.Consumption > 0
  );
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT c.CustomerID)
FROM customers AS c
WHERE c.Currency = 'EUR'
  AND EXISTS (
      SELECT 1
      FROM yearmonth AS y2012
      WHERE y2012.CustomerID = c.CustomerID
        AND y2012.Date >= '201201'
        AND y2012.Date < '201301'
  )
  AND EXISTS (
      SELECT 1
      FROM yearmonth AS y2013
      WHERE y2013.CustomerID = c.CustomerID
        AND y2013.Date >= '201301'
        AND y2013.Date < '201401'
  );
```



<a id="q162"></a>

## [Q162](historical-case-review.md#q162) · 歷史錯→本輪啱 · debit_card_specializing

候選關聯：R2／資料來源。transactions_1k抽樣交易改yearmonth當月總表。

歷史→本輪：model replies 5→7；tool attempts 12→16；SQL attempts 7→11。

Question：For my February 2013 activity report: how many SME customers actually purchased gas in February 2013? Please give me just a single whole number - the count of SME customers who consumed gas during the calendar month of February 2013 (Feb 1-28, 2013).

歷史SQL：
```sql
SELECT COUNT(DISTINCT c.CustomerID)
FROM customers AS c
JOIN transactions_1k AS t ON t.CustomerID = c.CustomerID
JOIN products AS p ON p.ProductID = t.ProductID
WHERE c.Segment = 'SME'
  AND t.Date >= '2013-02-01'
  AND t.Date < '2013-03-01'
  AND p.Description IN ('Special', 'Super', 'Natural', 'Mix', 'Natural +', 'Natural Plus');
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT y.CustomerID)
FROM yearmonth AS y
JOIN customers AS c ON c.CustomerID = y.CustomerID
WHERE c.Segment = 'SME'
  AND y.Date = '201302'
  AND y.Consumption > 0;
```



<a id="q174"></a>

## [Q174](failure-case-review.md#q174) · 歷史啱→本輪錯 · european_football_2

候選關聯：R3／零次實體。從 player_matches AVG，漏掉 shortlist 中該季零出場球員；日期字串界線亦不同。

歷史→本輪：model replies 4→5；tool attempts 5→6；SQL attempts 1→2。

Question：I've shortlisted the players whose overall rating as of 31 December 2010 was above 80 - strictly above 80, that is. How many matches did these players play on average during the 2010/2011 season? Please give me just that single average, rounded to two decimals.

歷史SQL：
```sql
WITH rating_snapshot AS (
    SELECT
        player_api_id,
        overall_rating,
        ROW_NUMBER() OVER (
            PARTITION BY player_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Player_Attributes
    WHERE date <= '2010-12-31'
),
shortlisted AS (
    SELECT player_api_id
    FROM rating_snapshot
    WHERE rn = 1
      AND overall_rating > 80
),
appearances AS (
    SELECT
        s.player_api_id,
        SUM(
            CASE WHEN m.home_player_1 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_2 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_3 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_4 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_5 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_6 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_7 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_8 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_9 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_10 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.home_player_11 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_1 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_2 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_3 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_4 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_5 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_6 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_7 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_8 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_9 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_10 = s.player_api_id THEN 1 ELSE 0 END +
            CASE WHEN m.away_player_11 = s.player_api_id THEN 1 ELSE 0 END
        ) AS match_count
    FROM shortlisted s
    JOIN Match m
      ON m.season = '2010/2011'
    GROUP BY s.player_api_id
)
SELECT ROUND(AVG(match_count), 2) AS average_matches
FROM appearances;
```

本輪SQL：
```sql
WITH ratings AS (
    SELECT
        player_api_id,
        overall_rating,
        ROW_NUMBER() OVER (
            PARTITION BY player_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Player_Attributes
    WHERE date <= '2010-12-31'
),
eligible AS (
    SELECT player_api_id
    FROM ratings
    WHERE rn = 1
      AND overall_rating > 80
),
player_matches AS (
    SELECT player_api_id, COUNT(*) AS match_count
    FROM (
        SELECT m.id, e.player_api_id
        FROM "Match" AS m
        JOIN eligible AS e
          ON e.player_api_id IN (
              m.home_player_1, m.home_player_2, m.home_player_3,
              m.home_player_4, m.home_player_5, m.home_player_6,
              m.home_player_7, m.home_player_8, m.home_player_9,
              m.home_player_10, m.home_player_11, m.away_player_1,
              m.away_player_2, m.away_player_3, m.away_player_4,
              m.away_player_5, m.away_player_6, m.away_player_7,
              m.away_player_8, m.away_player_9, m.away_player_10,
              m.away_player_11
          )
        WHERE m.season = '2010/2011'
    )
    GROUP BY player_api_id
)
SELECT ROUND(AVG(match_count), 2)
FROM player_matches;
```



<a id="q181"></a>

## [Q181](historical-case-review.md#q181) · 歷史錯→本輪啱 · european_football_2

候選關聯：R7／集合完整性。取消只保留最大home_win_count，輸出全部qualifying clubs。

歷史→本輪：model replies 4→5；tool attempts 5→6；SQL attempts 1→2。

Question：I'm looking at whether a fast attacking build-up actually converts into big results. Which clubs, playing at home, have won a match by at least 3 goals while their build-up play speed was rated fast at the time? For each such club, give me the club name, short name, and how many of those home wins it has - one row per club. Please treat clubs as separate even if two clubs share the same short name, and if several clubs tie on the number of wins, list all of them. The speed rating that counts is the club's most recent rating dated on or before the match's own date.

歷史SQL：
```sql
WITH qualifying_matches AS (
    SELECT
        m.id AS match_id,
        m.home_team_api_id AS team_api_id,
        m.date
    FROM "Match" AS m
    WHERE m.home_team_goal - m.away_team_goal >= 3
),
rated_matches AS (
    SELECT
        q.match_id,
        q.team_api_id,
        (
            SELECT ta.buildUpPlaySpeedClass
            FROM Team_Attributes AS ta
            WHERE ta.team_api_id = q.team_api_id
              AND ta.date <= q.date
            ORDER BY ta.date DESC, ta.id DESC
            LIMIT 1
        ) AS speed_class
    FROM qualifying_matches AS q
),
club_counts AS (
    SELECT
        t.id AS team_id,
        t.team_long_name,
        t.team_short_name,
        COUNT(*) AS home_win_count
    FROM rated_matches AS r
    JOIN Team AS t
      ON t.team_api_id = r.team_api_id
    WHERE r.speed_class = 'Fast'
    GROUP BY t.id, t.team_long_name, t.team_short_name
)
SELECT
    team_long_name,
    team_short_name,
    home_win_count
FROM club_counts
WHERE home_win_count = (SELECT MAX(home_win_count) FROM club_counts)
ORDER BY team_long_name, team_id;
```

本輪SQL：
```sql
WITH eligible_matches AS (
    SELECT
        m.id AS match_id,
        m.home_team_api_id AS team_api_id,
        m.date AS match_date
    FROM "Match" AS m
    WHERE m.home_team_goal - m.away_team_goal >= 3
),
rated_matches AS (
    SELECT
        em.match_id,
        em.team_api_id,
        ta.buildUpPlaySpeedClass,
        ROW_NUMBER() OVER (
            PARTITION BY em.match_id
            ORDER BY ta.date DESC, ta.id DESC
        ) AS rn
    FROM eligible_matches AS em
    JOIN Team_Attributes AS ta
      ON ta.team_api_id = em.team_api_id
     AND ta.date <= em.match_date
)
SELECT
    t.team_long_name AS club_name,
    t.team_short_name AS short_name,
    COUNT(*) AS home_wins
FROM rated_matches AS rm
JOIN Team AS t
  ON t.team_api_id = rm.team_api_id
WHERE rm.rn = 1
  AND rm.buildUpPlaySpeedClass = 'Fast'
GROUP BY t.team_api_id, t.team_long_name, t.team_short_name
ORDER BY home_wins DESC, t.team_long_name, t.team_api_id;
```



<a id="q186"></a>

## [Q186](failure-case-review.md#q186) · 歷史啱→本輪錯 · european_football_2

候選關聯：R3／零次實體。平均只覆蓋曾出現於 home_player_3 的玩家，Gold 分母涵蓋全部 Player。

歷史→本輪：model replies 4→4；tool attempts 4→4；SQL attempts 1→1。

Question：I'm reviewing home-match outcomes by lineup slot and want one number: across the whole player population, what is the average of the total home-team goals scored in the matches where a player appeared as the home team's third listed player? In other words, for each player, take all matches where they were the home team's third listed player and add up the home team's goals in those matches; give me the average of those totals over all players, rounded to two decimal places.

歷史SQL：
```sql
WITH player_totals AS (
  SELECT p.player_api_id, COALESCE(SUM(m.home_team_goal), 0) AS total_home_goals
  FROM Player p
  LEFT JOIN "Match" m ON m.home_player_3 = p.player_api_id
  GROUP BY p.player_api_id
)
SELECT ROUND(AVG(total_home_goals), 2) AS average_total_home_goals
FROM player_totals;
```

本輪SQL：
```sql
WITH player_totals AS (
  SELECT home_player_3 AS player_id,
         SUM(home_team_goal) AS total_home_goals
  FROM "Match"
  WHERE home_player_3 IS NOT NULL
  GROUP BY home_player_3
)
SELECT ROUND(AVG(total_home_goals), 2) AS average_total_home_goals
FROM player_totals;
```



<a id="q194"></a>

## [Q194](failure-case-review.md#q194) · 歷史啱→本輪錯 · financial

候選關聯：R2／欄位語義。把平均薪金欄 A11 錯認為 A12，影響地區選擇及差額。

歷史→本輪：model replies 8→10；tool attempts 10→12；SQL attempts 5→7。

Question：Among female clients living in the district with the lowest average salary, give the account IDs of the oldest client and the difference between the highest and lowest district-average salaries.

歷史SQL：
```sql
WITH lowest_salary_district AS (
    SELECT district_id
    FROM district
    WHERE A11 = (SELECT MIN(A11) FROM district)
),
oldest_female_client AS (
    SELECT c.client_id, c.birth_date
    FROM client c
    JOIN lowest_salary_district d ON d.district_id = c.district_id
    WHERE c.gender = 'F'
    ORDER BY c.birth_date ASC
    LIMIT 1
)
SELECT dp.account_id,
       (SELECT MAX(A11) - MIN(A11) FROM district) AS salary_difference
FROM oldest_female_client c
JOIN disp dp ON dp.client_id = c.client_id;
```

本輪SQL：
```sql
WITH lowest_salary_district AS (
    SELECT district_id
    FROM district
    WHERE A12 = (SELECT MIN(A12) FROM district)
),
oldest_female_clients AS (
    SELECT client_id
    FROM client
    WHERE gender = 'F'
      AND district_id IN (SELECT district_id FROM lowest_salary_district)
      AND birth_date = (
          SELECT MIN(c.birth_date)
          FROM client c
          WHERE c.gender = 'F'
            AND c.district_id IN (SELECT district_id FROM lowest_salary_district)
      )
)
SELECT dp.account_id,
       (SELECT MAX(A12) - MIN(A12) FROM district) AS salary_difference
FROM oldest_female_clients o
JOIN disp dp ON dp.client_id = o.client_id;
```



<a id="q203"></a>

## [Q203](historical-case-review.md#q203) · 歷史錯→本輪啱 · financial

候選關聯：R7／型別契約。人口輸出由A4原文改CAST INTEGER。

歷史→本輪：model replies 4→6；tool attempts 4→6；SQL attempts 1→3。

Question：We're reviewing our first month of operations. Looking at the districts where we opened at least one account during that first month, which district had the largest population, and how many inhabitants does it have? If several districts tie for the largest population, list all of them with their populations.

歷史SQL：
```sql
WITH first_month AS (
  SELECT date(MIN(date), 'start of month') AS month_start
  FROM account
),
opened_districts AS (
  SELECT DISTINCT a.district_id
  FROM account AS a
  CROSS JOIN first_month AS f
  WHERE date(a.date, 'start of month') = f.month_start
)
SELECT d.A2 AS district, d.A4 AS population
FROM district AS d
JOIN opened_districts AS o ON o.district_id = d.district_id
WHERE CAST(d.A4 AS INTEGER) = (
  SELECT MAX(CAST(d2.A4 AS INTEGER))
  FROM district AS d2
  JOIN opened_districts AS o2 ON o2.district_id = d2.district_id
);
```

本輪SQL：
```sql
WITH first_month AS (
    SELECT strftime('%Y-%m', MIN(date)) AS month
    FROM account
),
opened_districts AS (
    SELECT DISTINCT a.district_id
    FROM account AS a
    JOIN first_month AS f
      ON strftime('%Y-%m', a.date) = f.month
),
candidates AS (
    SELECT d.A2 AS district, CAST(d.A4 AS INTEGER) AS population
    FROM district AS d
    JOIN opened_districts AS o
      ON o.district_id = d.district_id
)
SELECT district, population
FROM candidates
WHERE population = (SELECT MAX(population) FROM candidates);
```



<a id="q206"></a>

## [Q206](failure-case-review.md#q206) · 歷史啱→本輪錯 · financial

候選關聯：R2／欄位語義。以 district.A2（district name）當 region，Gold 應按 A3 聚合；月末加月份亦有日期政策差異。

歷史→本輪：model replies 5→7；tool attempts 5→8；SQL attempts 1→4。

Question：For our 1995 year-end loan review: which of the bank's regions has the largest total approved amount among loans that were still being repaid on 31 December 1995, and what is that total? Only count loans approved on or before that day whose repayment term still covers that day; loans approved after it don't count yet. A loan's term includes both its approval day and its last day. If several regions tie for the largest total, list every tied region with the total. Just give me the region name and the single total figure.

歷史SQL：
```sql
WITH regional_totals AS (
  SELECT d.A3 AS region, SUM(l.amount) AS total_amount
  FROM loan AS l
  JOIN account AS a ON a.account_id = l.account_id
  JOIN district AS d ON d.district_id = a.district_id
  WHERE date(l.date) <= date('1995-12-31')
    AND date(l.date, '+' || l.duration || ' months') >= date('1995-12-31')
  GROUP BY d.A3
)
SELECT region, total_amount
FROM regional_totals
WHERE total_amount = (SELECT MAX(total_amount) FROM regional_totals);
```

本輪SQL：
```sql
WITH regional_totals AS (
    SELECT d.A2 AS region, SUM(l.amount) AS total_approved_amount
    FROM loan AS l
    JOIN account AS a ON a.account_id = l.account_id
    JOIN district AS d ON d.district_id = a.district_id
    WHERE date(l.date) <= date('1995-12-31')
      AND date(l.date, '+' || l.duration || ' months') >= date('1995-12-31')
    GROUP BY d.A2
)
SELECT region, total_approved_amount
FROM regional_totals
WHERE total_approved_amount = (SELECT MAX(total_approved_amount) FROM regional_totals);
```



<a id="q211"></a>

## [Q211](historical-case-review.md#q211) · 歷史錯→本輪啱 · financial

候選關聯：R4／集合與缺失值。取消t.type='VYDAJ'；其他purpose排空字串並用DISTINCT trans_id。

歷史→本輪：model replies 5→7；tool attempts 8→11；SQL attempts 3→6。

Question：I'm putting together a periodic report on large payments made by a specific customer cohort, split by what the payment was for. Among payments over $4000 (strictly more than $4000) made from the accounts of male customers born between 1974 and 1976, I need two figures: how many were household payments, and how many were made for a purpose other than household payment. A few rules to keep in mind: born between 1974 and 1976 means the birth year is 1974, 1975 or 1976; a customer's accounts are the ones they hold a disposition on; payments are the individual transactions executed on the account, not standing payment orders; a payment counts as other-purpose only if it has a recorded purpose different from household payment, and a payment with no purpose recorded counts in neither bucket.

歷史SQL：
```sql
SELECT
    SUM(CASE WHEN t.k_symbol = 'SIPO' THEN 1 ELSE 0 END) AS household_payments,
    SUM(CASE WHEN t.k_symbol IS NOT NULL AND t.k_symbol <> 'SIPO' THEN 1 ELSE 0 END) AS other_purpose_payments
FROM client c
JOIN disp d ON d.client_id = c.client_id
JOIN trans t ON t.account_id = d.account_id
WHERE c.gender = 'M'
  AND CAST(strftime('%Y', c.birth_date) AS INTEGER) BETWEEN 1974 AND 1976
  AND t.type = 'VYDAJ'
  AND t.amount > 4000;
```

本輪SQL：
```sql
SELECT
    COUNT(DISTINCT CASE WHEN t.k_symbol = 'SIPO' THEN t.trans_id END) AS household_payments,
    COUNT(DISTINCT CASE WHEN t.k_symbol IS NOT NULL AND t.k_symbol <> 'SIPO' AND TRIM(t.k_symbol) <> '' THEN t.trans_id END) AS other_purpose_payments
FROM trans AS t
JOIN disp AS d ON d.account_id = t.account_id
JOIN client AS c ON c.client_id = d.client_id
WHERE c.gender = 'M'
  AND CAST(strftime('%Y', c.birth_date) AS INTEGER) BETWEEN 1974 AND 1976
  AND t.amount > 4000;
```



<a id="q212"></a>

## [Q212](failure-case-review.md#q212) · 歷史啱→本輪錯 · financial

候選關聯：R2／欄位語義。home population 用 A8 而非 A4；counterparty 附加 operation清單且未 account>0。

歷史→本輪：model replies 6→5；tool attempts 10→11；SQL attempts 3→4。

Question：I want to find out whether our borrowing households from larger population centres transact differently from local ones. For every account at the Prachatice branch that has taken at least one loan, please give me: the account number, the account opening date, the total amount ever borrowed, how many outside bank counterparties the account has transacted with over its entire history, the owner's home district, the population of that district, and a rank of these borrowing households by home-district population from largest to smallest. Note that a counterparty means a particular bank account at another institution, identified by that account number, not by the bank code, and only transfers to or from another bank count — handling cash at our own branch does not involve a counterparty. A household's home district is the district its owner client is registered in, which is not necessarily Prachatice. For the ranking: largest population first, ties share the same rank and the next rank after a tie is skipped, and among households whose home districts have the same population, list the smaller account number first.

歷史SQL：
```sql
WITH loan_totals AS (
    SELECT account_id, SUM(amount) AS total_borrowed
    FROM loan
    GROUP BY account_id
),
counterparties AS (
    SELECT account_id, COUNT(DISTINCT counterparty_account) AS counterparty_count
    FROM (
        SELECT account_id, account AS counterparty_account
        FROM trans
        WHERE type = 'PRIJEM' AND bank IS NOT NULL AND account IS NOT NULL

        UNION

        SELECT account_id, account AS counterparty_account
        FROM trans
        WHERE type = 'VYDAJ' AND bank IS NOT NULL AND account IS NOT NULL
    )
    GROUP BY account_id
),
borrowing_accounts AS (
    SELECT a.account_id,
           a.date AS opening_date,
           lt.total_borrowed,
           COALESCE(cp.counterparty_count, 0) AS counterparty_count,
           d.A2 AS home_district,
           CAST(d.A4 AS INTEGER) AS district_population
    FROM account a
    JOIN district branch ON branch.district_id = a.district_id
    JOIN loan_totals lt ON lt.account_id = a.account_id
    JOIN disp dp ON dp.account_id = a.account_id AND dp.type = 'OWNER'
    JOIN client c ON c.client_id = dp.client_id
    JOIN district d ON d.district_id = c.district_id
    LEFT JOIN counterparties cp ON cp.account_id = a.account_id
    WHERE branch.A2 = 'Prachatice'
)
SELECT account_id,
       opening_date,
       total_borrowed,
       counterparty_count,
       home_district,
       district_population,
       RANK() OVER (ORDER BY district_population DESC) AS population_rank
FROM borrowing_accounts
ORDER BY district_population DESC, account_id;
```

本輪SQL：
```sql
WITH loan_totals AS (
    SELECT account_id, SUM(amount) AS total_amount_borrowed
    FROM loan
    GROUP BY account_id
),
counterparty_counts AS (
    SELECT account_id, COUNT(DISTINCT account) AS outside_counterparty_count
    FROM trans
    WHERE operation IN ('PREVOD NA UCET', 'PREVOD Z UCTU')
      AND bank IS NOT NULL
      AND account IS NOT NULL
    GROUP BY account_id
),
borrowing_households AS (
    SELECT
        a.account_id,
        a.date AS account_opening_date,
        lt.total_amount_borrowed,
        COALESCE(cc.outside_counterparty_count, 0) AS outside_counterparty_count,
        d.A2 AS home_district,
        d.A8 AS district_population
    FROM account AS a
    JOIN loan_totals AS lt ON lt.account_id = a.account_id
    JOIN disp AS dp ON dp.account_id = a.account_id
                   AND dp.type = 'OWNER'
    JOIN client AS c ON c.client_id = dp.client_id
    JOIN district AS d ON d.district_id = c.district_id
    LEFT JOIN counterparty_counts AS cc ON cc.account_id = a.account_id
    WHERE a.district_id = (
        SELECT district_id
        FROM district
        WHERE A2 = 'Prachatice'
    )
)
SELECT
    account_id,
    account_opening_date,
    total_amount_borrowed,
    outside_counterparty_count,
    home_district,
    district_population,
    RANK() OVER (
        ORDER BY district_population DESC
    ) AS population_rank
FROM borrowing_households
ORDER BY district_population DESC, account_id;
```



<a id="q213"></a>

## [Q213](historical-case-review.md#q213) · 歷史錯→本輪啱 · financial

候選關聯：R7／輸出內容。gender由women/men改F/M、district_id改district name；多處同時改變。

歷史→本輪：model replies 4→6；tool attempts 8→16；SQL attempts 1→8。

Question：I'm profiling our gold-card customers for a regional campaign, split by gender. For women first, then men, look at gold-card holders whose card's account has an average balance over 1,000. Among the branch districts holding those accounts, keep only the districts with over 100,000 inhabitants. For each gender, tell me: the number of those districts; which of them has the most inhabitants, with its inhabitants figure - if two districts tie, list both, one row per district; the average salary across those districts, rounded to two decimals; and the average ratio of urban inhabitants across those districts, rounded to two decimals. Nothing else. Please note: 'over' means strictly greater than, and an account's average balance is the mean of its balances after each transaction.

歷史SQL：
```sql
WITH avg_balance AS (
    SELECT account_id, AVG(balance) AS avg_balance
    FROM trans
    GROUP BY account_id
),
qualifying_districts AS (
    SELECT DISTINCT
        c.gender,
        d.district_id,
        CAST(d.A4 AS INTEGER) AS inhabitants,
        d.A11 AS salary,
        d.A10 AS urban_ratio
    FROM card AS ca
    JOIN disp AS dp
        ON dp.disp_id = ca.disp_id
       AND dp.type = 'OWNER'
    JOIN client AS c
        ON c.client_id = dp.client_id
    JOIN account AS a
        ON a.account_id = dp.account_id
    JOIN avg_balance AS ab
        ON ab.account_id = a.account_id
       AND ab.avg_balance > 1000
    JOIN district AS d
        ON d.district_id = a.district_id
    WHERE ca.type = 'gold'
      AND CAST(d.A4 AS INTEGER) > 100000
),
gender_summary AS (
    SELECT
        gender,
        COUNT(*) AS district_count,
        MAX(inhabitants) AS max_inhabitants,
        ROUND(AVG(salary), 2) AS avg_salary,
        ROUND(AVG(urban_ratio), 2) AS avg_urban_ratio
    FROM qualifying_districts
    GROUP BY gender
)
SELECT
    CASE s.gender WHEN 'F' THEN 'women' WHEN 'M' THEN 'men' ELSE s.gender END AS gender,
    s.district_count,
    q.district_id,
    q.inhabitants,
    s.avg_salary,
    s.avg_urban_ratio
FROM gender_summary AS s
JOIN qualifying_districts AS q
    ON q.gender = s.gender
   AND q.inhabitants = s.max_inhabitants
ORDER BY CASE s.gender WHEN 'F' THEN 0 WHEN 'M' THEN 1 ELSE 2 END,
         q.district_id;
```

本輪SQL：
```sql
WITH account_avg AS (
    SELECT account_id, AVG(balance) AS avg_balance
    FROM trans
    GROUP BY account_id
),
qualifying_districts AS (
    SELECT DISTINCT c.gender, d.district_id
    FROM card AS ca
    JOIN disp AS dp
      ON dp.disp_id = ca.disp_id
     AND dp.type = 'OWNER'
    JOIN client AS c
      ON c.client_id = dp.client_id
    JOIN account AS a
      ON a.account_id = dp.account_id
    JOIN account_avg AS aa
      ON aa.account_id = a.account_id
    JOIN district AS d
      ON d.district_id = a.district_id
    WHERE ca.type = 'gold'
      AND aa.avg_balance > 1000
      AND CAST(d.A4 AS INTEGER) > 100000
),
district_stats AS (
    SELECT q.gender,
           COUNT(*) AS district_count,
           MAX(CAST(d.A4 AS INTEGER)) AS max_inhabitants,
           ROUND(AVG(d.A11), 2) AS avg_salary,
           ROUND(AVG(d.A10), 2) AS avg_urban_ratio
    FROM qualifying_districts AS q
    JOIN district AS d
      ON d.district_id = q.district_id
    GROUP BY q.gender
)
SELECT s.gender,
       s.district_count,
       d.A2 AS district,
       CAST(d.A4 AS INTEGER) AS inhabitants,
       s.avg_salary,
       s.avg_urban_ratio
FROM district_stats AS s
JOIN qualifying_districts AS q
  ON q.gender = s.gender
JOIN district AS d
  ON d.district_id = q.district_id
WHERE CAST(d.A4 AS INTEGER) = s.max_inhabitants
ORDER BY CASE s.gender WHEN 'F' THEN 1 WHEN 'M' THEN 2 ELSE 3 END,
         d.A2;
```



<a id="q223"></a>

## [Q223](historical-case-review.md#q223) · 歷史錯→本輪啱 · financial

候選關聯：R3／平均權重。取消account join後重複district平均，直接平均district/year比率。

歷史→本輪：model replies 5→5；tool attempts 6→6；SQL attempts 2→2。

Question：I'm doing a lending review by account-opening year for my region. For accounts opened in the central Bohemia region from 1 January 1996 onward, broken down by the calendar year of the account creation date (as a text string like '1996', not an integer), I need: the number of accounts opened that year in the region, the total amount lent on those accounts, and the average across the districts of the amount lent per account opened in that district, rounded to two decimals. An account with no loan counts as having lent nothing.

歷史SQL：
```sql
WITH account_lending AS (
    SELECT
        a.account_id,
        a.district_id,
        a.date,
        COALESCE(SUM(l.amount), 0) AS lent
    FROM account AS a
    JOIN district AS d
        ON d.district_id = a.district_id
    LEFT JOIN loan AS l
        ON l.account_id = a.account_id
    WHERE d.A3 = 'central Bohemia'
      AND a.date >= '1996-01-01'
    GROUP BY a.account_id, a.district_id, a.date
),
district_year AS (
    SELECT
        strftime('%Y', date) AS year,
        district_id,
        SUM(lent) * 1.0 / COUNT(*) AS lent_per_account
    FROM account_lending
    GROUP BY strftime('%Y', date), district_id
)
SELECT
    strftime('%Y', al.date) AS year,
    COUNT(*) AS accounts_opened,
    SUM(al.lent) AS total_amount_lent,
    ROUND(AVG(dy.lent_per_account), 2) AS avg_district_amount_lent_per_account
FROM account_lending AS al
JOIN district_year AS dy
    ON dy.year = strftime('%Y', al.date)
   AND dy.district_id = al.district_id
GROUP BY strftime('%Y', al.date)
ORDER BY year;
```

本輪SQL：
```sql
WITH account_loans AS (
    SELECT a.account_id,
           a.district_id,
           a.date,
           COALESCE(SUM(l.amount), 0) AS amount_lent
    FROM account AS a
    LEFT JOIN loan AS l ON l.account_id = a.account_id
    WHERE a.date >= '1996-01-01'
      AND a.district_id IN (
          SELECT district_id
          FROM district
          WHERE A3 = 'central Bohemia'
      )
    GROUP BY a.account_id, a.district_id, a.date
),
district_year AS (
    SELECT strftime('%Y', date) AS creation_year,
           district_id,
           SUM(amount_lent) AS district_amount_lent,
           COUNT(*) AS district_accounts
    FROM account_loans
    GROUP BY strftime('%Y', date), district_id
)
SELECT creation_year,
       SUM(district_accounts) AS account_count,
       SUM(district_amount_lent) AS total_amount_lent,
       ROUND(AVG(1.0 * district_amount_lent / district_accounts), 2)
           AS average_district_amount_lent_per_account
FROM district_year
GROUP BY creation_year
ORDER BY creation_year;
```



<a id="q224"></a>

## [Q224](historical-case-review.md#q224) · 歷史錯→本輪啱 · financial

候選關聯：R5／as-of查詢。approval當日exact match改最新transaction date<=approval。

歷史→本輪：model replies 5→7；tool attempts 7→13；SQL attempts 2→6。

Question：For a regional risk review, I need to look at our largest 24-month loans. Please find the ten loans with the largest approved amount among loans with a 24-month duration on accounts that have weekly statement issuance. For each of these ten loans, give me: the district of the branch servicing the account, the approved amount, the approval date, and the account balance at the end of the day the loan was approved. Two rules: if two loans have the same approved amount, the one approved earlier counts as larger; and if several transactions share that last day, the one with the higher transaction id counts as the later one. List the results from the largest approved amount down.

歷史SQL：
```sql
WITH ranked_loans AS (
    SELECT
        l.loan_id,
        l.account_id,
        l.date AS approval_date,
        l.amount AS approved_amount,
        ROW_NUMBER() OVER (ORDER BY l.amount DESC, l.date ASC) AS loan_rank
    FROM loan AS l
    JOIN account AS a ON a.account_id = l.account_id
    WHERE l.duration = 24
      AND a.frequency = 'POPLATEK TYDNE'
)
SELECT
    d.A2 AS district,
    rl.approved_amount,
    rl.approval_date,
    (
        SELECT t.balance
        FROM trans AS t
        WHERE t.account_id = rl.account_id
          AND date(t.date) = date(rl.approval_date)
        ORDER BY t.trans_id DESC
        LIMIT 1
    ) AS approval_day_end_balance
FROM ranked_loans AS rl
JOIN account AS a ON a.account_id = rl.account_id
JOIN district AS d ON d.district_id = a.district_id
WHERE rl.loan_rank <= 10
ORDER BY rl.approved_amount DESC, rl.approval_date ASC;
```

本輪SQL：
```sql
WITH ranked_loans AS (
    SELECT
        l.loan_id,
        l.account_id,
        l.date,
        l.amount,
        d.A2 AS district,
        ROW_NUMBER() OVER (
            ORDER BY l.amount DESC, l.date ASC, l.loan_id ASC
        ) AS rn
    FROM loan AS l
    JOIN account AS a
        ON a.account_id = l.account_id
    JOIN district AS d
        ON d.district_id = a.district_id
    WHERE l.duration = 24
      AND a.frequency = 'POPLATEK TYDNE'
)
SELECT
    r.district,
    r.amount AS approved_amount,
    r.date AS approval_date,
    (
        SELECT t.balance
        FROM trans AS t
        WHERE t.account_id = r.account_id
          AND t.date <= r.date
        ORDER BY t.date DESC, t.trans_id DESC
        LIMIT 1
    ) AS balance
FROM ranked_loans AS r
WHERE r.rn <= 10
ORDER BY r.amount DESC, r.date ASC, r.loan_id ASC;
```



<a id="q236"></a>

## [Q236](historical-case-review.md#q236) · 歷史錯→本輪啱 · financial

候選關聯：R3／平均粒度。按district去重後AVG salary，取消按client/account重複加權。

歷史→本輪：model replies 5→8；tool attempts 7→10；SQL attempts 2→4。

Question：I'm planning services for our older female customers. For the clients who are female and were born before 1930, please look at the branches that hold their accounts, and then the districts those branches are located in. What is the average salary of those districts? Round the result to 2 decimal places. Note: born before 1930 means calendar birth dates before 1 January 1930.

歷史SQL：
```sql
SELECT ROUND(AVG(d.A11), 2) AS avg_salary
FROM client c
JOIN disp dp ON dp.client_id = c.client_id
JOIN account a ON a.account_id = dp.account_id
JOIN district d ON d.district_id = a.district_id
WHERE c.gender = 'F'
  AND c.birth_date < '1930-01-01';
```

本輪SQL：
```sql
SELECT ROUND(AVG(d.A11), 2) AS average_salary
FROM (
    SELECT DISTINCT a.district_id
    FROM client c
    JOIN disp dp ON dp.client_id = c.client_id
    JOIN account a ON a.account_id = dp.account_id
    WHERE c.gender = 'F'
      AND c.birth_date < '1930-01-01'
) AS qualifying_districts
JOIN district d ON d.district_id = qualifying_districts.district_id;
```



<a id="q242"></a>

## [Q242](historical-case-review.md#q242) · 歷史錯→本輪啱 · formula_1

候選關聯：R7／輸出契約。取消額外race_wins欄，保留四個要求欄。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：Which driver won the most recorded races? Give their first name, last name, nationality, and highest recorded driver-standings points total.

歷史SQL：
```sql
SELECT d.forename, d.surname, d.nationality,
       COUNT(*) AS race_wins,
       (SELECT MAX(ds.points)
        FROM driverStandings ds
        WHERE ds.driverId = d.driverId) AS highest_standings_points
FROM results r
JOIN drivers d ON d.driverId = r.driverId
WHERE r.position = 1
GROUP BY d.driverId
ORDER BY race_wins DESC
LIMIT 1;
```

本輪SQL：
```sql
WITH winner_counts AS (
    SELECT driverId, COUNT(*) AS wins
    FROM results
    WHERE position = 1
    GROUP BY driverId
),
max_wins AS (
    SELECT MAX(wins) AS wins
    FROM winner_counts
),
driver_points AS (
    SELECT driverId, MAX(points) AS highest_points
    FROM driverStandings
    GROUP BY driverId
)
SELECT d.forename, d.surname, d.nationality, dp.highest_points
FROM winner_counts AS wc
JOIN max_wins AS mw ON wc.wins = mw.wins
JOIN drivers AS d ON d.driverId = wc.driverId
LEFT JOIN driver_points AS dp ON dp.driverId = wc.driverId;
```



<a id="q253"></a>

## [Q253](historical-case-review.md#q253) · 歷史錯→本輪啱 · formula_1

候選關聯：R1／正確但脆弱的時間排序。本資料字串MIN為16:42.640、字串MAX為1:48.289；改MIN恰好符合真正最慢時間，但字典序MIN並非一般的最慢時間算法，EX改善不可當作一般時間推理已解決。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：I'm writing a retrospective on the 1995 Japanese Grand Prix and want to highlight how far off the pace the slowest qualifier was. Could you tell me who set the slowest time in the first qualifying session (Q1) of that race? For that driver (or drivers, if two share the same slowest time, please list them all), I'd like their short reference name, nationality, birthday, and their Q1 time. To be clear, I mean the race named 'Japanese Grand Prix' in the 1995 season. Nothing else needed.

歷史SQL：
```sql
SELECT d.driverRef, d.nationality, d.dob, q.q1
FROM races r
JOIN qualifying q ON q.raceId = r.raceId
JOIN drivers d ON d.driverId = q.driverId
WHERE r.year = 1995
  AND r.name = 'Japanese Grand Prix'
  AND q.q1 IS NOT NULL
  AND q.q1 <> ''
  AND q.q1 = (
      SELECT MAX(q2.q1)
      FROM qualifying q2
      WHERE q2.raceId = r.raceId
        AND q2.q1 IS NOT NULL
        AND q2.q1 <> ''
  );
```

本輪SQL：
```sql
SELECT d.driverRef, d.nationality, d.dob, q.q1
FROM races AS r
JOIN qualifying AS q ON q.raceId = r.raceId
JOIN drivers AS d ON d.driverId = q.driverId
WHERE r.year = 1995
  AND r.name = 'Japanese Grand Prix'
  AND q.q1 IS NOT NULL
  AND TRIM(q.q1) <> ''
  AND q.q1 = (
      SELECT MIN(q2.q1)
      FROM qualifying AS q2
      WHERE q2.raceId = r.raceId
        AND q2.q1 IS NOT NULL
        AND TRIM(q2.q1) <> ''
  );
```



<a id="q254"></a>

## [Q254](failure-case-review.md#q254) · 歷史啱→本輪錯 · formula_1

候選關聯：R1／時間編碼。MAX(q1) 用文字最大，Gold 按分秒數值排名（秒CAST INTEGER 的參考政策亦需留意）。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：For qualifying at the 1995 Japanese Grand Prix, I need the nationality of the driver who set the slowest time in Q1. If two drivers tie for the slowest Q1 time, give me each of their nationalities. I only want the nationality value(s), nothing else.

歷史SQL：
```sql
WITH qualifying_times AS (
    SELECT d.nationality, q.q1
    FROM qualifying AS q
    JOIN races AS r ON r.raceId = q.raceId
    JOIN drivers AS d ON d.driverId = q.driverId
    WHERE r.year = 1995
      AND r.name = 'Japanese Grand Prix'
      AND q.q1 IS NOT NULL
)
SELECT DISTINCT nationality
FROM qualifying_times
WHERE q1 = (SELECT MIN(q1) FROM qualifying_times);
```

本輪SQL：
```sql
SELECT DISTINCT d.nationality
FROM qualifying AS q
JOIN races AS r ON r.raceId = q.raceId
JOIN drivers AS d ON d.driverId = q.driverId
WHERE r.year = 1995
  AND r.name = 'Japanese Grand Prix'
  AND q.q1 = (
      SELECT MAX(q1)
      FROM qualifying
      WHERE raceId = r.raceId
        AND q1 IS NOT NULL
        AND TRIM(q1) <> ''
  );
```



<a id="q262"></a>

## [Q262](historical-case-review.md#q262) · 歷史錯→本輪啱 · formula_1

候選關聯：R1／缺失值／時間。排除q2空字串、COUNT DISTINCT driver；改文字時間比較，在本資料EX正確不代表一般可靠。

歷史→本輪：model replies 4→4；tool attempts 4→4；SQL attempts 1→1。

Question：For qualifying at the 2017 Italian Grand Prix, how many drivers set a time in the second qualifying session (Q2) faster than 1:40.000? I just need the count of drivers as a single number.

歷史SQL：
```sql
SELECT COUNT(*) AS driver_count
FROM qualifying q
JOIN races r ON r.raceId = q.raceId
WHERE r.year = 2017
  AND r.name = 'Italian Grand Prix'
  AND q.q2 IS NOT NULL
  AND q.q2 <> '\N'
  AND (
    CAST(substr(q.q2, 1, instr(q.q2, ':') - 1) AS INTEGER) * 60
    + CAST(substr(q.q2, instr(q.q2, ':') + 1) AS REAL)
  ) < 100;
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT q.driverId) AS driver_count
FROM qualifying AS q
JOIN races AS r ON r.raceId = q.raceId
WHERE r.year = 2017
  AND r.name = 'Italian Grand Prix'
  AND q.q2 IS NOT NULL
  AND q.q2 <> ''
  AND q.q2 < '1:40.000';
```



<a id="q264"></a>

## [Q264](historical-case-review.md#q264) · 歷史錯→本輪啱 · formula_1

候選關聯：R1／缺失值。Q3排除空字串，保留全出生cohort平均。

歷史→本輪：model replies 4→5；tool attempts 4→5；SQL attempts 1→2。

Question：I'm researching the generation of drivers born in the 1980s and want to know how much final-session qualifying that generation actually did as a whole cohort. How many Q3 lap times did a driver born between 1981 and 1991 set on average? Count every driver born in that period in the average, including any who never set a Q3 lap time. Please give me the average rounded to two decimal places.

歷史SQL：
```sql
SELECT ROUND(AVG(COALESCE(q3_counts.q3_count, 0)), 2) AS avg_q3_lap_times
FROM drivers d
LEFT JOIN (
    SELECT driverId, COUNT(q3) AS q3_count
    FROM qualifying
    WHERE q3 IS NOT NULL AND q3 <> '\\N'
    GROUP BY driverId
) q3_counts ON q3_counts.driverId = d.driverId
WHERE d.dob >= '1981-01-01' AND d.dob < '1992-01-01';
```

本輪SQL：
```sql
SELECT ROUND(
    1.0 * COUNT(CASE WHEN q.q3 IS NOT NULL AND TRIM(q.q3) <> '' THEN 1 END)
    / COUNT(DISTINCT d.driverId),
    2
) AS average_q3_lap_times_per_driver
FROM drivers AS d
LEFT JOIN qualifying AS q ON q.driverId = d.driverId
WHERE d.dob >= '1981-01-01'
  AND d.dob < '1992-01-01';
```



<a id="q272"></a>

## [Q272](failure-case-review.md#q272) · 歷史啱→本輪錯 · formula_1

候選關聯：R2／量度來源。career points 應取各年終 constructorStandings 再SUM，Agent SUM constructorResults 每場積分。

歷史→本輪：model replies 4→5；tool attempts 6→7；SQL attempts 1→2。

Question：Can you rank the Italian Formula 1 constructors by career points and give me the three highest-placed ones? For each, I'd like the constructor name, their career points, and their introduction website. Career points means the total of the points the constructor finished each season with (a season being one calendar year of racing). Constructors with no points still count, ranked with 0. If there are ties, they share a rank and the next rank is skipped (so 1, 1, 3), and I'd like every constructor within the top three ranks returned.

歷史SQL：
```sql
WITH season_final AS (
    SELECT
        cs.constructorId,
        r.year,
        cs.points,
        ROW_NUMBER() OVER (
            PARTITION BY cs.constructorId, r.year
            ORDER BY r.round DESC, cs.constructorStandingsId DESC
        ) AS rn
    FROM constructorStandings AS cs
    JOIN races AS r
        ON r.raceId = cs.raceId
),
totals AS (
    SELECT
        c.constructorId,
        c.name,
        c.url,
        COALESCE(SUM(sf.points), 0) AS career_points
    FROM constructors AS c
    LEFT JOIN season_final AS sf
        ON sf.constructorId = c.constructorId
       AND sf.rn = 1
    WHERE c.nationality = 'Italian'
    GROUP BY c.constructorId, c.name, c.url
),
ranked AS (
    SELECT
        name,
        career_points,
        url,
        RANK() OVER (ORDER BY career_points DESC) AS rnk
    FROM totals
)
SELECT
    name AS constructor_name,
    career_points,
    url AS introduction_website
FROM ranked
WHERE rnk <= 3
ORDER BY rnk, constructor_name;
```

本輪SQL：
```sql
WITH constructor_points AS (
    SELECT
        c.constructorId,
        c.name,
        c.url,
        COALESCE(SUM(cr.points), 0) AS career_points
    FROM constructors AS c
    LEFT JOIN constructorResults AS cr
        ON cr.constructorId = c.constructorId
    LEFT JOIN races AS r
        ON r.raceId = cr.raceId
    WHERE c.nationality = 'Italian'
    GROUP BY c.constructorId, c.name, c.url
),
ranked AS (
    SELECT
        name,
        career_points,
        url,
        RANK() OVER (ORDER BY career_points DESC) AS career_rank
    FROM constructor_points
)
SELECT name, career_points, url
FROM ranked
WHERE career_rank <= 3
ORDER BY career_points DESC, name;
```



<a id="q279"></a>

## [Q279](failure-case-review.md#q279) · 歷史啱→本輪錯 · formula_1

候選關聯：R3／重複計數。相同driver選擇及first win正確，career COUNT(*)=8，改COUNT(DISTINCT raceId)=7即與Gold吻合。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：I'm profiling the oldest driver ever to win a Formula 1 race. Please identify the winning driver with the earliest date of birth - if two winning drivers share that birth date, use the one whose full name (forename then surname) comes first alphabetically. For that driver, return his full name (forename then surname), his nationality, the name and date of the first race he won (the earliest date; if two of his wins share that date, the one whose race name comes first alphabetically), and the total number of races he started over his entire career. A win means finishing in position 1 in a race. The career covers every race in the database, from 1950 through 2017. Return a single row.

歷史SQL：
```sql
WITH winning_drivers AS (
    SELECT DISTINCT d.driverId, d.forename, d.surname, d.dob, d.nationality
    FROM drivers AS d
    JOIN results AS res ON res.driverId = d.driverId
    WHERE res.position = 1
),
oldest_winner AS (
    SELECT *
    FROM winning_drivers
    ORDER BY dob ASC, forename ASC, surname ASC
    LIMIT 1
),
first_win AS (
    SELECT r.name, r.date
    FROM results AS res
    JOIN races AS r ON r.raceId = res.raceId
    JOIN oldest_winner AS ow ON ow.driverId = res.driverId
    WHERE res.position = 1
    ORDER BY r.date ASC, r.name ASC
    LIMIT 1
),
career_starts AS (
    SELECT COUNT(DISTINCT res.raceId) AS starts
    FROM results AS res
    JOIN oldest_winner AS ow ON ow.driverId = res.driverId
    JOIN races AS r ON r.raceId = res.raceId
    WHERE r.year BETWEEN 1950 AND 2017
)
SELECT
    ow.forename || ' ' || ow.surname AS full_name,
    ow.nationality,
    fw.name AS first_race_won,
    fw.date AS first_win_date,
    cs.starts AS total_races_started
FROM oldest_winner AS ow
CROSS JOIN first_win AS fw
CROSS JOIN career_starts AS cs;
```

本輪SQL：
```sql
WITH eligible AS (
    SELECT d.driverId, d.forename, d.surname, d.nationality, d.dob
    FROM drivers AS d
    WHERE EXISTS (
        SELECT 1
        FROM results AS r
        WHERE r.driverId = d.driverId
          AND r.position = 1
    )
),
chosen AS (
    SELECT *
    FROM eligible
    ORDER BY dob ASC, (forename || ' ' || surname) COLLATE NOCASE ASC
    LIMIT 1
),
first_win AS (
    SELECT ra.name, ra.date
    FROM results AS r
    JOIN races AS ra ON ra.raceId = r.raceId
    WHERE r.driverId = (SELECT driverId FROM chosen)
      AND r.position = 1
    ORDER BY ra.date ASC, ra.name COLLATE NOCASE ASC
    LIMIT 1
)
SELECT
    c.forename || ' ' || c.surname AS full_name,
    c.nationality,
    fw.name AS first_win_race,
    fw.date AS first_win_date,
    (
        SELECT COUNT(*)
        FROM results AS r
        JOIN races AS ra ON ra.raceId = r.raceId
        WHERE r.driverId = c.driverId
    ) AS races_started
FROM chosen AS c
CROSS JOIN first_win AS fw;
```



<a id="q286"></a>

## [Q286](failure-case-review.md#q286) · 歷史啱→本輪錯 · formula_1

候選關聯：R7／值表示。要求 runner-up gap，Gold 為 results.time 字串，Agent 回傳 milliseconds差額數值。

歷史→本輪：model replies 6→7；tool attempts 7→8；SQL attempts 3→4。

Question：Which Chinese Grand Prix edition from the 2000s (2000–2009 seasons) had the earliest scheduled local start time? Give me the season year of that edition and the runner-up's time gap to the winner (the runner-up being the driver classified second at the finish). If several editions share the earliest scheduled local start time, use the most recent one.

歷史SQL：
```sql
SELECT r.year AS season_year,
       runner_up.time AS runner_up_gap
FROM races AS r
JOIN results AS runner_up
  ON runner_up.raceId = r.raceId
 AND runner_up.positionOrder = 2
WHERE r.name = 'Chinese Grand Prix'
  AND r.year BETWEEN 2000 AND 2009
  AND r.time = (
      SELECT MIN(time)
      FROM races
      WHERE name = 'Chinese Grand Prix'
        AND year BETWEEN 2000 AND 2009
        AND time IS NOT NULL
  )
ORDER BY r.year DESC
LIMIT 1;
```

本輪SQL：
```sql
SELECT r.year AS season_year,
       runner.milliseconds - winner.milliseconds AS runner_up_gap_milliseconds
FROM races AS r
JOIN results AS winner
  ON winner.raceId = r.raceId AND winner.positionOrder = 1
JOIN results AS runner
  ON runner.raceId = r.raceId AND runner.positionOrder = 2
WHERE r.name = 'Chinese Grand Prix'
  AND r.year BETWEEN 2000 AND 2009
  AND r.time = (
      SELECT MIN(time)
      FROM races
      WHERE name = 'Chinese Grand Prix'
        AND year BETWEEN 2000 AND 2009
        AND time IS NOT NULL
  )
ORDER BY r.year DESC
LIMIT 1;
```



<a id="q290"></a>

## [Q290](historical-case-review.md#q290) · 歷史錯→本輪啱 · formula_1

候選關聯：R7／輸出形狀。earliest/latest多行改單行兩個circuit清單及gap秒數。

歷史→本輪：model replies 7→8；tool attempts 7→8；SQL attempts 4→5。

Question：Across all seasons in the database, which circuit's Grand Prix started earliest in the day, and which started latest? I'd like the circuit reference name of the earliest one, the circuit reference name of the latest one, and the gap between those two start times in seconds. Include every season, and if several circuits share the earliest start time, list them all - same for the latest.

歷史SQL：
```sql
WITH timed_races AS (
    SELECT
        c.circuitRef,
        r.time,
        CAST(substr(r.time, 1, 2) AS INTEGER) * 3600
            + CAST(substr(r.time, 4, 2) AS INTEGER) * 60
            + CAST(substr(r.time, 7, 2) AS INTEGER) AS seconds_after_midnight
    FROM races AS r
    JOIN circuits AS c ON c.circuitId = r.circuitId
    WHERE r.time IS NOT NULL
),
extremes AS (
    SELECT
        MIN(seconds_after_midnight) AS earliest_seconds,
        MAX(seconds_after_midnight) AS latest_seconds
    FROM timed_races
)
SELECT
    t.circuitRef,
    t.time AS start_time,
    CASE
        WHEN t.seconds_after_midnight = e.earliest_seconds THEN 'earliest'
        WHEN t.seconds_after_midnight = e.latest_seconds THEN 'latest'
    END AS which_extreme,
    e.latest_seconds - e.earliest_seconds AS gap_seconds
FROM timed_races AS t
CROSS JOIN extremes AS e
WHERE t.seconds_after_midnight IN (e.earliest_seconds, e.latest_seconds)
GROUP BY t.circuitRef, t.time, which_extreme, gap_seconds
ORDER BY which_extreme, t.circuitRef;
```

本輪SQL：
```sql
WITH race_times AS (
    SELECT c.circuitRef, r.time
    FROM races AS r
    JOIN circuits AS c ON c.circuitId = r.circuitId
    WHERE r.time IS NOT NULL
),
bounds AS (
    SELECT MIN(time) AS earliest_time, MAX(time) AS latest_time
    FROM race_times
)
SELECT
    (SELECT group_concat(circuitRef, ', ')
     FROM (
         SELECT DISTINCT circuitRef
         FROM race_times, bounds
         WHERE time = earliest_time
         ORDER BY circuitRef
     )) AS earliest_circuit_refs,
    (SELECT group_concat(circuitRef, ', ')
     FROM (
         SELECT DISTINCT circuitRef
         FROM race_times, bounds
         WHERE time = latest_time
         ORDER BY circuitRef
     )) AS latest_circuit_refs,
    (
        CAST(substr(latest_time, 1, 2) AS INTEGER) * 3600
        + CAST(substr(latest_time, 4, 2) AS INTEGER) * 60
        + CAST(substr(latest_time, 7, 2) AS INTEGER)
        - CAST(substr(earliest_time, 1, 2) AS INTEGER) * 3600
        - CAST(substr(earliest_time, 4, 2) AS INTEGER) * 60
        - CAST(substr(earliest_time, 7, 2) AS INTEGER)
    ) AS gap_seconds
FROM bounds;
```



<a id="q293"></a>

## [Q293](historical-case-review.md#q293) · 歷史錯→本輪啱 · formula_1

候選關聯：R3／實體粒度。withdrawals由COUNT(*)改COUNT DISTINCT driverId。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：For my retrospective on the 1962 British Grand Prix – the race named 'British Grand Prix' in the 1962 season – how many drivers withdrew from that race? I just need a single whole number.

歷史SQL：
```sql
SELECT COUNT(*) AS withdrew_count
FROM results r
JOIN races ra ON r.raceId = ra.raceId
JOIN status s ON r.statusId = s.statusId
WHERE ra.year = 1962
  AND ra.name = 'British Grand Prix'
  AND s.status = 'Withdrew';
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT res.driverId) AS withdrawn_drivers
FROM races r
JOIN results res ON res.raceId = r.raceId
JOIN status s ON s.statusId = res.statusId
WHERE r.year = 1962
  AND r.name = 'British Grand Prix'
  AND s.status = 'Withdrew';
```



<a id="q294"></a>

## [Q294](historical-case-review.md#q294) · 歷史錯→本輪啱 · formula_1

候選關聯：R2／分類定義。finisher由status Finished/+Lap改position非空且以driver去重。

歷史→本輪：model replies 6→6；tool attempts 7→7；SQL attempts 3→3。

Question：For the 1957 British Grand Prix, what percentage of the drivers who took part in the race were classified finishers, rounded to two decimals? By classified finisher I mean a driver whose race record shows them finishing the race, whether on the lead lap or one or more laps behind the winner. I just need the one percentage figure.

歷史SQL：
```sql
SELECT ROUND(
    100.0 * SUM(CASE
        WHEN s.status = 'Finished' OR s.status LIKE '+% Lap%' THEN 1
        ELSE 0
    END) / COUNT(*),
    2
) AS percentage
FROM races AS r
JOIN results AS res ON res.raceId = r.raceId
JOIN status AS s ON s.statusId = res.statusId
WHERE r.year = 1957
  AND r.name = 'British Grand Prix';
```

本輪SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN r.position IS NOT NULL THEN r.driverId END)
    / COUNT(DISTINCT r.driverId),
    2
) AS percentage
FROM results r
JOIN races ra ON ra.raceId = r.raceId
WHERE ra.year = 1957
  AND ra.name = 'British Grand Prix';
```



<a id="q295"></a>

## [Q295](failure-case-review.md#q295) · 歷史啱→本輪錯 · student_club

候選關聯：R3／分組粒度。按 link_to_budget 分組計均值，Gold 經 budget.link_to_event 按活動分組。

歷史→本輪：model replies 6→5；tool attempts 7→6；SQL attempts 2→2。

Question：What was Elijah Allen's mean total expense per event for expenses dated in September or October? Round to two decimals.

歷史SQL：
```sql
SELECT ROUND(AVG(event_total), 2) AS mean_total_expense_per_event
FROM (
    SELECT b.link_to_event, SUM(x.cost) AS event_total
    FROM expense AS x
    JOIN member AS m ON m.member_id = x.link_to_member
    JOIN budget AS b ON b.budget_id = x.link_to_budget
    WHERE m.first_name = 'Elijah'
      AND m.last_name = 'Allen'
      AND strftime('%m', x.expense_date) IN ('09', '10')
    GROUP BY b.link_to_event
);
```

本輪SQL：
```sql
SELECT ROUND(AVG(event_total), 2) AS mean_total_expense_per_event
FROM (
    SELECT e.link_to_budget, SUM(e.cost) AS event_total
    FROM expense AS e
    JOIN member AS m ON m.member_id = e.link_to_member
    WHERE m.first_name = 'Elijah'
      AND m.last_name = 'Allen'
      AND strftime('%m', e.expense_date) IN ('09', '10')
    GROUP BY e.link_to_budget
);
```



<a id="q300"></a>

## [Q300](historical-case-review.md#q300) · 歷史錯→本輪啱 · student_club

候選關聯：R7／輸出形狀。合併姓名一欄改first_name,last_name兩欄。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：List the name of students that have attended more than 7 events.

歷史SQL：
```sql
SELECT m.first_name || ' ' || m.last_name AS name
FROM member AS m
JOIN attendance AS a ON a.link_to_member = m.member_id
GROUP BY m.member_id
HAVING COUNT(DISTINCT a.link_to_event) > 7;
```

本輪SQL：
```sql
SELECT m.first_name, m.last_name
FROM member AS m
JOIN attendance AS a
  ON a.link_to_member = m.member_id
GROUP BY m.member_id, m.first_name, m.last_name
HAVING COUNT(DISTINCT a.link_to_event) > 7;
```



<a id="q306"></a>

## [Q306](failure-case-review.md#q306) · 歷史啱→本輪錯 · student_club

候選關聯：R4／條件範圍。先找 cost>50 member 後納其所有budget lines，Gold 只納該member cost>50購買連結的budget lines。

歷史→本輪：model replies 5→5；tool attempts 6→7；SQL attempts 2→3。

Question：For the mid-year budget review: I need to see, for each member who had to spend more than fifty dollars on an expense, how much room was still left in the budget lines those purchases were charged against. Please give me, per member, their first name, last name, and the total amount left across those budget lines in dollars rounded to two decimals. Order the results from the largest total down to the smallest; if two members have the same total, list them alphabetically by last name and then first name. The totals should cover all expenses on record, and if a budget line ended up overdrawn, its negative remaining amount should count toward the total.

歷史SQL：
```sql
WITH qualifying_lines AS (
    SELECT DISTINCT link_to_member, link_to_budget
    FROM expense
    WHERE cost > 50
),
line_totals AS (
    SELECT
        q.link_to_member,
        q.link_to_budget,
        b.amount - COALESCE(SUM(all_expenses.cost), 0) AS remaining
    FROM qualifying_lines q
    JOIN budget b ON b.budget_id = q.link_to_budget
    LEFT JOIN expense all_expenses ON all_expenses.link_to_budget = q.link_to_budget
    GROUP BY q.link_to_member, q.link_to_budget, b.amount
)
SELECT
    m.first_name,
    m.last_name,
    ROUND(SUM(l.remaining), 2) AS total_remaining
FROM line_totals l
JOIN member m ON m.member_id = l.link_to_member
GROUP BY m.member_id, m.first_name, m.last_name
ORDER BY total_remaining DESC, m.last_name ASC, m.first_name ASC;
```

本輪SQL：
```sql
WITH qualifying_members AS (
    SELECT DISTINCT link_to_member
    FROM expense
    WHERE cost > 50
),
member_budget_lines AS (
    SELECT DISTINCT e.link_to_member, e.link_to_budget
    FROM expense e
    JOIN qualifying_members q ON q.link_to_member = e.link_to_member
    WHERE e.link_to_budget IS NOT NULL
)
SELECT
    m.first_name,
    m.last_name,
    ROUND(SUM(COALESCE(b.amount, 0) - COALESCE(b.spent, 0)), 2) AS total_remaining
FROM qualifying_members q
JOIN member m ON m.member_id = q.link_to_member
JOIN member_budget_lines mb ON mb.link_to_member = q.link_to_member
JOIN budget b ON b.budget_id = mb.link_to_budget
GROUP BY m.member_id, m.first_name, m.last_name
ORDER BY total_remaining DESC, m.last_name ASC, m.first_name ASC;
```



<a id="q307"></a>

## [Q307](failure-case-review.md#q307) · 歷史啱→本輪錯 · student_club

候選關聯：R3／重複計數。attendance join 可重複同一member dues，Gold 用 IN 半連接。

歷史→本輪：model replies 6→6；tool attempts 8→7；SQL attempts 3→2。

Question：I'm putting together our year-end budget summary. How much did we collect in membership dues, in total dollars, from the students who attended the Football game? Membership dues are the payments recorded under the source 'Dues'.

歷史SQL：
```sql
SELECT SUM(i.amount) AS total_dues
FROM (
    SELECT DISTINCT a.link_to_member
    FROM attendance AS a
    JOIN event AS e ON e.event_id = a.link_to_event
    WHERE e.event_name LIKE '%Football%'
) AS attendees
JOIN income AS i ON i.link_to_member = attendees.link_to_member
WHERE i.source = 'Dues';
```

本輪SQL：
```sql
SELECT SUM(i.amount)
FROM attendance AS a
JOIN event AS e ON e.event_id = a.link_to_event
JOIN income AS i ON i.link_to_member = a.link_to_member
WHERE e.event_name = 'Football game'
  AND i.source = 'Dues';
```



<a id="q309"></a>

## [Q309](historical-case-review.md#q309) · 歷史錯→本輪啱 · student_club

候選關聯：R1／類別值。budget category由advertising改advertisement。

歷史→本輪：model replies 5→6；tool attempts 6→7；SQL attempts 2→3。

Question：For our end-of-year report, I need one figure: the average number of members who attended each event that carried a budget line for advertising, covering every such event across the club's records regardless of when it took place. Please give it as a single number rounded to two decimal places.

歷史SQL：
```sql
WITH advertising_events AS (
    SELECT DISTINCT link_to_event
    FROM budget
    WHERE LOWER(category) = 'advertising'
      AND link_to_event IS NOT NULL
),
attendance_counts AS (
    SELECT ev.link_to_event, COUNT(a.link_to_member) AS member_count
    FROM advertising_events ev
    LEFT JOIN attendance a ON a.link_to_event = ev.link_to_event
    GROUP BY ev.link_to_event
)
SELECT ROUND(AVG(member_count), 2) AS average_members_per_event
FROM attendance_counts;
```

本輪SQL：
```sql
SELECT ROUND(AVG(attendee_count), 2)
FROM (
    SELECT e.event_id, COUNT(a.link_to_member) AS attendee_count
    FROM event AS e
    JOIN (
        SELECT DISTINCT link_to_event
        FROM budget
        WHERE LOWER(category) = 'advertisement'
    ) AS b ON b.link_to_event = e.event_id
    LEFT JOIN attendance AS a ON a.link_to_event = e.event_id
    GROUP BY e.event_id
);
```



<a id="q313"></a>

## [Q313](failure-case-review.md#q313) · 歷史啱→本輪錯 · student_club

候選關聯：R7／輸出形狀。Agent officer/other 群組兩行，Gold 單行兩個平均欄。

歷史→本輪：model replies 6→8；tool attempts 5→9；SQL attempts 1→5。

Question：Our officer team wants to settle a debate about whether we pull more weight than the rest of the club, so we need the attendance numbers before the next meeting. Could you tell us two things: the average number of events attended per officer, and the average number of events attended per other student, each rounded to two decimal places? To be clear on who counts where: officers are the members holding the position of President, Vice President, Secretary, or Treasurer, and everyone else in the club counts as an other student. Each average should cover every member of its group, and include every event in the club's records - there's no date cutoff.

歷史SQL：
```sql
WITH member_attendance AS (
    SELECT
        CASE
            WHEN position IN ('President', 'Vice President', 'Secretary', 'Treasurer')
                THEN 'officer'
            ELSE 'other'
        END AS member_group,
        COUNT(DISTINCT attendance.link_to_event) AS events_attended
    FROM member
    LEFT JOIN attendance
        ON attendance.link_to_member = member.member_id
    GROUP BY member.member_id
)
SELECT
    ROUND(AVG(CASE WHEN member_group = 'officer' THEN events_attended END), 2) AS average_events_per_officer,
    ROUND(AVG(CASE WHEN member_group = 'other' THEN events_attended END), 2) AS average_events_per_other_student
FROM member_attendance;
```

本輪SQL：
```sql
SELECT
  CASE
    WHEN position IN ('President', 'Vice President', 'Secretary', 'Treasurer') THEN 'officer'
    ELSE 'other student'
  END AS member_group,
  ROUND(AVG(event_count), 2) AS average_events_attended
FROM (
  SELECT
    m.member_id,
    m.position,
    COUNT(a.link_to_event) AS event_count
  FROM member AS m
  LEFT JOIN attendance AS a
    ON a.link_to_member = m.member_id
  GROUP BY m.member_id, m.position
)
GROUP BY
  CASE
    WHEN position IN ('President', 'Vice President', 'Secretary', 'Treasurer') THEN 'officer'
    ELSE 'other student'
  END;
```



<a id="q314"></a>

## [Q314](failure-case-review.md#q314) · 歷史啱→本輪錯 · student_club

候選關聯：R6／活動關係範圍。Agent 只拆負remaining budget line的購買，Gold 先找over-budget events再納其所有budget lines。

歷史→本輪：model replies 7→8；tool attempts 8→11；SQL attempts 4→7。

Question：I'm finalizing the semester wrap-up report and need one number: how many different kinds of things the club bought for events that went over budget this semester. A few things to keep in mind: an event counts as over budget if, in at least one of its budgeted categories, we spent more than we budgeted for that category - the budgeted amount minus what was actually spent came out below zero. Also, a single purchase can cover several kinds of things at once, and the purchase description lists what it bought, so make sure each kind is counted. The answer should cover the whole semester shown in the records, and I just need the single integer count, nothing else.

歷史SQL：
```sql
WITH RECURSIVE over_events AS (
    SELECT DISTINCT link_to_event
    FROM budget
    WHERE remaining < 0
),
item_names(item, rest) AS (
    SELECT
        lower(trim(substr(x.expense_description || ',', 1, instr(x.expense_description || ',', ',') - 1))),
        substr(x.expense_description || ',', instr(x.expense_description || ',', ',') + 1)
    FROM expense AS x
    JOIN budget AS b ON x.link_to_budget = b.budget_id
    JOIN over_events AS oe ON oe.link_to_event = b.link_to_event

    UNION ALL

    SELECT
        lower(trim(substr(rest, 1, instr(rest, ',') - 1))),
        substr(rest, instr(rest, ',') + 1)
    FROM item_names
    WHERE rest <> ''
)
SELECT COUNT(DISTINCT item)
FROM item_names
WHERE item <> '';
```

本輪SQL：
```sql
WITH RECURSIVE item_kinds(budget_id, rest, kind) AS (
    SELECT b.budget_id, x.expense_description || ',', ''
    FROM budget AS b
    JOIN expense AS x ON x.link_to_budget = b.budget_id
    WHERE b.remaining < 0

    UNION ALL

    SELECT budget_id,
           substr(rest, instr(rest, ',') + 1),
           trim(substr(rest, 1, instr(rest, ',') - 1))
    FROM item_kinds
    WHERE rest <> ''
)
SELECT COUNT(DISTINCT lower(kind))
FROM item_kinds
WHERE kind <> '';
```



<a id="q320"></a>

## [Q320](historical-case-review.md#q320) · 歷史錯→本輪啱 · student_club

候選關聯：R3／實體粒度。COUNT member rows改COUNT DISTINCT major_id。

歷史→本輪：model replies 4→4；tool attempts 4→4；SQL attempts 1→1。

Question：I'm putting together a recruitment report for the colleges and want to know which parts of the university our club's membership actually draws from. For every person on the roster-regardless of their position in the club-look at their major, and the college that houses the department offering that major. Which college or colleges do the most majors on our roster come from, and how many majors is that? If there's a tie at the top, give me every college tied at that count. Please list the colleges in alphabetical order by college name, and return just each college's name and its number of majors.

歷史SQL：
```sql
WITH college_counts AS (
  SELECT ma.college, COUNT(*) AS major_count
  FROM "member" AS me
  JOIN major AS ma ON me.link_to_major = ma.major_id
  GROUP BY ma.college
),
ranked AS (
  SELECT college, major_count, MAX(major_count) OVER () AS max_count
  FROM college_counts
)
SELECT college, major_count
FROM ranked
WHERE major_count = max_count
ORDER BY college;
```

本輪SQL：
```sql
WITH college_counts AS (
    SELECT ma.college, COUNT(DISTINCT ma.major_id) AS number_of_majors
    FROM member AS m
    JOIN major AS ma ON ma.major_id = m.link_to_major
    GROUP BY ma.college
)
SELECT college, number_of_majors
FROM college_counts
WHERE number_of_majors = (SELECT MAX(number_of_majors) FROM college_counts)
ORDER BY college;
```



<a id="q325"></a>

## [Q325](historical-case-review.md#q325) · 歷史錯→本輪啱 · student_club

候選關聯：R8／SQLite方言。移除SQLite不支援的 >= ALL，改CTE MAX等值。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：For our year-end review, I want to know which event formats bring in the most people. Looking at our whole club year (every event from September 2019 through May 2020), which event type was attended by the most members, and how many members attended that type's events? If several event types tie for the most, list every one of them. Just give me the event type and the number of members for it - nothing else.

歷史SQL：
```sql
SELECT e.type AS event_type, COUNT(DISTINCT a.link_to_member) AS member_count
FROM event AS e
JOIN attendance AS a ON a.link_to_event = e.event_id
WHERE date(e.event_date) BETWEEN date('2019-09-01') AND date('2020-05-31')
GROUP BY e.type
HAVING COUNT(DISTINCT a.link_to_member) >= ALL (
    SELECT COUNT(DISTINCT a2.link_to_member)
    FROM event AS e2
    JOIN attendance AS a2 ON a2.link_to_event = e2.event_id
    WHERE date(e2.event_date) BETWEEN date('2019-09-01') AND date('2020-05-31')
    GROUP BY e2.type
);
```

本輪SQL：
```sql
WITH type_counts AS (
    SELECT
        e.type AS event_type,
        COUNT(DISTINCT a.link_to_member) AS member_count
    FROM event AS e
    JOIN attendance AS a
        ON a.link_to_event = e.event_id
    WHERE date(e.event_date) >= '2019-09-01'
      AND date(e.event_date) < '2020-06-01'
    GROUP BY e.type
)
SELECT event_type, member_count
FROM type_counts
WHERE member_count = (SELECT MAX(member_count) FROM type_counts);
```



<a id="q327"></a>

## [Q327](historical-case-review.md#q327) · 歷史錯→本輪啱 · student_club

候選關聯：R8／拆解實作。json_each及未定義item改recursive CTE拆逗號物品。

歷史→本輪：model replies 6→8；tool attempts 9→12；SQL attempts 3→7。

Question：I'm wrapping up the October Meeting and need the final numbers broken down by what we actually bought, not just by budget category. For every item bought with approved money for the October Meeting, can you give me: the item's name, the budget category of the purchase that included the item, and the total cost in dollars of the approved October Meeting purchases that included the item? Only expenses marked as approved count - an expense without an approval mark doesn't. If an item was included in approved purchases recorded under more than one budget category, give me one row per category. Costs should be plain sums in US dollars with no rounding, and please sort the list by category and then by item name.

歷史SQL：
```sql
WITH approved_purchases AS (
    SELECT
        b.category,
        e.cost,
        e.expense_description
    FROM expense AS e
    JOIN budget AS b
        ON e.link_to_budget = b.budget_id
    JOIN event AS ev
        ON b.link_to_event = ev.event_id
    WHERE ev.event_name = 'October Meeting'
      AND e.approved = 'true'
),
purchase_items AS (
    SELECT
        category,
        cost,
        TRIM(item) AS item
    FROM approved_purchases,
         json_each(
             '["' || REPLACE(expense_description, ', ', '","') || '"]'
         )
)
SELECT
    item,
    category,
    SUM(cost) AS total_cost
FROM purchase_items
GROUP BY category, item
ORDER BY category, item;
```

本輪SQL：
```sql
WITH RECURSIVE items(expense_id, category, cost, remaining, item) AS (
    SELECT e.expense_id,
           b.category,
           e.cost,
           e.expense_description || ',',
           ''
    FROM expense AS e
    JOIN budget AS b ON e.link_to_budget = b.budget_id
    JOIN event AS v ON b.link_to_event = v.event_id
    WHERE v.event_name = 'October Meeting'
      AND e.approved = 'true'

    UNION ALL

    SELECT expense_id,
           category,
           cost,
           substr(remaining, instr(remaining, ',') + 1),
           trim(substr(remaining, 1, instr(remaining, ',') - 1))
    FROM items
    WHERE remaining <> ''
)
SELECT item AS item_name,
       category,
       SUM(cost) AS total_cost
FROM items
WHERE item <> ''
GROUP BY category, item
ORDER BY category, item_name;
```



<a id="q328"></a>

## [Q328](failure-case-review.md#q328) · 歷史啱→本輪錯 · student_club

候選關聯：R1／NULL與零。無budget時 SUM 子查詢回傳 NULL，Gold COALESCE為0；attendance DISTINCT改變計數政策。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：For every event in the club's records, can you give me the event name, event date, total amount budgeted for the event, and the number of members who attended it? Please sort the list by event name, then by event date, both in ascending order.

歷史SQL：
```sql
SELECT
    e.event_name,
    e.event_date,
    COALESCE(SUM(DISTINCT b.amount), 0) AS total_budgeted,
    COUNT(DISTINCT a.link_to_member) AS members_attended
FROM event AS e
LEFT JOIN budget AS b
    ON b.link_to_event = e.event_id
LEFT JOIN attendance AS a
    ON a.link_to_event = e.event_id
GROUP BY e.event_id, e.event_name, e.event_date
ORDER BY e.event_name ASC, e.event_date ASC;
```

本輪SQL：
```sql
SELECT
    e.event_name,
    e.event_date,
    (SELECT SUM(b.amount)
     FROM budget AS b
     WHERE b.link_to_event = e.event_id) AS total_budgeted,
    (SELECT COUNT(DISTINCT a.link_to_member)
     FROM attendance AS a
     WHERE a.link_to_event = e.event_id) AS members_attended
FROM event AS e
ORDER BY e.event_name ASC, e.event_date ASC;
```



<a id="q331"></a>

## [Q331](historical-case-review.md#q331) · 歷史錯→本輪啱 · student_club

候選關聯：R1／類別值。department由Political Science改完整Political Science Department。

歷史→本輪：model replies 4→7；tool attempts 4→7；SQL attempts 1→4。

Question：For our department report, I need to know how many different fields of study our club members from the Political Science Department represent. Only count members of the Political Science Department - members from other departments don't count. Just give me the number of different majors studied by those members.

歷史SQL：
```sql
SELECT COUNT(DISTINCT major.major_name) AS different_majors
FROM member
JOIN major ON member.link_to_major = major.major_id
WHERE major.department = 'Political Science';
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT m.major_name) AS different_majors
FROM member AS mem
JOIN major AS m ON mem.link_to_major = m.major_id
WHERE m.department = 'Political Science Department';
```



<a id="q332"></a>

## [Q332](historical-case-review.md#q332) · 歷史錯→本輪啱 · superhero

候選關聯：R4／取消附加篩選。取消Good alignment限制，並排No Colour佔位值。

歷史→本輪：model replies 8→5；tool attempts 10→10；SQL attempts 3→4。

Question：Among Marvel Comics superheroes with a known eye colour, rank the eye colours by number of superheroes. Give each colour, its hero count, and its rank, most common first; break display-order ties alphabetically.

歷史SQL：
```sql
SELECT c.colour,
       COUNT(*) AS hero_count,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS rank
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
JOIN colour AS c ON c.id = s.eye_colour_id
JOIN alignment AS a ON a.id = s.alignment_id
WHERE p.publisher_name = 'Marvel Comics'
  AND a.alignment = 'Good'
  AND s.eye_colour_id IS NOT NULL
GROUP BY c.colour
ORDER BY hero_count DESC, c.colour ASC;
```

本輪SQL：
```sql
SELECT
    c.colour,
    COUNT(*) AS hero_count,
    RANK() OVER (ORDER BY COUNT(*) DESC) AS rank
FROM superhero AS s
JOIN publisher AS p
    ON p.id = s.publisher_id
JOIN colour AS c
    ON c.id = s.eye_colour_id
WHERE p.publisher_name = 'Marvel Comics'
  AND c.colour IS NOT NULL
  AND c.colour <> ''
  AND c.colour <> 'No Colour'
GROUP BY c.id, c.colour
ORDER BY hero_count DESC, c.colour ASC;
```



<a id="q335"></a>

## [Q335](historical-case-review.md#q335) · 歷史錯→本輪啱 · superhero

候選關聯：R7／輸出契約。取消額外hero_count欄，回傳publisher及difference。

歷史→本輪：model replies 4→4；tool attempts 4→4；SQL attempts 1→1。

Question：Between Marvel Comics and DC Comics, which publisher has more superheroes, and by how many?

歷史SQL：
```sql
SELECT p.publisher_name AS publisher,
       COUNT(*) AS superhero_count,
       (SELECT COUNT(*) FROM superhero s2 JOIN publisher p2 ON p2.id = s2.publisher_id WHERE p2.publisher_name = 'Marvel Comics')
       - (SELECT COUNT(*) FROM superhero s3 JOIN publisher p3 ON p3.id = s3.publisher_id WHERE p3.publisher_name = 'DC Comics') AS difference
FROM superhero s
JOIN publisher p ON p.id = s.publisher_id
WHERE p.publisher_name IN ('Marvel Comics', 'DC Comics')
GROUP BY p.publisher_name
ORDER BY superhero_count DESC
LIMIT 1;
```

本輪SQL：
```sql
SELECT
    (SELECT publisher_name
     FROM publisher
     WHERE publisher_name IN ('Marvel Comics', 'DC Comics')
     ORDER BY (
         SELECT COUNT(*)
         FROM superhero
         WHERE publisher_id = publisher.id
     ) DESC
     LIMIT 1) AS publisher,
    ABS(
        (SELECT COUNT(*)
         FROM superhero
         WHERE publisher_id = (SELECT id FROM publisher WHERE publisher_name = 'Marvel Comics'))
        -
        (SELECT COUNT(*)
         FROM superhero
         WHERE publisher_id = (SELECT id FROM publisher WHERE publisher_name = 'DC Comics'))
    ) AS difference;
```



<a id="q339"></a>

## [Q339](historical-case-review.md#q339) · 歷史錯→本輪啱 · superhero

候選關聯：R1／佔位值。三色相同條件補排No Colour。

歷史→本輪：model replies 4→6；tool attempts 7→10；SQL attempts 1→4。

Question：List superheroes whose known eye, hair and skin colours are all the same, along with any recorded publisher name.

歷史SQL：
```sql
SELECT s.superhero_name, p.publisher_name
FROM superhero AS s
LEFT JOIN publisher AS p
    ON p.id = s.publisher_id
WHERE s.eye_colour_id IS NOT NULL
  AND s.hair_colour_id IS NOT NULL
  AND s.skin_colour_id IS NOT NULL
  AND s.eye_colour_id = s.hair_colour_id
  AND s.hair_colour_id = s.skin_colour_id;
```

本輪SQL：
```sql
SELECT s.superhero_name, p.publisher_name
FROM superhero AS s
LEFT JOIN publisher AS p ON p.id = s.publisher_id
JOIN colour AS eye ON eye.id = s.eye_colour_id
JOIN colour AS hair ON hair.id = s.hair_colour_id
JOIN colour AS skin ON skin.id = s.skin_colour_id
WHERE eye.colour = hair.colour
  AND hair.colour = skin.colour
  AND eye.colour <> 'No Colour';
```



<a id="q347"></a>

## [Q347](historical-case-review.md#q347) · 歷史錯→本輪啱 · superhero

候選關聯：R1／佔位值。full_name補排'-'。

歷史→本輪：model replies 4→7；tool attempts 6→9；SQL attempts 1→4。

Question：I'm building a fact box on Marvel heroes' civilian identities. Among Marvel Comics superheroes whose full name (their civilian identity, like 'Richard Milhouse Jones') is known, which superpower is the most common, and how many of those heroes have it? If several superpowers tie for most common, list all of them with their counts. Just give me the superpower name(s) and the counts.

歷史SQL：
```sql
SELECT p.power_name, COUNT(DISTINCT s.id) AS hero_count
FROM superhero AS s
JOIN publisher AS pub ON pub.id = s.publisher_id
JOIN hero_power AS hp ON hp.hero_id = s.id
JOIN superpower AS p ON p.id = hp.power_id
WHERE pub.publisher_name = 'Marvel Comics'
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> ''
GROUP BY p.id, p.power_name
HAVING COUNT(DISTINCT s.id) = (
  SELECT MAX(power_count)
  FROM (
    SELECT COUNT(DISTINCT s2.id) AS power_count
    FROM superhero AS s2
    JOIN publisher AS pub2 ON pub2.id = s2.publisher_id
    JOIN hero_power AS hp2 ON hp2.hero_id = s2.id
    JOIN superpower AS p2 ON p2.id = hp2.power_id
    WHERE pub2.publisher_name = 'Marvel Comics'
      AND s2.full_name IS NOT NULL
      AND TRIM(s2.full_name) <> ''
    GROUP BY p2.id
  )
)
ORDER BY p.power_name;
```

本輪SQL：
```sql
SELECT sp.power_name, COUNT(DISTINCT s.id) AS hero_count
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
JOIN hero_power AS hp ON hp.hero_id = s.id
JOIN superpower AS sp ON sp.id = hp.power_id
WHERE p.publisher_name = 'Marvel Comics'
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> ''
  AND TRIM(s.full_name) <> '-'
GROUP BY sp.id, sp.power_name
HAVING COUNT(DISTINCT s.id) = (
    SELECT MAX(power_count)
    FROM (
        SELECT COUNT(DISTINCT s2.id) AS power_count
        FROM superhero AS s2
        JOIN publisher AS p2 ON p2.id = s2.publisher_id
        JOIN hero_power AS hp2 ON hp2.hero_id = s2.id
        WHERE p2.publisher_name = 'Marvel Comics'
          AND s2.full_name IS NOT NULL
          AND TRIM(s2.full_name) <> ''
          AND TRIM(s2.full_name) <> '-'
        GROUP BY hp2.power_id
    )
);
```



<a id="q354"></a>

## [Q354](historical-case-review.md#q354) · 歷史錯→本輪啱 · superhero

候選關聯：R6／傳遞關係。由僅cryokinesis holders擴為與holders共享任何power的heroes。

歷史→本輪：model replies 4→5；tool attempts 5→6；SQL attempts 1→2。

Question：For my cryokinesis page, I want to know how broad the power portfolios are around ice-powered heroes. Consider all heroes who share at least one superpower with a cryokinesis holder - including the cryokinesis holders themselves, since they share cryokinesis with each other. What is the average number of superpowers these heroes have, rounded to one decimal place? Please send back just that single number.

歷史SQL：
```sql
SELECT ROUND(AVG(power_count), 1) AS average_superpowers
FROM (
    SELECT hp.hero_id, COUNT(DISTINCT hp.power_id) AS power_count
    FROM hero_power hp
    WHERE EXISTS (
        SELECT 1
        FROM hero_power cryo_hp
        JOIN superpower sp ON sp.id = cryo_hp.power_id
        WHERE LOWER(sp.power_name) = 'cryokinesis'
          AND EXISTS (
              SELECT 1
              FROM hero_power shared_hp
              WHERE shared_hp.hero_id = hp.hero_id
                AND shared_hp.power_id = cryo_hp.power_id
          )
    )
    GROUP BY hp.hero_id
);
```

本輪SQL：
```sql
WITH cryo_holders AS (
  SELECT DISTINCT hero_id
  FROM hero_power
  WHERE power_id = 19
),
related_heroes AS (
  SELECT DISTINCT hp.hero_id
  FROM hero_power AS hp
  JOIN hero_power AS holder_power
    ON holder_power.power_id = hp.power_id
  JOIN cryo_holders AS ch
    ON ch.hero_id = holder_power.hero_id
),
hero_counts AS (
  SELECT rh.hero_id, COUNT(DISTINCT hp.power_id) AS power_count
  FROM related_heroes AS rh
  JOIN hero_power AS hp
    ON hp.hero_id = rh.hero_id
  GROUP BY rh.hero_id
)
SELECT ROUND(AVG(power_count), 1)
FROM hero_counts;
```



<a id="q359"></a>

## [Q359](historical-case-review.md#q359) · 歷史錯→本輪啱 · superhero

候選關聯：R1／NULL集合語義。非DC集合改納publisher_id=NULL。

歷史→本輪：model replies 4→4；tool attempts 5→5；SQL attempts 1→1。

Question：For a licensing survey of non-DC heroic characters, I need a single total count of superheroes whose alignment is Good and who are not published by DC Comics. Just that one number, please.

歷史SQL：
```sql
SELECT COUNT(*) AS superhero_count
FROM superhero AS s
JOIN alignment AS a ON s.alignment_id = a.id
WHERE a.alignment = 'Good'
  AND s.publisher_id NOT IN (
      SELECT id
      FROM publisher
      WHERE publisher_name = 'DC Comics'
  );
```

本輪SQL：
```sql
SELECT COUNT(*) AS total_count
FROM superhero AS s
JOIN alignment AS a ON a.id = s.alignment_id
WHERE a.alignment = 'Good'
  AND (s.publisher_id IS NULL OR NOT EXISTS (
    SELECT 1
    FROM publisher AS p
    WHERE p.id = s.publisher_id
      AND p.publisher_name = 'DC Comics'
  ));
```



<a id="q367"></a>

## [Q367](historical-case-review.md#q367) · 歷史錯→本輪啱 · superhero

候選關聯：R1／零值語義。height/weight用NULLIF(value,0)排未量度0。

歷史→本輪：model replies 5→10；tool attempts 5→10；SQL attempts 2→5。

Question：I'm profiling publisher rosters and now want to look at the physical build of George Lucas's heroes. What is the average height of the heroes he created, in centimetres, and their average weight, in kilograms? Please round each average to one decimal place, and only include heroes whose height (for the height average) or weight (for the weight average) is actually known.

歷史SQL：
```sql
SELECT
  (SELECT ROUND(AVG(height_cm), 1)
   FROM superhero s
   JOIN publisher p ON s.publisher_id = p.id
   WHERE p.publisher_name = 'George Lucas'
     AND s.height_cm IS NOT NULL) AS avg_height_cm,
  (SELECT ROUND(AVG(weight_kg), 1)
   FROM superhero s
   JOIN publisher p ON s.publisher_id = p.id
   WHERE p.publisher_name = 'George Lucas'
     AND s.weight_kg IS NOT NULL) AS avg_weight_kg;
```

本輪SQL：
```sql
SELECT
    ROUND(AVG(NULLIF(s.height_cm, 0)), 1) AS average_height_cm,
    ROUND(AVG(NULLIF(s.weight_kg, 0)), 1) AS average_weight_kg
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
WHERE p.publisher_name = 'George Lucas';
```



<a id="q375"></a>

## [Q375](historical-case-review.md#q375) · 歷史錯→本輪啱 · superhero

候選關聯：R1／佔位值。full_name補排'-'。

歷史→本輪：model replies 4→6；tool attempts 4→6；SQL attempts 1→3。

Question：I'm auditing identity info on our hero profile pages. How many neutral-alignment heroes have a known full name? Just give me the count.

歷史SQL：
```sql
SELECT COUNT(*) AS count
FROM superhero AS s
JOIN alignment AS a ON s.alignment_id = a.id
WHERE LOWER(a.alignment) = 'neutral'
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> '';
```

本輪SQL：
```sql
SELECT COUNT(*) AS count
FROM superhero
JOIN alignment ON alignment.id = superhero.alignment_id
WHERE alignment.alignment = 'Neutral'
  AND full_name IS NOT NULL
  AND TRIM(full_name) <> ''
  AND TRIM(full_name) <> '-';
```



<a id="q378"></a>

## [Q378](historical-case-review.md#q378) · 歷史錯→本輪啱 · superhero

候選關聯：R1／佔位值。known full_name補排'-'。

歷史→本輪：model replies 5→6；tool attempts 6→10；SQL attempts 2→5。

Question：I'm preparing a report on Marvel's roster and want to gauge how heroic their catalogued heroes are. Among Marvel Comics superheroes whose civilian full name is documented, what percentage are good? Please give me just that single percentage, rounded to two decimal places. Note: the percentage should be taken over all Marvel Comics superheroes with a known full name - those whose moral alignment is unknown still count toward the total, just not as good.

歷史SQL：
```sql
SELECT ROUND(100.0 * SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) / COUNT(*), 2) AS percentage
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
LEFT JOIN alignment AS a ON a.id = s.alignment_id
WHERE p.publisher_name = 'Marvel Comics'
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> '';
```

本輪SQL：
```sql
SELECT ROUND(
    100.0 * SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) / COUNT(*),
    2
)
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
LEFT JOIN alignment AS a ON a.id = s.alignment_id
WHERE p.publisher_name = 'Marvel Comics'
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> ''
  AND TRIM(s.full_name) <> '-';
```



<a id="q387"></a>

## [Q387](failure-case-review.md#q387) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R5／年齡邊界。older than55 改為生日<=1970-10-09（56歲），Gold birthday<1971-10-09，漏掉介於55與56歲的人。

歷史→本輪：model replies 5→6；tool attempts 6→7；SQL attempts 2→3。

Question：Among patients older than 55 on 2026-10-09 who have at least one abnormal PT result, what percentage are female? Round to two decimals.

歷史SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN p.SEX = 'F' THEN p.ID END)
    / COUNT(DISTINCT p.ID),
    2
) AS female_percentage
FROM Patient AS p
JOIN Laboratory AS l ON l.ID = p.ID
WHERE date(p.Birthday) < date('2026-10-09', '-55 years')
  AND date(l.Date) <= '2026-10-09'
  AND l.PT >= 14;
```

本輪SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN p.SEX = 'F' THEN p.ID END)
    / COUNT(DISTINCT p.ID),
    2
) AS female_percentage
FROM Patient AS p
WHERE p.Birthday <= date('2026-10-09', '-56 years')
  AND EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND l.PT >= 14
  );
```



<a id="q389"></a>

## [Q389](historical-case-review.md#q389) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R1／編碼值。SEX從female改資料中的F。

歷史→本輪：model replies 4→7；tool attempts 5→8；SQL attempts 1→4。

Question：How many distinct female patients have a normal anti-Scl-70 result and no recorded non-null symptom on any examination?

歷史SQL：
```sql
SELECT COUNT(DISTINCT p.ID) AS patient_count
FROM Patient AS p
WHERE LOWER(TRIM(p.SEX)) = 'female'
  AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND LOWER(TRIM(l.SC170)) IN ('negative', '0')
  )
  AND NOT EXISTS (
    SELECT 1
    FROM Examination AS e
    WHERE e.ID = p.ID
      AND e.Symptoms IS NOT NULL
  );
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT p.ID) AS patient_count
FROM Patient AS p
WHERE p.SEX = 'F'
  AND EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND l.SC170 IN ('negative', '0')
  )
  AND NOT EXISTS (
      SELECT 1
      FROM Examination AS e
      WHERE e.ID = p.ID
        AND e.Symptoms IS NOT NULL
  );
```



<a id="q392"></a>

## [Q392](failure-case-review.md#q392) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R4／附加cohort條件。加入 Examination.Thrombosis>0，題目已明言全registry包括無labs；Gold不需事件確診。

歷史→本輪：model replies 11→7；tool attempts 12→11；SQL attempts 8→7。

Question：I'm describing our young-patient group and want to show how unusual a raised RNP antibody is in these patients. Could you tell me how many patients in the thrombosis cohort born after 1 January 1960 never had a raised RNP antibody result? A few points: the group should cover every patient born after that date, including patients with no laboratory results at all - they count as never having had a raised result. "Raised" means a result strictly above 10, so a result of exactly 10 doesn't count, and a result of "negative" (no antibody detected) is never raised. Please return just one row with a single integer: the number of these patients.

歷史SQL：
```sql
SELECT COUNT(*) AS patient_count
FROM Patient p
WHERE p.Birthday > '1960-01-01'
  AND NOT EXISTS (
    SELECT 1
    FROM Examination e
    WHERE e.ID = p.ID
      AND e.Thrombosis = 1
  )
  AND NOT EXISTS (
    SELECT 1
    FROM Laboratory l
    WHERE l.ID = p.ID
      AND l.RNP IS NOT NULL
      AND TRIM(LOWER(l.RNP)) <> 'negative'
      AND CAST(l.RNP AS REAL) > 10
  );
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT p.ID) AS patient_count
FROM Patient AS p
WHERE p.Birthday > '1960-01-01'
  AND EXISTS (
      SELECT 1
      FROM Examination AS e
      WHERE e.ID = p.ID
        AND e.Thrombosis > 0
  )
  AND NOT EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND CAST(l.RNP AS REAL) > 10
  );
```



<a id="q407"></a>

## [Q407](failure-case-review.md#q407) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R4／附加cohort條件。額外要求 Examination.Thrombosis<>0，Gold全Patient有RNP>=64。

歷史→本輪：model replies 5→13；tool attempts 6→19；SQL attempts 2→15。

Question：I'm studying how early in life a patient in the thrombosis cohort can show a high anti-ribonuclear protein (RNP) reading. Please tell me the youngest age, in whole years, at which a patient had a laboratory test showing an anti-RNP result of at least 64. Age in whole years means the year of the test minus the year of birth. If several patients or tests share that youngest age, report that age once. I just need that single youngest age value, nothing else.

歷史SQL：
```sql
SELECT MIN(CAST(strftime('%Y', l.Date) AS INTEGER) - CAST(strftime('%Y', p.Birthday) AS INTEGER)) AS youngest_age
FROM Laboratory AS l
JOIN Patient AS p ON p.ID = l.ID
WHERE CAST(l.RNP AS REAL) >= 64
  AND l.RNP GLOB '[0-9]*'
  AND p.Birthday IS NOT NULL
  AND l.Date IS NOT NULL;
```

本輪SQL：
```sql
SELECT MIN(
    CAST(strftime('%Y', l.Date) AS INTEGER) -
    CAST(strftime('%Y', p.Birthday) AS INTEGER)
) AS youngest_age
FROM Laboratory AS l
JOIN Patient AS p ON p.ID = l.ID
WHERE CAST(l.RNP AS INTEGER) >= 64
  AND EXISTS (
      SELECT 1
      FROM Examination AS e
      WHERE e.ID = l.ID
        AND e.Thrombosis <> 0
  );
```



<a id="q410"></a>

## [Q410](historical-case-review.md#q410) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R4／有效事件範圍。Thrombosis=1改>0、排NULL symptoms。

歷史→本輪：model replies 5→8；tool attempts 6→9；SQL attempts 2→5。

Question：I'm putting together a monitoring checklist for SLE patients. Among the thrombotic episodes recorded for patients diagnosed with SLE, which single symptom appears most frequently? I just need the symptom name back. Please count all recorded episodes with no date restriction. If two symptoms are equally frequent, give the one that comes first alphabetically. Note that a patient counts as having SLE only if their own diagnosis record names SLE among their diseases.

歷史SQL：
```sql
SELECT e.Symptoms
FROM Examination AS e
JOIN Patient AS p ON p.ID = e.ID
WHERE p.Diagnosis LIKE '%SLE%'
  AND e.Thrombosis = 1
GROUP BY e.Symptoms
ORDER BY COUNT(*) DESC, e.Symptoms ASC
LIMIT 1;
```

本輪SQL：
```sql
SELECT e.Symptoms
FROM Examination AS e
JOIN Patient AS p ON p.ID = e.ID
WHERE p.Diagnosis LIKE '%SLE%'
  AND e.Thrombosis > 0
  AND e.Symptoms IS NOT NULL
GROUP BY e.Symptoms
ORDER BY COUNT(*) DESC, e.Symptoms ASC
LIMIT 1;
```



<a id="q411"></a>

## [Q411](historical-case-review.md#q411) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R3／計數粒度。從exam列比例改DISTINCT patient比例，同時細化SLE診斷字串。

歷史→本輪：model replies 8→8；tool attempts 9→9；SQL attempts 5→5。

Question：In our autoimmune disease cohort, what percentage of thrombosis patients were diagnosed with SLE at the examination visit? I need the percentage on a 0-100 scale, rounded to two decimal places. Please use the diagnosis recorded at the examination visit, not the diagnosis on the patient's overall file. This is for a write-up on which diagnoses accompany thrombotic events in this cohort.

歷史SQL：
```sql
SELECT ROUND(
    100.0 * SUM(CASE WHEN Diagnosis LIKE 'SLE%' THEN 1 ELSE 0 END) / COUNT(*),
    2
) AS percentage
FROM Examination
WHERE Thrombosis > 0;
```

本輪SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE
        WHEN Diagnosis = 'SLE' OR Diagnosis LIKE 'SLE+%' THEN ID
    END) / COUNT(DISTINCT ID),
    2
) AS percentage
FROM Examination
WHERE Thrombosis > 0;
```



<a id="q417"></a>

## [Q417](historical-case-review.md#q417) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R7／欄位次序。輸出由Admission,T-CHO,ID改T-CHO,Admission,ID。

歷史→本輪：model replies 5→5；tool attempts 6→8；SQL attempts 2→3。

Question：In this cohort, I want to compare the most extreme total cholesterol (T-CHO) readings between patients admitted to the hospital and those followed at the outpatient clinic. Please give me, for each of the two groups, the single highest T-CHO reading, along with the admission status ('+' admitted, '-' outpatient) and the patient ID whose reading is the group's highest. List the admitted group's row first, then the outpatient group's. If several patients tie at a group's highest reading, list each of them.

歷史SQL：
```sql
WITH maxima AS (
  SELECT p.Admission, MAX(l.`T-CHO`) AS max_tcho
  FROM Patient AS p
  JOIN Laboratory AS l ON l.ID = p.ID
  WHERE p.Admission IN ('+', '-')
  GROUP BY p.Admission
)
SELECT m.Admission, m.max_tcho AS `T-CHO`, p.ID
FROM maxima AS m
JOIN Patient AS p ON p.Admission = m.Admission
JOIN Laboratory AS l ON l.ID = p.ID AND l.`T-CHO` = m.max_tcho
ORDER BY CASE m.Admission WHEN '+' THEN 1 WHEN '-' THEN 2 END, p.ID;
```

本輪SQL：
```sql
WITH patient_maxima AS (
    SELECT
        p.Admission,
        l.ID,
        MAX(l."T-CHO") AS reading
    FROM Patient AS p
    JOIN Laboratory AS l ON l.ID = p.ID
    WHERE p.Admission IN ('+', '-')
      AND l."T-CHO" IS NOT NULL
    GROUP BY p.Admission, l.ID
),
group_maxima AS (
    SELECT Admission, MAX(reading) AS highest_reading
    FROM patient_maxima
    GROUP BY Admission
)
SELECT
    p.reading AS "T-CHO",
    p.Admission,
    p.ID AS patient_id
FROM patient_maxima AS p
JOIN group_maxima AS g
  ON g.Admission = p.Admission
 AND g.highest_reading = p.reading
ORDER BY CASE p.Admission WHEN '+' THEN 1 ELSE 2 END, p.ID;
```



<a id="q421"></a>

## [Q421](failure-case-review.md#q421) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R2／量度來源。normal rheumatoid factor應依題意 Laboratory.RA IN('-','+-')，Agent用了RF值。

歷史→本輪：model replies 16→18；tool attempts 17→19；SQL attempts 13→15。

Question：How many patients in our thrombosis ward are followed at the outpatient clinic (rather than admitted) with a normal Rheumatoid Factor and no positive measure of degree of coagulation? Please give me a single number. For context: a normal Rheumatoid Factor is '-' or '+-', a positive measure of degree of coagulation is '+' on any of the coagulation measures (KCT, RVVT, LAC), and an outpatient-clinic patient is one with Admission = '-'. If a patient has no recorded coagulation measure, count them as having no positive measure.

歷史SQL：
```sql
SELECT COUNT(DISTINCT p.ID)
FROM Patient AS p
WHERE p.Admission = '-'
  AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.RA IN ('-', '+-')
  )
  AND NOT EXISTS (
    SELECT 1
    FROM Examination AS e
    WHERE e.ID = p.ID
      AND (e.KCT = '+' OR e.RVVT = '+' OR e.LAC = '+')
  );
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT p.ID)
FROM Patient AS p
WHERE p.Admission = '-'
  AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND (l.RF LIKE '<%' OR l.RF = '40')
  )
  AND NOT EXISTS (
    SELECT 1
    FROM Examination AS e
    WHERE e.ID = p.ID
      AND (e.KCT = '+' OR e.RVVT = '+' OR e.LAC = '+')
  );
```



<a id="q431"></a>

## [Q431](historical-case-review.md#q431) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R1／缺失值。未記錄sex由NULL擴至NULL或空字串。

歷史→本輪：model replies 4→5；tool attempts 5→6；SQL attempts 1→2。

Question：For patients whose sex is not recorded in the registry, I need two counts for the annual quality report: how many have at least one laboratory result on file, and of those, how many have at least one laboratory result showing elevated total bilirubin. The report covers all dates.

歷史SQL：
```sql
SELECT
    COUNT(DISTINCT p.ID) AS patients_with_lab_result,
    COUNT(DISTINCT CASE WHEN l.`T-BIL` >= 2.0 THEN p.ID END) AS patients_with_elevated_total_bilirubin
FROM Patient AS p
JOIN Laboratory AS l ON l.ID = p.ID
WHERE p.SEX IS NULL;
```

本輪SQL：
```sql
SELECT
    COUNT(DISTINCT p.ID) AS patients_with_any_lab,
    COUNT(DISTINCT CASE WHEN l.`T-BIL` >= 2.0 THEN p.ID END) AS patients_with_elevated_tbil
FROM Patient AS p
JOIN Laboratory AS l ON l.ID = p.ID
WHERE p.SEX IS NULL OR TRIM(p.SEX) = '';
```



<a id="q438"></a>

## [Q438](historical-case-review.md#q438) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R5／篩選順序。原要求所有GPT均正常，改只在正常GPT測量中選最高值。

歷史→本輪：model replies 6→5；tool attempts 7→6；SQL attempts 3→2。

Question：I'm reviewing patients with an elevated anti-ribonuclear protein result. Among patients who ever had an anti-ribonuclear protein result of 16 or higher, I want to follow up the three whose liver enzymes stayed in the normal range. The normal range for GPT is below 60. For each patient, take their highest GPT value among their laboratory tests that fall in the normal range. Rank patients from that highest value down; if two patients share the same value, the one with the smaller patient ID comes first. Please return exactly three patients, one row per patient, with only each patient's Birthday.

歷史SQL：
```sql
WITH elevated AS (
    SELECT DISTINCT ID
    FROM Laboratory
    WHERE CAST(RNP AS REAL) >= 16
),
normal_only AS (
    SELECT ID, MAX(GPT) AS max_gpt
    FROM Laboratory
    GROUP BY ID
    HAVING MAX(CASE WHEN GPT IS NULL OR GPT >= 60 THEN 1 ELSE 0 END) = 0
)
SELECT p.Birthday
FROM elevated e
JOIN normal_only n ON n.ID = e.ID
JOIN Patient p ON p.ID = e.ID
ORDER BY n.max_gpt DESC, p.ID ASC
LIMIT 3;
```

本輪SQL：
```sql
WITH eligible AS (
    SELECT DISTINCT ID
    FROM Laboratory
    WHERE CAST(RNP AS REAL) >= 16
),
max_gpt AS (
    SELECT ID, MAX(GPT) AS highest_gpt
    FROM Laboratory
    WHERE GPT < 60
    GROUP BY ID
)
SELECT p.Birthday
FROM eligible AS e
JOIN max_gpt AS m ON m.ID = e.ID
JOIN Patient AS p ON p.ID = e.ID
ORDER BY m.highest_gpt DESC, p.ID ASC
LIMIT 3;
```



<a id="q441"></a>

## [Q441](failure-case-review.md#q441) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R8／最終JSON修訂。最後測試SQL可執行；最終改以replace拼JSON交json_each，原生SQLite報 malformed JSON。

歷史→本輪：model replies 12→6；tool attempts 13→8；SQL attempts 9→4。

Question：I need to find lupus patients with liver lab abnormalities. Can you give me the ID and sex of every patient who has at least one total bilirubin (T-BIL) result at or above the upper normal limit of 1.2 mg/dL, and who has a confirmed diagnosis of systemic lupus erythematosus (SLE)? SLE counts if it's among the patient's confirmed diagnoses, even when other diseases are diagnosed or suspected alongside it, but a suspected SLE alone doesn't count. The diagnosis should be the patient's overall diagnosis, not something noted at a single examination. Please order results by sex, then patient ID, and return only the ID and sex.

歷史SQL：
```sql
SELECT p.ID, p.SEX
FROM Patient AS p
WHERE (
    p.Diagnosis = 'SLE'
    OR p.Diagnosis LIKE 'SLE,%'
    OR p.Diagnosis LIKE 'SLE %'
    OR p.Diagnosis LIKE '% SLE'
    OR p.Diagnosis LIKE '% SLE,%'
    OR p.Diagnosis LIKE '%SLE' || char(29) || '%'
    OR p.Diagnosis LIKE '%SLE,%'
)
AND p.Diagnosis NOT LIKE '%SLE susp%'
AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.`T-BIL` >= 1.2
)
ORDER BY p.SEX, p.ID;
```

本輪SQL：
```sql
SELECT p.ID, p.SEX
FROM Patient AS p
WHERE EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l."T-BIL" >= 1.2
)
AND EXISTS (
    SELECT 1
    FROM (
        SELECT trim(value) AS diagnosis
        FROM json_each('["' || replace(replace(p.Diagnosis, ', ', '","'), '"', '\\"') || '"]')
    ) AS d
    WHERE d.diagnosis = 'SLE'
)
ORDER BY p.SEX, p.ID;
```



<a id="q445"></a>

## [Q445](failure-case-review.md#q445) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R4／附加cohort條件。額外inner JOIN Examination並限Thrombosis=1，Gold納每個care setting全部Patient。

歷史→本輪：model replies 7→11；tool attempts 8→14；SQL attempts 4→10。

Question：For our thrombosis study cohort, I'd like to know how often patients have a normal IgG status at their most recent check, broken down by care setting. Please give me, for patients admitted to the hospital and for patients followed at the outpatient clinic, the percentage of that setting's patients whose most recent IgG measurement was normal. The percentage should be out of every patient in that setting, so patients who never had an IgG measurement count toward the denominator but not the numerator. Please round to one decimal place, and label the two results exactly as 'admitted to the hospital' and 'followed at the outpatient clinic'.

歷史SQL：
```sql
SELECT
  CASE WHEN p.Admission = '+' THEN 'admitted to the hospital'
       ELSE 'followed at the outpatient clinic'
  END AS care_setting,
  ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN l.IGG > 900 AND l.IGG < 2000 THEN p.ID END)
    / COUNT(DISTINCT p.ID),
    1
  ) AS percentage
FROM Patient AS p
LEFT JOIN Laboratory AS l
  ON l.ID = p.ID
 AND l.Date = (
   SELECT MAX(l2.Date)
   FROM Laboratory AS l2
   WHERE l2.ID = p.ID
     AND l2.IGG IS NOT NULL
 )
WHERE p.Admission IN ('+', '-')
GROUP BY p.Admission
ORDER BY p.Admission DESC;
```

本輪SQL：
```sql
WITH cohort AS (
    SELECT DISTINCT
        p.ID,
        CASE
            WHEN p.Admission = '+' THEN 'admitted to the hospital'
            WHEN p.Admission = '-' THEN 'followed at the outpatient clinic'
        END AS setting
    FROM Patient AS p
    JOIN Examination AS e ON e.ID = p.ID
    WHERE e.Thrombosis = 1
      AND p.Admission IN ('+', '-')
),
ranked_igg AS (
    SELECT
        ID,
        IGG,
        ROW_NUMBER() OVER (PARTITION BY ID ORDER BY Date DESC) AS rn
    FROM Laboratory
    WHERE IGG IS NOT NULL
),
latest_igg AS (
    SELECT ID, IGG
    FROM ranked_igg
    WHERE rn = 1
)
SELECT
    c.setting,
    ROUND(
        100.0 * SUM(CASE WHEN li.IGG > 900 AND li.IGG < 2000 THEN 1 ELSE 0 END)
        / COUNT(*),
        1
    ) AS percentage
FROM cohort AS c
LEFT JOIN latest_igg AS li ON li.ID = c.ID
GROUP BY c.setting;
```



<a id="q447"></a>

## [Q447](historical-case-review.md#q447) · 歷史錯→本輪啱 · thrombosis_prediction

候選關聯：R5／先篩後排名。最新RNP前先排RNP NULL，避免拿最新但無RNP的lab。

歷史→本輪：model replies 5→13；tool attempts 6→14；SQL attempts 2→10。

Question：In the thrombosis prediction cohort, I want to gauge how often the most recent anti-ribonuclear protein measurement among female patients was markedly elevated while CPK stayed low at that same measurement. Please give me a single integer: the number of female patients whose most recent anti-ribonuclear protein titer was above 64 and whose CPK from that same laboratory record was below 250. Above 64 means strictly greater than 64, and below 250 means strictly less than 250.

歷史SQL：
```sql
SELECT COUNT(*)
FROM (
    SELECT
        l.ID,
        l.RNP,
        l.CPK,
        ROW_NUMBER() OVER (PARTITION BY l.ID ORDER BY l.Date DESC) AS rn
    FROM Laboratory AS l
    JOIN Patient AS p ON p.ID = l.ID
    WHERE p.SEX = 'F'
) AS most_recent
WHERE rn = 1
  AND CAST(RNP AS REAL) > 64
  AND CPK < 250;
```

本輪SQL：
```sql
WITH ranked AS (
    SELECT
        ID,
        RNP,
        CPK,
        ROW_NUMBER() OVER (PARTITION BY ID ORDER BY Date DESC) AS rn
    FROM Laboratory
    WHERE RNP IS NOT NULL
)
SELECT COUNT(*) AS patient_count
FROM ranked AS l
JOIN Patient AS p ON p.ID = l.ID
WHERE p.SEX = 'F'
  AND l.rn = 1
  AND CAST(l.RNP AS REAL) > 64
  AND l.CPK < 250;
```



<a id="q448"></a>

## [Q448](failure-case-review.md#q448) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R1／診斷字串。NOT LIKE '%susp%' 排除任何疾病被懷疑的整筆診斷，Gold只排'SLE susp'。

歷史→本輪：model replies 15→6；tool attempts 16→9；SQL attempts 12→5。

Question：I'm preparing a capacity report for the lupus service. Among the patients whose profile lists a confirmed SLE diagnosis (not just suspected), I need: (1) how many were admitted to the hospital as inpatients, (2) how many were followed at the outpatient clinic, and (3) what percentage of the confirmed-SLE patients who were in one of these two care settings were inpatients. Please round the percentage to two decimals.

歷史SQL：
```sql
SELECT
  SUM(CASE WHEN Admission = '+' THEN 1 ELSE 0 END) AS inpatient_count,
  SUM(CASE WHEN Admission = '-' THEN 1 ELSE 0 END) AS outpatient_count,
  ROUND(
    100.0 * SUM(CASE WHEN Admission = '+' THEN 1 ELSE 0 END)
    / COUNT(*),
    2
  ) AS inpatient_percentage
FROM Patient
WHERE Diagnosis LIKE '%SLE%'
  AND Diagnosis NOT LIKE '%SLE susp%'
  AND Admission IN ('+', '-');
```

本輪SQL：
```sql
SELECT
    COUNT(DISTINCT CASE WHEN Admission = '+' THEN ID END) AS inpatients,
    COUNT(DISTINCT CASE WHEN Admission = '-' THEN ID END) AS outpatient_clinic,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN Admission = '+' THEN ID END) /
        NULLIF(COUNT(DISTINCT CASE WHEN Admission IN ('+', '-') THEN ID END), 0),
        2
    ) AS inpatient_percentage
FROM Patient
WHERE Diagnosis LIKE '%SLE%'
  AND Diagnosis NOT LIKE '%susp%';
```



<a id="q458"></a>

## [Q458](failure-case-review.md#q458) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R7／標籤值。輸出Female/Male而非原始F/M代碼。

歷史→本輪：model replies 4→6；tool attempts 4→6；SQL attempts 1→3。

Question：Among the patients who have laboratory test records on file, how many are female and how many are male? Please give me one line for the female patients and one line for the male patients, each showing the sex and the number of patients of that sex.

歷史SQL：
```sql
SELECT p.SEX, COUNT(DISTINCT p.ID) AS number_of_patients
FROM Patient AS p
WHERE p.SEX IN ('F', 'M')
  AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
  )
GROUP BY p.SEX
ORDER BY CASE p.SEX WHEN 'F' THEN 1 WHEN 'M' THEN 2 END;
```

本輪SQL：
```sql
SELECT
    CASE SEX WHEN 'F' THEN 'Female' WHEN 'M' THEN 'Male' END AS sex,
    COUNT(DISTINCT Patient.ID) AS number_of_patients
FROM Patient
WHERE SEX IN ('F', 'M')
  AND EXISTS (
      SELECT 1
      FROM Laboratory
      WHERE Laboratory.ID = Patient.ID
  )
GROUP BY SEX
ORDER BY CASE SEX WHEN 'F' THEN 1 WHEN 'M' THEN 2 END;
```



<a id="q459"></a>

## [Q459](failure-case-review.md#q459) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R1／診斷字串。Diagnosis='SJS'漏掉SJS已確診並同時其他疾病的token組合。

歷史→本輪：model replies 6→5；tool attempts 7→7；SQL attempts 3→3。

Question：I'm studying antiphospholipid antibodies in Sjögren's syndrome (SJS). Could you tell me the average anti-cardiolipin IgM concentration among SJS patients, rounded to two decimal places? To clarify: use only patients with an established SJS diagnosis recorded at the patient level (a diagnosis marked 'susp', such as 'SJS susp', is only a suspicion and those patients should not be included). Include every examination recorded for these patients regardless of date. A recorded anti-cardiolipin IgM value of 0 means the antibody was not detected at that examination, so treat it as no measurement and leave it out of the average - count only examinations where a concentration was detected.

歷史SQL：
```sql
SELECT ROUND(AVG(e.`aCL IgM`), 2) AS avg_acl_igm
FROM Patient AS p
JOIN Examination AS e ON e.ID = p.ID
WHERE p.Diagnosis LIKE '%SJS%'
  AND p.Diagnosis NOT LIKE '%SJS susp%'
  AND e.`aCL IgM` IS NOT NULL
  AND e.`aCL IgM` <> 0;
```

本輪SQL：
```sql
SELECT ROUND(AVG(e."aCL IgM"), 2)
FROM Examination AS e
JOIN Patient AS p ON p.ID = e.ID
WHERE p.Diagnosis = 'SJS'
  AND e."aCL IgM" IS NOT NULL
  AND e."aCL IgM" <> 0;
```



<a id="q466"></a>

## [Q466](failure-case-review.md#q466) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R8／最終修訂語法。工具測試SQL成功，最終別名改為未引用women's_percentage，單引號破壞SQL，parser拒收。

歷史→本輪：model replies 5→7；tool attempts 6→8；SQL attempts 2→4。

Question：As part of our clinical audit I'm profiling patients born between 1936 and 1956 inclusive who never had a creatinine phosphokinase (CPK) result above the normal range. A CPK of 250 or higher counts as above the normal range, and patients with no CPK results on record count as never having exceeded it. For that group, please give me the women's percentage of the group's men and women, rounded to one decimal place.

歷史SQL：
```sql
SELECT ROUND(
    100.0 * SUM(CASE WHEN p.SEX = 'F' THEN 1 ELSE 0 END) / COUNT(*),
    1
) AS women_percentage
FROM Patient AS p
WHERE date(p.Birthday) >= date('1936-01-01')
  AND date(p.Birthday) < date('1957-01-01')
  AND p.SEX IN ('F', 'M')
  AND NOT EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND l.CPK >= 250
  );
```

本輪SQL：
```sql
None
```



<a id="q467"></a>

## [Q467](failure-case-review.md#q467) · 歷史啱→本輪錯 · thrombosis_prediction

候選關聯：R4／附加有效性條件。age BETWEEN0 AND49額外排除負年齡記錄，Gold只要求age<50；日期上界及TRIM亦不同。

歷史→本輪：model replies 4→6；tool attempts 5→7；SQL attempts 1→3。

Question：I'm preparing a case series on early renal involvement and need to size my cohort. How many patients were under age 50 on the day of a laboratory test performed between 1 January 1981 and 31 December 1986 inclusive, had a platelet count from 100 through 400 at that test, and showed proteinuria at that test? Age means completed years on the day of the test, so under 50 is strictly below 50. The platelet range is inclusive. I just need the number of patients satisfying all conditions.

歷史SQL：
```sql
SELECT COUNT(DISTINCT l.ID) AS patient_count
FROM Laboratory AS l
JOIN Patient AS p ON p.ID = l.ID
WHERE l.Date BETWEEN '1981-01-01' AND '1986-12-31'
  AND l.PLT BETWEEN 100 AND 400
  AND l.`U-PRO` IS NOT NULL
  AND TRIM(l.`U-PRO`) NOT IN ('-', '0')
  AND p.Birthday IS NOT NULL
  AND CAST(strftime('%Y', l.Date) AS INTEGER)
      - CAST(strftime('%Y', p.Birthday) AS INTEGER)
      - (strftime('%m-%d', l.Date) < strftime('%m-%d', p.Birthday)) < 50;
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT p.ID)
FROM Patient AS p
JOIN Laboratory AS l ON l.ID = p.ID
WHERE l.Date BETWEEN '1981-01-01' AND '1986-12-31'
  AND l.PLT BETWEEN 100 AND 400
  AND l."U-PRO" IS NOT NULL
  AND TRIM(l."U-PRO") NOT IN ('-', '0')
  AND p.Birthday IS NOT NULL
  AND CAST(strftime('%Y', l.Date) AS INTEGER)
      - CAST(strftime('%Y', p.Birthday) AS INTEGER)
      - (strftime('%m-%d', l.Date) < strftime('%m-%d', p.Birthday))
      BETWEEN 0 AND 49;
```



<a id="q472"></a>

## [Q472](historical-case-review.md#q472) · 歷史錯→本輪啱 · toxicology

候選關聯：R1／元素編碼。fluorine由大寫F改lower(element)='f'。

歷史→本輪：model replies 4→5；tool attempts 5→7；SQL attempts 1→3。

Question：Among carcinogenic molecules, what percentage contain no fluorine atoms? Round to two decimal places.

歷史SQL：
```sql
SELECT ROUND(
    100.0 * SUM(
        CASE WHEN NOT EXISTS (
            SELECT 1
            FROM atom a
            WHERE a.molecule_id = m.molecule_id
              AND a.element = 'F'
        ) THEN 1 ELSE 0 END
    ) / COUNT(*),
    2
) AS percentage
FROM molecule m
WHERE m.label = '+';
```

本輪SQL：
```sql
WITH carcinogenic AS (
    SELECT molecule_id
    FROM molecule
    WHERE label = '+'
),
fluorinated AS (
    SELECT DISTINCT molecule_id
    FROM atom
    WHERE LOWER(element) = 'f'
)
SELECT ROUND(
    100.0 * SUM(CASE WHEN fluorinated.molecule_id IS NULL THEN 1 ELSE 0 END)
    / COUNT(*),
    2
) AS percentage
FROM carcinogenic
LEFT JOIN fluorinated USING (molecule_id);
```



<a id="q474"></a>

## [Q474](failure-case-review.md#q474) · 歷史啱→本輪錯 · toxicology

候選關聯：R1／元素編碼。元素用大寫P/N，資料Gold為小寫p/n；另多輸出molecule_id,bond_type。

歷史→本輪：model replies 6→6；tool attempts 8→7；SQL attempts 2→1。

Question：What are the bonds that have phosphorus and nitrogen as their atom elements?

歷史SQL：
```sql
SELECT DISTINCT b.bond_id
FROM bond AS b
JOIN connected AS c ON c.bond_id = b.bond_id
JOIN atom AS a1 ON a1.atom_id = c.atom_id
JOIN atom AS a2 ON a2.atom_id = c.atom_id2
WHERE (a1.element = 'p' AND a2.element = 'n')
   OR (a1.element = 'n' AND a2.element = 'p');
```

本輪SQL：
```sql
SELECT DISTINCT b.bond_id, b.molecule_id, b.bond_type
FROM bond AS b
JOIN connected AS c ON c.bond_id = b.bond_id
JOIN atom AS a1 ON a1.atom_id = c.atom_id
JOIN atom AS a2 ON a2.atom_id = c.atom_id2
WHERE (a1.element = 'P' AND a2.element = 'N')
   OR (a1.element = 'N' AND a2.element = 'P');
```



<a id="q478"></a>

## [Q478](historical-case-review.md#q478) · 歷史錯→本輪啱 · toxicology

候選關聯：R7／數值表示。文字分數'a/b'改數值除法fraction。

歷史→本輪：model replies 7→4；tool attempts 8→7；SQL attempts 4→3。

Question：What fraction of all atoms in molecule TR006 are hydrogen? Give the fraction and the molecule's recorded carcinogenicity label.

歷史SQL：
```sql
SELECT
  SUM(CASE WHEN LOWER(a.element) = 'h' THEN 1 ELSE 0 END) || '/' || COUNT(*) AS hydrogen_fraction,
  m.label AS carcinogenicity_label
FROM atom AS a
JOIN molecule AS m ON m.molecule_id = a.molecule_id
WHERE m.molecule_id = 'TR006'
GROUP BY m.molecule_id, m.label;
```

本輪SQL：
```sql
SELECT
  1.0 * SUM(CASE WHEN element = 'h' THEN 1 ELSE 0 END) / COUNT(*) AS hydrogen_fraction,
  (SELECT label FROM molecule WHERE molecule_id = 'TR006') AS carcinogenicity_label
FROM atom
WHERE molecule_id = 'TR006';
```



<a id="q483"></a>

## [Q483](historical-case-review.md#q483) · 歷史錯→本輪啱 · toxicology

候選關聯：R7／標籤值。bond_type由single/double/triple標籤改原始-/=/#。

歷史→本輪：model replies 7→8；tool attempts 10→13；SQL attempts 4→7。

Question：For the carcinogenic molecules in the toxicology database, how many carbon-carbon bonds are there of each bond type (single, double, and triple)? Please give me the bond type and the corresponding count.

歷史SQL：
```sql
SELECT
  CASE b.bond_type
    WHEN '-' THEN 'single'
    WHEN '=' THEN 'double'
    WHEN '#' THEN 'triple'
  END AS bond_type,
  COUNT(DISTINCT b.bond_id) AS bond_count
FROM molecule m
JOIN bond b ON b.molecule_id = m.molecule_id
JOIN connected c ON c.bond_id = b.bond_id
JOIN atom a1 ON a1.atom_id = c.atom_id
JOIN atom a2 ON a2.atom_id = c.atom_id2
WHERE m.label = '+'
  AND LOWER(a1.element) = 'c'
  AND LOWER(a2.element) = 'c'
GROUP BY b.bond_type
ORDER BY CASE b.bond_type WHEN '-' THEN 1 WHEN '=' THEN 2 WHEN '#' THEN 3 END;
```

本輪SQL：
```sql
SELECT b.bond_type, COUNT(DISTINCT b.bond_id) AS bond_count
FROM molecule m
JOIN atom a ON a.molecule_id = m.molecule_id
JOIN connected c ON c.atom_id = a.atom_id
JOIN atom a2 ON a2.atom_id = c.atom_id2
JOIN bond b ON b.bond_id = c.bond_id
WHERE m.label = '+'
  AND a.element = 'c'
  AND a2.element = 'c'
GROUP BY b.bond_type
ORDER BY CASE b.bond_type
  WHEN '-' THEN 1
  WHEN '=' THEN 2
  WHEN '#' THEN 3
END;
```



<a id="q486"></a>

## [Q486](failure-case-review.md#q486) · 歷史啱→本輪錯 · toxicology

候選關聯：R6／存在條件範圍。unique element條件綁定該bond端點，Gold只要求該molecule任何atom具unique element即可列全部bonds。

歷史→本輪：model replies 4→7；tool attempts 7→9；SQL attempts 1→3。

Question：I'm compiling bond records of unusual carcinogenic molecules for a structural alert review. Please find the bonds that belong to carcinogenic molecules (labelled '+') that contain an element recorded for no other molecule in the dataset. Note that this search covers the whole dataset, so an element counts as belonging to no other molecule when no molecule other than the one at hand records it. For each such bond, return only the bond id and molecule id.

歷史SQL：
```sql
WITH rare_elements AS (
    SELECT DISTINCT a.element, a.molecule_id
    FROM atom AS a
    WHERE a.element IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM atom AS other
          WHERE other.element = a.element
            AND other.molecule_id <> a.molecule_id
      )
),
eligible_molecules AS (
    SELECT DISTINCT r.molecule_id
    FROM rare_elements AS r
    JOIN molecule AS m ON m.molecule_id = r.molecule_id
    WHERE m.label = '+'
)
SELECT b.bond_id, b.molecule_id
FROM bond AS b
JOIN eligible_molecules AS e ON e.molecule_id = b.molecule_id;
```

本輪SQL：
```sql
SELECT DISTINCT b.bond_id, b.molecule_id
FROM bond AS b
JOIN molecule AS m
  ON m.molecule_id = b.molecule_id
JOIN connected AS c
  ON c.bond_id = b.bond_id
JOIN atom AS a
  ON a.atom_id IN (c.atom_id, c.atom_id2)
WHERE m.label = '+'
  AND NOT EXISTS (
    SELECT 1
    FROM atom AS other
    WHERE other.element = a.element
      AND other.molecule_id <> b.molecule_id
  );
```



<a id="q487"></a>

## [Q487](historical-case-review.md#q487) · 歷史錯→本輪啱 · toxicology

候選關聯：R6／端點關係。multiple bond排除從整molecule縮至nitrogen實際參與的connected端點。

歷史→本輪：model replies 5→5；tool attempts 9→7；SQL attempts 4→1。

Question：I'm building a control group of nitrogen-containing structures for a carcinogenicity review. How many molecules in the database contain at least one nitrogen atom, where none of those nitrogen atoms takes part in a double bond or a triple bond? A nitrogen held only by single bonds is fine; any nitrogen in a double or triple bond disqualifies the molecule. Molecules with no nitrogen at all don't count. I just need the single number of such molecules.

歷史SQL：
```sql
SELECT COUNT(*)
FROM molecule m
WHERE EXISTS (
    SELECT 1
    FROM atom a
    WHERE a.molecule_id = m.molecule_id
      AND a.element = 'n'
)
AND NOT EXISTS (
    SELECT 1
    FROM atom a
    JOIN bond b ON b.molecule_id = a.molecule_id
    WHERE a.molecule_id = m.molecule_id
      AND a.element = 'n'
      AND b.bond_type IN ('=', '#')
);
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT a.molecule_id)
FROM atom AS a
WHERE a.element = 'n'
  AND NOT EXISTS (
    SELECT 1
    FROM atom AS n
    JOIN connected AS c
      ON c.atom_id = n.atom_id OR c.atom_id2 = n.atom_id
    JOIN bond AS b
      ON b.bond_id = c.bond_id
     AND b.molecule_id = n.molecule_id
    WHERE n.molecule_id = a.molecule_id
      AND n.element = 'n'
      AND b.bond_type IN ('=', '#')
  );
```



<a id="q488"></a>

## [Q488](historical-case-review.md#q488) · 歷史錯→本輪啱 · toxicology

候選關聯：R3／去重與方向。COUNT connected列改雙向鄰接DISTINCT neighbor atom。

歷史→本輪：model replies 6→5；tool attempts 5→7；SQL attempts 1→1。

Question：In the toxicology database, how many atoms are bonded to chlorine atoms, taken across all molecules? I want a single number. By chlorine I mean the element 'cl'.

歷史SQL：
```sql
SELECT COUNT(*) AS atoms_bonded_to_chlorine
FROM connected c
JOIN atom chlorine ON chlorine.atom_id = c.atom_id
WHERE LOWER(chlorine.element) = 'cl';
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT neighbor.atom_id) AS count_atoms_bonded_to_chlorine
FROM atom AS chlorine
JOIN connected AS c
  ON c.atom_id = chlorine.atom_id OR c.atom_id2 = chlorine.atom_id
JOIN atom AS neighbor
  ON neighbor.atom_id = CASE
    WHEN c.atom_id = chlorine.atom_id THEN c.atom_id2
    ELSE c.atom_id
  END
WHERE LOWER(chlorine.element) = 'cl';
```



<a id="q492"></a>

## [Q492](historical-case-review.md#q492) · 歷史錯→本輪啱 · toxicology

候選關聯：R3／去重與查詢泛化。COUNT connected列改DISTINCT bond_id，並動態找yttrium molecule取消TR499硬編碼。

歷史→本輪：model replies 9→9；tool attempts 11→11；SQL attempts 5→5。

Question：I'm studying the hydrogen bonding pattern of the molecule that contains the yttrium atom. How many bonds in that molecule have a hydrogen atom at one end? Just give me the single overall count, please.

歷史SQL：
```sql
SELECT COUNT(*) AS hydrogen_bonds
FROM connected c
JOIN atom a1 ON a1.atom_id = c.atom_id
JOIN atom a2 ON a2.atom_id = c.atom_id2
WHERE a1.molecule_id = 'TR499'
  AND (LOWER(a1.element) = 'h' OR LOWER(a2.element) = 'h');
```

本輪SQL：
```sql
SELECT COUNT(DISTINCT b.bond_id)
FROM bond AS b
JOIN connected AS c ON c.bond_id = b.bond_id
JOIN atom AS a1 ON a1.atom_id = c.atom_id
JOIN atom AS a2 ON a2.atom_id = c.atom_id2
WHERE b.molecule_id = (
    SELECT molecule_id
    FROM atom
    WHERE lower(element) = 'y'
)
AND (lower(a1.element) = 'h' OR lower(a2.element) = 'h');
```



<a id="q493"></a>

## [Q493](failure-case-review.md#q493) · 歷史啱→本輪錯 · toxicology

候選關聯：R2／圖度數量度。bonds/atoms不是每atom degree平均；每bond連兩端且零degree也須納入。

歷史→本輪：model replies 6→6；tool attempts 8→9；SQL attempts 3→4。

Question：As part of a connectivity review, I'd like to know how heavily atoms are connected in molecule TR397: what is the average number of bonds an atom of TR397 has? Please give me just that one number, rounded to two decimal places.

歷史SQL：
```sql
SELECT ROUND(1.0 * (SELECT COUNT(*) FROM connected c JOIN atom a ON a.atom_id = c.atom_id WHERE a.molecule_id = 'TR397') / NULLIF((SELECT COUNT(*) FROM atom a WHERE a.molecule_id = 'TR397'), 0), 2) AS average_bonds_per_atom;
```

本輪SQL：
```sql
SELECT ROUND(
    1.0 * (SELECT COUNT(*) FROM bond WHERE molecule_id = 'TR397') /
    (SELECT COUNT(*) FROM atom WHERE molecule_id = 'TR397'),
    2
) AS average_bonds_per_atom;
```




> Repository archive: raw traces and local HTML viewers are intentionally excluded. Trace links above point to local-reproduction guidance; full local review artifacts remain preserved separately.
