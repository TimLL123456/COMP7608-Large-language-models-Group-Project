# 全部181題失敗個案審閱



每題的分類是主候選，不是保證可修復或prompt因果標籤。SQL、完整trace、原始診斷與未成功改寫均可在案例頁審閱。



<a id="q0"></a>

## [Q0](failure-case-review.md#q0) · test · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／量度來源。

使用已存百分比欄位代替 Free Meal Count／Enrollment；亦省略 rtype='S' 及 enrollment>0。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among schools with a school-level SAT excellence rate above 0.3, what is the highest ages-5-17 free-meal eligibility rate?

Evidence：SAT excellence rate is the share of test takers scoring at least 1500.

Gold SQL（離線）：
```sql
SELECT MAX(1.0 * f.`Free Meal Count (Ages 5-17)` / f.`Enrollment (Ages 5-17)`) FROM frpm AS f JOIN satscores AS s ON s.cds = f.CDSCode WHERE s.rtype = 'S' AND s.NumTstTakr > 0 AND f.`Enrollment (Ages 5-17)` > 0 AND 1.0 * s.NumGE1500 / s.NumTstTakr > 0.3
```

Agent SQL：
```sql
SELECT MAX(f.`Percent (%) Eligible Free (Ages 5-17)`) AS highest_free_meal_eligibility_rate
FROM frpm AS f
JOIN satscores AS s ON s.cds = f.CDSCode
WHERE s.NumTstTakr > 0
  AND 1.0 * s.NumGE1500 / s.NumTstTakr > 0.3;
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=15.962s；stop=final_sql_ready。



<a id="q2"></a>

## [Q2](failure-case-review.md#q2) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出契約。

最終多輸出 School 欄；另以已存 rate 代替計算值，並缺少 enrollment／tie-break 條件。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the five schools with ownership code 66 and the largest K-12 free-or-reduced-price meal counts, give each school's K-12 eligible meal rate rounded to six decimal places.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(1.0 * f."FRPM Count (K-12)" / NULLIF(f."Enrollment (K-12)", 0), 6) FROM frpm AS f JOIN schools AS s ON s.CDSCode = f.CDSCode WHERE s.SOC = '66' AND f."FRPM Count (K-12)" IS NOT NULL AND f."Enrollment (K-12)" > 0 ORDER BY f."FRPM Count (K-12)" DESC, s.CDSCode LIMIT 5
```

Agent SQL：
```sql
SELECT
    s.School,
    ROUND(f."Percent (%) Eligible FRPM (K-12)", 6) AS eligible_meal_rate
FROM schools AS s
JOIN frpm AS f ON f.CDSCode = s.CDSCode
WHERE s.SOC = '66'
ORDER BY f."FRPM Count (K-12)" DESC
LIMIT 5;
```

觀察：model replies=7、tool attempts=7、SQL attempts=4、latency=22.789s；stop=final_sql_ready。



<a id="q4"></a>

## [Q4](failure-case-review.md#q4) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／篩選對齊。

排名前未限制 SAT rtype='S'，亦未按 cds 決定同分次序。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What are the mailing street address and name of the school with the seventh-highest recorded average mathematics score?

Evidence：

Gold SQL（離線）：
```sql
SELECT sc.MailStreet, sc.School FROM satscores AS sat JOIN schools AS sc ON sc.CDSCode = sat.cds WHERE sat.rtype = 'S' AND sat.AvgScrMath IS NOT NULL ORDER BY sat.AvgScrMath DESC, sat.cds LIMIT 1 OFFSET 6
```

Agent SQL：
```sql
SELECT s.MailStreet, s.School
FROM satscores AS ss
JOIN schools AS s ON s.CDSCode = ss.cds
WHERE ss.AvgScrMath IS NOT NULL
ORDER BY ss.AvgScrMath DESC
LIMIT 1 OFFSET 6;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=12.747s；stop=final_sql_ready。



<a id="q5"></a>

## [Q5](failure-case-review.md#q5) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／百分比尺度。

以已存比例欄位 <0.18 代替題目 0.18% 的 count*100/enrollment；篩選資料來源亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：How many non-charter schools in Los Angeles County have a K-12 free-meal percentage below 0.18%?

Evidence：

Gold SQL（離線）：
```sql
SELECT COUNT(T2.School) FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Los Angeles' AND T2.Charter = 0 AND CAST(T1.`Free Meal Count (K-12)` AS REAL) * 100 / T1.`Enrollment (K-12)` < 0.18
```

Agent SQL：
```sql
SELECT COUNT(*) AS school_count
FROM frpm
WHERE "County Name" = 'Los Angeles'
  AND "Charter School (Y/N)" = 0
  AND "Percent (%) Eligible Free (K-12)" < 0.18;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=17.590s；stop=final_sql_ready。



<a id="q6"></a>

## [Q6](failure-case-review.md#q6) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／百分比尺度。

使用已存 FRPM 比例欄，沒有依 evidence 計算 count/enrollment*100。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which schools served a grade span of Kindergarten to 9th grade in the county of Los Angeles and what is its Percent (%) Eligible FRPM (Ages 5-17)?

Evidence：FRPM eligibility percentage is free-or-reduced-price meal recipients divided by same-age-band enrollment, times 100.

Gold SQL（離線）：
```sql
SELECT T2.School, T1.`FRPM Count (Ages 5-17)` * 100 / T1.`Enrollment (Ages 5-17)` FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Los Angeles' AND T2.GSserved = 'K-9'
```

Agent SQL：
```sql
SELECT s.School,
       f."Percent (%) Eligible FRPM (Ages 5-17)"
FROM schools AS s
JOIN frpm AS f
  ON s.CDSCode = f.CDSCode
WHERE s.County = 'Los Angeles'
  AND s.GSserved = 'K-9';
```

觀察：model replies=7、tool attempts=8、SQL attempts=5、latency=25.923s；stop=final_sql_ready。



<a id="q7"></a>

## [Q7](failure-case-review.md#q7) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／欄位次序。

Agent 輸出 district code、percentage，Gold 次序為 percentage、district code。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the Percent (%) Eligible Free (K-12) in the school administered by an administrator whose first name is Alusine. List the district code of the school.

Evidence：K-12 free-meal eligibility percentage is K-12 free-meal recipients divided by K-12 enrollment, times 100.

Gold SQL（離線）：
```sql
SELECT T1.`Free Meal Count (K-12)` * 100 / T1.`Enrollment (K-12)`, T1.`District Code` FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.AdmFName1 = 'Alusine'
```

Agent SQL：
```sql
SELECT
    f."District Code",
    f."Free Meal Count (K-12)" * 100.0 / f."Enrollment (K-12)" AS "Percent (%) Eligible Free (K-12)"
FROM schools AS s
JOIN frpm AS f ON f.CDSCode = s.CDSCode
WHERE s.AdmFName1 = 'Alusine';
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=13.337s；stop=final_sql_ready。



<a id="q11"></a>

## [Q11](failure-case-review.md#q11) · dev · california_schools

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R7／排名／集合。

缺少最低起始年級選擇，直接回傳全部合資格學校；另加入 EILName='High School'。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Following up on the SAT participation review: among the currently operating high schools in the district with NCES identification number 0613360 that had no SAT test takers, which one begins serving students at the earliest grade? Please give me each such school's name and grade span served. Note that a high school must actually enroll students through grade 12-offering grade 12 without enrollment doesn't count. A school with no SAT record counts as having zero SAT test takers and should be included; only exclude schools with a positive number of SAT test takers. Compare starting grades as school grades-preschool comes before kindergarten, which comes before grade 1-and use the lowest grade the school actually serves, not just what it offers. If several schools tie at the earliest grade, list them all alphabetically by school name.

Evidence：NCES identification number 0613360 is the school district identification number assigned by the National Center for Education Statistics.

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT s.School AS school_name, s.GSserved AS grade_span_served, CASE WHEN SUBSTR(s.GSserved,1,INSTR(s.GSserved||'-','-')-1) = 'P' THEN -1 WHEN SUBSTR(s.GSserved,1,INSTR(s.GSserved||'-','-')-1) = 'K' THEN 0 ELSE CAST(SUBSTR(s.GSserved,1,INSTR(s.GSserved||'-','-')-1) AS INTEGER) END AS start_rank FROM schools s LEFT JOIN satscores t ON s.CDSCode = t.cds WHERE s.NCESDist = '0613360' AND s.StatusType = 'Active' AND s.GSserved LIKE '%12' AND COALESCE(t.NumTstTakr,0) = 0) SELECT school_name, grade_span_served FROM cohort WHERE start_rank = (SELECT MIN(start_rank) FROM cohort) ORDER BY school_name
```

Agent SQL：
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

觀察：model replies=8、tool attempts=9、SQL attempts=5、latency=31.563s；stop=final_sql_ready。



<a id="q12"></a>

## [Q12](failure-case-review.md#q12) · dev · california_schools

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／篩選對齊。

以 DOC='56'、District 特定名稱及 Active 代替 DOCType='State Board of Education'，候選學校集合不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling schools run directly by the California State Board of Education. Which of those schools has the highest average SAT reading score? If several tie for the highest, give me all of them. For each school, I need its name and its full mailing street address - the complete address, not an abbreviated one. Only include schools the State Board runs directly, and the score must be the school's own result, not a district-wide figure.

Evidence：State Board of Education: the state authority that directly runs and oversees certain California schools.

Gold SQL（離線）：
```sql
SELECT s.School, s.MailStreet FROM satscores AS t JOIN schools AS s ON t.cds = s.CDSCode WHERE s.DOCType = 'State Board of Education' AND t.sname IS NOT NULL AND t.AvgScrRead IS NOT NULL AND t.AvgScrRead = (SELECT MAX(t2.AvgScrRead) FROM satscores AS t2 JOIN schools AS s2 ON t2.cds = s2.CDSCode WHERE s2.DOCType = 'State Board of Education' AND t2.sname IS NOT NULL AND t2.AvgScrRead IS NOT NULL)
```

Agent SQL：
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

觀察：model replies=6、tool attempts=9、SQL attempts=6、latency=26.974s；stop=final_sql_ready。



<a id="q19"></a>

## [Q19](failure-case-review.md#q19) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／編碼／排序。

自製 grade rank 把 K 與數字1映成同值，並於 ELSE 減1；資料來源與 Gold Low Grade 不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the lowest grade level at which any school in our district begins serving students? If several schools tie at the lowest grade, just report that single grade level for the whole district. Our district is NCES district ID 0632640.

Evidence：'P' stands for preschool.

Gold SQL（離線）：
```sql
SELECT T1.`Low Grade` AS lowest_grade FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.NCESDist = '0632640' ORDER BY (T1.`Low Grade` = 'P') DESC, (T1.`Low Grade` = 'K') DESC, CAST(T1.`Low Grade` AS INTEGER), T1.`Low Grade` LIMIT 1
```

Agent SQL：
```sql
SELECT CASE MIN(CASE
    WHEN substr(GSserved, 1, 1) = 'P' THEN 0
    WHEN substr(GSserved, 1, 1) = 'K' THEN 1
    ELSE CAST(substr(GSserved, 1, instr(GSserved || '-', '-') - 1) AS INTEGER)
END)
    WHEN 0 THEN 'P'
    WHEN 1 THEN 'K'
    ELSE CAST(MIN(CASE
        WHEN substr(GSserved, 1, 1) = 'P' THEN 0
        WHEN substr(GSserved, 1, 1) = 'K' THEN 1
        ELSE CAST(substr(GSserved, 1, instr(GSserved || '-', '-') - 1) AS INTEGER)
    END) - 1 AS TEXT)
END AS lowest_grade
FROM schools
WHERE NCESDist = '0632640'
  AND GSserved IS NOT NULL;
```

觀察：model replies=5、tool attempts=4、SQL attempts=2、latency=19.239s；stop=final_sql_ready。



<a id="q21"></a>

## [Q21](failure-case-review.md#q21) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／實體來源。

Youth Authority 以 EdOpsName 識別，Gold 用 SOCType LIKE '%Youth Authority%'；母體來源不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the 2014-2015 academic year, what was the average number of enrolled students aged 5 to 17 eligible for free or reduced price meals per Youth Authority school? Count every Youth Authority school regardless of its status (active, closed, or merged), and treat a Youth Authority school with no meal-program record as zero. Please give me just that one number, rounded to two decimal places.

Evidence：A Youth Authority school is a school the state directory classifies as a Youth Authority Facility.

Gold SQL（離線）：
```sql
SELECT ROUND(SUM(COALESCE(T1.`FRPM Count (Ages 5-17)`, 0.0)) * 1.0 / COUNT(T2.CDSCode), 2) AS avg_frpm_ages_5_17 FROM schools AS T2 LEFT JOIN frpm AS T1 ON T1.CDSCode = T2.CDSCode WHERE T2.SOCType LIKE '%Youth Authority%'
```

Agent SQL：
```sql
SELECT ROUND(AVG(COALESCE(f.`FRPM Count (Ages 5-17)`, 0)), 2)
FROM schools AS s
LEFT JOIN frpm AS f
  ON f.CDSCode = s.CDSCode
 AND f.`Academic Year` = '2014-2015'
WHERE s.EdOpsName = 'Youth Authority School';
```

觀察：model replies=9、tool attempts=9、SQL attempts=6、latency=29.898s；stop=final_sql_ready。



<a id="q24"></a>

## [Q24](failure-case-review.md#q24) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／欄位來源。

以 schools.SOCType／School 代替題目指定 frpm School Type／School Name。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：We're relocating to far Northern California and want to know how far north California's middle schools reach. A middle school means a school serving the middle grades, the level between elementary school and high school — count it as a middle school if either its school type or its school name marks it as serving the middle grades, so a junior high school whose name says 'Middle' counts. Include both open and closed schools. Please tell me which middle school is located furthest north in California, along with its school type (the value of the field named 'School Type'), its school name, and its latitude in degrees. If several middle schools tie for the highest latitude, list all of them.

Evidence：middle school: a school serving the middle grades, the level between elementary school and high school

Gold SQL（離線）：
```sql
SELECT T1.`School Type`, T1.`School Name`, T2.Latitude FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE (T1.`School Type` LIKE '%Middle%' OR T1.`School Name` LIKE '%Middle%') AND T2.Latitude = (SELECT MAX(T2b.Latitude) FROM frpm AS T1b INNER JOIN schools AS T2b ON T1b.CDSCode = T2b.CDSCode WHERE T1b.`School Type` LIKE '%Middle%' OR T1b.`School Name` LIKE '%Middle%')
```

Agent SQL：
```sql
SELECT
    SOCType AS "School Type",
    School AS "School Name",
    Latitude
FROM schools
WHERE Latitude = (
    SELECT MAX(Latitude)
    FROM schools
    WHERE Latitude IS NOT NULL
      AND (SOCType LIKE '%Middle%' OR School LIKE '%Middle%')
)
  AND (SOCType LIKE '%Middle%' OR School LIKE '%Middle%');
```

觀察：model replies=7、tool attempts=7、SQL attempts=5、latency=26.413s；stop=final_sql_ready。



<a id="q28"></a>

## [Q28](failure-case-review.md#q28) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／欄位來源。

以解析 GSserved 上限代替 frpm High Grade 的1至8，且缺少最低1限制。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a brief on SAT participation among California's larger public schools. How many individual named school sites in the state with a K-12 enrollment over 500 and a highest grade served of 8 or below had no SAT test takers? I just need the school_count, a single whole number. Please count a school as an individual school site with a name - district and county offices of education are not schools. Include every qualifying school site statewide even if it shows no SAT results at all; such a site simply had no test takers. By highest grade served I mean the top grade level the school serves, as a grade number from 1 through 12.

Evidence：

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS school_count FROM schools AS s JOIN frpm AS f ON f.CDSCode = s.CDSCode LEFT JOIN satscores AS t ON t.cds = s.CDSCode WHERE s.School IS NOT NULL AND f.`Enrollment (K-12)` > 500 AND CAST(f.`High Grade` AS INTEGER) BETWEEN 1 AND 8 AND COALESCE(t.NumTstTakr, 0) = 0
```

Agent SQL：
```sql
SELECT COUNT(*) AS school_count
FROM schools AS s
JOIN frpm AS f
  ON f.CDSCode = s.CDSCode
LEFT JOIN satscores AS sat
  ON sat.cds = s.CDSCode
WHERE s.School IS NOT NULL
  AND TRIM(s.School) <> ''
  AND f."Enrollment (K-12)" > 500
  AND (
    CASE
      WHEN INSTR(s.GSserved, '-') > 0
        THEN CAST(SUBSTR(s.GSserved, INSTR(s.GSserved, '-') + 1) AS INTEGER)
      WHEN s.GSserved GLOB '[0-9]*'
        THEN CAST(s.GSserved AS INTEGER)
      ELSE NULL
    END
  ) <= 8
  AND COALESCE(sat.NumTstTakr, 0) = 0;
```

觀察：model replies=7、tool attempts=10、SQL attempts=6、latency=29.164s；stop=final_sql_ready。



<a id="q30"></a>

## [Q30](failure-case-review.md#q30) · test · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／篩選對齊。

閉校排名前缺少 SAT sname IS NOT NULL；DENSE_RANK 本身已處理同分。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm documenting now-closed California schools whose students performed best on the SAT writing section, and I need the runner-up. Among schools whose status is Closed (not Active, Merged or Pending), and which have an average SAT writing score, can you tell me which school had the second-highest average SAT writing score? By second-highest I mean the best score strictly below the highest – if several schools share that score, please list them all. For each school, give me its name, its own district and county, and its average SAT writing score.

Evidence：SAT writing score: the average writing score of the school's SAT test takers.

Gold SQL（離線）：
```sql
WITH j AS (SELECT T2.School AS School, T2.District AS District, T2.County AS County, T1.AvgScrWrite AS AvgScrWrite FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE T2.StatusType = 'Closed' AND T1.AvgScrWrite IS NOT NULL AND T1.sname IS NOT NULL) SELECT School, District, County, AvgScrWrite FROM j WHERE AvgScrWrite = (SELECT MAX(AvgScrWrite) FROM j WHERE AvgScrWrite < (SELECT MAX(AvgScrWrite) FROM j))
```

Agent SQL：
```sql
WITH eligible AS (
    SELECT
        s.School,
        s.District,
        s.County,
        t.AvgScrWrite,
        DENSE_RANK() OVER (ORDER BY t.AvgScrWrite DESC) AS score_rank
    FROM schools AS s
    JOIN satscores AS t
        ON t.cds = s.CDSCode
    WHERE s.StatusType = 'Closed'
      AND t.AvgScrWrite IS NOT NULL
)
SELECT School, District, County, AvgScrWrite
FROM eligible
WHERE score_rank = 2
ORDER BY School;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=13.530s；stop=final_sql_ready。



<a id="q34"></a>

## [Q34](failure-case-review.md#q34) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／篩選對齊。

計算百分比前缺少 rtype='S'，新增 State='CA'；學校層母體不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among California schools whose students have an average SAT Math score above 400, what percentage offer virtual instruction, either exclusively or in part? Please give me a single percentage value rounded to one decimal place.

Evidence：In the school directory, the exclusive-virtual category is coded 'F' and the partial-virtual category is coded 'P'.

Gold SQL（離線）：
```sql
SELECT ROUND(100.0 * SUM(CASE WHEN s.Virtual IN ('F','P') THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct FROM satscores AS sat JOIN schools AS s ON sat.cds = s.CDSCode WHERE sat.rtype = 'S' AND sat.AvgScrMath > 400
```

Agent SQL：
```sql
SELECT ROUND(
    100.0 * SUM(CASE WHEN s.Virtual IN ('F', 'P') THEN 1 ELSE 0 END) / COUNT(*),
    1
)
FROM satscores AS sat
JOIN schools AS s ON s.CDSCode = sat.cds
WHERE s.State = 'CA'
  AND sat.AvgScrMath > 400;
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=14.056s；stop=final_sql_ready。



<a id="q36"></a>

## [Q36](failure-case-review.md#q36) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／數值型別。

printf('%.4f') 回傳文字，Gold ROUND 回傳數值；school name 來源及 NULL 判定亦不同。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a profile of Alameda County high schools, focusing on economic disadvantage among schools that serve up through 12th grade. Among those schools, can you tell me which one has the highest free meal rate? For each school you identify, give me one line with: the school name, its free meal rate to 4 decimal places, whether it is a charter school (Yes/No/Unknown), the grades it serves, and its SAT performance level (Below Average, Average, Above Average, or No SAT Data). Please use the school's grade span of enrollment from the school directory (the GSserved field of the schools table) both to decide whether it serves up through 12th grade and for the grades-it-serves column-do not use the free-meal program record's Low Grade/High Grade for either. If several schools tie for the highest free meal rate, list every one of them.

Evidence：Free meal rate = Free Meal Count (K-12) / Enrollment (K-12). SAT performance level is based on the SAT total (Reading + Math + Writing): Below Average if below 1200, Average if 1200 to 1500, Above Average if above 1500, and 'No SAT Data' if no SAT scores are available.

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT f.`School Name` AS school_name, f.`Free Meal Count (K-12)`*1.0/f.`Enrollment (K-12)` AS free_rate, sc.Charter, sc.GSserved, s.AvgScrRead, s.AvgScrMath, s.AvgScrWrite FROM frpm f LEFT JOIN schools sc ON sc.CDSCode = f.CDSCode LEFT JOIN satscores s ON s.cds = f.CDSCode WHERE f.`County Name` = 'Alameda' AND substr(sc.GSserved, -2) = '12') SELECT school_name, ROUND(free_rate, 4) AS highest_free_meal_rate, CASE WHEN Charter = 1 THEN 'Yes' WHEN Charter = 0 THEN 'No' ELSE 'Unknown' END AS is_charter, GSserved AS grades_served, CASE WHEN AvgScrRead IS NULL THEN 'No SAT Data' WHEN AvgScrRead + AvgScrMath + AvgScrWrite < 1200 THEN 'Below Average' WHEN AvgScrRead + AvgScrMath + AvgScrWrite <= 1500 THEN 'Average' ELSE 'Above Average' END AS sat_performance FROM cohort WHERE free_rate = (SELECT MAX(f2.`Free Meal Count (K-12)`*1.0/f2.`Enrollment (K-12)`) FROM frpm f2 JOIN schools s2 ON s2.CDSCode = f2.CDSCode WHERE f2.`County Name` = 'Alameda' AND substr(s2.GSserved, -2) = '12')
```

Agent SQL：
```sql
SELECT
    s.School AS school_name,
    printf('%.4f', f."Free Meal Count (K-12)" * 1.0 / f."Enrollment (K-12)") AS free_meal_rate,
    CASE
        WHEN s.Charter = 1 THEN 'Yes'
        WHEN s.Charter = 0 THEN 'No'
        ELSE 'Unknown'
    END AS charter_school,
    s.GSserved AS grades_served,
    CASE
        WHEN sat.AvgScrRead IS NULL OR sat.AvgScrMath IS NULL OR sat.AvgScrWrite IS NULL THEN 'No SAT Data'
        WHEN sat.AvgScrRead + sat.AvgScrMath + sat.AvgScrWrite < 1200 THEN 'Below Average'
        WHEN sat.AvgScrRead + sat.AvgScrMath + sat.AvgScrWrite <= 1500 THEN 'Average'
        ELSE 'Above Average'
    END AS sat_performance_level
FROM schools AS s
JOIN frpm AS f ON f.CDSCode = s.CDSCode
LEFT JOIN satscores AS sat ON sat.cds = s.CDSCode
WHERE s.County = 'Alameda'
  AND (s.GSserved LIKE '%-12' OR s.GSserved = '12')
  AND f."Enrollment (K-12)" > 0
  AND f."Free Meal Count (K-12)" * 1.0 / f."Enrollment (K-12)" = (
      SELECT MAX(f2."Free Meal Count (K-12)" * 1.0 / f2."Enrollment (K-12)")
      FROM schools AS s2
      JOIN frpm AS f2 ON f2.CDSCode = s2.CDSCode
      WHERE s2.County = 'Alameda'
        AND (s2.GSserved LIKE '%-12' OR s2.GSserved = '12')
        AND f2."Enrollment (K-12)" > 0
  );
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=30.268s；stop=final_sql_ready。



<a id="q45"></a>

## [Q45](failure-case-review.md#q45) · dev · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／同分處理。

以整個 cds 代替 School Code 作同分排序，且省略 rtype='S'／NumGE1500 非空。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm working on a story about the largest schools in the state with the worst SAT excellence rates. Among schools where at least 700 students took the SAT, can you find the school with the lowest SAT excellence rate? If several schools tie for the lowest rate, go with the one with the smallest school code. I just need that school's street, city, ZIP code and state so I can visit and request an interview.

Evidence：The SAT excellence rate is the share of SAT test takers scoring at least 1500. A school code is a number.

Gold SQL（離線）：
```sql
SELECT s.Street, s.City, s.Zip, s.State FROM satscores AS sat JOIN schools AS s ON s.CDSCode = sat.cds LEFT JOIN frpm AS f ON f.CDSCode = sat.cds WHERE sat.rtype = 'S' AND sat.NumGE1500 IS NOT NULL AND sat.NumTstTakr >= 700 ORDER BY 1.0 * sat.NumGE1500 / sat.NumTstTakr ASC, CAST(f.`School Code` AS INTEGER) ASC LIMIT 1
```

Agent SQL：
```sql
SELECT sch.Street, sch.City, sch.Zip, sch.State
FROM satscores AS s
JOIN schools AS sch ON sch.CDSCode = s.cds
WHERE s.NumTstTakr >= 700
ORDER BY s.NumGE1500 * 1.0 / s.NumTstTakr ASC,
         CAST(s.cds AS INTEGER) ASC
LIMIT 1;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=15.090s；stop=final_sql_ready。



<a id="q46"></a>

## [Q46](failure-case-review.md#q46) · test · california_schools

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／類別值。

精確比對 Provision 2 漏掉 Breakfast Provision 2（Washington Elementary／Santa Barbara）；資料探查顯示這是唯一額外Gold行，非混合provision字串。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm planning reviews of Provision 2 meal programs under the NSLP and want to see which cities concentrate magnet schools under that provision. For each city that has at least one, can you give me the number of the city's magnet schools that run a Provision 2 meal program? Use the city where the school is located, not its mailing city. Also, if a school's NSLP entry lists multiple provision types, don't count it as running Provision 2.

Evidence：NSLP is the National School Lunch Program. Provision 2 is a federal provision under the NSLP that lets a school serve meals at no charge to all students regardless of family income.

Gold SQL（離線）：
```sql
SELECT s.City AS City, COUNT(*) AS magnet_schools FROM frpm AS f JOIN schools AS s ON f.CDSCode = s.CDSCode WHERE s.Magnet = 1 AND f.`NSLP Provision Status` LIKE '%Provision 2%' GROUP BY s.City ORDER BY magnet_schools DESC, City
```

Agent SQL：
```sql
SELECT s.City, COUNT(DISTINCT s.CDSCode) AS magnet_school_count
FROM schools AS s
JOIN frpm AS f ON f.CDSCode = s.CDSCode
WHERE s.Magnet = 1
  AND f.`NSLP Provision Status` = 'Provision 2'
  AND s.City IS NOT NULL
GROUP BY s.City
ORDER BY s.City;
```

觀察：model replies=6、tool attempts=6、SQL attempts=3、latency=16.652s；stop=final_sql_ready。



<a id="q52"></a>

## [Q52](failure-case-review.md#q52) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／文字格式。

缺少 REPLACE(text, CHAR(10), ' ')，未將 rules text 轉為一行。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What rules text is printed on Benalish Knight? Return the distinct text as one line.

Evidence：

Gold SQL（離線）：
```sql
SELECT DISTINCT REPLACE(text, CHAR(10), ' ') FROM cards WHERE name = 'Benalish Knight' AND text IS NOT NULL
```

Agent SQL：
```sql
SELECT DISTINCT text
FROM cards
WHERE name = 'Benalish Knight';
```

觀察：model replies=4、tool attempts=3、SQL attempts=1、latency=10.388s；stop=final_sql_ready。



<a id="q59"></a>

## [Q59](failure-case-review.md#q59) · test · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／缺失值。

Italian language 記錄未要求 translation IS NOT NULL，將空翻譯記錄計入。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among the sets in the block "Ice Age", how many of them have an Italian translation?

Evidence：

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T1.id) FROM sets AS T1 INNER JOIN set_translations AS T2 ON T2.setCode = T1.code WHERE T1.block = 'Ice Age' AND T2.language = 'Italian' AND T2.translation IS NOT NULL
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT s.code)
FROM sets AS s
JOIN set_translations AS st ON st.setCode = s.code
WHERE s.block = 'Ice Age'
  AND st.language = 'Italian';
```

觀察：model replies=6、tool attempts=5、SQL attempts=2、latency=16.282s；stop=final_sql_ready。



<a id="q62"></a>

## [Q62](failure-case-review.md#q62) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／定義來源。

Brawl 合法性代替 leadershipSkills 的 commander 資格；計數單位亦改為 oracle ID。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I collect promotional printings and play Brawl. How many different creature cards that have a promotional printing can serve as a Brawl commander? I just want a single number back.

Evidence：A promotional printing is a printing of a card made as a promotion, as opposed to a regular set printing. Brawl is a Magic: The Gathering format; the deck's commander is the card that leads it, and only certain cards are legal as a Brawl commander.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT name) AS creature_cards_legal_brawl_commanders FROM cards WHERE isPromo = 1 AND instr(types, 'Creature') > 0 AND instr(leadershipSkills, '''brawl'': True') > 0
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT c.scryfallOracleId) AS n
FROM cards AS c
JOIN legalities AS l
  ON l.uuid = c.uuid
 AND l.format = 'brawl'
 AND l.status = 'Legal'
WHERE c.isPromo = 1
  AND c.types LIKE '%Creature%';
```

觀察：model replies=5、tool attempts=8、SQL attempts=4、latency=19.473s；stop=final_sql_ready。



<a id="q65"></a>

## [Q65](failure-case-review.md#q65) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／量度來源。

以 cards 實際列數代替 qualifying sets 的 SUM(totalSetSize)。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I have the count of sets with fewer than five translations of their name — now I need the gap in cards to size the translation budget. Can you give me the total number of cards contained in those sets? A few things to keep in mind: 'fewer than five' is strict, so a set with exactly five translations doesn't count. All sets count regardless of type or release (core set, expansion, promotional, online-only, etc.). If two languages have the identical translated name string for a set, that's one translation, not two. And a set's card count should be its full size, including promotional and related supplemental printings.

Evidence：A 'translation of a set's name' means the localized name of the set in another language, e.g. its French or Simplified Chinese name.

Gold SQL（離線）：
```sql
SELECT SUM(totalSetSize) AS total_cards FROM sets WHERE (SELECT COUNT(DISTINCT translation) FROM set_translations WHERE setCode = sets.code) < 5
```

Agent SQL：
```sql
WITH translation_counts AS (
    SELECT setCode, COUNT(DISTINCT translation) AS translation_count
    FROM set_translations
    GROUP BY setCode
),
qualifying_sets AS (
    SELECT s.code
    FROM sets AS s
    LEFT JOIN translation_counts AS t
        ON t.setCode = s.code
    WHERE COALESCE(t.translation_count, 0) < 5
)
SELECT COUNT(*) AS total_cards
FROM cards AS c
JOIN qualifying_sets AS q
    ON q.code = c.setCode;
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=14.142s；stop=final_sql_ready。



<a id="q66"></a>

## [Q66](failure-case-review.md#q66) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／量度來源。

total cards 使用 cards COUNT(*)，Gold 使用 totalSetSize；翻譯非空附加限制亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a multilingual catalog and want to gauge how much localizable content exists per kind of set. For every set type, I need the number of sets of that type that have an officially translated name, and the total number of cards in those sets. Please include every set type in the results, even ones where no set has an officially translated name (show zero for both values in that case), and sort the results alphabetically by set type.

Evidence：Set type: the expansion type of a set, such as core, expansion or promo. Officially translated name: the set's name rendered in another language, such as Italian or Chinese Traditional.

Gold SQL（離線）：
```sql
SELECT s.type, SUM(CASE WHEN EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code) THEN 1 ELSE 0 END) AS sets_with_translation, SUM(CASE WHEN EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code) THEN s.totalSetSize ELSE 0 END) AS total_cards FROM sets s GROUP BY s.type ORDER BY s.type
```

Agent SQL：
```sql
WITH translated_sets AS (
    SELECT DISTINCT setCode
    FROM set_translations
    WHERE translation IS NOT NULL
      AND TRIM(translation) <> ''
),
card_counts AS (
    SELECT setCode, COUNT(*) AS card_count
    FROM cards
    GROUP BY setCode
)
SELECT
    s.type AS set_type,
    COUNT(DISTINCT CASE WHEN ts.setCode IS NOT NULL THEN s.code END) AS translated_set_count,
    COALESCE(
        SUM(CASE WHEN ts.setCode IS NOT NULL THEN COALESCE(cc.card_count, 0) ELSE 0 END),
        0
    ) AS translated_set_card_count
FROM sets AS s
LEFT JOIN translated_sets AS ts ON ts.setCode = s.code
LEFT JOIN card_counts AS cc ON cc.setCode = s.code
GROUP BY s.type
ORDER BY s.type;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=24.654s；stop=final_sql_ready。



<a id="q67"></a>

## [Q67](failure-case-review.md#q67) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複計數。

COUNT(*) 重複計算多個 printing 共用的 ruling text，Gold COUNT(DISTINCT text)。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：How many rulings were issued for Mishra's Factory on the latest date any ruling for it exists? By "latest date" I mean the most recent calendar date on which any ruling for the card exists, and by Mishra's Factory I mean the card by that name across all of its printings. I only want that count.

Evidence：ruling: an official rules statement issued for a card on a given date

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T2.text) AS ruling_count FROM cards AS T1 INNER JOIN rulings AS T2 ON T1.uuid = T2.uuid WHERE T1.name = 'Mishra''s Factory' AND T2.date = (SELECT MAX(T4.date) FROM cards AS T3 INNER JOIN rulings AS T4 ON T3.uuid = T4.uuid WHERE T3.name = 'Mishra''s Factory')
```

Agent SQL：
```sql
SELECT COUNT(*) AS ruling_count
FROM rulings r
JOIN cards c ON c.uuid = r.uuid
WHERE c.name = 'Mishra''s Factory'
  AND r.date = (
    SELECT MAX(r2.date)
    FROM rulings r2
    JOIN cards c2 ON c2.uuid = r2.uuid
    WHERE c2.name = 'Mishra''s Factory'
  );
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=13.339s；stop=final_sql_ready。



<a id="q69"></a>

## [Q69](failure-case-review.md#q69) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／數值／文字排序。

MAX(frameVersion) 以文字比較，Gold CAST(frameVersion AS REAL) 後取最大。

診斷改寫：2次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a showcase of zero-mana-cost cards. What is the newest frame version used by any card with a converted mana cost of 0? Please give me that frame version value, and the number of cards in the database that use that frame version. The count should cover all cards in the database, not just the zero-cost ones. If several frame versions tie as the newest, give me each of them with its own count.

Evidence：Frame version: the edition of the card frame style a printing uses.

Gold SQL（離線）：
```sql
SELECT frameVersion, COUNT(*) AS card_count FROM cards WHERE CAST(frameVersion AS REAL) = (SELECT MAX(CAST(frameVersion AS REAL)) FROM cards WHERE convertedManaCost = 0) GROUP BY frameVersion
```

Agent SQL：
```sql
WITH newest_version AS (
    SELECT MAX(frameVersion) AS frameVersion
    FROM cards
    WHERE convertedManaCost = 0
)
SELECT c.frameVersion, COUNT(*) AS card_count
FROM cards AS c
JOIN newest_version AS n ON c.frameVersion = n.frameVersion
GROUP BY c.frameVersion;
```

觀察：model replies=5、tool attempts=4、SQL attempts=2、latency=15.867s；stop=final_sql_ready。



<a id="q76"></a>

## [Q76](failure-case-review.md#q76) · test · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／數值驗證。

GLOB '[0-9]*' 並非完整數字驗證，與 Gold 可正規化整數條件不同，亦排除負值。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling the weak end of the white-bordered printings. How many white-bordered cards have a power less than 3? I just need that single count - only white-bordered cards are in scope, and please don't include anything else in the answer.

Evidence：Power is a card's combat strength. A card whose power is shown as * has no known power.

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS weak_attackers FROM cards WHERE borderColor = 'white' AND power IS NOT NULL AND power <> '*' AND power = CAST(CAST(power AS INTEGER) AS TEXT) AND CAST(power AS INTEGER) < 3
```

Agent SQL：
```sql
SELECT COUNT(*) AS count
FROM cards
WHERE borderColor = 'white'
  AND power GLOB '[0-9]*'
  AND CAST(power AS REAL) < 3;
```

觀察：model replies=5、tool attempts=4、SQL attempts=2、latency=18.851s；stop=final_sql_ready。



<a id="q78"></a>

## [Q78](failure-case-review.md#q78) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／缺失值。

翻譯語言計數未要求 translation IS NOT NULL。ORDER BY 不影響 set-based EX。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing localized set icon assets and need to know the foreign-language name coverage of every Magic: The Gathering set released in 2020. For each set released in 2020 (meaning its release date falls within the calendar year 2020), please give me the set's name, its keyrune code, and the number of languages in which the set has an official translated name. Nothing else.

Evidence：keyrune code: the code for the set's image icon; official translated name: the set's name rendered in a foreign language by the game's publisher.

Gold SQL（離線）：
```sql
SELECT s.name, s.keyruneCode, COUNT(DISTINCT st.language) AS translated_languages FROM sets s LEFT JOIN set_translations st ON st.setCode = s.code AND st.translation IS NOT NULL WHERE strftime('%Y', s.releaseDate) = '2020' GROUP BY s.id, s.name, s.keyruneCode ORDER BY s.name
```

Agent SQL：
```sql
SELECT
    s.name,
    s.keyruneCode,
    COUNT(DISTINCT st.language) AS language_count
FROM sets AS s
LEFT JOIN set_translations AS st
    ON st.setCode = s.code
WHERE s.releaseDate >= '2020-01-01'
  AND s.releaseDate < '2021-01-01'
GROUP BY s.id, s.name, s.keyruneCode
ORDER BY s.releaseDate, s.name;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=18.992s；stop=final_sql_ready。



<a id="q79"></a>

## [Q79](failure-case-review.md#q79) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／量度來源。

計 cards 列數而非 SUM(totalSetSize)，並額外排除 English／空翻譯。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm sizing a catalogue page of 2017 sets that were localized for international markets. How many cards were there in total across the Magic: The Gathering sets released in 2017 (between January 1 and December 31, 2017) that have a name in a language other than English? A set counts as localized if its name has a foreign-language translation. Include every card in each qualifying set, counting promotional and related supplemental printings as part of the set. I just need the single total across all qualifying sets, not per-set numbers.

Evidence：A foreign-language translation is a set's name rendered in a language other than English (e.g. Chinese Simplified, German, Spanish).

Gold SQL（離線）：
```sql
SELECT SUM(s.totalSetSize) AS total_cards FROM sets s WHERE s.releaseDate BETWEEN '2017-01-01' AND '2017-12-31' AND EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code)
```

Agent SQL：
```sql
SELECT COUNT(*) AS total_cards
FROM cards c
JOIN sets s ON s.code = c.setCode
WHERE s.releaseDate >= '2017-01-01'
  AND s.releaseDate < '2018-01-01'
  AND EXISTS (
      SELECT 1
      FROM set_translations st
      WHERE st.setCode = s.code
        AND st.language <> 'English'
        AND st.translation IS NOT NULL
        AND TRIM(st.translation) <> ''
  );
```

觀察：model replies=9、tool attempts=10、SQL attempts=6、latency=34.001s；stop=final_sql_ready。



<a id="q80"></a>

## [Q80](failure-case-review.md#q80) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／數值驗證。

直接 CAST(power AS REAL)<3，未過濾非數字 power；SQLite 可把非數字轉為0。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I've already looked at the heavy hitters in duel deck B (the 'b' deck). Now I want to check the light end: how many cards in duel deck B are not available in foil and have attack power below 3? Note that 'below 3' means strictly below 3 — a power of exactly 3 doesn't count.

Evidence：

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS card_count FROM cards WHERE duelDeck = 'b' AND hasFoil = 0 AND power IS NOT NULL AND power = TRIM(CAST(power AS INTEGER)) AND CAST(power AS REAL) < 3
```

Agent SQL：
```sql
SELECT COUNT(*) AS count
FROM cards
WHERE duelDeck = 'b'
  AND hasFoil = 0
  AND CAST(power AS REAL) < 3;
```

觀察：model replies=6、tool attempts=5、SQL attempts=3、latency=22.785s；stop=final_sql_ready。



<a id="q81"></a>

## [Q81](failure-case-review.md#q81) · dev · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／過度去重。

先 DISTINCT name,artist，將 printing 計數改為卡名計數，與 Gold COUNT(*) 不同。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm writing a spotlight piece on card artists, and I need to know: among black-bordered cards that are obtainable on Magic Arena and have a printed power of 10 or greater, which artist illustrated the most of them? Please give me the artist's name and the number of those cards they illustrated. A card counts even if it's also available outside Arena, as long as it can be obtained on Arena. If several artists tie for the most, list every one of them along with that count.

Evidence：Black border means the card's border color is black; power is the combat strength printed on a creature card, and '10 or greater' means the printed power reads as a number that is at least 10 (10, 11, 12, and so on).

Gold SQL（離線）：
```sql
WITH counts AS (SELECT artist, COUNT(*) AS card_count FROM cards WHERE borderColor='black' AND LOWER(availability) LIKE '%arena%' AND CAST(power AS INTEGER) >= 10 GROUP BY artist) SELECT artist, card_count FROM counts WHERE card_count=(SELECT MAX(card_count) FROM counts)
```

Agent SQL：
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

觀察：model replies=8、tool attempts=7、SQL attempts=5、latency=29.567s；stop=final_sql_ready。



<a id="q82"></a>

## [Q82](failure-case-review.md#q82) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／跨列條件。

availability='paper' 只檢查個別 printing，未按 name 檢查曾否出現 MTGO printing。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm going through my paper collection before sharing it publicly, and I want to check something about the cards Wizards of the Coast has flagged. How many different cards are there that carry a sensitive content warning, are available in paper form, and have never been available on Magic Online (MTGO)? I just need that one count.

Evidence：MTGO means Magic: The Gathering Online, the official online version of the game. A sensitive content warning means Wizards of the Coast has marked the card for having sensitive content.

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS card_count FROM (SELECT name FROM cards WHERE hasContentWarning = 1 GROUP BY name HAVING MAX(CASE WHEN availability LIKE '%paper%' THEN 1 ELSE 0 END) = 1 AND MAX(CASE WHEN availability LIKE '%mtgo%' THEN 1 ELSE 0 END) = 0)
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT name) AS card_count
FROM cards
WHERE hasContentWarning = 1
  AND availability = 'paper';
```

觀察：model replies=6、tool attempts=5、SQL attempts=3、latency=16.955s；stop=final_sql_ready。



<a id="q84"></a>

## [Q84](failure-case-review.md#q84) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加篩選。

限定 availability 的兩個字串及 type Creature／數字字首，較 Gold 包含 arena、排除 mtgo 的條件更窄。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm cataloguing Arena-exclusive illustrated art of big creatures. How many artists have illustrated at least one black-bordered card that is available on Arena but never on Magic Online and has a fixed printed power of at least 5? I want just the number of artists, nothing else. Count across all printings in the collection with no time restriction. Note that a card whose power varies is not a fixed number, so it shouldn't count as power 5 or more.

Evidence：Arena and Magic Online are online platforms; a card's availability lists every platform it can be played on: 'arena' is Arena and 'mtgo' is Magic Online. Power is the attack strength printed on a creature card. Black-bordered refers to the standard card border color black.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT artist) AS artists FROM cards WHERE borderColor = 'black' AND availability LIKE '%arena%' AND availability NOT LIKE '%mtgo%' AND CAST(power AS REAL) >= 5
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT artist)
FROM cards
WHERE availability IN ('arena', 'arena,paper')
  AND borderColor = 'black'
  AND type LIKE '%Creature%'
  AND power GLOB '[0-9]*'
  AND CAST(power AS INTEGER) >= 5
  AND artist IS NOT NULL;
```

觀察：model replies=9、tool attempts=8、SQL attempts=6、latency=26.405s；stop=final_sql_ready。



<a id="q86"></a>

## [Q86](failure-case-review.md#q86) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／編碼／排序。

把 latest calendar frame year 硬設為 'future'，沒有按 CAST(frameVersion AS INTEGER) 選年份。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among the Commander-leadable cards that the Card Kingdom catalog lists for both a foil printing and a regular non-foil printing – cards listed for only one of the two printings don't count – I want the single most recent card frame year (the latest calendar year among the frame versions), and the count of cards in that group whose frame version is that year. Please return just that one row: the frame year and its card count.

Evidence：A card 'may lead a Commander deck' if it can be the deck's commander – the one card that leads the deck and sets its color identity – not merely be included among the deck's other cards.

Gold SQL（離線）：
```sql
WITH cmd AS (SELECT frameVersion, substr(leadershipSkills, instr(leadershipSkills, 'commander')) AS tail FROM cards WHERE cardKingdomId IS NOT NULL AND cardKingdomFoilId IS NOT NULL) SELECT frameVersion AS frame_year, COUNT(*) AS card_count FROM cmd WHERE substr(tail, length('commander') + length('True'), length('True')) = 'True' GROUP BY frameVersion ORDER BY CAST(frameVersion AS INTEGER) DESC LIMIT 1
```

Agent SQL：
```sql
SELECT frameVersion AS frame_year, COUNT(*) AS card_count
FROM cards
WHERE cardKingdomId IS NOT NULL
  AND cardKingdomId <> ''
  AND cardKingdomFoilId IS NOT NULL
  AND cardKingdomFoilId <> ''
  AND leadershipSkills LIKE '%''commander'': True%'
  AND frameVersion = 'future'
GROUP BY frameVersion;
```

觀察：model replies=10、tool attempts=11、SQL attempts=7、latency=43.472s；stop=final_sql_ready。



<a id="q87"></a>

## [Q87](failure-case-review.md#q87) · test · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複計數。

跨 printing 的 rulings 未以 date,text 去重。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm compiling the official rulings archive for the Magic: The Gathering card Fireball. How many official rulings have ever been issued for Fireball? I need the total across all time, with no date restriction.

Evidence：A ruling is an official clarification issued by Wizards of the Coast about how a card works.

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS ruling_count FROM (SELECT DISTINCT r.date, r.text FROM rulings AS r INNER JOIN cards AS c ON r.uuid = c.uuid WHERE c.name = 'Fireball')
```

Agent SQL：
```sql
SELECT COUNT(*) AS ruling_count
FROM rulings r
JOIN cards c ON c.uuid = r.uuid
WHERE c.name = 'Fireball';
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=10.216s；stop=final_sql_ready。



<a id="q88"></a>

## [Q88](failure-case-review.md#q88) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複計數。

按 card name COUNT(*) 前未按 name,date,text 去重，亦只保留 originalType 直接相符的 printings。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which card whose original type is 'Creature - Elf' has received the most rulings, and how many rulings has it received? I want the card name and the number of rulings. A card and all of its printings/reprints count as one and the same card. If several cards tie for the most rulings, list every one of them.

Evidence：A ruling is an official rules clarification issued for a card, on the date it was issued.

Gold SQL（離線）：
```sql
WITH elf_cards AS (SELECT DISTINCT name FROM cards WHERE originalType = 'Creature - Elf'), elf_rulings AS (SELECT c.name, r.date, r.text FROM cards c JOIN rulings r ON c.uuid = r.uuid WHERE c.name IN (SELECT name FROM elf_cards) GROUP BY c.name, r.date, r.text), counts AS (SELECT name, COUNT(*) AS ruling_count FROM elf_rulings GROUP BY name) SELECT name, ruling_count FROM counts WHERE ruling_count = (SELECT MAX(ruling_count) FROM counts) ORDER BY name
```

Agent SQL：
```sql
SELECT c.name, COUNT(*) AS ruling_count
FROM cards AS c
JOIN rulings AS r ON r.uuid = c.uuid
WHERE c.originalType = 'Creature - Elf'
GROUP BY c.name
HAVING COUNT(*) = (
    SELECT MAX(ruling_count)
    FROM (
        SELECT COUNT(*) AS ruling_count
        FROM cards AS c2
        JOIN rulings AS r2 ON r2.uuid = c2.uuid
        WHERE c2.originalType = 'Creature - Elf'
        GROUP BY c2.name
    )
)
ORDER BY c.name;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=23.014s；stop=final_sql_ready。



<a id="q92"></a>

## [Q92](failure-case-review.md#q92) · dev · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R7／排序契約。

題目要求 Foil id alphabetical order，Agent 改用 CAST(... AS INTEGER) 排序。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I keep a Card Kingdom catalogue and want to list the creature cards that Card Kingdom stocks in both foil and non-foil printings. A card counts as stocked in both printings when both its Card Kingdom Foil id and its Card Kingdom id are present. Please give me one row per card, with each card's Card Kingdom Foil id and Card Kingdom id, and nothing else. I only need the three cards with the lowest Card Kingdom Foil ids in alphabetical order, with ties broken by the Card Kingdom id.

Evidence：Card Kingdom Foil id: the retailer's identifier for the foil printing; Card Kingdom id: the retailer's identifier for the non-foil printing.

Gold SQL（離線）：
```sql
SELECT cardKingdomFoilId, cardKingdomId FROM cards WHERE cardKingdomFoilId IS NOT NULL AND cardKingdomId IS NOT NULL AND types LIKE '%Creature%' ORDER BY cardKingdomFoilId, cardKingdomId LIMIT 3
```

Agent SQL：
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

觀察：model replies=4、tool attempts=3、SQL attempts=1、latency=14.124s；stop=final_sql_ready。



<a id="q96"></a>

## [Q96](failure-case-review.md#q96) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／定義來源。

有文字框以 text 非空代替 isTextless=0；frame 包含 future 且計 oracle ID 而非卡名。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm cataloguing modern-frame printings. How many different cards that have a text box were printed with a frame version of 2015 or a later year? I just need that single count.

Evidence：Frame version: the version of the card frame style, given as the year the frame style was introduced.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT name) AS number_of_cards FROM cards WHERE isTextless = 0 AND CAST(frameVersion AS INTEGER) >= 2015
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT scryfallOracleId)
FROM cards
WHERE frameVersion IN ('2015', 'future')
  AND text IS NOT NULL
  AND TRIM(text) <> '';
```

觀察：model replies=5、tool attempts=4、SQL attempts=2、latency=16.934s；stop=final_sql_ready。



<a id="q98"></a>

## [Q98](failure-case-review.md#q98) · dev · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／條件替換。

layout 清單代替 side IS NOT NULL；日期 replace/date 與 Gold substr 年份不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a retrospective of promotional cards. Can you get me the card name of every promotional card that has multiple faces printed on it (like split, transform, or adventure cards) and was originally released in 2019? By "originally released" I mean the card's own first-release date, not the release date of the set its promotional printing belongs to, and "in 2019" means January 1 through December 31, 2019. If a card has more than one promotional printing from that year, list it just once. I only want the card names, nothing else.

Evidence：

Gold SQL（離線）：
```sql
SELECT DISTINCT name FROM cards WHERE isPromo = 1 AND side IS NOT NULL AND substr(originalReleaseDate, 1, 4) = '2019'
```

Agent SQL：
```sql
SELECT DISTINCT name
FROM cards
WHERE isPromo = 1
  AND layout IN ('split', 'transform', 'adventure', 'modal_dfc', 'aftermath', 'meld', 'flip')
  AND date(replace(originalReleaseDate, '/', '-')) BETWEEN '2019-01-01' AND '2019-12-31'
ORDER BY name;
```

觀察：model replies=9、tool attempts=9、SQL attempts=6、latency=33.406s；stop=final_sql_ready。



<a id="q102"></a>

## [Q102](failure-case-review.md#q102) · dev · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／數值／文字排序。

MAX(frameVersion) 使用文字排序，Gold 將 frameVersion CAST 為 INTEGER。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which set contains the Aven Mindcensor printing that uses the newest card frame? I want the set's name and its release date. Count every printing, including promotional and online-only ones. If several printings share the newest frame, use the most recently released one; if the release dates tie too, list each such set once. Please give me the set name, not its code.

Evidence：Frame version: the frame style used for a printing; frame styles are identified by the year that style was introduced.

Gold SQL（離線）：
```sql
SELECT DISTINCT s.name AS setName, s.releaseDate FROM cards AS c JOIN sets AS s ON s.code = c.setCode WHERE c.name = 'Aven Mindcensor' AND CAST(c.frameVersion AS INTEGER) = (SELECT MAX(CAST(frameVersion AS INTEGER)) FROM cards WHERE name = 'Aven Mindcensor') AND s.releaseDate = (SELECT MAX(s2.releaseDate) FROM cards AS c2 JOIN sets AS s2 ON s2.code = c2.setCode WHERE c2.name = 'Aven Mindcensor' AND CAST(c2.frameVersion AS INTEGER) = (SELECT MAX(CAST(frameVersion AS INTEGER)) FROM cards WHERE name = 'Aven Mindcensor'))
```

Agent SQL：
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

觀察：model replies=7、tool attempts=7、SQL attempts=4、latency=25.203s；stop=final_sql_ready。



<a id="q103"></a>

## [Q103](failure-case-review.md#q103) · dev · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／缺失值。

NOT EXISTS 未限制 Spanish translation 非空，把只有 NULL 翻譯記錄當已有西班牙名。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm auditing which recent products were never localized for Spanish-speaking markets. Can you find every set released in calendar year 2020 that has no Spanish name? For each of those, I just need the set code and the set's release date.

Evidence：By "Spanish name" I mean the Spanish-language version of a set's name.

Gold SQL（離線）：
```sql
SELECT s.code, s.releaseDate FROM sets s WHERE s.releaseDate BETWEEN '2020-01-01' AND '2020-12-31' AND NOT EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code AND t.language = 'Spanish' AND t.translation IS NOT NULL) ORDER BY s.releaseDate, s.code
```

Agent SQL：
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

觀察：model replies=8、tool attempts=7、SQL attempts=4、latency=26.636s；stop=final_sql_ready。



<a id="q105"></a>

## [Q105](failure-case-review.md#q105) · dev · card_games

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／缺失值。

COUNT(DISTINCT language) 未排除 NULL／空 translation，零翻譯處理已有 LEFT JOIN。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：We're planning translation work for upcoming set releases and want to know how extensively a recent release year was localized. What was the average number of languages in which sets released in 2016 had their names translated? By 'released in 2016' I mean the release date falls within calendar year 2016. Every set released in 2016 counts toward the average, including any whose names were translated into no language at all (those count as zero). A language counts for a set when the set's name is rendered in that language. Please give me just that one number, rounded to two decimals.

Evidence：Set name translation: the set's name rendered in another language.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(n), 2) AS avg_languages FROM (SELECT s.id, COUNT(DISTINCT CASE WHEN st.translation IS NOT NULL AND TRIM(st.translation) <> '' THEN st.language END) AS n FROM sets s LEFT JOIN set_translations st ON s.code = st.setCode WHERE substr(s.releaseDate, 1, 4) = '2016' GROUP BY s.id)
```

Agent SQL：
```sql
SELECT ROUND(AVG(language_count), 2) AS average_languages
FROM (
    SELECT s.id, COUNT(DISTINCT st.language) AS language_count
    FROM sets AS s
    LEFT JOIN set_translations AS st ON st.setCode = s.code
    WHERE s.releaseDate >= '2016-01-01'
      AND s.releaseDate < '2017-01-01'
    GROUP BY s.id
);
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=18.467s；stop=final_sql_ready。



<a id="q108"></a>

## [Q108](failure-case-review.md#q108) · dev · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R6／關係限制。

把 set translation 語言集合額外綁定相同 setCode 的 printing，且改 COUNT(*) 為 DISTINCT uuid。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a localization coverage report. Among the languages into which the card sets themselves were translated (i.e., have a set translation), which language has the fewest printings whose flavor text was translated into that language? Please give me the language name and the number of such printings. If several languages tie for the fewest, list all of them, ordered alphabetically by language name.

Evidence：Set translation: a card set's official release in another language.

Gold SQL（離線）：
```sql
WITH set_langs AS (
    SELECT DISTINCT language FROM set_translations
),
counts AS (
    SELECT fd.language, COUNT(*) AS printings
    FROM foreign_data fd
    WHERE fd.language IN
        (SELECT language FROM set_langs)
    AND fd.flavorText IS NOT NULL
    AND fd.flavorText <> ''
    GROUP BY fd.language
)
SELECT language, printings
FROM counts
WHERE printings = (SELECT MIN(printings) FROM counts)
ORDER BY language ASC;
```

Agent SQL：
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

觀察：model replies=6、tool attempts=8、SQL attempts=3、latency=22.101s；stop=final_sql_ready。



<a id="q117"></a>

## [Q117](failure-case-review.md#q117) · test · card_games

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／計數單位。

以 printing uuid 去重代替卡名 name 去重。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a black artifact flavor-showcase section for a trade binder. How many mono-black Artifact cards have a foreign-language printing that shows flavor text in that language? By mono-black I mean black is the card's only colour, and by Artifact cards I include artifacts combined with another card type, like an Artifact Creature. I'm counting cards, not printings – a card is the same card regardless of set, print run, or language. Just give me one number.

Evidence：In Magic colour notation, B denotes black, and a card is mono-black when black is its only colour.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT c.name) AS card_count FROM cards AS c WHERE c.colors = 'B' AND c.type LIKE '%Artifact%' AND EXISTS (SELECT 1 FROM foreign_data AS f WHERE f.uuid = c.uuid AND LENGTH(f.flavorText) > 0)
```

Agent SQL：
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

觀察：model replies=7、tool attempts=7、SQL attempts=4、latency=24.380s；stop=final_sql_ready。



<a id="q120"></a>

## [Q120](failure-case-review.md#q120) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／分母定義。

分母用了每年全部 badges，而非所有年份 Student badges 總數。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the difference in percentage points between the 2010 and 2011 shares of all Student badges, taking the 2010 share minus the 2011 share?

Evidence：

Gold SQL（離線）：
```sql
SELECT CAST(SUM(IIF(STRFTIME('%Y', Date) = '2010', 1, 0)) AS REAL) * 100 / COUNT(Id) - CAST(SUM(IIF(STRFTIME('%Y', Date) = '2011', 1, 0)) AS REAL) * 100 / COUNT(Id) FROM badges WHERE Name = 'Student'
```

Agent SQL：
```sql
WITH yearly AS (
    SELECT
        substr(Date, 1, 4) AS year,
        SUM(CASE WHEN Name = 'Student' THEN 1 ELSE 0 END) AS student_badges,
        COUNT(*) AS all_badges
    FROM badges
    WHERE substr(Date, 1, 4) IN ('2010', '2011')
    GROUP BY substr(Date, 1, 4)
)
SELECT
    100.0 * MAX(CASE WHEN year = '2010' THEN student_badges END)
          / MAX(CASE WHEN year = '2010' THEN all_badges END)
  - 100.0 * MAX(CASE WHEN year = '2011' THEN student_badges END)
          / MAX(CASE WHEN year = '2011' THEN all_badges END)
    AS difference_in_percentage_points
FROM yearly;
```

觀察：model replies=6、tool attempts=5、SQL attempts=3、latency=21.182s；stop=final_sql_ready。



<a id="q128"></a>

## [Q128](failure-case-review.md#q128) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複加權。

AVG(user.Age) 在 comment join 後計算，重複發連結的用戶被重複加權。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to profile the users who drop links in comment threads. What is the average age of the users who posted a comment containing a website link? Please round it to two decimal places. That single value is all I need back.

Evidence：A comment counts as containing a website if its content contains 'http://'.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(T.Age), 2) AS average_age FROM (SELECT DISTINCT T2.Id, T2.Age FROM comments AS T1 INNER JOIN users AS T2 ON T1.UserId = T2.Id WHERE T1.Text LIKE '%http://%') AS T
```

Agent SQL：
```sql
SELECT ROUND(AVG(u.Age), 2) AS average_age
FROM comments AS c
JOIN users AS u ON u.Id = c.UserId
WHERE instr(c.Text, 'http://') > 0;
```

觀察：model replies=5、tool attempts=4、SQL attempts=1、latency=15.732s；stop=final_sql_ready。



<a id="q130"></a>

## [Q130](failure-case-review.md#q130) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／地點編碼。

Location 精確等於 India，漏掉逗號分隔城市／國家中的 India token。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a report for the site owners on where people who started posting during 2010 were located, with a focus on India. Could you tell me how many of the users whose first post was created in 2010 are located in India? By 2010 I mean the calendar year 2010, and by India I mean the country itself, not any place whose name merely contains the word.

Evidence：A user's first post is the earliest-created post among the posts that user owns.

Gold SQL（離線）：
```sql
WITH RECURSIVE fp AS (SELECT OwnerUserId AS uid, MIN(CreaionDate) AS fdate FROM posts WHERE OwnerUserId IS NOT NULL GROUP BY OwnerUserId), locs AS (SELECT u.Id AS uid, u.Location AS loc FROM users u JOIN fp ON fp.uid = u.Id WHERE fp.fdate >= '2010-01-01' AND fp.fdate < '2011-01-01'), parts(uid, head, tail) AS (SELECT uid, CASE WHEN instr(loc, ',') > 0 THEN substr(loc, 1, instr(loc, ',') - 1) ELSE loc END, CASE WHEN instr(loc, ',') > 0 THEN substr(loc, instr(loc, ',') + 1) ELSE NULL END FROM locs UNION ALL SELECT uid, CASE WHEN instr(tail, ',') > 0 THEN substr(tail, 1, instr(tail, ',') - 1) ELSE tail END, CASE WHEN instr(tail, ',') > 0 THEN substr(tail, instr(tail, ',') + 1) ELSE NULL END FROM parts WHERE tail IS NOT NULL) SELECT COUNT(*) AS users_in_india FROM parts WHERE TRIM(head) = 'India'
```

Agent SQL：
```sql
WITH first_posts AS (
    SELECT OwnerUserId, MIN(CreaionDate) AS first_post_date
    FROM posts
    WHERE OwnerUserId IS NOT NULL
    GROUP BY OwnerUserId
)
SELECT COUNT(*) AS users_count
FROM first_posts AS fp
JOIN users AS u ON u.Id = fp.OwnerUserId
WHERE fp.first_post_date >= '2010-01-01'
  AND fp.first_post_date < '2011-01-01'
  AND TRIM(u.Location) = 'India';
```

觀察：model replies=5、tool attempts=6、SQL attempts=3、latency=20.829s；stop=final_sql_ready。



<a id="q131"></a>

## [Q131](failure-case-review.md#q131) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複加權。

AVG(Reputation) 在 posts join 後計算，未先按使用者去重。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling the authors behind poorly received R posts to see if they tend to be low-reputation members. Can you give me the average reputation of the users who own posts tagged with the R tag that have a score below 20? Just the single number, rounded to the nearest whole number.

Evidence：'r' is the tag used on this site for the R programming language for statistical computing.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(u.Reputation)) AS avg_reputation FROM users u WHERE u.Id IN (SELECT p.OwnerUserId FROM posts p WHERE p.Score < 20 AND p.Tags LIKE '%' || '<' || 'r' || '>' || '%')
```

Agent SQL：
```sql
SELECT ROUND(AVG(u.Reputation)) AS avg_reputation
FROM posts p
JOIN users u ON u.Id = p.OwnerUserId
WHERE p.Score < 20
  AND p.Tags LIKE '%<r>%';
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=11.607s；stop=final_sql_ready。



<a id="q132"></a>

## [Q132](failure-case-review.md#q132) · test · codebase_community

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R7／輸出形狀。

Gold 單行四個 scalar，Agent 輸出兩個群組行，並額外加入群組名稱欄。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together the yearly activity report with a Germany-focused breakdown of who did the editing, covering posts created in calendar year 2012. For the 2012 posts whose last editor is a user based in Germany, I need the total score; and for all other posts created in 2012, I need their total score as well. Also, how many Germany-based users were the last editor of at least one 2012 post, and what their combined reputation is, as shown on their profiles. A user based in Germany is one whose profile location is in Germany.

Evidence：A post's last editor is the user who made its most recent edit.

Gold SQL（離線）：
```sql
WITH posts_2012 AS (SELECT Id, Score, LastEditorUserId AS EditorId FROM posts WHERE CreaionDate >= '2012-01-01' AND CreaionDate < '2013-01-01'), german_editors AS (SELECT DISTINCT u.Id, u.Reputation FROM posts_2012 p JOIN users u ON u.Id = p.EditorId WHERE u.Location LIKE '%Germany%') SELECT (SELECT SUM(p.Score) FROM posts_2012 p JOIN german_editors g ON g.Id = p.EditorId) AS german_edited_score, (SELECT SUM(Score) FROM posts_2012 WHERE EditorId IS NULL OR EditorId NOT IN (SELECT Id FROM german_editors)) AS remaining_score, (SELECT COUNT(*) FROM german_editors) AS editor_count, (SELECT SUM(Reputation) FROM german_editors) AS editor_reputation
```

Agent SQL：
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

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=32.478s；stop=final_sql_ready。



<a id="q134"></a>

## [Q134](failure-case-review.md#q134) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複加權。

SUM(Reputation) 直接 join 多篇 posts，未按 owner 唯一計算。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'd like to gauge the standing of the community members behind the R posts on one day. Could you tell me the combined reputation of the users who own the posts tagged R that were last active on 2014-08-27? I just need that one number, covering the whole calendar day 2014-08-27.

Evidence：R: the R language for statistical computing.

Gold SQL（離線）：
```sql
SELECT SUM(Reputation) AS combined_reputation FROM users WHERE Id IN (SELECT OwnerUserId FROM posts WHERE Tags LIKE '%' || '<' || 'R' || '>' || '%' AND LasActivityDate LIKE '2014-08-27%')
```

Agent SQL：
```sql
SELECT SUM(u.Reputation) AS combined_reputation
FROM posts AS p
JOIN users AS u ON u.Id = p.OwnerUserId
WHERE p.LasActivityDate >= '2014-08-27'
  AND p.LasActivityDate < '2014-08-28'
  AND p.Tags LIKE '%<R>%';
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=16.811s；stop=final_sql_ready。



<a id="q135"></a>

## [Q135](failure-case-review.md#q135) · test · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／連結方向。

把 incoming links 改為雙向，並硬設 target ID及未按 PostId 去重。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the total score of the questions tagged 'r' that link to the question titled "A Probability distribution value exceeding 1 is OK?"? I only need the total score of those linking questions.

Evidence：'r' here means the R programming language for statistical computing, not the letter on its own.

Gold SQL（離線）：
```sql
WITH target AS (SELECT Id FROM posts WHERE Title = 'A Probability distribution value exceeding 1 is OK?'), linkers AS (SELECT DISTINCT pl.PostId AS pid FROM postLinks pl INNER JOIN target tg ON pl.RelatedPostId = tg.Id) SELECT SUM(p.Score) AS total_score FROM linkers l INNER JOIN posts p ON p.Id = l.pid WHERE EXISTS (SELECT 1 FROM tags t WHERE t.TagName = 'r' AND p.Tags LIKE '%' || '<' || t.TagName || '>' || '%')
```

Agent SQL：
```sql
SELECT SUM(p.Score) AS total_score
FROM postLinks AS l
JOIN posts AS p
  ON p.Id = CASE
      WHEN l.PostId = 4220 THEN l.RelatedPostId
      ELSE l.PostId
  END
WHERE (l.PostId = 4220 OR l.RelatedPostId = 4220)
  AND p.PostTypeId = 1
  AND p.Tags LIKE '%<r>%';
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=19.977s；stop=final_sql_ready。



<a id="q136"></a>

## [Q136](failure-case-review.md#q136) · dev · codebase_community

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／地點編碼。

Location='Germany' 漏掉城市加國家的 location；排名邏輯已處理第二不同值。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling users by where they say they live. Among the users located in Germany, who has the second most badges of all time? By second most I mean the highest badge total strictly below the top holder's total. If several users tie at that total, include all of them. Please give me each such user's display name and their badge total, ordered by display name.

Evidence：Badges: the badges a user has obtained, one badge award per record.

Gold SQL（離線）：
```sql
WITH per_user AS (SELECT u.Id, u.DisplayName, COUNT(b.Id) AS badge_count FROM users u LEFT JOIN badges b ON b.UserId = u.Id WHERE u.Location LIKE '%Germany%' GROUP BY u.Id, u.DisplayName) SELECT DisplayName, badge_count FROM per_user WHERE badge_count = (SELECT MAX(badge_count) FROM per_user p2 WHERE p2.badge_count < (SELECT MAX(badge_count) FROM per_user)) ORDER BY DisplayName
```

Agent SQL：
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

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=17.425s；stop=final_sql_ready。



<a id="q137"></a>

## [Q137](failure-case-review.md#q137) · test · codebase_community

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／地點編碼。

LIKE '%CA%' 不是 California／CA token 匹配，會誤配其他字串並漏掉完整 California。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm planning regional outreach and want to know which California-based account draws the most profile attention. Among users whose stated location shows they are based in California, give me the user id, display name, profile view count, and reputation of the user or users with the most profile views. If several such users tie for the most profile views, list every one of them with those same four values.

Evidence：CA is the two-letter state code for California.

Gold SQL（離線）：
```sql
WITH ca AS (SELECT Id, DisplayName, Views, Reputation FROM users WHERE INSTR(',' || REPLACE(UPPER(TRIM(Location)), ' ', '') || ',', ',' || 'CA' || ',') > 0 OR INSTR(',' || REPLACE(UPPER(TRIM(Location)), ' ', '') || ',', ',' || UPPER('California') || ',') > 0) SELECT Id, DisplayName, Views, Reputation FROM ca WHERE Views = (SELECT MAX(Views) FROM ca)
```

Agent SQL：
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

觀察：model replies=6、tool attempts=5、SQL attempts=3、latency=19.723s；stop=final_sql_ready。



<a id="q139"></a>

## [Q139](failure-case-review.md#q139) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／地點編碼。

Location 精確等於 India，Gold 包含城市／地區文字中的 India。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a report on international participation. How many users located in India had earned a Yearling badge before 2014? 'Before 2014' should mean before 1 January 2014. I just need the single count, nothing else.

Evidence：'Yearling' is a badge a member earns for a year of activity on the site.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T1.UserId) AS user_count FROM badges AS T1 INNER JOIN users AS T2 ON T1.UserId = T2.Id WHERE T2.Location LIKE '%India%' AND T1.Name = 'Yearling' AND T1.Date < '2014-01-01'
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT b.UserId) AS user_count
FROM badges AS b
JOIN users AS u ON u.Id = b.UserId
WHERE b.Name = 'Yearling'
  AND u.Location = 'India'
  AND b.Date < '2014-01-01';
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=11.586s；stop=final_sql_ready。



<a id="q140"></a>

## [Q140](failure-case-review.md#q140) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／佔位值。

COUNT(DISTINCT DisplayName) 未排除字串 'NaN' 佔位名稱。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a summary of how active badge-holders present themselves on the site. How many different display names appear among the adult users who obtained the Supporter badge? By adult I mean age 19 to 65 inclusive, and please cover all time. I just need that one number.

Evidence：NaN stands for a user who never set a display name.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT CASE WHEN u.DisplayName IS NULL OR u.DisplayName = 'NaN' THEN NULL ELSE u.DisplayName END) AS different_display_names FROM users AS u INNER JOIN badges AS b ON u.Id = b.UserId WHERE b.Name = 'Supporter' AND u.Age BETWEEN 19 AND 65
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT u.DisplayName) AS display_name_count
FROM badges AS b
JOIN users AS u ON u.Id = b.UserId
WHERE b.Name = 'Supporter'
  AND u.Age BETWEEN 19 AND 65;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=12.310s；stop=final_sql_ready。



<a id="q142"></a>

## [Q142](failure-case-review.md#q142) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／指標誤解。

youngest 用 CreationDate ASC 代替最小 Age。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm auditing accounts on the stats forum. What is the id of the youngest user account whose display name is Michael? If two or more such accounts tie as the youngest, give me the smallest id.

Evidence：

Gold SQL（離線）：
```sql
SELECT Id FROM users WHERE DisplayName = 'Michael' AND Age = (SELECT MIN(Age) FROM users WHERE DisplayName = 'Michael') ORDER BY Id LIMIT 1
```

Agent SQL：
```sql
SELECT Id
FROM users
WHERE DisplayName = 'Michael'
ORDER BY CreationDate ASC, Id ASC
LIMIT 1;
```

觀察：model replies=4、tool attempts=3、SQL attempts=1、latency=10.620s；stop=final_sql_ready。



<a id="q144"></a>

## [Q144](failure-case-review.md#q144) · test · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／地點編碼。

只接受整欄 India，漏掉 City, India；EXISTS 已避免重複使用者。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What was the average reputation of users located in India who created a post in 2010? Please give me a single number rounded to two decimal places. Note: 'in 2010' means the calendar year 2010 based on the post's creation date, and any type of post counts. A user counts as located in India only if their location is actually India - a place that merely contains the word India (like the US state Indiana) doesn't count.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(u.Reputation), 2) AS avg_reputation FROM users u WHERE (trim(u.Location) = 'India' OR (instr(u.Location, ',') > 0 AND trim(substr(u.Location, instr(u.Location, ',') + 1)) = 'India')) AND u.Id IN (SELECT p.OwnerUserId FROM posts p WHERE p.CreaionDate >= '2010-01-01' AND p.CreaionDate < '2011-01-01')
```

Agent SQL：
```sql
SELECT ROUND(AVG(u.Reputation), 2)
FROM users AS u
WHERE TRIM(LOWER(u.Location)) = 'india'
  AND EXISTS (
      SELECT 1
      FROM posts AS p
      WHERE p.OwnerUserId = u.Id
        AND p.CreaionDate >= '2010-01-01'
        AND p.CreaionDate < '2011-01-01'
  );
```

觀察：model replies=5、tool attempts=4、SQL attempts=1、latency=14.613s；stop=final_sql_ready。



<a id="q145"></a>

## [Q145](failure-case-review.md#q145) · dev · codebase_community

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／量度來源。

以 votes 明細 COUNT(VoteTypeId=2) 代替使用者 profile UpVotes。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling our most active contributors of 2012. Among the users who created more than ten posts in 2012 (judged by each post's creation date), what is their average number of up-votes cast and their average age? Please give me a single row with both averages, each rounded to two decimal places.

Evidence：Up-vote: a vote a user cast in favor of a post.

Gold SQL（離線）：
```sql
WITH active AS (SELECT OwnerUserId FROM posts WHERE CreaionDate >= '2012-01-01' AND CreaionDate < '2013-01-01' GROUP BY OwnerUserId HAVING COUNT(*) > 10) SELECT ROUND(AVG(u.UpVotes), 2) AS avg_upvotes, ROUND(AVG(u.Age), 2) AS avg_age FROM active AS a JOIN users AS u ON u.Id = a.OwnerUserId
```

Agent SQL：
```sql
WITH prolific_users AS (
    SELECT OwnerUserId AS UserId
    FROM posts
    WHERE CreaionDate >= '2012-01-01'
      AND CreaionDate < '2013-01-01'
      AND OwnerUserId IS NOT NULL
    GROUP BY OwnerUserId
    HAVING COUNT(*) > 10
),
upvotes_cast AS (
    SELECT UserId, COUNT(*) AS UpVotesCast
    FROM votes
    WHERE VoteTypeId = 2
      AND UserId IS NOT NULL
    GROUP BY UserId
)
SELECT
    ROUND(AVG(COALESCE(upvotes_cast.UpVotesCast, 0)), 2) AS AverageUpVotesCast,
    ROUND(AVG(users.Age), 2) AS AverageAge
FROM prolific_users
JOIN users ON users.Id = prolific_users.UserId
LEFT JOIN upvotes_cast ON upvotes_cast.UserId = prolific_users.UserId;
```

觀察：model replies=10、tool attempts=11、SQL attempts=7、latency=39.833s；stop=final_sql_ready。



<a id="q153"></a>

## [Q153](failure-case-review.md#q153) · dev · debit_card_specializing

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加篩選。

yearmonth 年度有消費後，再要求 transactions_1k 抽樣表存在2012交易，排除原集合。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing our 2012 performance and want to see which client segments hold our small-scale customers. For each client segment, can you tell me how many customers had total consumption below 30,000 over the whole of 2012? Please count only customers who used their cards at some point during 2012, and treat 30,000 as a strict limit - someone at exactly 30,000 doesn't count. I just need the client segment and the number of such customers per segment.

Evidence：Consumption means the amount spent through a customer's fuel cards.

Gold SQL（離線）：
```sql
WITH yearly AS (SELECT CustomerID, SUM(Consumption) AS total_consumption FROM yearmonth WHERE Date >= '201201' AND Date <= '201212' GROUP BY CustomerID HAVING SUM(Consumption) < 30000) SELECT c.Segment AS segment, COUNT(*) AS customers FROM yearly AS y INNER JOIN customers AS c ON c.CustomerID = y.CustomerID GROUP BY c.Segment ORDER BY c.Segment
```

Agent SQL：
```sql
SELECT c.Segment, COUNT(*) AS customer_count
FROM customers AS c
JOIN (
    SELECT CustomerID
    FROM yearmonth
    WHERE Date >= '201201' AND Date <= '201212'
    GROUP BY CustomerID
    HAVING SUM(Consumption) < 30000
) AS annual
    ON annual.CustomerID = c.CustomerID
WHERE EXISTS (
    SELECT 1
    FROM transactions_1k AS t
    WHERE t.CustomerID = c.CustomerID
      AND t.Date >= '2012-01-01'
      AND t.Date < '2013-01-01'
)
GROUP BY c.Segment;
```

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=25.393s；stop=final_sql_ready。



<a id="q155"></a>

## [Q155](failure-case-review.md#q155) · dev · debit_card_specializing

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／浮點截斷。

同一首末時間端點，julianday差*1440=3669.9999998509884，CAST截成3669；unix秒差整除為3670。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to gauge how spread out our high-value fuelling activity in the Czech Republic was over the recorded window. How many whole minutes elapsed from the first to the last fuel transaction at gas stations in the Czech Republic with a price over 1000? Please round down to whole minutes.

Evidence：Czech Republic means the gas station is in the CZE country.

Gold SQL（離線）：
```sql
SELECT (strftime('%s', MAX(Date || ' ' || Time)) - strftime('%s', MIN(Date || ' ' || Time))) / (5 * 13 - 5) AS minutes FROM transactions_1k AS T1 INNER JOIN gasstations AS T2 ON T1.GasStationID = T2.GasStationID WHERE T2.Country = 'CZE' AND T1.Price > 1000
```

Agent SQL：
```sql
SELECT CAST(
    (julianday(MAX(t.Date || ' ' || t.Time)) -
     julianday(MIN(t.Date || ' ' || t.Time))) * 1440
    AS INTEGER
) AS elapsed_minutes
FROM transactions_1k AS t
JOIN gasstations AS g
    ON g.GasStationID = t.GasStationID
WHERE g.Country = 'CZE'
  AND t.Price > 1000;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=23.120s；stop=final_sql_ready。



<a id="q157"></a>

## [Q157](failure-case-review.md#q157) · dev · debit_card_specializing

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

Gold 單行 EUR、CZK 兩個均值，Agent 輸出 Currency 群組兩行。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together currency-specific pricing proposals and need a sense of typical quarterly fuel consumption. Among customers who have fuel consumption recorded in the second quarter of 2013 (April, May and June 2013), what is the average amount of fuel consumed over the whole quarter by an EUR-paying customer, and the same average for a CZK-paying customer? Please round both averages to two decimal places. By EUR-paying / CZK-paying I mean a customer whose account currency is EUR / CZK.

Evidence：EUR-paying / CZK-paying: a customer whose account currency is EUR / CZK

Gold SQL（離線）：
```sql
WITH q2 AS (SELECT CustomerID, SUM(Consumption) AS total FROM yearmonth WHERE Date BETWEEN '201304' AND '201306' GROUP BY CustomerID) SELECT ROUND(AVG(CASE WHEN c.Currency = 'EUR' THEN q2.total END), 2) AS eur_avg_quarter, ROUND(AVG(CASE WHEN c.Currency = 'CZK' THEN q2.total END), 2) AS czk_avg_quarter FROM customers c JOIN q2 ON q2.CustomerID = c.CustomerID
```

Agent SQL：
```sql
WITH quarterly AS (
    SELECT CustomerID, SUM(Consumption) AS quarter_consumption
    FROM yearmonth
    WHERE Date IN ('201304', '201305', '201306')
    GROUP BY CustomerID
)
SELECT
    c.Currency,
    ROUND(AVG(q.quarter_consumption), 2) AS average_quarter_consumption
FROM quarterly q
JOIN customers c ON c.CustomerID = q.CustomerID
WHERE c.Currency IN ('EUR', 'CZK')
GROUP BY c.Currency
ORDER BY c.Currency;
```

觀察：model replies=6、tool attempts=10、SQL attempts=6、latency=23.016s；stop=final_sql_ready。



<a id="q165"></a>

## [Q165](failure-case-review.md#q165) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／額外欄位。

題目列 players，Gold 只回傳 player_name；Agent 加 player_api_id、height、平均值。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：List the ten players taller than 180 cm with the highest mean recorded heading accuracy, highest first. Break mean ties by player API ID.

Evidence：

Gold SQL（離線）：
```sql
SELECT p.player_name FROM Player AS p JOIN Player_Attributes AS a ON a.player_api_id = p.player_api_id WHERE p.height > 180 GROUP BY p.player_api_id, p.player_name ORDER BY AVG(a.heading_accuracy) DESC, p.player_api_id LIMIT 10
```

Agent SQL：
```sql
SELECT
    p.player_api_id,
    p.player_name,
    p.height,
    AVG(pa.heading_accuracy) AS mean_heading_accuracy
FROM Player AS p
JOIN Player_Attributes AS pa
    ON pa.player_api_id = p.player_api_id
WHERE p.height > 180
  AND pa.heading_accuracy IS NOT NULL
GROUP BY p.player_api_id, p.player_name, p.height
ORDER BY mean_heading_accuracy DESC, p.player_api_id ASC
LIMIT 10;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=14.757s；stop=final_sql_ready。



<a id="q172"></a>

## [Q172](failure-case-review.md#q172) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複加權。

在 Match join 後 AVG(height)，同一球員按出賽次數加權，Gold 每個 player 一次。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the average height, in centimetres, of the players taller than 180 cm who have appeared in the home team's number-3 lineup slot? This should cover the whole recorded match history with no season or date restriction. 'Taller than 180' means strictly taller than 180 cm. Please round the final average to two decimal places and return just that single value.

Evidence：Number-3 lineup slot: each match records a home team's starting eleven as eleven ordered player slots; the number-3 slot is the home team's third slot.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(height), 2) AS avg_height FROM (SELECT p.height AS height FROM Player p JOIN Match m ON m.home_player_3 = p.player_api_id WHERE p.height > 180 GROUP BY p.player_api_id)
```

Agent SQL：
```sql
SELECT ROUND(AVG(p.height), 2) AS average_height_cm
FROM Match AS m
JOIN Player AS p ON p.player_api_id = m.home_player_3
WHERE p.height > 180;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=15.437s；stop=final_sql_ready。



<a id="q173"></a>

## [Q173](failure-case-review.md#q173) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／有效值域。

防守評級僅排除 NULL，未限制 low/medium/high，分母可包含無效字串。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm sizing up how defensive-minded the young generation is. Among players born after 1990 (i.e., born in 1991 or later) who have a defensive work rate rating, what share are rated high? A player counts as rated high if they've been rated high at any point in their career. Give me that share as a percentage rounded to two decimal places - nothing else.

Evidence：Defensive work rate: a player's rating for defensive effort, on a low / medium / high scale.

Gold SQL（離線）：
```sql
SELECT ROUND(100.0 * (SELECT COUNT(DISTINCT pa.player_api_id) FROM Player p JOIN Player_Attributes pa ON pa.player_api_id = p.player_api_id WHERE CAST(STRFTIME('%Y', p.birthday) AS INTEGER) > 1990 AND pa.defensive_work_rate = 'high') / (SELECT COUNT(DISTINCT pa.player_api_id) FROM Player p JOIN Player_Attributes pa ON pa.player_api_id = p.player_api_id WHERE CAST(STRFTIME('%Y', p.birthday) AS INTEGER) > 1990 AND pa.defensive_work_rate IN ('low','medium','high')), 2) AS share_pct
```

Agent SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN a.defensive_work_rate = 'high' THEN p.player_api_id END)
    / COUNT(DISTINCT p.player_api_id),
    2
) AS percentage
FROM Player AS p
JOIN Player_Attributes AS a
    ON a.player_api_id = p.player_api_id
WHERE p.birthday >= '1991-01-01'
  AND a.defensive_work_rate IS NOT NULL;
```

觀察：model replies=6、tool attempts=5、SQL attempts=2、latency=17.098s；stop=final_sql_ready。



<a id="q174"></a>

## [Q174](failure-case-review.md#q174) · dev · european_football_2

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／零次實體。

從 player_matches AVG，漏掉 shortlist 中該季零出場球員；日期字串界線亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I've shortlisted the players whose overall rating as of 31 December 2010 was above 80 - strictly above 80, that is. How many matches did these players play on average during the 2010/2011 season? Please give me just that single average, rounded to two decimals.

Evidence：

Gold SQL（離線）：
```sql
WITH latest AS (SELECT player_api_id, MAX(date) AS md FROM Player_Attributes WHERE date <= '2010-12-31 00:00:00' GROUP BY player_api_id), shortlist AS (SELECT p.player_api_id FROM latest l JOIN Player_Attributes a ON a.player_api_id = l.player_api_id AND a.date = l.md JOIN Player p ON p.player_api_id = l.player_api_id WHERE a.overall_rating > 80 GROUP BY p.player_api_id), slots AS (SELECT id, home_player_1 AS pid FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_2 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_3 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_4 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_5 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_6 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_7 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_8 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_9 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_10 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, home_player_11 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_1 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_2 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_3 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_4 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_5 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_6 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_7 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_8 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_9 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_10 FROM Match WHERE season = '2010/2011' UNION ALL SELECT id, away_player_11 FROM Match WHERE season = '2010/2011'), apps AS (SELECT pid, COUNT(DISTINCT id) AS matches FROM slots WHERE pid IS NOT NULL GROUP BY pid) SELECT ROUND(AVG(COALESCE(x.matches, 0)), 2) AS average_matches FROM shortlist s LEFT JOIN apps x ON x.pid = s.player_api_id
```

Agent SQL：
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

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=96.735s；stop=final_sql_ready。



<a id="q175"></a>

## [Q175](failure-case-review.md#q175) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／有效值域。

<> 'medium' 未限制 low/high，空白或無效 current rating 亦納入。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the average height in centimeters of players whose current defensive work rate grade is not medium? Use each player's most recent rating record to determine their current grade, and round the result to two decimal places. I just need that single number.

Evidence：Defensive work rate grades run low, medium and high.

Gold SQL（離線）：
```sql
WITH latest AS (SELECT player_api_id, defensive_work_rate, ROW_NUMBER() OVER (PARTITION BY player_api_id ORDER BY date DESC, id DESC) AS rn FROM Player_Attributes) SELECT ROUND(AVG(p.height), 2) AS average_height FROM latest l JOIN Player p ON p.player_api_id = l.player_api_id WHERE l.rn = 1 AND l.defensive_work_rate IN ('low', 'high')
```

Agent SQL：
```sql
WITH ranked AS (
    SELECT
        player_api_id,
        defensive_work_rate,
        ROW_NUMBER() OVER (
            PARTITION BY player_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Player_Attributes
)
SELECT ROUND(AVG(p.height), 2) AS average_height_cm
FROM Player p
JOIN ranked r ON r.player_api_id = p.player_api_id
WHERE r.rn = 1
  AND LOWER(TRIM(r.defensive_work_rate)) <> 'medium';
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=13.999s；stop=final_sql_ready。



<a id="q176"></a>

## [Q176](failure-case-review.md#q176) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／日期邊界。

date <= '2014-09-19' 與含時間 '2014-09-19 00:00:00' 字串比較不同；球隊去重用 t.id 而非 team_api_id。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a report on team playing styles. First, consider only teams whose chance creation passing class was Risky at any point in the recorded history. Among those, I want the short names that are carried by more than one club. For each such short name, please give me: the short name, the number of clubs that carry it, and the average chance creation passing risk of those clubs that was in force on 19 September 2014, rounded to one decimal place. Sort the results by that average, highest first; if two averages are the same, order them alphabetically by short name.

Evidence：A team's chance creation passing class is 'Risky' when chanceCreationPassingClass = 'Risky'; its chance creation passing risk is the chanceCreationPassing value in force on the date in question.

Gold SQL（離線）：
```sql
WITH risky AS (SELECT DISTINCT team_api_id FROM Team_Attributes WHERE chanceCreationPassingClass = 'Risky'), cur AS (SELECT team_api_id, chanceCreationPassing FROM Team_Attributes ta WHERE ta.date = (SELECT MAX(date) FROM Team_Attributes x WHERE x.team_api_id = ta.team_api_id AND x.date <= '2014-09-19 00:00:00')) SELECT t.team_short_name AS team_short_name, COUNT(DISTINCT t.team_api_id) AS n_teams, ROUND(AVG(c.chanceCreationPassing), 1) AS avg_passing FROM Team t JOIN risky r ON r.team_api_id = t.team_api_id JOIN cur c ON c.team_api_id = t.team_api_id GROUP BY t.team_short_name HAVING COUNT(DISTINCT t.team_api_id) > 1 ORDER BY avg_passing DESC, t.team_short_name
```

Agent SQL：
```sql
WITH risky_teams AS (
    SELECT DISTINCT team_api_id
    FROM Team_Attributes
    WHERE chanceCreationPassingClass = 'Risky'
),
attributes_as_of_date AS (
    SELECT
        team_api_id,
        chanceCreationPassing,
        ROW_NUMBER() OVER (
            PARTITION BY team_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Team_Attributes
    WHERE date <= '2014-09-19'
)
SELECT
    t.team_short_name,
    COUNT(DISTINCT t.id) AS club_count,
    ROUND(AVG(a.chanceCreationPassing), 1) AS avg_chance_creation_passing_risk
FROM risky_teams AS r
JOIN Team AS t
    ON t.team_api_id = r.team_api_id
JOIN attributes_as_of_date AS a
    ON a.team_api_id = t.team_api_id
   AND a.rn = 1
GROUP BY t.team_short_name
HAVING COUNT(DISTINCT t.id) > 1
ORDER BY avg_chance_creation_passing_risk DESC, t.team_short_name ASC;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=18.759s；stop=final_sql_ready。



<a id="q177"></a>

## [Q177](failure-case-review.md#q177) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／先篩後排名。

最新有效 defensive grade 應先篩 low/medium/high，Agent 改篩 overall_rating 非空再排名。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to gauge how tall the current medium-defensive-work players from the 1990-1995 birth cohort are. Please find the average height, in centimetres, of players born from 1990 through 1995 inclusive whose defensive work rating is medium, and round the average to two decimals. A player's rating is the grade on their most recent record that carries a grade.

Evidence：The defensive work rating grades are low, medium and high.

Gold SQL（離線）：
```sql
WITH latest_grade AS (SELECT player_api_id, defensive_work_rate, ROW_NUMBER() OVER (PARTITION BY player_api_id ORDER BY date DESC, id DESC) AS rn FROM Player_Attributes WHERE defensive_work_rate IN ('low', 'medium', 'high')) SELECT ROUND(AVG(p.height), 2) AS average_height FROM Player p JOIN latest_grade g ON g.player_api_id = p.player_api_id AND g.rn = 1 WHERE SUBSTR(p.birthday, 1, 4) BETWEEN '1990' AND '1995' AND g.defensive_work_rate = 'medium'
```

Agent SQL：
```sql
WITH ranked_attributes AS (
    SELECT
        player_api_id,
        defensive_work_rate,
        ROW_NUMBER() OVER (
            PARTITION BY player_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Player_Attributes
    WHERE overall_rating IS NOT NULL
)
SELECT ROUND(AVG(p.height), 2) AS average_height_cm
FROM Player AS p
JOIN ranked_attributes AS a
    ON a.player_api_id = p.player_api_id
WHERE a.rn = 1
  AND a.defensive_work_rate = 'medium'
  AND CAST(strftime('%Y', p.birthday) AS INTEGER) BETWEEN 1990 AND 1995
  AND p.height IS NOT NULL;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=15.462s；stop=final_sql_ready。



<a id="q186"></a>

## [Q186](failure-case-review.md#q186) · dev · european_football_2

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／零次實體。

平均只覆蓋曾出現於 home_player_3 的玩家，Gold 分母涵蓋全部 Player。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing home-match outcomes by lineup slot and want one number: across the whole player population, what is the average of the total home-team goals scored in the matches where a player appeared as the home team's third listed player? In other words, for each player, take all matches where they were the home team's third listed player and add up the home team's goals in those matches; give me the average of those totals over all players, rounded to two decimal places.

Evidence：The home team's third listed player means the player recorded third in the home team's lineup for a match.

Gold SQL（離線）：
```sql
SELECT ROUND(SUM(m.home_team_goal) * 1.0 / COUNT(DISTINCT p.player_api_id), 2) AS avg_home_goals_per_player FROM Player AS p LEFT JOIN Match AS m ON m.home_player_3 = p.player_api_id
```

Agent SQL：
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

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=16.227s；stop=final_sql_ready。



<a id="q187"></a>

## [Q187](failure-case-review.md#q187) · test · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／計數單位。

按國家 COUNT(*) 計 player-match 次數，Gold 計 DISTINCT player_api_id。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm studying where small, low-weight players are concentrated across European leagues. Which country's league matches featured the fewest players weighing at most 160 pounds? If several countries tie for the fewest, give me every tied country's name. Include all seasons in the database, and count the players who took part in those matches.

Evidence：Players are associated with a country through the matches they played in that country's league; all 22 players of a match, the 11 of the home team and the 11 of the away team, took part in it.

Gold SQL（離線）：
```sql
WITH appearances AS (SELECT country_id, home_player_1 AS player_api_id FROM Match UNION SELECT country_id, home_player_2 FROM Match UNION SELECT country_id, home_player_3 FROM Match UNION SELECT country_id, home_player_4 FROM Match UNION SELECT country_id, home_player_5 FROM Match UNION SELECT country_id, home_player_6 FROM Match UNION SELECT country_id, home_player_7 FROM Match UNION SELECT country_id, home_player_8 FROM Match UNION SELECT country_id, home_player_9 FROM Match UNION SELECT country_id, home_player_10 FROM Match UNION SELECT country_id, home_player_11 FROM Match UNION SELECT country_id, away_player_1 FROM Match UNION SELECT country_id, away_player_2 FROM Match UNION SELECT country_id, away_player_3 FROM Match UNION SELECT country_id, away_player_4 FROM Match UNION SELECT country_id, away_player_5 FROM Match UNION SELECT country_id, away_player_6 FROM Match UNION SELECT country_id, away_player_7 FROM Match UNION SELECT country_id, away_player_8 FROM Match UNION SELECT country_id, away_player_9 FROM Match UNION SELECT country_id, away_player_10 FROM Match UNION SELECT country_id, away_player_11 FROM Match), counts AS (SELECT T1.name AS name, COUNT(DISTINCT T3.player_api_id) AS n_players FROM Country AS T1 INNER JOIN appearances AS T2 ON T1.id = T2.country_id INNER JOIN Player AS T3 ON T3.player_api_id = T2.player_api_id WHERE T3.weight <= 160 GROUP BY T1.name) SELECT name FROM counts WHERE n_players = (SELECT MIN(n_players) FROM counts)
```

Agent SQL：
```sql
WITH match_players AS (
    SELECT m.country_id, m.id AS match_id, p.player_id
    FROM "Match" AS m
    JOIN (
        SELECT id, home_player_1 AS player_id FROM "Match"
        UNION ALL SELECT id, home_player_2 FROM "Match"
        UNION ALL SELECT id, home_player_3 FROM "Match"
        UNION ALL SELECT id, home_player_4 FROM "Match"
        UNION ALL SELECT id, home_player_5 FROM "Match"
        UNION ALL SELECT id, home_player_6 FROM "Match"
        UNION ALL SELECT id, home_player_7 FROM "Match"
        UNION ALL SELECT id, home_player_8 FROM "Match"
        UNION ALL SELECT id, home_player_9 FROM "Match"
        UNION ALL SELECT id, home_player_10 FROM "Match"
        UNION ALL SELECT id, home_player_11 FROM "Match"
        UNION ALL SELECT id, away_player_1 FROM "Match"
        UNION ALL SELECT id, away_player_2 FROM "Match"
        UNION ALL SELECT id, away_player_3 FROM "Match"
        UNION ALL SELECT id, away_player_4 FROM "Match"
        UNION ALL SELECT id, away_player_5 FROM "Match"
        UNION ALL SELECT id, away_player_6 FROM "Match"
        UNION ALL SELECT id, away_player_7 FROM "Match"
        UNION ALL SELECT id, away_player_8 FROM "Match"
        UNION ALL SELECT id, away_player_9 FROM "Match"
        UNION ALL SELECT id, away_player_10 FROM "Match"
        UNION ALL SELECT id, away_player_11 FROM "Match"
    ) AS p ON p.id = m.id
    WHERE p.player_id IS NOT NULL
),
country_counts AS (
    SELECT c.id AS country_id, c.name, COUNT(*) AS player_match_count
    FROM match_players AS mp
    JOIN Player AS p ON p.player_api_id = mp.player_id
    JOIN Country AS c ON c.id = mp.country_id
    WHERE p.weight <= 160
    GROUP BY c.id, c.name
)
SELECT name
FROM country_counts
WHERE player_match_count = (SELECT MIN(player_match_count) FROM country_counts);
```

觀察：model replies=4、tool attempts=7、SQL attempts=1、latency=29.376s；stop=final_sql_ready。



<a id="q189"></a>

## [Q189](failure-case-review.md#q189) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／有效值域。

current attacking grade 的分母只排 NULL/空字串，未限制 low/medium/high。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What percentage of left-footed players currently has a low attacking work rate? Use each player's most recent attribute record. Only count left-footed players whose current record includes an attacking work rate rating - those without one should be left out of the share. Give me a single percentage, rounded to one decimal place.

Evidence：Attacking work rate: how much effort a player puts into attacking plays, rated low, medium or high.

Gold SQL（離線）：
```sql
WITH latest AS (SELECT player_api_id, MAX(date) AS d FROM Player_Attributes GROUP BY player_api_id) SELECT ROUND(100.0 * COUNT(DISTINCT CASE WHEN pa.attacking_work_rate = 'low' THEN pa.player_api_id END) / COUNT(DISTINCT CASE WHEN pa.attacking_work_rate IN ('low','medium','high') THEN pa.player_api_id END), 1) AS pct FROM Player_Attributes pa JOIN latest l ON pa.player_api_id = l.player_api_id AND pa.date = l.d WHERE pa.preferred_foot = 'left'
```

Agent SQL：
```sql
WITH ranked AS (
    SELECT
        player_api_id,
        preferred_foot,
        attacking_work_rate,
        ROW_NUMBER() OVER (
            PARTITION BY player_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Player_Attributes
)
SELECT ROUND(
    100.0 * SUM(CASE WHEN LOWER(TRIM(attacking_work_rate)) = 'low' THEN 1 ELSE 0 END)
    / COUNT(*),
    1
) AS percentage
FROM ranked
WHERE rn = 1
  AND LOWER(TRIM(preferred_foot)) = 'left'
  AND attacking_work_rate IS NOT NULL
  AND TRIM(attacking_work_rate) <> '';
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=16.704s；stop=final_sql_ready。



<a id="q191"></a>

## [Q191](failure-case-review.md#q191) · dev · european_football_2

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／日期邊界。

date <= '2007-08-30' 對 timestamp 排除當日有時間記錄，Gold date(date) 包括全天。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：How many players had a jumping score of 80 or higher in the player fitness assessments made between 22 February 2007 and 30 August 2007, with both of those dates included in the period? For clarity, the jumping score is the player's jumping assessment on a 1-100 scale.

Evidence：jumping score: the player's jumping assessment on a 1-100 scale

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT player_api_id) AS player_count FROM Player_Attributes WHERE jumping >= 80 AND date(date) BETWEEN '2007-02-22' AND '2007-08-30'
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT player_api_id) AS player_count
FROM Player_Attributes
WHERE date >= '2007-02-22'
  AND date <= '2007-08-30'
  AND jumping >= 80;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=10.798s；stop=final_sql_ready。



<a id="q194"></a>

## [Q194](failure-case-review.md#q194) · dev · financial

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R2／欄位語義。

把平均薪金欄 A11 錯認為 A12，影響地區選擇及差額。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among female clients living in the district with the lowest average salary, give the account IDs of the oldest client and the difference between the highest and lowest district-average salaries.

Evidence：

Gold SQL（離線）：
```sql
WITH oldest AS (SELECT c.client_id FROM client AS c JOIN district AS d ON d.district_id = c.district_id WHERE c.gender = 'F' AND d.A11 = (SELECT MIN(A11) FROM district) ORDER BY c.birth_date, c.client_id LIMIT 1) SELECT DISTINCT a.account_id, (SELECT MAX(A11) - MIN(A11) FROM district) FROM oldest AS o JOIN disp AS x ON x.client_id = o.client_id JOIN account AS a ON a.account_id = x.account_id ORDER BY a.account_id
```

Agent SQL：
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

觀察：model replies=10、tool attempts=12、SQL attempts=7、latency=34.134s；stop=final_sql_ready。



<a id="q201"></a>

## [Q201](failure-case-review.md#q201) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／擁有人關係。

male_accounts 沒有限制 disp.type='OWNER'，可把獲授權男性算為擁有人。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For loans dated in 1996 and 1997 across accounts owned by male clients, what was the percentage growth in total loan amount from 1996 to 1997?

Evidence：

Gold SQL（離線）：
```sql
SELECT CAST((SUM(CASE WHEN STRFTIME('%Y', T1.date) = '1997' THEN T1.amount ELSE 0 END) - SUM(CASE WHEN STRFTIME('%Y', T1.date) = '1996' THEN T1.amount ELSE 0 END)) AS REAL) * 100 / SUM(CASE WHEN STRFTIME('%Y', T1.date) = '1996' THEN T1.amount ELSE 0 END) FROM loan AS T1 INNER JOIN account AS T2 ON T1.account_id = T2.account_id INNER JOIN disp AS T3 ON T3.account_id = T2.account_id INNER JOIN client AS T4 ON T4.client_id = T3.client_id WHERE T4.gender = 'M' AND T3.type = 'OWNER'
```

Agent SQL：
```sql
WITH male_accounts AS (
    SELECT DISTINCT d.account_id
    FROM disp AS d
    JOIN client AS c ON c.client_id = d.client_id
    WHERE c.gender = 'M'
),
yearly_totals AS (
    SELECT
        CAST(strftime('%Y', l.date) AS INTEGER) AS year,
        SUM(l.amount) AS total_amount
    FROM loan AS l
    JOIN male_accounts AS ma ON ma.account_id = l.account_id
    WHERE l.date >= '1996-01-01'
      AND l.date < '1998-01-01'
    GROUP BY year
)
SELECT
    100.0 * (
        SUM(CASE WHEN year = 1997 THEN total_amount END)
        - SUM(CASE WHEN year = 1996 THEN total_amount END)
    ) / SUM(CASE WHEN year = 1996 THEN total_amount END) AS percentage_growth
FROM yearly_totals;
```

觀察：model replies=5、tool attempts=8、SQL attempts=3、latency=20.953s；stop=final_sql_ready。



<a id="q204"></a>

## [Q204](failure-case-review.md#q204) · test · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加篩選。

加 disp.type='OWNER'，Gold 的 held accounts 包含所有 disposition；join 亦可能重複交易。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：As part of a data-quality review for a segment report, I need to know how much of the recorded transaction activity for one of our segments has no payment purpose noted. How many transactions are there, over the whole recorded history, on the accounts held by male customers born between 1974 and 1976 (birth years 1974, 1975 and 1976), for which no payment purpose is noted? Please give me just that single number.

Evidence：Payment purpose: the stated reason or note recorded for a transaction.

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS txn_count FROM trans AS t WHERE (t.k_symbol IS NULL OR TRIM(t.k_symbol) = '') AND t.account_id IN (SELECT d.account_id FROM disp AS d INNER JOIN client AS c ON d.client_id = c.client_id WHERE c.gender = 'M' AND STRFTIME('%Y', c.birth_date) BETWEEN '1974' AND '1976')
```

Agent SQL：
```sql
SELECT COUNT(*) AS transaction_count
FROM trans AS t
JOIN disp AS d
  ON d.account_id = t.account_id
 AND d.type = 'OWNER'
JOIN client AS c
  ON c.client_id = d.client_id
WHERE c.gender = 'M'
  AND CAST(strftime('%Y', c.birth_date) AS INTEGER) BETWEEN 1974 AND 1976
  AND (t.k_symbol IS NULL OR TRIM(t.k_symbol) = '');
```

觀察：model replies=5、tool attempts=7、SQL attempts=2、latency=22.103s；stop=final_sql_ready。



<a id="q205"></a>

## [Q205](failure-case-review.md#q205) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：QA／題意與參考疑點。

Agent 只輸出最高平均地區，Gold 輸出五區；問題同時要求各五區及最高同分，輸出範圍有歧義。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among the bank's five most populous districts (the five with the largest numbers of inhabitants), which carries the heaviest active-lending burden relative to the account base it serves? For each of those five districts, please give me the district name and the average active loan per account, rounded to the nearest whole koruna. An active loan is a running loan contract with status 'C' (repaid OK so far) or status 'D' (client in debt). The average should be taken over every account held in the district, not just accounts with loans, and accounts and their loans count toward the district of the branch that holds the account, not the client's district. If several districts tie for the highest average, list them all.

Evidence：

Gold SQL（離線）：
```sql
WITH populous AS (SELECT district_id FROM district ORDER BY CAST(A4 AS INTEGER) DESC LIMIT 5), per_district AS (SELECT d.A2 AS district_name, SUM(CASE WHEN l.status IN ('C','D') THEN l.amount ELSE 0 END) * 1.0 / COUNT(a.account_id) AS raw_avg FROM district d JOIN account a ON a.district_id = d.district_id LEFT JOIN loan l ON l.account_id = a.account_id WHERE d.district_id IN (SELECT district_id FROM populous) GROUP BY d.district_id, d.A2) SELECT district_name, ROUND(raw_avg, 0) AS avg_active_loan_per_account FROM per_district ORDER BY raw_avg DESC, district_name
```

Agent SQL：
```sql
WITH top_districts AS (
    SELECT district_id, A2 AS district_name
    FROM district
    ORDER BY CAST(A4 AS INTEGER) DESC
    LIMIT 5
),
per_account AS (
    SELECT
        a.account_id,
        a.district_id,
        COALESCE(SUM(CASE WHEN l.status IN ('C', 'D') THEN l.amount ELSE 0 END), 0) AS active_loan_amount
    FROM account AS a
    LEFT JOIN loan AS l ON l.account_id = a.account_id
    GROUP BY a.account_id, a.district_id
),
district_averages AS (
    SELECT
        td.district_id,
        td.district_name,
        ROUND(1.0 * SUM(pa.active_loan_amount) / COUNT(*)) AS average_active_loan_per_account
    FROM top_districts AS td
    JOIN per_account AS pa ON pa.district_id = td.district_id
    GROUP BY td.district_id, td.district_name
)
SELECT district_name, average_active_loan_per_account
FROM district_averages
WHERE average_active_loan_per_account = (
    SELECT MAX(average_active_loan_per_account)
    FROM district_averages
);
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=22.901s；stop=final_sql_ready。



<a id="q206"></a>

## [Q206](failure-case-review.md#q206) · dev · financial

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R2／欄位語義。

以 district.A2（district name）當 region，Gold 應按 A3 聚合；月末加月份亦有日期政策差異。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For our 1995 year-end loan review: which of the bank's regions has the largest total approved amount among loans that were still being repaid on 31 December 1995, and what is that total? Only count loans approved on or before that day whose repayment term still covers that day; loans approved after it don't count yet. A loan's term includes both its approval day and its last day. If several regions tie for the largest total, list every tied region with the total. Just give me the region name and the single total figure.

Evidence：A loan is repaid over a term that starts on its approval day and lasts the number of months recorded for the loan; the loan is being repaid on every day of its term. Status 'C' means a running contract, OK so far; status 'D' means a running contract, client in debt. The regions are the bank's district regions.

Gold SQL（離線）：
```sql
WITH ends AS (SELECT d.A3 AS region, l.amount, date(CAST(CAST(substr(l.date, 1, 4) AS INTEGER) + (CAST(substr(l.date, 6, 2) AS INTEGER) - 1 + l.duration) / 12 AS TEXT) || '-' || substr('0' || ((CAST(substr(l.date, 6, 2) AS INTEGER) - 1 + l.duration) % 12 + 1), -2) || '-' || substr(l.date, 9, 2)) AS end_date FROM loan l JOIN account a ON l.account_id = a.account_id JOIN district d ON a.district_id = d.district_id WHERE l.date <= '1995-12-31'), totals AS (SELECT region, SUM(amount) AS total_amount, RANK() OVER (ORDER BY SUM(amount) DESC) AS rnk FROM ends WHERE end_date >= '1995-12-31' GROUP BY region) SELECT region, total_amount FROM totals WHERE rnk = 1
```

Agent SQL：
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

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=21.318s；stop=final_sql_ready。



<a id="q212"></a>

## [Q212](failure-case-review.md#q212) · dev · financial

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R2／欄位語義。

home population 用 A8 而非 A4；counterparty 附加 operation清單且未 account>0。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to find out whether our borrowing households from larger population centres transact differently from local ones. For every account at the Prachatice branch that has taken at least one loan, please give me: the account number, the account opening date, the total amount ever borrowed, how many outside bank counterparties the account has transacted with over its entire history, the owner's home district, the population of that district, and a rank of these borrowing households by home-district population from largest to smallest. Note that a counterparty means a particular bank account at another institution, identified by that account number, not by the bank code, and only transfers to or from another bank count — handling cash at our own branch does not involve a counterparty. A household's home district is the district its owner client is registered in, which is not necessarily Prachatice. For the ranking: largest population first, ties share the same rank and the next rank after a tie is skipped, and among households whose home districts have the same population, list the smaller account number first.

Evidence：An outside bank counterparty is a bank account at another institution that money was sent to or received from on a transfer transaction. District population is the number of inhabitants of the district.

Gold SQL（離線）：
```sql
WITH borrowers AS (SELECT a.account_id, a.date AS opening_date, (SELECT SUM(l.amount) FROM loan l WHERE l.account_id = a.account_id) AS total_borrowed FROM account a WHERE a.district_id = (SELECT district_id FROM district WHERE A2 = 'Prachatice') AND a.account_id IN (SELECT account_id FROM loan)), owners AS (SELECT d.account_id, c.district_id AS home_district_id FROM disp d JOIN client c ON c.client_id = d.client_id WHERE d.type = 'OWNER'), counterparties AS (SELECT account_id, COUNT(DISTINCT account) AS cnt FROM trans WHERE account > 0 GROUP BY account_id) SELECT bo.account_id, bo.opening_date, bo.total_borrowed, COALESCE(cp.cnt, 0) AS counterparty_count, hd.A2 AS home_district, CAST(hd.A4 AS INTEGER) AS home_population, RANK() OVER (ORDER BY CAST(hd.A4 AS INTEGER) DESC) AS population_rank FROM borrowers bo LEFT JOIN counterparties cp ON cp.account_id = bo.account_id LEFT JOIN owners o ON o.account_id = bo.account_id LEFT JOIN district hd ON hd.district_id = o.home_district_id ORDER BY population_rank ASC, bo.account_id ASC
```

Agent SQL：
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

觀察：model replies=5、tool attempts=11、SQL attempts=4、latency=24.636s；stop=final_sql_ready。



<a id="q214"></a>

## [Q214](failure-case-review.md#q214) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／佔位值。

未要求 counterparty account>0，可能把無外部帳戶的支出納入排名。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a partner-bank negotiation and want to focus on our big-city clients. Please tell me, for 1998 (1 January through 31 December 1998), where the money went from gold credit card clients' accounts held at branches in large districts. Specifically: for accounts whose owner has a gold credit card, and whose branch is located in a district with at least 250,000 inhabitants, look at their outgoing payments (debit transactions, type VYDAJ). I need a ranking of the recipient bank and counter-account pairs by the total amount paid. If two pairs tie for the largest total, list both. For each pair, give me: the recipient bank code, the recipient counter-account number, the number of outgoing payments, and the total amount paid.

Evidence：Gold credit card means card type 'gold'; account owner means disposition type 'OWNER'; the counter-account is the partner account at another bank to which a payment is sent; the district is the one where the account's branch is located.

Gold SQL（離線）：
```sql
WITH gold_accounts AS (SELECT d.account_id FROM card c JOIN disp d ON c.disp_id = d.disp_id WHERE c.type = 'gold' AND d.type = 'OWNER'), outgoing AS (SELECT t.bank AS bank, t.account AS account, COUNT(*) AS n_payments, SUM(t.amount) AS total_amount FROM trans t JOIN account a ON a.account_id = t.account_id JOIN district di ON di.district_id = a.district_id WHERE t.account_id IN (SELECT account_id FROM gold_accounts) AND t.type = 'VYDAJ' AND t.date >= '1998-01-01' AND t.date <= '1998-12-31' AND t.account > 0 AND CAST(di.A4 AS INTEGER) >= 250000 GROUP BY t.bank, t.account) SELECT bank, account, n_payments, total_amount FROM outgoing WHERE total_amount = (SELECT MAX(total_amount) FROM outgoing) ORDER BY bank, account
```

Agent SQL：
```sql
WITH eligible_accounts AS (
    SELECT DISTINCT d.account_id
    FROM disp AS d
    JOIN card AS c ON c.disp_id = d.disp_id
    JOIN account AS a ON a.account_id = d.account_id
    JOIN district AS x ON x.district_id = a.district_id
    WHERE d.type = 'OWNER'
      AND c.type = 'gold'
      AND CAST(x.A4 AS INTEGER) >= 250000
),
pair_totals AS (
    SELECT
        t.bank,
        t.account,
        COUNT(*) AS outgoing_payments,
        SUM(t.amount) AS total_amount
    FROM trans AS t
    JOIN eligible_accounts AS e ON e.account_id = t.account_id
    WHERE t.type = 'VYDAJ'
      AND t.date >= '1998-01-01'
      AND t.date < '1999-01-01'
    GROUP BY t.bank, t.account
)
SELECT bank, account, outgoing_payments, total_amount
FROM pair_totals
WHERE total_amount = (SELECT MAX(total_amount) FROM pair_totals);
```

觀察：model replies=10、tool attempts=13、SQL attempts=7、latency=45.473s；stop=final_sql_ready。



<a id="q216"></a>

## [Q216](failure-case-review.md#q216) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／欄位語義。

most populous 用 A8 而非 A4；薪金及失業率欄位已正確。

診斷改寫：2次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm planning a regional campaign for female customers who hold a credit card and a loan, and I need a demographic profile per region. For each region, please give me: the region, the average district salary of the districts where these female clients live, and the average 1996 district unemployment rate of those same districts – both averages rounded to 2 decimal places. I also want the name of the most populous district among those districts in each region, so I know where to focus local advertising. A few rules: count only female clients who own the account (disposition type OWNER) and who have at least one credit card and at least one loan on that account. 'Most populous' means the district with the largest number of inhabitants; if two tie, take the one whose name comes first alphabetically. One row per region, and include every region that has at least one such client – nothing else.

Evidence：Disposition type OWNER means the client owns the account. Unemployment rate in 1996 is the district's unemployment rate for 1996; average salary is the district's average salary.

Gold SQL（離線）：
```sql
WITH cohort AS ( SELECT DISTINCT c.district_id FROM client c JOIN disp d ON d.client_id = c.client_id AND d.type = 'OWNER' WHERE c.gender = 'F' AND d.disp_id IN (SELECT disp_id FROM card) AND d.account_id IN (SELECT account_id FROM loan) ) SELECT di.A3 AS region, ROUND(AVG(di.A11), 2) AS average_district_salary, ROUND(AVG(di.A13), 2) AS average_unemployment_rate_1996, (SELECT di2.A2 FROM district di2 WHERE di2.district_id IN (SELECT district_id FROM cohort) AND di2.A3 = di.A3 ORDER BY CAST(di2.A4 AS INTEGER) DESC, di2.A2 LIMIT 1) AS most_populous_district FROM district di WHERE di.district_id IN (SELECT district_id FROM cohort) GROUP BY di.A3 ORDER BY di.A3
```

Agent SQL：
```sql
WITH eligible_districts AS (
    SELECT DISTINCT
        d.A3 AS region,
        d.district_id,
        d.A11 AS salary,
        d.A13 AS unemployment_1996,
        d.A2 AS district_name,
        d.A8 AS inhabitants
    FROM client AS c
    JOIN disp AS dp
        ON dp.client_id = c.client_id
       AND dp.type = 'OWNER'
    JOIN account AS a
        ON a.account_id = dp.account_id
    JOIN district AS d
        ON d.district_id = c.district_id
    WHERE c.gender = 'F'
      AND EXISTS (
          SELECT 1
          FROM card AS ca
          WHERE ca.disp_id = dp.disp_id
      )
      AND EXISTS (
          SELECT 1
          FROM loan AS l
          WHERE l.account_id = a.account_id
      )
),
ranked_districts AS (
    SELECT
        region,
        district_name,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY inhabitants DESC, district_name ASC
        ) AS district_rank
    FROM eligible_districts
)
SELECT
    e.region,
    ROUND(AVG(e.salary), 2) AS average_district_salary,
    ROUND(AVG(e.unemployment_1996), 2) AS average_1996_district_unemployment_rate,
    MAX(CASE WHEN r.district_rank = 1 THEN r.district_name END) AS most_populous_district
FROM eligible_districts AS e
JOIN ranked_districts AS r
    ON r.region = e.region
   AND r.district_name = e.district_name
GROUP BY e.region
ORDER BY e.region;
```

觀察：model replies=8、tool attempts=12、SQL attempts=5、latency=30.941s；stop=final_sql_ready。



<a id="q217"></a>

## [Q217](failure-case-review.md#q217) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／量度來源。

將1996 crime count 錯用1996交易筆數代替 district.A16。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing our presence in central Bohemia. Please tell me: the names of the three most populous districts of central Bohemia (largest by inhabitants), the number of crimes committed in 1996 in each of them, the average 1996 crime count across those three districts, the average 1996 crime count across all districts in the country, and the difference between the three-district average and the overall average (three-district average minus overall average). Rank districts by inhabitants, breaking ties by district name alphabetically (ignoring accents). Round all averages and the difference to 2 decimal places. The overall average should cover every district in the country, whether or not it has any accounts.

Evidence：Central Bohemia is the region of the Czech Republic surrounding Prague.

Gold SQL（離線）：
```sql
WITH ranked AS ( SELECT d.A2 AS district_name, CAST(d.A4 AS INTEGER) AS inhabitants, d.A16 AS crimes_1996 FROM district d WHERE d.A3 = 'central Bohemia' ORDER BY CAST(d.A4 AS INTEGER) DESC, d.A2 LIMIT 3 ) SELECT r.district_name, r.crimes_1996, ROUND((SELECT AVG(crimes_1996) FROM ranked), 2) AS avg_crimes_top3_1996, ROUND((SELECT AVG(A16) FROM district), 2) AS avg_crimes_all_districts_1996, ROUND((SELECT AVG(crimes_1996) FROM ranked) - (SELECT AVG(A16) FROM district), 2) AS difference FROM ranked r ORDER BY r.inhabitants DESC, r.district_name
```

Agent SQL：
```sql
WITH district_crimes AS (
    SELECT
        d.district_id,
        d.A2 AS district_name,
        d.A3 AS region,
        CAST(d.A4 AS INTEGER) AS inhabitants,
        COUNT(DISTINCT t.trans_id) AS crimes_1996
    FROM district AS d
    LEFT JOIN account AS a
        ON a.district_id = d.district_id
    LEFT JOIN trans AS t
        ON t.account_id = a.account_id
       AND t.date >= '1996-01-01'
       AND t.date < '1997-01-01'
    GROUP BY d.district_id
),
ranked_districts AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY inhabitants DESC, district_name COLLATE NOCASE
        ) AS district_rank
    FROM district_crimes
),
averages AS (
    SELECT AVG(crimes_1996) AS overall_average
    FROM district_crimes
)
SELECT
    district_name,
    crimes_1996,
    ROUND(AVG(crimes_1996) OVER (), 2) AS three_district_average,
    ROUND((SELECT overall_average FROM averages), 2) AS overall_district_average,
    ROUND(
        AVG(crimes_1996) OVER () - (SELECT overall_average FROM averages),
        2
    ) AS difference
FROM ranked_districts
WHERE region = 'central Bohemia'
  AND district_rank <= 3
ORDER BY district_rank;
```

觀察：model replies=19、tool attempts=21、SQL attempts=15、latency=69.695s；stop=final_sql_ready。



<a id="q218"></a>

## [Q218](failure-case-review.md#q218) · test · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／欄位語義。

人口用 district.A8 而非 A4。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For planning region-targeted card offers, I need to look at the smallest markets behind each credit card type. For each credit card type (gold, classic and junior), which home district of the clients holding that type has the fewest inhabitants, and how many inhabitants does that district have? Please include all three card types, and if several districts tie for the fewest inhabitants, list them all.

Evidence：By "home district" I mean the district a client lives in, and a district's inhabitants are its number of inhabitants.

Gold SQL（離線）：
```sql
WITH holder_districts AS (SELECT DISTINCT cd.type AS card_type, cl.district_id FROM card cd JOIN disp dp ON dp.disp_id = cd.disp_id JOIN client cl ON cl.client_id = dp.client_id), ranked AS (SELECT hd.card_type, ds.A2 AS district_name, CAST(ds.A4 AS INTEGER) AS inhabitants, RANK() OVER (PARTITION BY hd.card_type ORDER BY CAST(ds.A4 AS INTEGER)) AS rnk FROM holder_districts hd JOIN district ds ON ds.district_id = hd.district_id) SELECT card_type, district_name, inhabitants FROM ranked WHERE rnk = 1 ORDER BY card_type
```

Agent SQL：
```sql
WITH markets AS (
    SELECT DISTINCT
        c.type,
        d.district_id,
        d.A2 AS district,
        d.A8 AS inhabitants
    FROM card AS c
    JOIN disp AS p ON p.disp_id = c.disp_id
    JOIN client AS cl ON cl.client_id = p.client_id
    JOIN district AS d ON d.district_id = cl.district_id
    WHERE c.type IN ('gold', 'classic', 'junior')
)
SELECT type, district, inhabitants
FROM (
    SELECT
        type,
        district,
        inhabitants,
        MIN(inhabitants) OVER (PARTITION BY type) AS min_inhabitants
    FROM markets
)
WHERE inhabitants = min_inhabitants
ORDER BY type, district;
```

觀察：model replies=7、tool attempts=9、SQL attempts=4、latency=30.775s；stop=final_sql_ready。



<a id="q219"></a>

## [Q219](failure-case-review.md#q219) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

以 UNION ALL 分開 district、region average、winner 行，Gold 需每district同列附帶兩個摘要。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing how our branches performed in 1996, and I'd like a picture of the money standing in accounts opened during that year, across the region that Litomerice belongs to (the region as given in the district table's region field).

For each district in that region where at least one account was opened in 1996 (openings counted by account creation date within the calendar year 1996), please give me:
- the district name,
- the number of accounts opened in 1996,
- the average end-of-1996 balance of those accounts,
with rows ordered by district name.

Also give me:
- the region-wide average end-of-1996 balance, taken across all those accounts (not as the mean of the district averages),
- the district with the highest average end-of-1996 balance; if two districts tie, name the one that comes first alphabetically.

By end-of-1996 balance I mean the balance after the account's last transaction dated on or before 1996-12-31; transactions dated 1997 or later don't count, and if several transactions fall on that last date, the one with the highest transaction id is the one that matters. Please round all averages to two decimals.

Evidence：Balance means the balance after a transaction.

Gold SQL（離線）：
```sql
WITH region AS (SELECT A3 AS r FROM district WHERE A2 = 'Litomerice'), op AS (SELECT a.account_id, a.district_id FROM account a JOIN district d ON d.district_id = a.district_id WHERE d.A3 = (SELECT r FROM region) AND a.date >= '1996-01-01' AND a.date < '1997-01-01'), lastd AS (SELECT t.account_id, MAX(t.date) AS md FROM trans t WHERE t.date <= '1996-12-31' AND t.account_id IN (SELECT account_id FROM op) GROUP BY t.account_id), lastt AS (SELECT l.account_id, MAX(t.trans_id) AS mt FROM lastd l JOIN trans t ON t.account_id = l.account_id AND t.date = l.md GROUP BY l.account_id), eb AS (SELECT x.account_id, tr.balance AS bal FROM lastt x JOIN trans tr ON tr.trans_id = x.mt), rd AS (SELECT d.A2 AS district_name, COUNT(*) AS accounts_opened_in_1996, AVG(e.bal) AS raw_avg FROM op o JOIN district d ON d.district_id = o.district_id JOIN eb e ON e.account_id = o.account_id GROUP BY d.district_id, d.A2) SELECT rd.district_name, rd.accounts_opened_in_1996, ROUND(rd.raw_avg, 2) AS average_end_of_1996_balance, (SELECT ROUND(AVG(bal), 2) FROM eb) AS region_average_end_of_1996_balance, (SELECT district_name FROM rd ORDER BY raw_avg DESC, district_name ASC LIMIT 1) AS district_with_highest_average_end_of_1996_balance FROM rd ORDER BY rd.district_name
```

Agent SQL：
```sql
WITH region AS (
    SELECT A3 AS region_name
    FROM district
    WHERE A2 = 'Litomerice'
),
selected_accounts AS (
    SELECT a.account_id, a.district_id
    FROM account AS a
    JOIN district AS d ON d.district_id = a.district_id
    WHERE d.A3 = (SELECT region_name FROM region)
      AND a.date >= '1996-01-01'
      AND a.date < '1997-01-01'
),
ranked_transactions AS (
    SELECT
        t.account_id,
        t.balance,
        ROW_NUMBER() OVER (
            PARTITION BY t.account_id
            ORDER BY t.date DESC, t.trans_id DESC
        ) AS rn
    FROM trans AS t
    JOIN selected_accounts AS sa ON sa.account_id = t.account_id
    WHERE t.date < '1997-01-01'
),
account_balances AS (
    SELECT sa.account_id, sa.district_id, rt.balance
    FROM selected_accounts AS sa
    JOIN ranked_transactions AS rt
      ON rt.account_id = sa.account_id
     AND rt.rn = 1
),
district_stats AS (
    SELECT
        d.A2 AS district_name,
        COUNT(*) AS accounts_opened,
        ROUND(AVG(ab.balance), 2) AS avg_balance
    FROM account_balances AS ab
    JOIN district AS d ON d.district_id = ab.district_id
    GROUP BY d.district_id, d.A2
)
SELECT
    district_name,
    accounts_opened,
    avg_balance,
    NULL AS region_avg_balance,
    NULL AS highest_average_district
FROM district_stats

UNION ALL

SELECT
    NULL,
    NULL,
    NULL,
    ROUND(AVG(balance), 2),
    NULL
FROM account_balances

UNION ALL

SELECT
    NULL,
    NULL,
    NULL,
    NULL,
    district_name
FROM district_stats
ORDER BY district_name;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=30.672s；stop=final_sql_ready。



<a id="q220"></a>

## [Q220](failure-case-review.md#q220) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／欄位內容。

第一輸出為 district_id，Gold 應為 district name A2。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to check whether our biggest short-term loans cluster in populous branch districts and how well-off those areas are. Looking at 24-month loans on accounts with weekly statement issuance, take the ten largest loans ranked by approved amount from highest to lowest — if two loans have the same amount, the one with the smaller loan id ranks first, and ranking continues consecutively after a tie. The district of a loan is the district where the branch managing the loan account is located. Among the districts those ten loans come from, I need: the district with the most inhabitants (if two districts tie on inhabitants, the one with the smaller district id counts as more populous), that district's number of inhabitants, and the average salary across those districts rounded to two decimals.

Evidence：Weekly statement issuance means account issuance frequency 'POPLATEK TYDNE'. A district's inhabitants are its number of inhabitants, and its average salary is its average yearly salary.

Gold SQL（離線）：
```sql
WITH ranked AS ( SELECT l.loan_id, a.district_id, ROW_NUMBER() OVER (ORDER BY l.amount DESC, l.loan_id ASC) AS rn FROM loan AS l JOIN account AS a ON a.account_id = l.account_id WHERE l.duration = 24 AND a.frequency = 'POPLATEK TYDNE' ), top10 AS ( SELECT * FROM ranked WHERE rn <= 10 ), districts AS ( SELECT d.district_id, d.A2 AS district_name, CAST(d.A4 AS INTEGER) AS inhabitants, d.A11 AS avg_salary FROM district AS d JOIN (SELECT DISTINCT district_id FROM top10) AS t ON t.district_id = d.district_id ) SELECT (SELECT district_name FROM districts ORDER BY inhabitants DESC, district_id ASC LIMIT 1) AS most_populous_district, (SELECT inhabitants FROM districts ORDER BY inhabitants DESC, district_id ASC LIMIT 1) AS inhabitants, (SELECT ROUND(AVG(avg_salary), 2) FROM districts) AS avg_district_salary;
```

Agent SQL：
```sql
WITH ranked_loans AS (
    SELECT
        l.loan_id,
        l.amount,
        a.district_id,
        ROW_NUMBER() OVER (ORDER BY l.amount DESC, l.loan_id ASC) AS loan_rank
    FROM loan AS l
    JOIN account AS a ON a.account_id = l.account_id
    WHERE l.duration = 24
      AND a.frequency = 'POPLATEK TYDNE'
),
selected_districts AS (
    SELECT DISTINCT district_id
    FROM ranked_loans
    WHERE loan_rank <= 10
),
district_stats AS (
    SELECT
        d.district_id,
        CAST(d.A4 AS INTEGER) AS inhabitants,
        d.A11 AS average_salary
    FROM selected_districts AS sd
    JOIN district AS d ON d.district_id = sd.district_id
)
SELECT
    (SELECT district_id FROM district_stats ORDER BY inhabitants DESC, district_id ASC LIMIT 1) AS district_id,
    (SELECT inhabitants FROM district_stats ORDER BY inhabitants DESC, district_id ASC LIMIT 1) AS inhabitants,
    ROUND(AVG(average_salary), 2) AS average_salary
FROM district_stats;
```

觀察：model replies=5、tool attempts=8、SQL attempts=4、latency=23.726s；stop=final_sql_ready。



<a id="q222"></a>

## [Q222](failure-case-review.md#q222) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／欄位語義。

把 A4 當 region、A8 當 inhabitants，導致區域人數／最大地區／排名均失準。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a client review for client 3541. For each account this client can access, I need one row with: the account id, the date the account was opened, its frequency, the name and region of the district where the account is held, whether that district is the client's home district (Yes/No), that district's average salary, the loan repayment status (none if there's no loan), the loan amount (0 if no loan), the number of transactions over the account's whole recorded history, total income, total expense, net balance, the number of clients whose home district lies in that region, the name of the most populous district in that region, that district's number of inhabitants, and the account district's population rank within its region. Order the rows by number of transactions, most first, with ties broken by ascending account id. The client's home district is the district recorded for the client, and population means number of inhabitants. For ranks, the most populous district is rank 1; districts with equal population share a rank and the next rank skips.

Evidence：PRIJEM = incoming transaction; VYDAJ = outgoing transaction; net balance = total income - total expense

Gold SQL（離線）：
```sql
WITH acct AS (SELECT d.account_id, a.date AS opened, a.frequency AS freq, a.district_id AS branch_district, c.district_id AS home_district FROM client c JOIN disp d ON d.client_id = c.client_id JOIN account a ON a.account_id = d.account_id WHERE c.client_id = 3541), stats AS (SELECT ac.account_id, ac.opened, ac.freq, ac.branch_district, ac.home_district, COUNT(t.trans_id) AS transaction_count, SUM(CASE WHEN t.type = 'PRIJEM' THEN t.amount ELSE 0 END) AS total_income, SUM(CASE WHEN t.type = 'VYDAJ' THEN t.amount ELSE 0 END) AS total_expense FROM acct ac LEFT JOIN trans t ON t.account_id = ac.account_id GROUP BY ac.account_id, ac.opened, ac.freq, ac.branch_district, ac.home_district), ranked AS (SELECT district_id, A3 AS region, A2 AS district_name, CAST(A4 AS INTEGER) AS inhabitants, RANK() OVER (PARTITION BY A3 ORDER BY CAST(A4 AS INTEGER) DESC) AS pop_rank FROM district) SELECT s.account_id, s.opened AS opening_date, s.freq AS frequency, bd.A2 AS district_where_held, bd.A3 AS region, CASE WHEN bd.district_id = s.home_district THEN 'Yes' ELSE 'No' END AS is_client_home_district, bd.A11 AS district_avg_salary, COALESCE(l.status, 'none') AS loan_status, COALESCE(l.amount, 0) AS loan_amount, s.transaction_count, s.total_income, s.total_expense, s.total_income - s.total_expense AS net_balance, (SELECT COUNT(DISTINCT c2.client_id) FROM client c2 JOIN district d2 ON d2.district_id = c2.district_id WHERE d2.A3 = bd.A3) AS clients_home_district_in_region, mp.district_name AS most_populous_district, mp.inhabitants AS most_populous_inhabitants, rk.pop_rank AS population_rank_in_region FROM stats s JOIN district bd ON bd.district_id = s.branch_district JOIN ranked rk ON rk.district_id = bd.district_id JOIN ranked mp ON mp.region = bd.A3 AND mp.pop_rank = 1 LEFT JOIN loan l ON l.account_id = s.account_id ORDER BY s.transaction_count DESC, s.account_id ASC
```

Agent SQL：
```sql
WITH client_access AS (
    SELECT DISTINCT account_id
    FROM disp
    WHERE client_id = 3541
),
transaction_summary AS (
    SELECT
        account_id,
        COUNT(*) AS transaction_count,
        SUM(CASE WHEN type = 'PRIJEM' THEN amount ELSE 0 END) AS total_income,
        SUM(CASE WHEN type = 'VYDAJ' THEN amount ELSE 0 END) AS total_expense
    FROM trans
    GROUP BY account_id
),
region_client_counts AS (
    SELECT d.A4 AS region, COUNT(DISTINCT c.client_id) AS client_count
    FROM client c
    JOIN district d ON d.district_id = c.district_id
    GROUP BY d.A4
),
ranked_districts AS (
    SELECT
        district_id,
        A4 AS region,
        A2 AS district_name,
        A8 AS inhabitants,
        RANK() OVER (PARTITION BY A4 ORDER BY A8 DESC) AS population_rank,
        FIRST_VALUE(A2) OVER (
            PARTITION BY A4 ORDER BY A8 DESC, district_id
        ) AS most_populous_district,
        FIRST_VALUE(A8) OVER (
            PARTITION BY A4 ORDER BY A8 DESC, district_id
        ) AS most_populous_inhabitants
    FROM district
)
SELECT
    a.account_id,
    a.date AS date_opened,
    a.frequency,
    d.A2 AS district_name,
    d.A3 AS district_region,
    CASE WHEN d.district_id = home.district_id THEN 'Yes' ELSE 'No' END AS is_home_district,
    d.A11 AS average_salary,
    COALESCE(l.status, 'none') AS loan_repayment_status,
    COALESCE(l.amount, 0) AS loan_amount,
    COALESCE(ts.transaction_count, 0) AS transaction_count,
    COALESCE(ts.total_income, 0) AS total_income,
    COALESCE(ts.total_expense, 0) AS total_expense,
    COALESCE(ts.total_income, 0) - COALESCE(ts.total_expense, 0) AS net_balance,
    COALESCE(rcc.client_count, 0) AS clients_in_region,
    rd.most_populous_district,
    rd.most_populous_inhabitants,
    rd.population_rank AS account_district_population_rank
FROM client_access ca
JOIN account a ON a.account_id = ca.account_id
JOIN district d ON d.district_id = a.district_id
JOIN client home ON home.client_id = 3541
LEFT JOIN loan l ON l.account_id = a.account_id
LEFT JOIN transaction_summary ts ON ts.account_id = a.account_id
LEFT JOIN region_client_counts rcc ON rcc.region = d.A4
JOIN ranked_districts rd ON rd.district_id = d.district_id
ORDER BY transaction_count DESC, a.account_id ASC;
```

觀察：model replies=6、tool attempts=12、SQL attempts=5、latency=30.915s；stop=final_sql_ready。



<a id="q226"></a>

## [Q226](failure-case-review.md#q226) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／缺失值。

無用途只接受 NULL，漏掉 TRIM(k_symbol)=''。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing branches in the north Moravia region ahead of a client meeting. For each branch there, how many transactions dated on or before 14 October 1998 have no characterization recorded? A branch is the district the account belongs to, and the count should cover all of the branch's accounts' transactions. Please list only the top three branches by this count, with the branch name and its count, ranked first to third. If any branches tie on the count, order them alphabetically by branch name and keep three rows after that ordering.

Evidence：A transaction with no characterization recorded means the bank did not tag it with any characterization.

Gold SQL（離線）：
```sql
WITH branch_counts AS ( SELECT d.A2 AS branch_name, COUNT(*) AS unstated_transactions FROM trans t JOIN account a ON t.account_id = a.account_id JOIN district d ON a.district_id = d.district_id WHERE d.A3 = 'north Moravia' AND t.date <= '1998-10-14' AND (t.k_symbol IS NULL OR TRIM(t.k_symbol) = '') GROUP BY d.A2 ) SELECT branch_name, unstated_transactions FROM branch_counts ORDER BY unstated_transactions DESC, branch_name ASC LIMIT 3
```

Agent SQL：
```sql
SELECT d.A2 AS branch_name, COUNT(*) AS transaction_count
FROM trans AS t
JOIN account AS a ON a.account_id = t.account_id
JOIN district AS d ON d.district_id = a.district_id
WHERE d.A3 = 'north Moravia'
  AND t.date <= '1998-10-14'
  AND t.k_symbol IS NULL
GROUP BY d.district_id, d.A2
ORDER BY transaction_count DESC, branch_name ASC
LIMIT 3;
```

觀察：model replies=5、tool attempts=7、SQL attempts=3、latency=17.847s；stop=final_sql_ready。



<a id="q227"></a>

## [Q227](failure-case-review.md#q227) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／必要篩選。

未限制 loan amount=98832，亦未排除 counterparty account<=0。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：The loan of 98832 approved on January 3rd, 1996 has one applicant account. For that account, list every counterparty it had paid before January 3rd, 1996. A counterparty means a specific account number at a specific bank, so give me one row per bank code and account number combination. For each counterparty I need the bank code, the account number, the number of outgoing payments made to them, and the total amount paid to them. Count only outgoing payments (VYDAJ, i.e. debits) made before January 3rd, 1996, and sort the counterparties by total amount paid, largest first.

Evidence：VYDAJ denotes an outgoing payment (debit); PRIJEM denotes an incoming payment (credit).

Gold SQL（離線）：
```sql
SELECT t.bank AS bank_code, t.account AS counterparty_account, COUNT(*) AS payment_count, SUM(t.amount) AS total_paid FROM trans t WHERE t.account_id = (SELECT l.account_id FROM loan l WHERE l.date = '1996-01-03' AND l.amount = 98832) AND t.type = 'VYDAJ' AND t.date < '1996-01-03' AND t.account > 0 GROUP BY t.bank, t.account ORDER BY total_paid DESC
```

Agent SQL：
```sql
SELECT
    t.bank AS bank_code,
    t.account AS account_number,
    COUNT(*) AS number_of_outgoing_payments,
    SUM(t.amount) AS total_amount_paid
FROM loan AS l
JOIN trans AS t ON t.account_id = l.account_id
WHERE l.date = '1996-01-03'
  AND t.type = 'VYDAJ'
  AND t.date < '1996-01-03'
GROUP BY t.bank, t.account
ORDER BY total_amount_paid DESC;
```

觀察：model replies=12、tool attempts=14、SQL attempts=9、latency=38.725s；stop=final_sql_ready。



<a id="q228"></a>

## [Q228](failure-case-review.md#q228) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／多加時間條件。

as-of 條件應用於 account opening；Agent 額外限制 loan approval date<=1995-12-31。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the year-end review of my branch at location 1: how many accounts that were on the branch's books as of 31 December 1995 hold an active loan contract? I want a single integer, nothing else. An account counts only if it belonged to the branch on that date, and only contracts that are still active by their repayment status count - statuses A and B are finished contracts and shouldn't be included.

Evidence：Loan status C means an active contract in good standing; loan status D means an active contract with the client in debt. Both are active contracts.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT a.account_id) AS account_count FROM account AS a JOIN loan AS l ON l.account_id = a.account_id WHERE a.district_id = 1 AND a.date <= '1995-12-31' AND l.status IN ('C', 'D')
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT a.account_id)
FROM account AS a
JOIN loan AS l ON l.account_id = a.account_id
WHERE a.district_id = 1
  AND a.date <= '1995-12-31'
  AND l.date <= '1995-12-31'
  AND l.status IN ('C', 'D');
```

觀察：model replies=5、tool attempts=6、SQL attempts=1、latency=15.919s；stop=final_sql_ready。



<a id="q230"></a>

## [Q230](failure-case-review.md#q230) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／統計母體。

transaction_count 只計 deposits(PRIJEM)，而非全交易；未限制 disp OWNER，排名 RANK 改 DENSE_RANK。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I need to profile our three largest loans held by female clients. Please report for each of these loans: the client id, loan amount, duration in months, total payments, interest paid, loan status, the district and region of the branch where the loan's account is held, the account's transaction count and total deposits, an income category, the number of loans the bank has granted in that region, the average of the average salaries of that region's districts, and the client's completed age on 2026-10-09. A few notes: the three largest loans are the three highest approved loan amounts, and if amounts tie, include all tied loans. Total payments is the monthly payment times the duration, and interest paid is total payments minus the approved amount; round money figures to two decimals. The income category is High Income if total deposits exceed twice the loan amount, Medium Income if they exceed the loan amount, and Low Income otherwise. Loans in a region counts every loan the bank has granted in that region for all clients, not only female clients. The region's average salary is the average of the average salaries of the districts in that region, rounded to two decimals. For the age, use the completed age on 2026-10-09, subtracting one if the birthday hasn't occurred by that date.

Evidence：Female means client gender = 'F'. Deposits are transactions recorded as PRIJEM (credits to the account). District average salary is the district's average salary figure.

Gold SQL（離線）：
```sql
WITH female_loans AS (SELECT c.client_id, c.birth_date, d.account_id, l.loan_id, l.amount, l.duration, l.payments, l.status, a.district_id, RANK() OVER (ORDER BY l.amount DESC) AS rnk FROM client c JOIN disp d ON c.client_id = d.client_id AND d.type = 'OWNER' JOIN loan l ON d.account_id = l.account_id JOIN account a ON l.account_id = a.account_id WHERE c.gender = 'F'), region_loans AS (SELECT da.A3 AS region, COUNT(*) AS loans_in_region FROM loan l JOIN account a ON l.account_id = a.account_id JOIN district da ON a.district_id = da.district_id GROUP BY da.A3), region_salary AS (SELECT A3 AS region, ROUND(AVG(A11), 2) AS avg_district_salary FROM district GROUP BY A3), acct_trans AS (SELECT account_id, COUNT(*) AS transaction_count, SUM(CASE WHEN type = 'PRIJEM' THEN amount ELSE 0 END) AS total_credits FROM trans GROUP BY account_id) SELECT fl.client_id, fl.amount AS loan_amount, fl.duration AS loan_duration_months, ROUND(fl.payments * fl.duration, 2) AS total_payments, ROUND(fl.payments * fl.duration - fl.amount, 2) AS interest_paid, fl.status AS loan_status, di.A2 AS branch_district, di.A3 AS region, at.transaction_count, at.total_credits AS total_deposits, CASE WHEN at.total_credits > fl.amount * 2 THEN 'High Income' WHEN at.total_credits > fl.amount THEN 'Medium Income' ELSE 'Low Income' END AS income_category, rl.loans_in_region, rs.avg_district_salary AS region_avg_district_salary, STRFTIME('%Y', '2026-10-09') - STRFTIME('%Y', fl.birth_date) - CASE WHEN STRFTIME('%m-%d', '2026-10-09') < STRFTIME('%m-%d', fl.birth_date) THEN 1 ELSE 0 END AS client_age FROM female_loans fl JOIN district di ON fl.district_id = di.district_id JOIN region_loans rl ON di.A3 = rl.region JOIN region_salary rs ON di.A3 = rs.region LEFT JOIN acct_trans at ON fl.account_id = at.account_id WHERE fl.rnk <= 3 ORDER BY fl.amount DESC
```

Agent SQL：
```sql
WITH loan_region AS (
    SELECT
        l.loan_id,
        l.account_id,
        l.amount,
        l.duration,
        l.payments,
        l.status,
        c.client_id,
        c.birth_date,
        branch.A2 AS branch_district,
        branch.A3 AS region
    FROM loan AS l
    JOIN account AS a ON a.account_id = l.account_id
    JOIN district AS branch ON branch.district_id = a.district_id
    JOIN disp AS dp ON dp.account_id = l.account_id
    JOIN client AS c ON c.client_id = dp.client_id
    WHERE c.gender = 'F'
),
regional_loans AS (
    SELECT d.A3 AS region, COUNT(*) AS loan_count
    FROM loan AS l
    JOIN account AS a ON a.account_id = l.account_id
    JOIN district AS d ON d.district_id = a.district_id
    GROUP BY d.A3
),
regional_salary AS (
    SELECT A3 AS region, ROUND(AVG(A11), 2) AS avg_salary
    FROM district
    GROUP BY A3
),
deposits AS (
    SELECT account_id, COUNT(*) AS transaction_count, SUM(amount) AS total_deposits
    FROM trans
    WHERE type = 'PRIJEM'
    GROUP BY account_id
),
ranked AS (
    SELECT loan_region.*, DENSE_RANK() OVER (ORDER BY amount DESC) AS amount_rank
    FROM loan_region
)
SELECT
    ranked.client_id,
    ranked.amount AS loan_amount,
    ranked.duration AS duration_months,
    ROUND(ranked.payments * ranked.duration, 2) AS total_payments,
    ROUND(ranked.payments * ranked.duration - ranked.amount, 2) AS interest_paid,
    ranked.status AS loan_status,
    ranked.branch_district,
    ranked.region,
    COALESCE(deposits.transaction_count, 0) AS transaction_count,
    COALESCE(deposits.total_deposits, 0) AS total_deposits,
    CASE
        WHEN COALESCE(deposits.total_deposits, 0) > 2 * ranked.amount THEN 'High Income'
        WHEN COALESCE(deposits.total_deposits, 0) > ranked.amount THEN 'Medium Income'
        ELSE 'Low Income'
    END AS income_category,
    regional_loans.loan_count,
    regional_salary.avg_salary,
    CAST(strftime('%Y', '2026-10-09') AS INTEGER)
        - CAST(strftime('%Y', ranked.birth_date) AS INTEGER)
        - CASE WHEN strftime('%m-%d', ranked.birth_date) > '10-09' THEN 1 ELSE 0 END AS age
FROM ranked
LEFT JOIN deposits ON deposits.account_id = ranked.account_id
JOIN regional_loans ON regional_loans.region = ranked.region
JOIN regional_salary ON regional_salary.region = ranked.region
WHERE ranked.amount_rank <= 3
ORDER BY ranked.amount DESC, ranked.loan_id, ranked.client_id;
```

觀察：model replies=6、tool attempts=10、SQL attempts=3、latency=48.019s；stop=final_sql_ready。



<a id="q231"></a>

## [Q231](failure-case-review.md#q231) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／日期來源。

opened before 1997 用 loan.date 而非 account.date。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I need to find out where our pre-1997 long-term mortgage exposure is concentrated geographically. Long-term means a loan duration of more than 24 months, and "opened before 1997" should exclude anything opened during 1997. Please tell me: for each region, which districts have at least one such account, and give me the region whose qualifying districts have the largest combined number of inhabitants. Along with the region's name, I want the number of those districts in it, their combined population, and the total number of those accounts in the region. If two regions tie on combined population, pick the one whose name comes first alphabetically.

Evidence：

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT l.account_id, a.district_id FROM loan AS l JOIN account AS a ON l.account_id = a.account_id WHERE l.duration > 24 AND STRFTIME('%Y', a.date) < '1997'), region_districts AS (SELECT DISTINCT d.district_id, d.A3 AS region, CAST(d.A4 AS INTEGER) AS population FROM district AS d JOIN cohort AS c ON d.district_id = c.district_id) SELECT r.region, COUNT(*) AS num_districts, SUM(r.population) AS total_population, (SELECT COUNT(*) FROM cohort AS c JOIN region_districts AS x ON c.district_id = x.district_id WHERE x.region = r.region) AS num_accounts FROM region_districts AS r GROUP BY r.region ORDER BY total_population DESC, r.region ASC LIMIT 1
```

Agent SQL：
```sql
WITH qualifying_districts AS (
    SELECT
        d.district_id,
        d.A3 AS region_name,
        CAST(d.A4 AS INTEGER) AS population,
        COUNT(l.loan_id) AS account_count
    FROM district AS d
    JOIN account AS a
        ON a.district_id = d.district_id
    JOIN loan AS l
        ON l.account_id = a.account_id
    WHERE l.duration > 24
      AND l.date < '1997-01-01'
    GROUP BY d.district_id, d.A3, d.A4
),
region_totals AS (
    SELECT
        region_name,
        COUNT(*) AS district_count,
        SUM(population) AS combined_population,
        SUM(account_count) AS account_count
    FROM qualifying_districts
    GROUP BY region_name
)
SELECT
    region_name,
    district_count,
    combined_population,
    account_count
FROM region_totals
ORDER BY combined_population DESC, region_name ASC
LIMIT 1;
```

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=23.231s；stop=final_sql_ready。



<a id="q235"></a>

## [Q235](failure-case-review.md#q235) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／關係母體。

交易 join 到所有 account，未要求該account存在 classic owner；Gold 僅計該等holders帳戶交易。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'd like a district-by-district picture of where our classic-card-holding account owners send money outside the bank. For every district, give me: the district name, the number of clients who own an account and hold a classic credit card, the number of external accounts at other banks those clients paid through outgoing payments, and the total amount of those outgoing payments. A district means the district of the branch where the owned account is held — not the client's home district — and each client and every outgoing payment from the account they own counts toward that account's branch district. Include every district, even ones with no such clients or no such outgoing payments (show zeros). Use the whole recorded payment history. Order by total amount paid from highest to lowest, and alphabetically by district name when totals tie. Don't round the totals.

Evidence：An account owner is the client recorded as 'OWNER' on the account. An outgoing payment is a transaction recorded with type 'VYDAJ' (money paid out of the account). An external account is an account held at another bank to which the account holder sends money; the receiving bank together with the receiving account number identifies it.

Gold SQL（離線）：
```sql
WITH holders AS ( SELECT dp.client_id, dp.account_id, a.district_id FROM card c JOIN disp dp ON dp.disp_id = c.disp_id AND dp.type = 'OWNER' JOIN account a ON a.account_id = dp.account_id WHERE c.type = 'classic' ) SELECT d.A2 AS district, COUNT(DISTINCT h.client_id) AS classic_card_holders, COUNT(DISTINCT t.account) AS external_accounts_paid, COALESCE(SUM(t.amount), 0) AS total_amount_paid FROM district d LEFT JOIN holders h ON h.district_id = d.district_id LEFT JOIN trans t ON t.account_id = h.account_id AND t.type = 'VYDAJ' AND t.account > 0 GROUP BY d.district_id, d.A2 ORDER BY total_amount_paid DESC, district ASC
```

Agent SQL：
```sql
WITH classic_owner_accounts AS (
    SELECT DISTINCT d.client_id, d.account_id
    FROM disp AS d
    JOIN card AS c ON c.disp_id = d.disp_id
    WHERE d.type = 'OWNER'
      AND c.type = 'classic'
),
district_metrics AS (
    SELECT
        a.district_id,
        COUNT(DISTINCT coa.client_id) AS classic_card_holding_clients,
        COUNT(DISTINCT CASE
            WHEN t.type = 'VYDAJ' AND t.bank IS NOT NULL AND t.account IS NOT NULL
            THEN t.bank || ':' || t.account
        END) AS external_accounts,
        COALESCE(SUM(CASE WHEN t.type = 'VYDAJ' THEN t.amount ELSE 0 END), 0) AS total_outgoing_amount
    FROM account AS a
    LEFT JOIN classic_owner_accounts AS coa ON coa.account_id = a.account_id
    LEFT JOIN trans AS t ON t.account_id = a.account_id
    GROUP BY a.district_id
)
SELECT
    d.A2 AS district_name,
    COALESCE(dm.classic_card_holding_clients, 0) AS classic_card_holding_clients,
    COALESCE(dm.external_accounts, 0) AS external_accounts,
    COALESCE(dm.total_outgoing_amount, 0) AS total_outgoing_amount
FROM district AS d
LEFT JOIN district_metrics AS dm ON dm.district_id = d.district_id
ORDER BY total_outgoing_amount DESC, district_name ASC;
```

觀察：model replies=6、tool attempts=9、SQL attempts=2、latency=23.791s；stop=final_sql_ready。



<a id="q238"></a>

## [Q238](failure-case-review.md#q238) · dev · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／欄位語義。

AVG district.A10 代替平均薪金 A11；已做 district 去重。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to know whether our small, healthy loans are concentrated in richer or poorer districts before we decide where to grow the small-loan business. Please give me one number: the average district salary, rounded to two decimals, across the districts where the accounts holding these loans are located. The cohort is loans with an approved amount below 100,000 that are still running without issues.

Evidence：Loan status C means the contract is running with no problems so far. District average salary is the average salary recorded for a district.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(d.A11), 2) AS average_district_salary FROM district d WHERE d.district_id IN (SELECT a.district_id FROM account a WHERE a.account_id IN (SELECT l.account_id FROM loan l WHERE l.amount < 100000 AND l.status = 'C'))
```

Agent SQL：
```sql
SELECT ROUND(AVG(d.A10), 2) AS avg_district_salary
FROM (
    SELECT DISTINCT a.district_id
    FROM loan AS l
    JOIN account AS a ON a.account_id = l.account_id
    WHERE l.amount < 100000
      AND l.status = 'C'
) AS loan_districts
JOIN district AS d ON d.district_id = loan_districts.district_id;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=19.772s；stop=final_sql_ready。



<a id="q239"></a>

## [Q239](failure-case-review.md#q239) · test · financial

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／重複加權。

cohort_accounts 按 account 去重，AVG district salary 仍按帳戶數加權；Gold 按 district,cohort 去重，標籤 young/old亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm studying how client age relates to branch location. For each of two client cohorts, I want the cohort label and the average salary across the districts where the branches holding that cohort's accounts are located, rounded to the nearest whole number. A client's cohort is based on birth date: born 1980 or later is the young cohort, born 1919 or earlier is the old cohort. Note the district of an account is the district of its branch, not the client's home district. Give me one row per cohort, young cohort first. Nothing else.

Evidence：

Gold SQL（離線）：
```sql
WITH cohort_districts AS (SELECT a.district_id, CASE WHEN c.birth_date >= '1980-01-01' THEN 'young' ELSE 'old' END AS cohort FROM client c JOIN disp d ON d.client_id = c.client_id JOIN account a ON a.account_id = d.account_id WHERE c.birth_date >= '1980-01-01' OR c.birth_date <= '1919-12-31' GROUP BY a.district_id, CASE WHEN c.birth_date >= '1980-01-01' THEN 'young' ELSE 'old' END) SELECT cohort, CAST(ROUND(AVG(x.A11)) AS INTEGER) AS avg_salary FROM cohort_districts cd JOIN district x ON x.district_id = cd.district_id GROUP BY cohort ORDER BY CASE cohort WHEN 'young' THEN 1 ELSE 2 END
```

Agent SQL：
```sql
WITH cohort_accounts AS (
    SELECT DISTINCT
        CASE
            WHEN c.birth_date >= '1980-01-01' THEN 'young cohort'
            WHEN c.birth_date <= '1919-12-31' THEN 'old cohort'
        END AS cohort,
        a.account_id,
        a.district_id
    FROM client AS c
    JOIN disp AS dp ON dp.client_id = c.client_id
    JOIN account AS a ON a.account_id = dp.account_id
    WHERE c.birth_date >= '1980-01-01'
       OR c.birth_date <= '1919-12-31'
)
SELECT
    cohort,
    ROUND(AVG(d.A11)) AS average_salary
FROM cohort_accounts AS ca
JOIN district AS d ON d.district_id = ca.district_id
GROUP BY cohort
ORDER BY CASE cohort WHEN 'young cohort' THEN 1 ELSE 2 END;
```

觀察：model replies=10、tool attempts=13、SQL attempts=7、latency=46.991s；stop=final_sql_ready。



<a id="q245"></a>

## [Q245](failure-case-review.md#q245) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／精確小數捨入。

1952年winner時間總毫秒88492680／8=11061585，平均11061.585秒；Agent浮點ROUND給11061.58，精確half-away規則應11061.59。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For each year before 1975 with recorded winner times, what was the mean race winner elapsed time in seconds? Round the exact mean to two decimal places; if it is exactly halfway, round away from zero. Order by year.

Evidence：

Gold SQL（離線）：
```sql
SELECT r.year, FLOOR((SUM(x.milliseconds) + 5 * COUNT(*)) / (10 * COUNT(*))) / 100.0 FROM results AS x JOIN races AS r ON r.raceId = x.raceId WHERE r.year < 1975 AND x.positionOrder = 1 AND x.milliseconds IS NOT NULL GROUP BY r.year ORDER BY r.year
```

Agent SQL：
```sql
SELECT
    r.year,
    ROUND(AVG(res.milliseconds) / 1000.0, 2) AS mean_winner_elapsed_seconds
FROM races AS r
JOIN results AS res
    ON res.raceId = r.raceId
WHERE r.year < 1975
  AND res.positionOrder = 1
  AND res.milliseconds IS NOT NULL
GROUP BY r.year
ORDER BY r.year;
```

觀察：model replies=8、tool attempts=8、SQL attempts=5、latency=28.167s；stop=final_sql_ready。



<a id="q247"></a>

## [Q247](failure-case-review.md#q247) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／欄位次序。

Agent 輸出 name,nationality,score，Gold 為 score,name,nationality；points 來源亦 results 而非 constructorResults。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which constructor scored most points from Monaco Grand Prix between 1980 and 2010? List the score, name and nationality of this team.

Evidence：

Gold SQL（離線）：
```sql
SELECT SUM(T1.points), T2.name, T2.nationality FROM constructorResults AS T1 INNER JOIN constructors AS T2 ON T1.constructorId = T2.constructorId INNER JOIN races AS T3 ON T3.raceId = T1.raceId WHERE T3.name = 'Monaco Grand Prix' AND T3.year BETWEEN 1980 AND 2010 GROUP BY T2.name ORDER BY SUM(T1.points) DESC LIMIT 1
```

Agent SQL：
```sql
SELECT c.name, c.nationality, SUM(res.points) AS score
FROM races AS r
JOIN circuits AS ci ON ci.circuitId = r.circuitId
JOIN results AS res ON res.raceId = r.raceId
JOIN constructors AS c ON c.constructorId = res.constructorId
WHERE ci.name = 'Circuit de Monaco'
  AND r.year BETWEEN 1980 AND 2010
GROUP BY c.constructorId, c.name, c.nationality
ORDER BY score DESC
LIMIT 1;
```

觀察：model replies=4、tool attempts=6、SQL attempts=1、latency=15.016s；stop=final_sql_ready。



<a id="q251"></a>

## [Q251](failure-case-review.md#q251) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／實體識別。

是否2000年hosted 用 circuitId 判定，Gold 用 race name；場地與賽事身份不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm comparing pit stop activity at the newer Grand Prix weekends. Among the 2017 races that were not hosted in 2000, what was the average number of pit stops per race? Please take the average of all of those races and round it to two decimal places.

Evidence：Hosted in 2000 means the race was on the 2000 race calendar.

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT raceId FROM races WHERE year = 2017 AND name NOT IN (SELECT name FROM races WHERE year = 2000)) SELECT ROUND(1.0 * (SELECT COUNT(*) FROM pitStops WHERE raceId IN (SELECT raceId FROM cohort)) / (SELECT COUNT(*) FROM cohort), 2) AS avg_pit_stops_per_race
```

Agent SQL：
```sql
WITH hosted_2000 AS (
    SELECT DISTINCT circuitId
    FROM races
    WHERE year = 2000
),
race_stops AS (
    SELECT r.raceId, COUNT(p.stop) AS pit_stop_count
    FROM races AS r
    LEFT JOIN pitStops AS p ON p.raceId = r.raceId
    WHERE r.year = 2017
      AND r.circuitId NOT IN (SELECT circuitId FROM hosted_2000)
    GROUP BY r.raceId
)
SELECT ROUND(AVG(pit_stop_count), 2)
FROM race_stops;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=15.545s；stop=final_sql_ready。



<a id="q252"></a>

## [Q252](failure-case-review.md#q252) · test · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／缺失值。

COUNT(q3) 仍計空字串，Gold COUNT(NULLIF(q3,''))。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm writing a retrospective on German F1 drivers born between 1971 and 1985, and I'd like to quantify how often each of them reached the final part of qualifying. For every German driver born in 1971 through 1985 inclusive, over their entire career (every race on record), please give me their forename, surname, Wikipedia page link, date of birth, and the number of Q3 times they set. Sort the list from most Q3 times to fewest, and where two drivers have the same number, put the older one (by date of birth) first.

Evidence：Q3 is the third and final part of the qualifying session that sets the starting grid; a driver's Q3 time is the lap time recorded for them in that part.

Gold SQL（離線）：
```sql
SELECT d.forename, d.surname, d.url, d.dob, COUNT(NULLIF(q.q3, '')) AS q3_times FROM drivers d LEFT JOIN qualifying q ON q.driverId = d.driverId WHERE d.nationality = 'German' AND STRFTIME('%Y', d.dob) BETWEEN '1971' AND '1985' GROUP BY d.driverId ORDER BY q3_times DESC, d.dob ASC
```

Agent SQL：
```sql
SELECT
    d.forename,
    d.surname,
    d.url,
    d.dob,
    COUNT(q.q3) AS q3_times
FROM drivers AS d
LEFT JOIN qualifying AS q
    ON q.driverId = d.driverId
WHERE d.nationality = 'German'
  AND d.dob BETWEEN '1971-01-01' AND '1985-12-31'
GROUP BY d.driverId
ORDER BY q3_times DESC, d.dob ASC;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=22.565s；stop=final_sql_ready。



<a id="q254"></a>

## [Q254](failure-case-review.md#q254) · test · formula_1

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／時間編碼。

MAX(q1) 用文字最大，Gold 按分秒數值排名（秒CAST INTEGER 的參考政策亦需留意）。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For qualifying at the 1995 Japanese Grand Prix, I need the nationality of the driver who set the slowest time in Q1. If two drivers tie for the slowest Q1 time, give me each of their nationalities. I only want the nationality value(s), nothing else.

Evidence：

Gold SQL（離線）：
```sql
WITH t AS (SELECT d.nationality, RANK() OVER (ORDER BY CAST(replace(substr(q.q1, 1, instr(q.q1, ':')), ':', '') AS INTEGER) DESC, CAST(substr(q.q1, instr(q.q1, ':') + 1) AS INTEGER) DESC) AS rnk FROM qualifying q JOIN drivers d ON d.driverId = q.driverId JOIN races r ON r.raceId = q.raceId WHERE r.year = 1995 AND r.name = 'Japanese Grand Prix' AND q.q1 IS NOT NULL AND q.q1 <> '') SELECT nationality FROM t WHERE rnk = 1;
```

Agent SQL：
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

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=22.009s；stop=final_sql_ready。



<a id="q255"></a>

## [Q255](failure-case-review.md#q255) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／時間編碼。

MIN(q1) 用文字排序，未將 minute:second 轉為數值。Gold LIMIT1 與題目同分全列亦有政策差異。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Who set the fastest time in Q1 at the 1995 Japanese Grand Prix, and what was that time? Please give me the driver's forename and surname, and the Q1 time. By '1995 Japanese Grand Prix' I mean the race of the 1995 season named 'Japanese Grand Prix'. If two drivers tied for the fastest Q1 time, list them all.

Evidence：Q1: the time a driver set in the first qualifying session.

Gold SQL（離線）：
```sql
SELECT d.forename, d.surname, q.q1 FROM qualifying AS q JOIN drivers AS d ON d.driverId = q.driverId JOIN races AS r ON r.raceId = q.raceId WHERE r.year = 1995 AND r.name = 'Japanese Grand Prix' AND q.q1 IS NOT NULL ORDER BY CAST(SUBSTR(q.q1, 1, INSTR(q.q1, ':') - 1) AS INTEGER) ASC, CAST(SUBSTR(q.q1, INSTR(q.q1, ':') + 1) AS REAL) ASC LIMIT 1;
```

Agent SQL：
```sql
SELECT d.forename, d.surname, q.q1
FROM qualifying AS q
JOIN races AS r ON r.raceId = q.raceId
JOIN drivers AS d ON d.driverId = q.driverId
WHERE r.year = 1995
  AND r.name = 'Japanese Grand Prix'
  AND q.q1 = (
      SELECT MIN(q2.q1)
      FROM qualifying AS q2
      WHERE q2.raceId = r.raceId
        AND q2.q1 IS NOT NULL
  );
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=74.209s；stop=final_sql_ready。



<a id="q258"></a>

## [Q258](failure-case-review.md#q258) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／計數單位。

COUNT(DISTINCT raceId) 計亞軍賽事次數，Gold 計 DISTINCT driverId。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm writing an article about the Italian Grand Prix and want to know which first names recur among the drivers who finished second in that race. For every forename carried by two or more runners-up of the Italian Grand Prix across all its editions in the data, please give me one row with the forename and the number of runners-up who carried it. Order the rows from the most runners-up to the fewest, and alphabetically by forename when two forenames are tied. Leave out any forename held by only one runner-up.

Evidence：A runner-up is the driver who finished second in an edition of the Italian Grand Prix.

Gold SQL（離線）：
```sql
SELECT d.forename AS forename, COUNT(DISTINCT d.driverId) AS runner_ups FROM races AS r INNER JOIN results AS x ON x.raceId = r.raceId INNER JOIN drivers AS d ON d.driverId = x.driverId WHERE r.name = 'Italian Grand Prix' AND x.position = 2 GROUP BY d.forename HAVING COUNT(DISTINCT d.driverId) > 1 ORDER BY runner_ups DESC, d.forename
```

Agent SQL：
```sql
SELECT d.forename, COUNT(DISTINCT res.raceId) AS runners_up
FROM races AS r
JOIN results AS res ON res.raceId = r.raceId
JOIN drivers AS d ON d.driverId = res.driverId
WHERE r.name = 'Italian Grand Prix'
  AND res.position = 2
GROUP BY d.forename
HAVING COUNT(DISTINCT res.raceId) >= 2
ORDER BY runners_up DESC, d.forename ASC;
```

觀察：model replies=5、tool attempts=7、SQL attempts=2、latency=15.732s；stop=final_sql_ready。



<a id="q259"></a>

## [Q259](failure-case-review.md#q259) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R8／SQLite方言。

time() 使用 '+N milliseconds' modifier，SQLite 不支援，可產生NULL；需秒的小數 modifier。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Who won the 2017 Azerbaijan Grand Prix? I'd like the winner's forename and surname, the local clock time (hours:minutes:seconds.milliseconds) at the circuit at which he crossed the finish line, and the url of his information page, so I can compare the moment the race ended with the TV coverage.

Evidence：A driver's race time is the duration from the start of the race to the moment he crosses the finish line.

Gold SQL（離線）：
```sql
SELECT d.forename, d.surname, time(r.time, '0' || res.time) || '.' || substr(res.time, -3) AS finish_time, d.url FROM races r JOIN results res ON res.raceId = r.raceId JOIN drivers d ON d.driverId = res.driverId WHERE r.year = 2017 AND r.name = 'Azerbaijan Grand Prix' AND res.positionOrder = 1
```

Agent SQL：
```sql
SELECT
    d.forename,
    d.surname,
    time(
        r.time,
        printf('+%d seconds', res.milliseconds / 1000),
        printf('+%d milliseconds', res.milliseconds % 1000)
    ) || '.' || printf('%03d', res.milliseconds % 1000) AS finish_local_time,
    d.url
FROM races AS r
JOIN results AS res ON res.raceId = r.raceId
JOIN drivers AS d ON d.driverId = res.driverId
WHERE r.year = 2017
  AND r.name = 'Azerbaijan Grand Prix'
  AND res.positionOrder = 1;
```

觀察：model replies=5、tool attempts=7、SQL attempts=2、latency=18.588s；stop=final_sql_ready。



<a id="q266"></a>

## [Q266](failure-case-review.md#q266) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／零次實體。

inner JOIN results 只保留有 qualifying races 的 Robert，漏掉應列為0的其他 Robert。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm checking how much of the championship points for drivers named Robert came from races covered by the lap-by-lap timing archive. For every driver whose forename is Robert, I need their reference name and the total points they scored in races where lap-by-lap timing data exists for that driver in that race. The totals should cover all seasons and races on record.

Evidence：The reference name is the driver's short identifier, and points are championship points recorded for that driver's race result.

Gold SQL（離線）：
```sql
SELECT d.driverRef AS reference_name, COALESCE(SUM(r.points), 0) AS total_points FROM drivers d LEFT JOIN results r ON r.driverId = d.driverId AND EXISTS (SELECT 1 FROM lapTimes l WHERE l.raceId = r.raceId AND l.driverId = d.driverId) WHERE d.forename = 'Robert' GROUP BY d.driverId, d.driverRef ORDER BY total_points DESC, reference_name
```

Agent SQL：
```sql
SELECT d.driverRef AS reference_name,
       SUM(r.points) AS total_points
FROM drivers AS d
JOIN results AS r
  ON r.driverId = d.driverId
WHERE d.forename = 'Robert'
  AND EXISTS (
      SELECT 1
      FROM lapTimes AS lt
      WHERE lt.driverId = r.driverId
        AND lt.raceId = r.raceId
  )
GROUP BY d.driverId, d.driverRef;
```

觀察：model replies=4、tool attempts=6、SQL attempts=1、latency=15.649s；stop=final_sql_ready。



<a id="q272"></a>

## [Q272](failure-case-review.md#q272) · dev · formula_1

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R2／量度來源。

career points 應取各年終 constructorStandings 再SUM，Agent SUM constructorResults 每場積分。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Can you rank the Italian Formula 1 constructors by career points and give me the three highest-placed ones? For each, I'd like the constructor name, their career points, and their introduction website. Career points means the total of the points the constructor finished each season with (a season being one calendar year of racing). Constructors with no points still count, ranked with 0. If there are ties, they share a rank and the next rank is skipped (so 1, 1, 3), and I'd like every constructor within the top three ranks returned.

Evidence：

Gold SQL（離線）：
```sql
WITH season AS (
    SELECT cs.constructorId, cs.points,
           ROW_NUMBER() OVER (PARTITION BY cs.constructorId, r.year ORDER BY cs.raceId DESC) AS rn
    FROM constructorStandings cs
    JOIN races r ON r.raceId = cs.raceId
),
career AS (
    SELECT constructorId, SUM(points) AS pts
    FROM season
    WHERE rn = 1
    GROUP BY constructorId
),
ranked AS (
    SELECT c.name, COALESCE(cr.pts, 0) AS pts, c.url,
           RANK() OVER (ORDER BY COALESCE(cr.pts, 0) DESC) AS rnk
    FROM constructors c
    LEFT JOIN career cr ON cr.constructorId = c.constructorId
    WHERE c.nationality = 'Italian'
)
SELECT name, pts, url
FROM ranked
WHERE rnk <= 3
ORDER BY rnk, pts DESC, name
```

Agent SQL：
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

觀察：model replies=5、tool attempts=7、SQL attempts=2、latency=17.446s；stop=final_sql_ready。



<a id="q277"></a>

## [Q277](failure-case-review.md#q277) · dev · formula_1

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／時間精度。

秒只截兩位INTEGER，忽略毫秒，2:00.xxx 會誤當120秒而排除。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the 1995 season (races held in the calendar year 1995), how many drivers set a Q1 lap time of more than two minutes - i.e., strictly longer than 2:00.000? I just need the number of drivers.

Evidence：Q1: the first of the qualifying sessions; a Q1 time is the lap time a driver set in that session.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T1.driverId) FROM qualifying AS T1 INNER JOIN races AS T2 ON T2.raceId = T1.raceId WHERE T2.year = 1995 AND (length(T1.q1) > length('2:00.000') OR T1.q1 > '2:00.000')
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT q.driverId) AS driver_count
FROM qualifying AS q
JOIN races AS r ON r.raceId = q.raceId
WHERE r.year = 1995
  AND q.q1 IS NOT NULL
  AND q.q1 <> ''
  AND (
    CAST(substr(q.q1, 1, instr(q.q1, ':') - 1) AS INTEGER) * 60
    + CAST(substr(q.q1, instr(q.q1, ':') + 1, 2) AS INTEGER)
  ) > 120;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=16.623s；stop=final_sql_ready。



<a id="q279"></a>

## [Q279](failure-case-review.md#q279) · dev · formula_1

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／重複計數。

相同driver選擇及first win正確，career COUNT(*)=8，改COUNT(DISTINCT raceId)=7即與Gold吻合。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling the oldest driver ever to win a Formula 1 race. Please identify the winning driver with the earliest date of birth - if two winning drivers share that birth date, use the one whose full name (forename then surname) comes first alphabetically. For that driver, return his full name (forename then surname), his nationality, the name and date of the first race he won (the earliest date; if two of his wins share that date, the one whose race name comes first alphabetically), and the total number of races he started over his entire career. A win means finishing in position 1 in a race. The career covers every race in the database, from 1950 through 2017. Return a single row.

Evidence：Grand Prix: any race event in the database, whatever its name is; some race names do not contain the words 'Grand Prix'.

Gold SQL（離線）：
```sql
WITH winner AS (SELECT d.driverId, d.forename, d.surname, d.nationality FROM drivers d WHERE EXISTS (SELECT 1 FROM results res WHERE res.driverId = d.driverId AND res.position = 1) ORDER BY d.dob ASC, d.forename ASC, d.surname ASC LIMIT 1) SELECT w.forename || ' ' || w.surname AS full_name, w.nationality, (SELECT r.name FROM results res JOIN races r ON r.raceId = res.raceId WHERE res.driverId = w.driverId AND res.position = 1 ORDER BY r.date ASC, r.name ASC LIMIT 1) AS first_win_race, (SELECT r.date FROM results res JOIN races r ON r.raceId = res.raceId WHERE res.driverId = w.driverId AND res.position = 1 ORDER BY r.date ASC, r.name ASC LIMIT 1) AS first_win_date, (SELECT COUNT(DISTINCT res.raceId) FROM results res WHERE res.driverId = w.driverId) AS races_started FROM winner w
```

Agent SQL：
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

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=19.437s；stop=final_sql_ready。



<a id="q286"></a>

## [Q286](failure-case-review.md#q286) · dev · formula_1

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R7／值表示。

要求 runner-up gap，Gold 為 results.time 字串，Agent 回傳 milliseconds差額數值。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which Chinese Grand Prix edition from the 2000s (2000–2009 seasons) had the earliest scheduled local start time? Give me the season year of that edition and the runner-up's time gap to the winner (the runner-up being the driver classified second at the finish). If several editions share the earliest scheduled local start time, use the most recent one.

Evidence：Scheduled local start time: the time of day the race was scheduled to start, local to the circuit.

Gold SQL（離線）：
```sql
SELECT r.year, res.time AS runner_up_gap FROM races r JOIN results res ON res.raceId = r.raceId WHERE r.name = 'Chinese Grand Prix' AND r.year BETWEEN 2000 AND 2009 AND res.positionOrder = 2 AND r.time IS NOT NULL AND r.time = (SELECT MIN(r2.time) FROM races r2 WHERE r2.name = 'Chinese Grand Prix' AND r2.year BETWEEN 2000 AND 2009 AND r2.time IS NOT NULL) ORDER BY r.year DESC LIMIT 1
```

Agent SQL：
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

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=25.596s；stop=final_sql_ready。



<a id="q295"></a>

## [Q295](failure-case-review.md#q295) · dev · student_club

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／分組粒度。

按 link_to_budget 分組計均值，Gold 經 budget.link_to_event 按活動分組。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What was Elijah Allen's mean total expense per event for expenses dated in September or October? Round to two decimals.

Evidence：

Gold SQL（離線）：
```sql
WITH per_event AS ( SELECT b.link_to_event, SUM(e.cost) AS event_spend FROM expense AS e JOIN member AS m ON m.member_id = e.link_to_member JOIN budget AS b ON b.budget_id = e.link_to_budget WHERE m.first_name = 'Elijah' AND m.last_name = 'Allen' AND SUBSTR(e.expense_date, 6, 2) IN ('09','10') AND b.link_to_event IS NOT NULL GROUP BY b.link_to_event ) SELECT ROUND(AVG(event_spend), 2) FROM per_event
```

Agent SQL：
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

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=17.717s；stop=final_sql_ready。



<a id="q303"></a>

## [Q303](failure-case-review.md#q303) · test · student_club

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：QA／輸出／參考疑點。

Agent 輸出 majors 名稱清單，Gold 輸出 majors_offered／held 數目；題目用語有歧義；學院篩選亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing our roster against the catalog and want to see how much of the College of Humanities and Social Sciences' coverage our members actually hold, department by department. For each department in that college, give me: the department's name, the majors it offers, the majors held by at least one of our members, and the average members per major it offers, rounded to two decimals. Membership is as currently listed in the member records, and count a department as belonging to the college when any of its majors sits in the college.

Evidence：College of Humanities and Social Sciences: one of the colleges that houses departments offering majors.

Gold SQL（離線）：
```sql
SELECT m.department, COUNT(DISTINCT m.major_id) AS majors_offered, COUNT(DISTINCT mem.link_to_major) AS majors_held, ROUND(1.0 * COUNT(DISTINCT mem.member_id) / COUNT(DISTINCT m.major_id), 2) AS avg_members_per_major FROM major m LEFT JOIN member mem ON mem.link_to_major = m.major_id WHERE m.college = 'College of Humanities and Social Sciences' GROUP BY m.department
```

Agent SQL：
```sql
WITH department_majors AS (
    SELECT
        department,
        major_id,
        major_name
    FROM major
    WHERE department IN (
        SELECT department
        FROM major
        WHERE college = 'College of Humanities and Social Sciences'
    )
),
major_member_counts AS (
    SELECT
        dm.department,
        dm.major_id,
        dm.major_name,
        COUNT(m.member_id) AS member_count
    FROM department_majors AS dm
    LEFT JOIN member AS m
        ON m.link_to_major = dm.major_id
    GROUP BY dm.department, dm.major_id, dm.major_name
)
SELECT
    department AS department_name,
    GROUP_CONCAT(major_name, ', ') AS majors_offered,
    GROUP_CONCAT(
        CASE WHEN member_count > 0 THEN major_name END,
        ', '
    ) AS majors_held_by_members,
    ROUND(SUM(member_count) * 1.0 / COUNT(*), 2) AS average_members_per_major
FROM major_member_counts
GROUP BY department
ORDER BY department_name;
```

觀察：model replies=9、tool attempts=9、SQL attempts=6、latency=35.660s；stop=final_sql_ready。



<a id="q306"></a>

## [Q306](failure-case-review.md#q306) · dev · student_club

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／條件範圍。

先找 cost>50 member 後納其所有budget lines，Gold 只納該member cost>50購買連結的budget lines。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the mid-year budget review: I need to see, for each member who had to spend more than fifty dollars on an expense, how much room was still left in the budget lines those purchases were charged against. Please give me, per member, their first name, last name, and the total amount left across those budget lines in dollars rounded to two decimals. Order the results from the largest total down to the smallest; if two members have the same total, list them alphabetically by last name and then first name. The totals should cover all expenses on record, and if a budget line ended up overdrawn, its negative remaining amount should count toward the total.

Evidence：Spending more than fifty dollars on an expense means the expense's dollar cost is over 50. The amount left in a budget line is the amount budgeted for that line minus the amount spent against it.

Gold SQL（離線）：
```sql
SELECT m.first_name, m.last_name, ROUND(SUM(b.remaining), 2) AS remaining_total FROM member AS m JOIN (SELECT DISTINCT link_to_member, link_to_budget FROM expense WHERE cost > 50) AS e ON e.link_to_member = m.member_id JOIN budget AS b ON b.budget_id = e.link_to_budget GROUP BY m.member_id, m.first_name, m.last_name ORDER BY remaining_total DESC, m.last_name ASC, m.first_name ASC
```

Agent SQL：
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

觀察：model replies=5、tool attempts=7、SQL attempts=3、latency=21.110s；stop=final_sql_ready。



<a id="q307"></a>

## [Q307](failure-case-review.md#q307) · test · student_club

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R3／重複計數。

attendance join 可重複同一member dues，Gold 用 IN 半連接。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together our year-end budget summary. How much did we collect in membership dues, in total dollars, from the students who attended the Football game? Membership dues are the payments recorded under the source 'Dues'.

Evidence：membership dues: payments recorded under the source 'Dues'

Gold SQL（離線）：
```sql
SELECT SUM(i.amount) AS total_dues FROM income AS i WHERE i.source = 'Dues' AND i.link_to_member IN (SELECT a.link_to_member FROM attendance AS a INNER JOIN event AS e ON a.link_to_event = e.event_id WHERE e.event_name = 'Football game')
```

Agent SQL：
```sql
SELECT SUM(i.amount)
FROM attendance AS a
JOIN event AS e ON e.event_id = a.link_to_event
JOIN income AS i ON i.link_to_member = a.link_to_member
WHERE e.event_name = 'Football game'
  AND i.source = 'Dues';
```

觀察：model replies=6、tool attempts=7、SQL attempts=2、latency=20.323s；stop=final_sql_ready。



<a id="q313"></a>

## [Q313](failure-case-review.md#q313) · dev · student_club

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R7／輸出形狀。

Agent officer/other 群組兩行，Gold 單行兩個平均欄。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Our officer team wants to settle a debate about whether we pull more weight than the rest of the club, so we need the attendance numbers before the next meeting. Could you tell us two things: the average number of events attended per officer, and the average number of events attended per other student, each rounded to two decimal places? To be clear on who counts where: officers are the members holding the position of President, Vice President, Secretary, or Treasurer, and everyone else in the club counts as an other student. Each average should cover every member of its group, and include every event in the club's records - there's no date cutoff.

Evidence：

Gold SQL（離線）：
```sql
WITH t AS (SELECT m.member_id, m.position, COUNT(a.link_to_event) AS cnt FROM member m LEFT JOIN attendance a ON a.link_to_member = m.member_id GROUP BY m.member_id, m.position) SELECT ROUND(AVG(CASE WHEN t.position IN ('President','Vice President','Secretary','Treasurer') THEN t.cnt END), 2) AS officer_avg, ROUND(AVG(CASE WHEN t.position NOT IN ('President','Vice President','Secretary','Treasurer') THEN t.cnt END), 2) AS other_students_avg FROM t
```

Agent SQL：
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

觀察：model replies=8、tool attempts=9、SQL attempts=5、latency=28.829s；stop=final_sql_ready。



<a id="q314"></a>

## [Q314](failure-case-review.md#q314) · dev · student_club

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R6／活動關係範圍。

Agent 只拆負remaining budget line的購買，Gold 先找over-budget events再納其所有budget lines。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm finalizing the semester wrap-up report and need one number: how many different kinds of things the club bought for events that went over budget this semester. A few things to keep in mind: an event counts as over budget if, in at least one of its budgeted categories, we spent more than we budgeted for that category - the budgeted amount minus what was actually spent came out below zero. Also, a single purchase can cover several kinds of things at once, and the purchase description lists what it bought, so make sure each kind is counted. The answer should cover the whole semester shown in the records, and I just need the single integer count, nothing else.

Evidence：went over budget: a budgeted category of the event ended with more spent than was budgeted for it, i.e. the amount budgeted minus the amount spent is below zero; kind of thing: a type of item bought, like water, pizza or posters

Gold SQL（離線）：
```sql
WITH RECURSIVE over_budget_events AS (SELECT DISTINCT link_to_event FROM budget WHERE amount - spent < 0), purchases AS (SELECT ex.expense_description AS d FROM expense ex JOIN budget b ON ex.link_to_budget = b.budget_id WHERE b.link_to_event IN (SELECT link_to_event FROM over_budget_events)), items(item, rest) AS (SELECT TRIM(SUBSTR(d || ',', 1, INSTR(d || ',', ',') - 1)), SUBSTR(d || ',', INSTR(d || ',', ',') + 1) FROM purchases UNION ALL SELECT TRIM(SUBSTR(rest, 1, INSTR(rest, ',') - 1)), SUBSTR(rest, INSTR(rest, ',') + 1) FROM items WHERE rest <> '') SELECT COUNT(DISTINCT LOWER(item)) AS kinds FROM items WHERE item <> ''
```

Agent SQL：
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

觀察：model replies=8、tool attempts=11、SQL attempts=7、latency=28.127s；stop=final_sql_ready。



<a id="q321"></a>

## [Q321](failure-case-review.md#q321) · dev · student_club

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／複合欄位拆解。

將整段 expense_description 當單一 item，未拆逗號分隔物品。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to review what the money actually went on for the well-funded events, by venue. For events that had a budget line of more than forty dollars, how many different things were bought for them at each location? Please give me, for each location, the location of the event and the number of different things bought for such events at that location, and nothing else. Note that a budget line of more than forty dollars means a single budgeted amount strictly over 40 dollars, and all qualifying events held at a location should be pooled together.

Evidence：

Gold SQL（離線）：
```sql
WITH RECURSIVE split(item, rest, loc) AS (SELECT '', x.expense_description || ',', e.location FROM expense x JOIN budget b ON b.budget_id = x.link_to_budget JOIN event e ON e.event_id = b.link_to_event WHERE b.amount > 40 UNION ALL SELECT trim(substr(rest, 1, instr(rest, ',') - 1)), substr(rest, instr(rest, ',') + 1), loc FROM split WHERE rest <> '') SELECT loc AS location, COUNT(DISTINCT item) AS things_bought FROM split WHERE item <> '' GROUP BY loc ORDER BY loc
```

Agent SQL：
```sql
SELECT e.location, COUNT(DISTINCT x.expense_description) AS different_things_bought
FROM event AS e
JOIN budget AS b ON b.link_to_event = e.event_id
JOIN expense AS x ON x.link_to_budget = b.budget_id
WHERE b.amount > 40
GROUP BY e.location;
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=12.754s；stop=final_sql_ready。



<a id="q326"></a>

## [Q326](failure-case-review.md#q326) · test · student_club

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／複合欄位拆解。

按完整 expense_description 計數，未拆 item 並計 DISTINCT expense_id。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together next semester's purchasing plan and want to know which food and drink item the club buys most often. Among purchases made under the food budget only, which single item appears on the most purchase records, and how many purchase records mention it? If two items are tied, go with the one whose name comes first alphabetically. Please give me just the item's name and that record count.

Evidence：A purchase record is an entry in the club's expense records for money spent on a purchase.

Gold SQL（離線）：
```sql
WITH RECURSIVE items(expense_id, item, rest) AS (SELECT e.expense_id, '', e.expense_description || ',' FROM expense e JOIN budget b ON e.link_to_budget = b.budget_id WHERE b.category = 'Food' UNION ALL SELECT expense_id, trim(substr(rest, 1, instr(rest, ',') - 1)), substr(rest, instr(rest, ',') + 1) FROM items WHERE rest <> '') SELECT item AS item_name, COUNT(DISTINCT expense_id) AS record_count FROM items WHERE item <> '' GROUP BY item ORDER BY record_count DESC, item LIMIT 1
```

Agent SQL：
```sql
SELECT e.expense_description, COUNT(*) AS record_count
FROM expense AS e
JOIN budget AS b ON b.budget_id = e.link_to_budget
WHERE b.category = 'Food'
GROUP BY e.expense_description
ORDER BY record_count DESC, e.expense_description ASC
LIMIT 1;
```

觀察：model replies=5、tool attempts=6、SQL attempts=3、latency=24.450s；stop=final_sql_ready。



<a id="q328"></a>

## [Q328](failure-case-review.md#q328) · dev · student_club

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／NULL與零。

無budget時 SUM 子查詢回傳 NULL，Gold COALESCE為0；attendance DISTINCT改變計數政策。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For every event in the club's records, can you give me the event name, event date, total amount budgeted for the event, and the number of members who attended it? Please sort the list by event name, then by event date, both in ascending order.

Evidence：

Gold SQL（離線）：
```sql
SELECT e.event_name, e.event_date, COALESCE(b.total_budgeted_amount, 0) AS total_budgeted_amount, COALESCE(a.attendee_count, 0) AS attendee_count FROM event AS e LEFT JOIN (SELECT link_to_event, SUM(amount) AS total_budgeted_amount FROM budget GROUP BY link_to_event) AS b ON b.link_to_event = e.event_id LEFT JOIN (SELECT link_to_event, COUNT(*) AS attendee_count FROM attendance GROUP BY link_to_event) AS a ON a.link_to_event = e.event_id ORDER BY e.event_name ASC, e.event_date ASC
```

Agent SQL：
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

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=13.053s；stop=final_sql_ready。



<a id="q329"></a>

## [Q329](failure-case-review.md#q329) · dev · student_club

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／複合欄位拆解。

把完整 expense_description 當 item，未拆分每個物品。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing the year-end audit of club spending. For each item Sacha Harrison bought with club money, I need the item name and how many times she bought it. Can you give me that list?

Evidence：By "item" I mean an individual thing named in a record of what money was spent for.

Gold SQL（離線）：
```sql
WITH RECURSIVE split(rest, item) AS (SELECT expense_description || ',', '' FROM expense WHERE link_to_member = (SELECT member_id FROM member WHERE first_name = 'Sacha' AND last_name = 'Harrison') UNION ALL SELECT substr(rest, instr(rest, ',') + 1), trim(substr(rest, 1, instr(rest, ',') - 1)) FROM split WHERE rest <> '') SELECT item, COUNT(*) AS times FROM split WHERE item <> '' GROUP BY item ORDER BY item
```

Agent SQL：
```sql
SELECT e.expense_description AS item_name, COUNT(*) AS times_bought
FROM expense AS e
JOIN member AS m
  ON e.link_to_member = m.member_id
WHERE m.first_name = 'Sacha'
  AND m.last_name = 'Harrison'
GROUP BY e.expense_description
ORDER BY e.expense_description;
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=12.172s；stop=final_sql_ready。



<a id="q338"></a>

## [Q338](failure-case-review.md#q338) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／佔位值。

已知姓名未排除 '-' 佔位字串。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What known full names belong to superheroes tied for the highest strength attribute value?

Evidence：

Gold SQL（離線）：
```sql
SELECT DISTINCT s.full_name FROM superhero AS s JOIN hero_attribute AS ha ON ha.hero_id = s.id JOIN attribute AS a ON a.id = ha.attribute_id WHERE a.attribute_name = 'Strength' AND ha.attribute_value = ( SELECT MAX(ha2.attribute_value) FROM hero_attribute AS ha2 JOIN attribute AS a2 ON a2.id = ha2.attribute_id WHERE a2.attribute_name = 'Strength' ) AND s.full_name IS NOT NULL AND s.full_name <> '-' ORDER BY s.full_name ASC
```

Agent SQL：
```sql
SELECT DISTINCT s.full_name
FROM superhero AS s
JOIN hero_attribute AS ha ON ha.hero_id = s.id
JOIN attribute AS a ON a.id = ha.attribute_id
WHERE lower(a.attribute_name) = 'strength'
  AND ha.attribute_value = (
    SELECT MAX(ha2.attribute_value)
    FROM hero_attribute AS ha2
    JOIN attribute AS a2 ON a2.id = ha2.attribute_id
    WHERE lower(a2.attribute_name) = 'strength'
  )
  AND s.full_name IS NOT NULL
  AND trim(s.full_name) <> ''
ORDER BY s.full_name;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=26.593s；stop=final_sql_ready。



<a id="q342"></a>

## [Q342](failure-case-review.md#q342) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

把 publisher 與差額串成一欄，Gold 為 publisher、ABS差額兩欄。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which publisher has more superheroes, DC Comics or Marvel Comics, and by how many? Return Tie if their counts are equal.

Evidence：

Gold SQL（離線）：
```sql
WITH counts AS (SELECT SUM(CASE WHEN p.publisher_name = 'DC Comics' THEN 1 ELSE 0 END) AS dc, SUM(CASE WHEN p.publisher_name = 'Marvel Comics' THEN 1 ELSE 0 END) AS marvel FROM superhero AS s JOIN publisher AS p ON p.id = s.publisher_id) SELECT CASE WHEN dc > marvel THEN 'DC Comics' WHEN marvel > dc THEN 'Marvel Comics' ELSE 'Tie' END, ABS(dc - marvel) FROM counts
```

Agent SQL：
```sql
WITH counts AS (
    SELECT
        p.publisher_name,
        COUNT(s.id) AS superhero_count
    FROM publisher AS p
    LEFT JOIN superhero AS s
        ON s.publisher_id = p.id
    WHERE p.publisher_name IN ('DC Comics', 'Marvel Comics')
    GROUP BY p.publisher_name
)
SELECT CASE
           WHEN dc.superhero_count = marvel.superhero_count THEN 'Tie'
           WHEN dc.superhero_count > marvel.superhero_count
               THEN 'DC Comics by ' || (dc.superhero_count - marvel.superhero_count)
           ELSE 'Marvel Comics by ' || (marvel.superhero_count - dc.superhero_count)
       END AS result
FROM counts AS dc
CROSS JOIN counts AS marvel
WHERE dc.publisher_name = 'DC Comics'
  AND marvel.publisher_name = 'Marvel Comics';
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=12.743s；stop=final_sql_ready。



<a id="q343"></a>

## [Q343](failure-case-review.md#q343) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

measured height 只排 NULL，未排0佔位值。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm comparing Marvel and DC rosters and want to quantify how tall Marvel's roster is for characters whose abilities DC cannot match. What is the average height, in centimetres, of Marvel Comics characters who have at least one power that no DC Comics character has? Only characters with a measured height count.

Evidence：A "power" is any single ability listed for a character in the database.

Gold SQL（離線）：
```sql
SELECT AVG(s.height_cm) AS average_height_cm FROM superhero AS s JOIN publisher AS p ON s.publisher_id = p.id WHERE p.publisher_name = 'Marvel Comics' AND s.height_cm > 0 AND EXISTS (SELECT 1 FROM hero_power AS hp WHERE hp.hero_id = s.id AND NOT EXISTS (SELECT 1 FROM hero_power AS hp2 JOIN superhero AS s2 ON s2.id = hp2.hero_id JOIN publisher AS p2 ON p2.id = s2.publisher_id WHERE p2.publisher_name = 'DC Comics' AND hp2.power_id = hp.power_id))
```

Agent SQL：
```sql
WITH dc_powers AS (
  SELECT DISTINCT hp.power_id
  FROM hero_power AS hp
  JOIN superhero AS h ON h.id = hp.hero_id
  JOIN publisher AS p ON p.id = h.publisher_id
  WHERE p.publisher_name = 'DC Comics'
),
marvel_characters AS (
  SELECT DISTINCT h.id, h.height_cm
  FROM superhero AS h
  JOIN publisher AS p ON p.id = h.publisher_id
  JOIN hero_power AS hp ON hp.hero_id = h.id
  WHERE p.publisher_name = 'Marvel Comics'
    AND h.height_cm IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM dc_powers AS d
      WHERE d.power_id = hp.power_id
    )
)
SELECT AVG(height_cm)
FROM marvel_characters;
```

觀察：model replies=5、tool attempts=7、SQL attempts=2、latency=23.853s；stop=final_sql_ready。



<a id="q345"></a>

## [Q345](failure-case-review.md#q345) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

known weight 只排 NULL，未排0佔位值。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm setting a typical weight for a green-skinned creature class. Can you tell me the average weight in kg of the heroes with green skin? Count only heroes whose weight is known, and give me one number rounded to one decimal place.

Evidence：Green skin means the hero's skin colour is green.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(T1.weight_kg), 1) AS average_weight_kg FROM superhero AS T1 INNER JOIN colour AS T2 ON T1.skin_colour_id = T2.id WHERE T2.colour = 'Green' AND T1.weight_kg > 0
```

Agent SQL：
```sql
SELECT ROUND(AVG(s.weight_kg), 1)
FROM superhero AS s
JOIN colour AS c ON c.id = s.skin_colour_id
WHERE c.colour = 'Green'
  AND s.weight_kg IS NOT NULL;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=11.323s；stop=final_sql_ready。



<a id="q346"></a>

## [Q346](failure-case-review.md#q346) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／可選關係。

INNER JOIN alignment 排除沒有 alignment 關係的英雄，Gold LEFT JOIN保留。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm writing an article about heroes who fall outside the classic good-versus-evil divide. How many superheroes in the database have an alignment that is neither good nor bad? Please give me just that count. Note that this should cover all superheroes in the database.

Evidence：good: a superhero whose alignment is Good; bad: a superhero whose alignment is Bad; alignment: the moral category assigned to a superhero

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS neither_good_nor_bad FROM superhero AS s LEFT JOIN alignment AS a ON s.alignment_id = a.id WHERE a.alignment IS NULL OR a.alignment NOT IN ('Good', 'Bad')
```

Agent SQL：
```sql
SELECT COUNT(*)
FROM superhero AS s
JOIN alignment AS a ON a.id = s.alignment_id
WHERE LOWER(a.alignment) NOT IN ('good', 'bad')
   OR a.alignment IS NULL;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=13.591s；stop=final_sql_ready。



<a id="q348"></a>

## [Q348](failure-case-review.md#q348) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

平均 weight 未排除未量度的0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to profile the cohort of heroes whose Intelligence score matches Abomination's Intelligence score. What is their average measured weight in kg? Please round the average to two decimals.

Evidence：Intelligence is one of the six attribute scores a hero has (Intelligence, Strength, Speed, Durability, Power, Combat)

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END), 2) AS average_weight_kg FROM superhero s JOIN hero_attribute ha ON ha.hero_id = s.id JOIN attribute a ON a.id = ha.attribute_id WHERE a.attribute_name = 'Intelligence' AND ha.attribute_value = (SELECT abom_ha.attribute_value FROM superhero abom JOIN hero_attribute abom_ha ON abom_ha.hero_id = abom.id JOIN attribute abom_a ON abom_a.id = abom_ha.attribute_id WHERE abom.superhero_name = 'Abomination' AND abom_a.attribute_name = 'Intelligence')
```

Agent SQL：
```sql
SELECT ROUND(AVG(s.weight_kg), 2) AS average_weight_kg
FROM superhero AS s
JOIN hero_attribute AS ha ON ha.hero_id = s.id
JOIN attribute AS a ON a.id = ha.attribute_id
WHERE a.attribute_name = 'Intelligence'
  AND ha.attribute_value = (
      SELECT ha2.attribute_value
      FROM superhero AS s2
      JOIN hero_attribute AS ha2 ON ha2.hero_id = s2.id
      JOIN attribute AS a2 ON a2.id = ha2.attribute_id
      WHERE s2.superhero_name = 'Abomination'
        AND a2.attribute_name = 'Intelligence'
  );
```

觀察：model replies=5、tool attempts=8、SQL attempts=4、latency=19.696s；stop=final_sql_ready。



<a id="q349"></a>

## [Q349](failure-case-review.md#q349) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／零次群組。

從合資格英雄GROUP BY，缺少零人gender，Gold從gender LEFT JOIN；power COUNT DISTINCT政策亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a trivia page profiling blue-haired heroes by their abilities. For each gender, male and female, how many blue-haired superheroes have at least ten listed powers? I need the count for both groups, and by 'at least ten' I mean ten or more.

Evidence：Listed powers: the superpowers recorded for a hero.

Gold SQL（離線）：
```sql
SELECT g.gender AS gender, COUNT(s.id) AS superhero_count FROM gender g LEFT JOIN superhero s ON s.gender_id = g.id AND s.hair_colour_id = (SELECT id FROM colour WHERE colour = 'Blue') AND (SELECT COUNT(*) FROM hero_power hp WHERE hp.hero_id = s.id) >= 10 WHERE g.gender IN ('Male','Female') GROUP BY g.gender ORDER BY g.gender
```

Agent SQL：
```sql
SELECT g.gender, COUNT(*) AS hero_count
FROM superhero AS s
JOIN gender AS g ON g.id = s.gender_id
JOIN colour AS c ON c.id = s.hair_colour_id
JOIN (
    SELECT hero_id, COUNT(DISTINCT power_id) AS power_count
    FROM hero_power
    GROUP BY hero_id
) AS hp ON hp.hero_id = s.id
WHERE g.gender IN ('Male', 'Female')
  AND c.colour = 'Blue'
  AND hp.power_count >= 10
GROUP BY g.gender
ORDER BY CASE g.gender WHEN 'Male' THEN 1 WHEN 'Female' THEN 2 END;
```

觀察：model replies=5、tool attempts=9、SQL attempts=3、latency=27.200s；stop=final_sql_ready。



<a id="q350"></a>

## [Q350](failure-case-review.md#q350) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

known weight 只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a comparison of the heaviest brick-strength characters. What is the average weight, in kilograms, of all superheroes whose Strength score equals the Hulk's? I just need a single integer rounded to the nearest kilogram. Include every superhero in the database, no restrictions on publisher or alignment. If a hero's weight is unknown, leave them out and average only over the heroes whose weight has actually been measured.

Evidence：Strength is one of the six measured hero attributes, each scored on a 1-100 scale; the Hulk is the superhero named 'Hulk'; weight is the superhero's weight in kilograms.

Gold SQL（離線）：
```sql
SELECT CAST(ROUND(AVG(s.weight_kg)) AS INTEGER) AS average_weight_kg FROM superhero s INNER JOIN hero_attribute ha ON ha.hero_id = s.id INNER JOIN attribute a ON a.id = ha.attribute_id WHERE a.attribute_name = 'Strength' AND ha.attribute_value = (SELECT ha2.attribute_value FROM superhero s2 INNER JOIN hero_attribute ha2 ON ha2.hero_id = s2.id INNER JOIN attribute a2 ON a2.id = ha2.attribute_id WHERE s2.superhero_name = 'Hulk' AND a2.attribute_name = 'Strength') AND s.weight_kg > 0
```

Agent SQL：
```sql
SELECT CAST(ROUND(AVG(s.weight_kg)) AS INTEGER) AS average_weight_kg
FROM superhero AS s
JOIN hero_attribute AS ha ON ha.hero_id = s.id
JOIN attribute AS a ON a.id = ha.attribute_id
WHERE a.attribute_name = 'Strength'
  AND ha.attribute_value = (
      SELECT hha.attribute_value
      FROM superhero AS h
      JOIN hero_attribute AS hha ON hha.hero_id = h.id
      JOIN attribute AS ha_attr ON ha_attr.id = hha.attribute_id
      WHERE h.superhero_name = 'Hulk'
        AND ha_attr.attribute_name = 'Strength'
  )
  AND s.weight_kg IS NOT NULL;
```

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=27.161s；stop=final_sql_ready。



<a id="q352"></a>

## [Q352](failure-case-review.md#q352) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／佔位值。

no race 只接受race_id NULL，未納race='-'。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：How many characters published by A-Bomb's publisher have no race listed? I just need a single count. (By A-Bomb's publisher, I mean the publisher that publishes the character A-Bomb.)

Evidence：race: the character's race or group, e.g. Human, Alien, Mutant

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS character_count FROM superhero WHERE publisher_id = (SELECT publisher_id FROM superhero WHERE superhero_name = 'A-Bomb') AND (race_id IS NULL OR race_id = (SELECT id FROM race WHERE race = '-'))
```

Agent SQL：
```sql
SELECT COUNT(*) AS count
FROM superhero
WHERE publisher_id = (
    SELECT publisher_id
    FROM superhero
    WHERE superhero_name = 'A-Bomb'
)
AND race_id IS NULL;
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=14.359s；stop=final_sql_ready。



<a id="q353"></a>

## [Q353](failure-case-review.md#q353) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加集合。

race IN ('God / Eternal','Eternal')，多納未要求的Eternal類別。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Hey, following up on my count of the God / Eternal heroes – among those who are male, what's the average number of superpowers per hero? Just give me the average rounded to two decimal places.

Evidence：A superpower is any power linked to a hero.

Gold SQL（離線）：
```sql
WITH power_counts AS (SELECT s.id, (SELECT COUNT(*) FROM hero_power AS hp WHERE hp.hero_id = s.id) AS power_count FROM superhero AS s INNER JOIN race AS r ON s.race_id = r.id INNER JOIN gender AS g ON s.gender_id = g.id WHERE r.race = 'God / Eternal' AND g.gender = 'Male') SELECT ROUND(AVG(power_count), 2) AS average_superpowers FROM power_counts
```

Agent SQL：
```sql
SELECT ROUND(AVG(power_count), 2)
FROM (
    SELECT s.id, COUNT(hp.power_id) AS power_count
    FROM superhero AS s
    JOIN race AS r ON r.id = s.race_id
    JOIN gender AS g ON g.id = s.gender_id
    LEFT JOIN hero_power AS hp ON hp.hero_id = s.id
    WHERE r.race IN ('God / Eternal', 'Eternal')
      AND g.gender = 'Male'
    GROUP BY s.id
);
```

觀察：model replies=14、tool attempts=22、SQL attempts=14、latency=58.521s；stop=final_sql_ready。



<a id="q355"></a>

## [Q355](failure-case-review.md#q355) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

已知weight只排NULL，未排0；matching eye colour本身已有處理。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the average weight in kilograms of the DC Comics heroes whose eye colour is also shared by at least one Marvel Comics hero? Leave out any heroes whose weight is unknown, round the result to the nearest kilogram, and treat 'No Colour' as an eye colour like any other when matching between publishers. I just want that single number.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END)) AS average_weight_kg FROM superhero AS s JOIN publisher AS p ON s.publisher_id = p.id WHERE p.publisher_name = 'DC Comics' AND s.eye_colour_id IN (SELECT s2.eye_colour_id FROM superhero AS s2 JOIN publisher AS p2 ON s2.publisher_id = p2.id WHERE p2.publisher_name = 'Marvel Comics')
```

Agent SQL：
```sql
SELECT ROUND(AVG(dc.weight_kg)) AS average_weight_kg
FROM superhero AS dc
JOIN publisher AS dp ON dp.id = dc.publisher_id
JOIN colour AS eye ON eye.id = dc.eye_colour_id
WHERE dp.publisher_name = 'DC Comics'
  AND dc.weight_kg IS NOT NULL
  AND EXISTS (
    SELECT 1
    FROM superhero AS marvel
    JOIN publisher AS mp ON mp.id = marvel.publisher_id
    JOIN colour AS marvel_eye ON marvel_eye.id = marvel.eye_colour_id
    WHERE mp.publisher_name = 'Marvel Comics'
      AND marvel_eye.colour = eye.colour
  );
```

觀察：model replies=5、tool attempts=8、SQL attempts=4、latency=19.251s；stop=final_sql_ready。



<a id="q356"></a>

## [Q356](failure-case-review.md#q356) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

recorded height只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm researching heroes like A-Bomb. What is the average height in centimetres of the superheroes in A-Bomb's group? Please give me just that single number, rounded to one decimal place. Note that A-Bomb itself belongs to its group and should be included, and only heroes whose height is actually on record should count toward the average-anyone without a recorded height should be left out rather than counted as some height.

Evidence：In this request, "group" refers to race.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CASE WHEN height_cm > 0 THEN height_cm END), 1) AS average_height_cm FROM superhero WHERE race_id = (SELECT race_id FROM superhero WHERE superhero_name = 'A-Bomb')
```

Agent SQL：
```sql
SELECT ROUND(AVG(height_cm), 1)
FROM superhero
WHERE race_id = (SELECT race_id FROM superhero WHERE superhero_name = 'A-Bomb')
  AND height_cm IS NOT NULL;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=14.202s；stop=final_sql_ready。



<a id="q357"></a>

## [Q357](failure-case-review.md#q357) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

recorded weight只排NULL，未排0；eligible_races使用gender inner join另可能失去未知gender資料。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the average weight, in kg, of the heroes who belong to races in which no hero is female? Heroes whose weight is not recorded should not count toward the average. I just need that single value.

Evidence：female: the hero's gender is female

Gold SQL（離線）：
```sql
SELECT AVG(T1.weight_kg) AS average_weight_kg FROM superhero AS T1 INNER JOIN race AS T2 ON T1.race_id = T2.id WHERE T1.weight_kg > 0 AND NOT EXISTS (SELECT 1 FROM superhero AS T3 INNER JOIN gender AS T4 ON T3.gender_id = T4.id WHERE T3.race_id = T2.id AND T4.gender = 'Female')
```

Agent SQL：
```sql
WITH eligible_races AS (
    SELECT s.race_id
    FROM superhero AS s
    JOIN gender AS g ON g.id = s.gender_id
    WHERE s.race_id IS NOT NULL
    GROUP BY s.race_id
    HAVING SUM(CASE WHEN g.gender = 'Female' THEN 1 ELSE 0 END) = 0
)
SELECT AVG(s.weight_kg) AS average_weight_kg
FROM superhero AS s
JOIN eligible_races AS er ON er.race_id = s.race_id
WHERE s.weight_kg IS NOT NULL;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=24.747s；stop=final_sql_ready。



<a id="q358"></a>

## [Q358](failure-case-review.md#q358) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／佔位值。

只要求publisher_id非空，未排除publisher_name=''的無名publisher。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm writing a piece about which real publishing companies have put out very tall heroes. How many publishers in the database have released at least one hero taller than 200 cm? Note that taller than 200 cm means strictly more than 200 cm, and it counts if even one of their heroes is that tall. I just need the number of publishers, nothing else.

Evidence：A hero's publisher being 'released' means the publisher the hero is attributed to in the database.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T1.publisher_id) AS publisher_count FROM superhero AS T1 INNER JOIN publisher AS T2 ON T1.publisher_id = T2.id WHERE T1.height_cm > 200 AND T2.publisher_name <> ''
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT publisher_id) AS publisher_count
FROM superhero
WHERE height_cm > 200
  AND publisher_id IS NOT NULL;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=9.739s；stop=final_sql_ready。



<a id="q360"></a>

## [Q360](failure-case-review.md#q360) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

known weight只排NULL，未排0，平均及count母體均改變。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm comparing superhero body weights to typical human weights for an article. What is the average weight in kilograms of superheroes published by DC Comics, rounded to one decimal place, and how many DC Comics superheroes is that average based on? Only superheroes with a known weight should count toward the average, so the count should be the number of superheroes it's based on. DC Comics means the publisher named DC Comics.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(s.weight_kg), 1) AS avg_weight_kg, COUNT(*) AS hero_count FROM superhero s JOIN publisher p ON s.publisher_id = p.id WHERE p.publisher_name = 'DC Comics' AND s.weight_kg > 0
```

Agent SQL：
```sql
SELECT ROUND(AVG(s.weight_kg), 1) AS average_weight_kg,
       COUNT(*) AS superhero_count
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
WHERE p.publisher_name = 'DC Comics'
  AND s.weight_kg IS NOT NULL;
```

觀察：model replies=5、tool attempts=5、SQL attempts=2、latency=15.201s；stop=final_sql_ready。



<a id="q362"></a>

## [Q362](failure-case-review.md#q362) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／佔位值。

no race只排race_id NULL，未排race='-'，可能選中佔位race。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Which race is the most common among the superheroes published by the same publisher as the superhero whose full name is Charles Chandler? I'd like, for that publisher's superheroes only, the name of the most common race and the count of that publisher's superheroes of that race. Ignore any superhero with no race recorded. If several races tie for most common, list every tied race with its count.

Evidence：Race: the superhero's species or type, e.g. Human, Mutant, Alien.

Gold SQL（離線）：
```sql
WITH counts AS (SELECT r.race AS race, COUNT(*) AS hero_count FROM superhero AS s INNER JOIN race AS r ON s.race_id = r.id WHERE s.publisher_id = (SELECT publisher_id FROM superhero WHERE full_name = 'Charles Chandler') AND r.race <> '-' GROUP BY r.id, r.race) SELECT race, hero_count FROM counts WHERE hero_count = (SELECT MAX(hero_count) FROM counts)
```

Agent SQL：
```sql
SELECT r.race, COUNT(*) AS superhero_count
FROM superhero AS s
JOIN race AS r ON r.id = s.race_id
WHERE s.publisher_id = (
    SELECT publisher_id
    FROM superhero
    WHERE full_name = 'Charles Chandler'
)
  AND s.race_id IS NOT NULL
GROUP BY r.id, r.race
HAVING COUNT(*) = (
    SELECT MAX(race_count)
    FROM (
        SELECT COUNT(*) AS race_count
        FROM superhero
        WHERE publisher_id = (
            SELECT publisher_id
            FROM superhero
            WHERE full_name = 'Charles Chandler'
        )
          AND race_id IS NOT NULL
        GROUP BY race_id
    )
);
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=25.432s；stop=final_sql_ready。



<a id="q363"></a>

## [Q363](failure-case-review.md#q363) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

known weight只排NULL，未排0；gender_id硬編碼需trace確認。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What is the average weight in kg of the Female heroes in the database? Round it to two decimal places, and skip any heroes whose weight is unknown. I just need that single number.

Evidence：kg: kilograms

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(weight_kg), 2) AS average_weight_kg FROM superhero WHERE gender_id = (SELECT id FROM gender WHERE gender = 'Female') AND weight_kg > 0
```

Agent SQL：
```sql
SELECT ROUND(AVG(weight_kg), 2)
FROM superhero
WHERE gender_id = 2
  AND weight_kg IS NOT NULL;
```

觀察：model replies=6、tool attempts=5、SQL attempts=2、latency=13.918s；stop=final_sql_ready。



<a id="q365"></a>

## [Q365](failure-case-review.md#q365) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

按gender輸出兩行，Gold為male/female兩個平均欄單行。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm comparing how power-rich male and female heroes are. For all male heroes and all female heroes that have a documented real full name, what is the average number of superpowers per hero for each gender? Please compute each average over the entire hero population of that gender, not just the heroes that happen to have power records. Give me both averages, each rounded to two decimal places, and nothing else.

Evidence：Full name: the hero's real, full personal name (first name plus last name, and optionally middle names); single names such as mononyms or aliases are not a full name.

Gold SQL（離線）：
```sql
SELECT ROUND(CAST(SUM(CASE WHEN g.gender = 'Male' THEN COALESCE(pc.cnt, 0) ELSE 0 END) AS REAL) / SUM(CASE WHEN g.gender = 'Male' THEN 1 ELSE 0 END), 2) AS avg_superpowers_male, ROUND(CAST(SUM(CASE WHEN g.gender = 'Female' THEN COALESCE(pc.cnt, 0) ELSE 0 END) AS REAL) / SUM(CASE WHEN g.gender = 'Female' THEN 1 ELSE 0 END), 2) AS avg_superpowers_female FROM superhero AS s INNER JOIN gender AS g ON s.gender_id = g.id LEFT JOIN (SELECT hero_id, COUNT(*) AS cnt FROM hero_power GROUP BY hero_id) AS pc ON pc.hero_id = s.id WHERE s.full_name LIKE '% %'
```

Agent SQL：
```sql
WITH hero_counts AS (
    SELECT
        s.id,
        g.gender,
        COUNT(DISTINCT hp.power_id) AS power_count
    FROM superhero AS s
    JOIN gender AS g ON g.id = s.gender_id
    LEFT JOIN hero_power AS hp ON hp.hero_id = s.id
    WHERE g.gender IN ('Male', 'Female')
      AND TRIM(COALESCE(s.full_name, '')) NOT IN ('', '-')
      AND instr(TRIM(s.full_name), ' ') > 0
    GROUP BY s.id, g.gender
)
SELECT
    gender,
    ROUND(AVG(power_count), 2) AS average_superpowers
FROM hero_counts
GROUP BY gender
ORDER BY gender;
```

觀察：model replies=5、tool attempts=8、SQL attempts=3、latency=17.715s；stop=final_sql_ready。



<a id="q366"></a>

## [Q366](failure-case-review.md#q366) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

兩個AVG各自未排0 measurement，Gold用各欄CASE>0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a physical profile of the green-skinned villain corner of the universe for a fan wiki page. Could you tell me the average height in centimetres and the average weight in kilograms of the green-skinned villains? Please average only over the characters whose measurement is actually on record - a character with no recorded height or weight shouldn't drag the average down - and round each average to two decimals. I just need those two numbers.

Evidence：By 'villain' I mean a character whose alignment is Bad, and by 'green-skinned' I mean a character whose skin colour is Green. Height in centimetres and weight in kilograms are the character's height_cm and weight_kg as commonly understood physical measurements.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CASE WHEN T1.height_cm > 0 THEN T1.height_cm END), 2) AS avg_height_cm, ROUND(AVG(CASE WHEN T1.weight_kg > 0 THEN T1.weight_kg END), 2) AS avg_weight_kg FROM superhero AS T1 INNER JOIN alignment AS T2 ON T1.alignment_id = T2.id INNER JOIN colour AS T3 ON T1.skin_colour_id = T3.id WHERE T2.alignment = 'Bad' AND T3.colour = 'Green'
```

Agent SQL：
```sql
SELECT
    ROUND(AVG(s.height_cm), 2) AS average_height_cm,
    ROUND(AVG(s.weight_kg), 2) AS average_weight_kg
FROM superhero AS s
JOIN alignment AS a ON s.alignment_id = a.id
JOIN colour AS c ON s.skin_colour_id = c.id
WHERE a.alignment = 'Bad'
  AND c.colour = 'Green';
```

觀察：model replies=4、tool attempts=6、SQL attempts=1、latency=13.758s；stop=final_sql_ready。



<a id="q368"></a>

## [Q368](failure-case-review.md#q368) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

known height只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'd like to know how tall the heroes are who share at least one superpower with 3-D Man. Can you give me the average height in centimetres of those heroes, rounded to one decimal place? Please leave 3-D Man himself out of it, and don't count heroes whose height isn't known.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(s.height_cm), 1) AS avg_height_cm FROM superhero AS s WHERE s.height_cm > 0 AND s.id <> (SELECT id FROM superhero WHERE superhero_name = '3-D Man') AND s.id IN (SELECT hp2.hero_id FROM hero_power AS hp2 WHERE hp2.power_id IN (SELECT power_id FROM hero_power WHERE hero_id = (SELECT id FROM superhero WHERE superhero_name = '3-D Man')))
```

Agent SQL：
```sql
SELECT ROUND(AVG(s.height_cm), 1) AS average_height_cm
FROM superhero AS s
WHERE s.id <> (
    SELECT id
    FROM superhero
    WHERE superhero_name = '3-D Man'
)
  AND s.height_cm IS NOT NULL
  AND EXISTS (
      SELECT 1
      FROM hero_power AS hp
      WHERE hp.hero_id = s.id
        AND hp.power_id IN (
            SELECT hp3.power_id
            FROM hero_power AS hp3
            WHERE hp3.hero_id = (
                SELECT id
                FROM superhero
                WHERE superhero_name = '3-D Man'
            )
        )
  );
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=17.602s；stop=final_sql_ready。



<a id="q369"></a>

## [Q369](failure-case-review.md#q369) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

measured weight只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm writing an article about green-skinned flying villains and need a body-statistics fact. What is the average weight, in kilograms, of all green-skinned villains who can fly? By villain I mean a character whose moral affiliation is Bad. Please include only characters whose weight was actually measured-any character whose weight was never measured should be left out of the average. Give me just the single number, rounded to the nearest kilogram.

Evidence：Flight: the power to fly.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END)) AS average_weight_kg FROM superhero AS s INNER JOIN alignment AS a ON s.alignment_id = a.id INNER JOIN colour AS c ON s.skin_colour_id = c.id INNER JOIN hero_power AS hp ON hp.hero_id = s.id INNER JOIN superpower AS sp ON sp.id = hp.power_id WHERE a.alignment = 'Bad' AND c.colour = 'Green' AND sp.power_name = 'Flight'
```

Agent SQL：
```sql
SELECT ROUND(AVG(s.weight_kg)) AS average_weight_kg
FROM superhero AS s
JOIN alignment AS a ON a.id = s.alignment_id
JOIN colour AS c ON c.id = s.skin_colour_id
JOIN hero_power AS hp ON hp.hero_id = s.id
JOIN superpower AS p ON p.id = hp.power_id
WHERE a.alignment = 'Bad'
  AND c.colour = 'Green'
  AND p.power_name = 'Flight'
  AND s.weight_kg IS NOT NULL;
```

觀察：model replies=5、tool attempts=11、SQL attempts=5、latency=25.702s；stop=final_sql_ready。



<a id="q370"></a>

## [Q370](failure-case-review.md#q370) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

recorded weight只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm doing a physical-profile breakdown of the George Lucas catalogue. For the heroes published by George Lucas that have at least one superpower in the database, what is their average weight in kilograms, counting only the heroes whose weight is recorded? Please give me just that one number, rounded to two decimal places.

Evidence：George Lucas refers to the publisher name.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END), 2) AS avg_weight_kg FROM superhero AS s INNER JOIN publisher AS p ON s.publisher_id = p.id WHERE p.publisher_name = 'George Lucas' AND EXISTS (SELECT 1 FROM hero_power AS hp WHERE hp.hero_id = s.id)
```

Agent SQL：
```sql
SELECT ROUND(AVG(s.weight_kg), 2)
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
WHERE p.publisher_name = 'George Lucas'
  AND s.weight_kg IS NOT NULL
  AND EXISTS (
      SELECT 1
      FROM hero_power AS hp
      WHERE hp.hero_id = s.id
  );
```

觀察：model replies=5、tool attempts=7、SQL attempts=2、latency=17.128s；stop=final_sql_ready。



<a id="q371"></a>

## [Q371](failure-case-review.md#q371) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

known weight只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the article I'm writing on heroic female characters, I'd like a physique stat for the trivia box: what is the average weight in kilograms of female superheroes whose alignment is good? Only count superheroes whose weight is known. Please round the result to two decimal places.

Evidence：Alignment: the superhero's moral category, e.g. good, bad, neutral.

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(s.weight_kg), 2) AS average_weight_kg FROM superhero AS s JOIN gender AS g ON g.id = s.gender_id JOIN alignment AS a ON a.id = s.alignment_id WHERE g.gender = 'Female' AND a.alignment = 'Good' AND s.weight_kg > 0
```

Agent SQL：
```sql
SELECT ROUND(AVG(CAST(s.weight_kg AS REAL)), 2) AS average_weight_kg
FROM superhero AS s
JOIN gender AS g ON s.gender_id = g.id
JOIN alignment AS a ON s.alignment_id = a.id
WHERE g.gender = 'Female'
  AND a.alignment = 'Good'
  AND s.weight_kg IS NOT NULL;
```

觀察：model replies=5、tool attempts=7、SQL attempts=3、latency=15.537s；stop=final_sql_ready。



<a id="q372"></a>

## [Q372](failure-case-review.md#q372) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

under70 weight只排NULL，0佔位值被當輕量英雄納入。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm picking powers for a lightweight male hero archetype. How many different superpowers are held by at least one male superhero who weighs under 70 kilograms? Heroes whose weight isn't recorded shouldn't count as weighing under 70.

Evidence：

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT hp.power_id) AS power_count FROM superhero AS s JOIN hero_power AS hp ON hp.hero_id = s.id JOIN superpower AS sp ON sp.id = hp.power_id JOIN gender AS g ON g.id = s.gender_id WHERE g.gender = 'Male' AND s.weight_kg > 0 AND s.weight_kg < 70;
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT hp.power_id)
FROM superhero AS s
JOIN gender AS g ON g.id = s.gender_id
JOIN hero_power AS hp ON hp.hero_id = s.id
WHERE g.gender = 'Male'
  AND s.weight_kg < 70
  AND s.weight_kg IS NOT NULL;
```

觀察：model replies=4、tool attempts=6、SQL attempts=1、latency=15.171s；stop=final_sql_ready。



<a id="q373"></a>

## [Q373](failure-case-review.md#q373) · test · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／必要篩選。

缺少Human race條件，且最低height未排0。

診斷改寫：1次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a trivia fact box on tiny heroes. Could you tell me the hair colour of the shortest human superhero? Please treat heroes with no recorded height as unmeasured rather than as being the shortest. I just need the colour, nothing else.

Evidence：

Gold SQL（離線）：
```sql
SELECT DISTINCT c.colour FROM superhero AS s INNER JOIN race AS r ON s.race_id = r.id INNER JOIN colour AS c ON s.hair_colour_id = c.id WHERE r.race = 'Human' AND s.height_cm = (SELECT MIN(x.height_cm) FROM superhero AS x INNER JOIN race AS y ON x.race_id = y.id WHERE y.race = 'Human' AND x.height_cm > 0)
```

Agent SQL：
```sql
SELECT c.colour
FROM superhero AS s
LEFT JOIN colour AS c ON c.id = s.hair_colour_id
WHERE s.height_cm = (
    SELECT MIN(height_cm)
    FROM superhero
    WHERE height_cm IS NOT NULL
);
```

觀察：model replies=8、tool attempts=10、SQL attempts=5、latency=30.729s；stop=final_sql_ready。



<a id="q374"></a>

## [Q374](failure-case-review.md#q374) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

MIN(weight)只排NULL，0可被誤當最輕量體重。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to know about the lightest superhero whose weight has actually been recorded. Among all heroes sharing that lightest weight, give me the largest number of superpowers any of them has. If such a hero has no powers, that counts as 0. Please return just that one number.

Evidence：A superpower is one power a hero has, identified by its name.

Gold SQL（離線）：
```sql
SELECT MAX(cnt) AS power_count FROM (SELECT COUNT(hp.power_id) AS cnt FROM superhero AS h LEFT JOIN hero_power hp ON h.id = hp.hero_id WHERE h.weight_kg = (SELECT MIN(weight_kg) FROM superhero WHERE weight_kg > 0) GROUP BY h.id)
```

Agent SQL：
```sql
WITH lightest_weight AS (
    SELECT MIN(weight_kg) AS weight_kg
    FROM superhero
    WHERE weight_kg IS NOT NULL
),
hero_power_counts AS (
    SELECT h.id, COUNT(DISTINCT hp.power_id) AS power_count
    FROM superhero AS h
    JOIN lightest_weight AS lw ON h.weight_kg = lw.weight_kg
    LEFT JOIN hero_power AS hp ON hp.hero_id = h.id
    GROUP BY h.id
)
SELECT MAX(power_count)
FROM hero_power_counts;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=19.712s；stop=final_sql_ready。



<a id="q377"></a>

## [Q377](failure-case-review.md#q377) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／NULL集合語義。

Agent把未知hair_colour也計not brown；Gold條件h.colour<>'Brown'不計NULL，且保留零次eye group。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm looking at how designers pair hair and eye colours. For every eye colour that appears on at least one brown-haired hero, how many heroes have that eye colour while their hair is NOT brown? Just give me each eye colour and that count, listing the eye colour with the highest count first. If two eye colours have the same count, the one whose name comes first alphabetically should come first.

Evidence：By a brown-haired hero I mean a hero whose hair colour is Brown.

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT DISTINCT s.eye_colour_id AS eid FROM superhero AS s INNER JOIN colour AS h ON s.hair_colour_id = h.id WHERE h.colour = 'Brown') SELECT c.colour AS eye_colour, COUNT(CASE WHEN h.colour <> 'Brown' THEN 1 END) AS heroes FROM cohort AS t INNER JOIN colour AS c ON c.id = t.eid LEFT JOIN superhero AS s ON s.eye_colour_id = t.eid LEFT JOIN colour AS h ON h.id = s.hair_colour_id GROUP BY c.colour ORDER BY heroes DESC, eye_colour
```

Agent SQL：
```sql
SELECT eye_colour, hero_count
FROM (
    SELECT eye.colour AS eye_colour, COUNT(*) AS hero_count
    FROM superhero AS hero
    JOIN colour AS eye ON eye.id = hero.eye_colour_id
    WHERE hero.eye_colour_id IN (
        SELECT brown_hero.eye_colour_id
        FROM superhero AS brown_hero
        JOIN colour AS hair ON hair.id = brown_hero.hair_colour_id
        WHERE hair.colour = 'Brown'
    )
      AND (hero.hair_colour_id IS NULL OR hero.hair_colour_id NOT IN (
          SELECT id FROM colour WHERE colour = 'Brown'
      ))
    GROUP BY eye.colour
)
ORDER BY hero_count DESC, eye_colour ASC;
```

觀察：model replies=4、tool attempts=4、SQL attempts=1、latency=13.980s；stop=final_sql_ready。



<a id="q379"></a>

## [Q379](failure-case-review.md#q379) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／可選關係。

INNER JOIN alignment 排除未知alignment的Marvel英雄，Gold LEFT JOIN納入分母。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What percentage of Marvel Comics superheroes with a recorded superpower are classified as good? Round the percentage to two decimal places, and give me just that single value.

Evidence：Good means alignment 'Good'; superpower refers to a hero's recorded power.

Gold SQL（離線）：
```sql
SELECT ROUND(CAST(SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*), 2) AS good_percentage FROM superhero s JOIN publisher p ON s.publisher_id = p.id LEFT JOIN alignment a ON s.alignment_id = a.id WHERE p.publisher_name = 'Marvel Comics' AND EXISTS (SELECT 1 FROM hero_power hp WHERE hp.hero_id = s.id)
```

Agent SQL：
```sql
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN a.alignment = 'Good' THEN s.id END)
    / COUNT(DISTINCT s.id),
    2
) AS percentage
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
JOIN hero_power AS hp ON hp.hero_id = s.id
JOIN alignment AS a ON a.id = s.alignment_id
WHERE p.publisher_name = 'Marvel Comics';
```

觀察：model replies=6、tool attempts=11、SQL attempts=5、latency=22.044s；stop=final_sql_ready。



<a id="q380"></a>

## [Q380](failure-case-review.md#q380) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

recorded weight只排NULL，未排0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm comparing the builds of heroes whose power sets overlap with 3-D Man's. What is the average weight in kg of the heroes other than 3-D Man that share at least one superpower with him? Please round it to two decimal places, leave out any heroes whose weight isn't recorded, and return just that single number.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(weight_kg), 2) AS average_weight_kg FROM superhero WHERE superhero_name <> '3-D Man' AND weight_kg > 0 AND id IN (SELECT hero_id FROM hero_power WHERE power_id IN (SELECT power_id FROM hero_power WHERE hero_id = (SELECT id FROM superhero WHERE superhero_name = '3-D Man')))
```

Agent SQL：
```sql
WITH target_powers AS (
    SELECT power_id
    FROM hero_power
    WHERE hero_id = (SELECT id FROM superhero WHERE superhero_name = '3-D Man')
),
qualifying_heroes AS (
    SELECT DISTINCT hp.hero_id
    FROM hero_power AS hp
    JOIN target_powers AS tp ON tp.power_id = hp.power_id
    WHERE hp.hero_id <> (SELECT id FROM superhero WHERE superhero_name = '3-D Man')
)
SELECT ROUND(AVG(s.weight_kg), 2)
FROM qualifying_heroes AS q
JOIN superhero AS s ON s.id = q.hero_id
WHERE s.weight_kg IS NOT NULL;
```

觀察：model replies=5、tool attempts=7、SQL attempts=3、latency=16.438s；stop=final_sql_ready。



<a id="q381"></a>

## [Q381](failure-case-review.md#q381) · dev · superhero

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／零值語義。

unknown weight只篩NULL，Gold unknown包含0。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among superheroes whose weight is not recorded, how many more have the 'No Colour' eye category than have blue eyes? I want a single whole number: the count of 'No Colour' eyes minus the count of blue eyes in that group - it can be negative if blue is more common. Please give me just that one number, with no other results or breakdowns.

Evidence：'No Colour' is an eye category meaning the hero's eye colour is unspecified.

Gold SQL（離線）：
```sql
SELECT SUM(CASE WHEN co.colour = 'No Colour' THEN 1 ELSE 0 END) - SUM(CASE WHEN co.colour = 'Blue' THEN 1 ELSE 0 END) AS diff FROM superhero AS s JOIN colour AS co ON co.id = s.eye_colour_id WHERE s.weight_kg = 0 OR s.weight_kg IS NULL
```

Agent SQL：
```sql
SELECT
  SUM(CASE WHEN c.colour = 'No Colour' THEN 1 ELSE 0 END)
  - SUM(CASE WHEN c.colour = 'Blue' THEN 1 ELSE 0 END)
FROM superhero AS s
JOIN colour AS c ON c.id = s.eye_colour_id
WHERE s.weight_kg IS NULL
  AND c.colour IN ('No Colour', 'Blue');
```

觀察：model replies=5、tool attempts=7、SQL attempts=3、latency=15.967s；stop=final_sql_ready。



<a id="q387"></a>

## [Q387](failure-case-review.md#q387) · test · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R5／年齡邊界。

older than55 改為生日<=1970-10-09（56歲），Gold birthday<1971-10-09，漏掉介於55與56歲的人。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among patients older than 55 on 2026-10-09 who have at least one abnormal PT result, what percentage are female? Round to two decimals.

Evidence：For this task, PT of at least 14 is abnormal.

Gold SQL（離線）：
```sql
SELECT ROUND(100.0 * SUM(CASE WHEN p.SEX = 'F' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) FROM Patient AS p WHERE p.Birthday < '1971-10-09' AND EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.PT >= 14)
```

Agent SQL：
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

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=22.404s；stop=final_sql_ready。



<a id="q392"></a>

## [Q392](failure-case-review.md#q392) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／附加cohort條件。

加入 Examination.Thrombosis>0，題目已明言全registry包括無labs；Gold不需事件確診。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm describing our young-patient group and want to show how unusual a raised RNP antibody is in these patients. Could you tell me how many patients in the thrombosis cohort born after 1 January 1960 never had a raised RNP antibody result? A few points: the group should cover every patient born after that date, including patients with no laboratory results at all - they count as never having had a raised result. "Raised" means a result strictly above 10, so a result of exactly 10 doesn't count, and a result of "negative" (no antibody detected) is never raised. Please return just one row with a single integer: the number of these patients.

Evidence：RNP: anti-ribonuclear protein antibody; a result of "negative" means no antibody was detected. A raised RNP result is a laboratory result strictly above 10.

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS patient_count FROM Patient AS p WHERE p.Birthday > '1960-01-01' AND NOT EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.RNP IS NOT NULL AND l.RNP <> 'negative' AND CAST(l.RNP AS REAL) > 10)
```

Agent SQL：
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

觀察：model replies=7、tool attempts=11、SQL attempts=7、latency=24.027s；stop=final_sql_ready。



<a id="q393"></a>

## [Q393](failure-case-review.md#q393) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／數值表示。

將RNP原始文字titer改為CAST INTEGER聚合後輸出；Gold回傳原始RNP。

診斷改寫：2次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among patients followed at the outpatient clinic who ever had an abnormal anti-SSA result, which one showed the highest anti-RNP titer? Please give me the patient's ID and the anti-RNP titer value. This should cover the hospital's full records across all years, and if several patients tie for the highest anti-RNP titer, list every one of them.

Evidence：Abnormal anti-SSA means any SSA result other than negative or 0. "Followed at the outpatient clinic" is the admission status marked with a minus sign. Anti-RNP titer is the strength of the anti-ribonuclear protein result.

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT DISTINCT T1.ID FROM Patient AS T1 JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE T1.Admission = '-' AND T2.SSA IS NOT NULL AND T2.SSA NOT IN ('negative', '0')), titers AS (SELECT T.ID, T.RNP FROM Laboratory AS T JOIN cohort AS C ON T.ID = C.ID WHERE T.RNP IS NOT NULL AND T.RNP <> 'negative') SELECT DISTINCT ID, RNP FROM titers WHERE CAST(RNP AS REAL) = (SELECT MAX(CAST(RNP AS REAL)) FROM titers)
```

Agent SQL：
```sql
WITH eligible_patients AS (
    SELECT DISTINCT l.ID
    FROM Laboratory AS l
    JOIN Patient AS p ON p.ID = l.ID
    WHERE p.Admission = '-'
      AND l.SSA IS NOT NULL
      AND LOWER(TRIM(l.SSA)) NOT IN ('negative', '0', '')
),
patient_titers AS (
    SELECT l.ID, MAX(CAST(l.RNP AS INTEGER)) AS rnp_titer
    FROM Laboratory AS l
    JOIN eligible_patients AS e ON e.ID = l.ID
    WHERE l.RNP IS NOT NULL
      AND LOWER(TRIM(l.RNP)) NOT IN ('negative', '')
    GROUP BY l.ID
)
SELECT ID, rnp_titer
FROM patient_titers
WHERE rnp_titer = (SELECT MAX(rnp_titer) FROM patient_titers);
```

觀察：model replies=7、tool attempts=9、SQL attempts=5、latency=26.698s；stop=final_sql_ready。



<a id="q398"></a>

## [Q398](failure-case-review.md#q398) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／必要篩選。

漏掉 outpatient Admission='-'。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among the thrombosis registry patients followed at the outpatient clinic, how many have a non-normal hematocrit and an anti-ribonuclear protein measurement above 16? I need a single count. A patient counts if they have at least one hematocrit reading outside the normal range, regardless of test date, and at least one anti-ribonuclear protein reading above 16, regardless of test date. Include every patient in the registry, not only those with a recorded thrombosis event.

Evidence：Hematocrit is normal when the value lies strictly between 29 and 52; outside that range it is abnormal. A negative anti-ribonuclear protein result means none was detected.

Gold SQL（離線）：
```sql
WITH cohort AS (SELECT DISTINCT p.ID FROM Patient p JOIN Laboratory l ON p.ID = l.ID WHERE p.Admission = '-' AND (l.HCT >= 52 OR l.HCT <= 29)) SELECT COUNT(DISTINCT l.ID) AS patient_count FROM Laboratory l WHERE l.ID IN (SELECT ID FROM cohort) AND l.RNP IS NOT NULL AND CAST(l.RNP AS REAL) > 16
```

Agent SQL：
```sql
SELECT COUNT(*) AS patient_count
FROM Patient AS p
WHERE EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.HCT IS NOT NULL
      AND (l.HCT <= 29 OR l.HCT >= 52)
)
AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND CAST(l.RNP AS REAL) > 16
);
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=16.054s；stop=final_sql_ready。



<a id="q400"></a>

## [Q400](failure-case-review.md#q400) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／診斷字串。

只接受兩個精確空格格式 'RA, SJS'/'SJS, RA'，Gold忽略空格及大小寫。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm studying patients who carry exactly the rheumatoid arthritis and Sjögren's syndrome overlap. Please look at each patient's own record and find those whose record names exactly rheumatoid arthritis and Sjögren's syndrome, in either order, and no other disease – a disease recorded only as suspected does not count as a diagnosis. For those patients, considering their whole recorded laboratory history regardless of date, I need two numbers: how many have had at least one laboratory result showing a normal platelet level, and how many have never had a laboratory result showing a normal platelet level – count a patient with no laboratory results at all as never having had a normal platelet result.

Evidence：Rheumatoid arthritis is recorded as the code RA and Sjögren's syndrome as the code SJS. A normal platelet level means a platelet count above 100 and below 400.

Gold SQL（離線）：
```sql
SELECT SUM(CASE WHEN EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.PLT > 100 AND l.PLT < 400) THEN 1 ELSE 0 END) AS had_normal_platelet_result, SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.PLT > 100 AND l.PLT < 400) THEN 1 ELSE 0 END) AS never_normal_platelet_result FROM Patient AS p WHERE LENGTH(LOWER(REPLACE(p.Diagnosis, ' ', ''))) - LENGTH(REPLACE(LOWER(REPLACE(p.Diagnosis, ' ', '')), ',', '')) = 1 AND REPLACE(REPLACE(REPLACE(LOWER(REPLACE(p.Diagnosis, ' ', '')), 'ra', ''), 'sjs', ''), ',', '') = ''
```

Agent SQL：
```sql
SELECT
    SUM(CASE WHEN EXISTS (
        SELECT 1
        FROM Laboratory l
        WHERE l.ID = p.ID
          AND l.PLT > 100
          AND l.PLT < 400
    ) THEN 1 ELSE 0 END) AS patients_with_normal_platelet,
    SUM(CASE WHEN NOT EXISTS (
        SELECT 1
        FROM Laboratory l
        WHERE l.ID = p.ID
          AND l.PLT > 100
          AND l.PLT < 400
    ) THEN 1 ELSE 0 END) AS patients_never_with_normal_platelet
FROM Patient p
WHERE p.Diagnosis IN ('RA, SJS', 'SJS, RA');
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=26.777s；stop=final_sql_ready。



<a id="q404"></a>

## [Q404](failure-case-review.md#q404) · test · thrombosis_prediction

狀態：missing_sql；歷史轉變：兩次均錯；主候選：BUDGET／探索未收斂。

41st總tool attempt觸發40上限；37個SQL attempts中36有成功結果，無最終答案。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a department audit on how often anti-ribonuclear protein testing comes back clearly elevated among the women in the thrombosis cohort. Among the women in the cohort, what percentage of those with an available anti-ribonuclear protein test result had a clearly elevated result? Please give me the percentage rounded to two decimal places on the 0-100 scale. Note: elevated means a titer strictly above 1:64. Patients never tested for anti-ribonuclear protein should be excluded from both the numerator and the denominator, while a negative reading counts as an available result and is never elevated.

Evidence：Anti-ribonuclear protein is a serology test reported as a titer reading; a negative reading is a result of zero titer.

Gold SQL（離線）：
```sql
SELECT ROUND(CAST(SUM(CASE WHEN EXISTS (SELECT 1 FROM Laboratory L WHERE L.ID = P.ID AND CAST(L.RNP AS REAL) > 64) THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*), 2) AS pct FROM Patient P WHERE P.SEX = 'F' AND EXISTS (SELECT 1 FROM Laboratory L WHERE L.ID = P.ID AND L.RNP IS NOT NULL)
```

Agent SQL：
```sql
None
```

觀察：model replies=29、tool attempts=41、SQL attempts=37、latency=136.899s；stop=ToolCallLimitExceededError。



<a id="q406"></a>

## [Q406](failure-case-review.md#q406) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

依SEX兩行，Gold單行women,men兩欄。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm looking at patients whose anti-ribonuclear protein antibody measurement came out higher than 32. Of those patients, how many were women and how many were men? Note that 'higher than 32' means strictly above 32, not equal to it, and a patient qualifies if any of their laboratory measurements exceeded 32.

Evidence：A woman means a patient recorded as F, and a man means a patient recorded as M.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT CASE WHEN T1.SEX = 'F' THEN T1.ID END) AS women, COUNT(DISTINCT CASE WHEN T1.SEX = 'M' THEN T1.ID END) AS men FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE CAST(T2.RNP AS REAL) > 32
```

Agent SQL：
```sql
SELECT p.SEX, COUNT(DISTINCT p.ID) AS patient_count
FROM Patient AS p
WHERE p.SEX IN ('F', 'M')
  AND EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND CAST(l.RNP AS REAL) > 32
  )
GROUP BY p.SEX;
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=15.308s；stop=final_sql_ready。



<a id="q407"></a>

## [Q407](failure-case-review.md#q407) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／附加cohort條件。

額外要求 Examination.Thrombosis<>0，Gold全Patient有RNP>=64。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm studying how early in life a patient in the thrombosis cohort can show a high anti-ribonuclear protein (RNP) reading. Please tell me the youngest age, in whole years, at which a patient had a laboratory test showing an anti-RNP result of at least 64. Age in whole years means the year of the test minus the year of birth. If several patients or tests share that youngest age, report that age once. I just need that single youngest age value, nothing else.

Evidence：Anti-ribonuclear protein (RNP): an antibody measured in the laboratory panel, reported as a titer number or as negative.

Gold SQL（離線）：
```sql
SELECT MIN(STRFTIME('%Y', T2.`Date`) - STRFTIME('%Y', T1.Birthday)) AS youngest_age FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE CAST(T2.RNP AS REAL) >= 64
```

Agent SQL：
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

觀察：model replies=13、tool attempts=19、SQL attempts=15、latency=46.073s；stop=final_sql_ready。



<a id="q412"></a>

## [Q412](failure-case-review.md#q412) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加診斷條件。

額外加 Diagnosis LIKE '%SLE%'，題目只要求Admission含+。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For the thrombosis cohort, I need to describe how long admitted patients typically wait from their first hospital visit until their first examination. Please give me the average delay in days across admitted patients, based on each patient's own first visit and first examination, rounded to the nearest whole number. A patient counts as admitted whenever her admission entry carries a plus sign, regardless of anything else in that entry.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(gap), 0) AS average_days FROM (SELECT T1.ID, MIN(JULIANDAY(T3.`Examination Date`)) - JULIANDAY(T1.`First Date`) AS gap FROM Patient AS T1 INNER JOIN Examination AS T3 ON T1.ID = T3.ID WHERE T1.Admission LIKE '%+%' GROUP BY T1.ID)
```

Agent SQL：
```sql
WITH first_examination AS (
    SELECT ID, MIN("Examination Date") AS examination_date
    FROM Examination
    GROUP BY ID
)
SELECT ROUND(AVG(julianday(e.examination_date) - julianday(p."First Date"))) AS average_delay_days
FROM Patient AS p
JOIN first_examination AS e ON e.ID = p.ID
WHERE p.Diagnosis LIKE '%SLE%'
  AND instr(p.Admission, '+') > 0
  AND p."First Date" IS NOT NULL;
```

觀察：model replies=13、tool attempts=19、SQL attempts=15、latency=48.153s；stop=final_sql_ready。



<a id="q418"></a>

## [Q418](failure-case-review.md#q418) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／數值表示。

輸出CAST INTEGER的MAX RNP，Gold輸出原始RNP字串；值比較以REAL。

診斷改寫：2次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among patients whose first visit to the hospital was in 1991, which patients mounted the strongest anti-ribonuclear protein (RNP) response? Please give me the patient ID and anti-RNP level for every patient tied at the highest recorded level. Only consider patients for whom a level was actually recorded.

Evidence：anti-ribonuclear protein (RNP): an antibody titer; a higher titer means a higher level.

Gold SQL（離線）：
```sql
SELECT DISTINCT T1.ID, T2.RNP FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE STRFTIME('%Y', T1.`First Date`) = '1991' AND T2.RNP IS NOT NULL AND CAST(T2.RNP AS REAL) = (SELECT MAX(CAST(L.RNP AS REAL)) FROM Patient AS P INNER JOIN Laboratory AS L ON P.ID = L.ID WHERE STRFTIME('%Y', P.`First Date`) = '1991' AND L.RNP IS NOT NULL)
```

Agent SQL：
```sql
WITH patient_levels AS (
    SELECT p.ID, MAX(CAST(l.RNP AS INTEGER)) AS anti_RNP_level
    FROM Patient AS p
    JOIN Laboratory AS l ON l.ID = p.ID
    WHERE p."First Date" >= '1991-01-01'
      AND p."First Date" < '1992-01-01'
      AND l.RNP IS NOT NULL
      AND l.RNP <> 'negative'
    GROUP BY p.ID
)
SELECT ID, anti_RNP_level
FROM patient_levels
WHERE anti_RNP_level = (SELECT MAX(anti_RNP_level) FROM patient_levels)
ORDER BY ID;
```

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=27.376s；stop=final_sql_ready。



<a id="q420"></a>

## [Q420](failure-case-review.md#q420) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

分care setting兩行，Gold單行inpatient/outpatient兩個count；ELSE亦納其他admission。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a care-setting summary of severe SLE cases for the rheumatology department. Among patients diagnosed with SLE, considering only those whose only diagnosis is SLE and who had abnormally high proteinuria, how many were admitted to the hospital and how many were followed at the outpatient clinic? Please count each patient based on their full history at the hospital.

Evidence：Abnormally high proteinuria means a proteinuria level of 30 or higher.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT CASE WHEN T1.Admission = '+' THEN T1.ID END) AS admitted_to_hospital, COUNT(DISTINCT CASE WHEN T1.Admission = '-' THEN T1.ID END) AS followed_at_outpatient_clinic FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE T1.Diagnosis = 'SLE' AND CAST(T2.`U-PRO` AS REAL) >= 30
```

Agent SQL：
```sql
SELECT
  CASE WHEN Admission = '+' THEN 'Hospital' ELSE 'Outpatient clinic' END AS care_setting,
  COUNT(DISTINCT ID) AS patient_count
FROM Patient
WHERE Diagnosis = 'SLE'
  AND EXISTS (
    SELECT 1
    FROM Laboratory
    WHERE Laboratory.ID = Patient.ID
      AND CAST(Laboratory."U-PRO" AS INTEGER) >= 30
  )
GROUP BY CASE WHEN Admission = '+' THEN 'Hospital' ELSE 'Outpatient clinic' END;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=18.537s；stop=final_sql_ready。



<a id="q421"></a>

## [Q421](failure-case-review.md#q421) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R2／量度來源。

normal rheumatoid factor應依題意 Laboratory.RA IN('-','+-')，Agent用了RF值。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：How many patients in our thrombosis ward are followed at the outpatient clinic (rather than admitted) with a normal Rheumatoid Factor and no positive measure of degree of coagulation? Please give me a single number. For context: a normal Rheumatoid Factor is '-' or '+-', a positive measure of degree of coagulation is '+' on any of the coagulation measures (KCT, RVVT, LAC), and an outpatient-clinic patient is one with Admission = '-'. If a patient has no recorded coagulation measure, count them as having no positive measure.

Evidence：

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T1.ID) AS patient_count FROM Patient AS T1 WHERE T1.Admission = '-' AND T1.ID IN (SELECT ID FROM Laboratory WHERE RA IN ('-', '+-')) AND NOT EXISTS (SELECT 1 FROM Examination E WHERE E.ID = T1.ID AND (E.KCT = '+' OR E.RVVT = '+' OR E.LAC = '+'))
```

Agent SQL：
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

觀察：model replies=18、tool attempts=19、SQL attempts=15、latency=56.898s；stop=final_sql_ready。



<a id="q423"></a>

## [Q423](failure-case-review.md#q423) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R1／編碼值。

U-PRO排negative/none文字，但資料Gold無蛋白編碼為'-'/'0'。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'd like to know how many patients on record have both an abnormal anti-SSA antibody result and a positive proteinuria finding at some point in their record. Abnormal anti-SSA means any recorded test result other than negative or zero. Proteinuria counts as positive if any urine test on file returned a result other than negative or none. The two findings don't need to come from the same visit – I'm looking across each patient's entire record. Please just give me the number of such patients.

Evidence：anti-SSA: anti-SSA antibody laboratory test; proteinuria: protein found in the urine

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS patient_count FROM Patient AS T1 WHERE T1.ID IN (SELECT ID FROM Laboratory WHERE SSA IS NOT NULL AND SSA NOT IN ('negative', '0')) AND T1.ID IN (SELECT ID FROM Laboratory WHERE `U-PRO` IS NOT NULL AND `U-PRO` NOT IN ('-', '0'))
```

Agent SQL：
```sql
SELECT COUNT(*) AS patient_count
FROM Patient AS p
WHERE EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.SSA IS NOT NULL
      AND LOWER(TRIM(l.SSA)) NOT IN ('negative', '0')
)
AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.`U-PRO` IS NOT NULL
      AND LOWER(TRIM(l.`U-PRO`)) NOT IN ('negative', 'none')
);
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=20.974s；stop=final_sql_ready。



<a id="q430"></a>

## [Q430](failure-case-review.md#q430) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加診斷條件。

額外加入 Diagnosis LIKE '%aps%'，Gold全Admission+/-患者。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：In the thrombosis and autoimmune-disease cohort, I want to compare how often lactate dehydrogenase stays in the normal range between patients admitted to the hospital and patients followed at the outpatient clinic. Please give me one row per patient group showing the number of lactate dehydrogenase measurements within the normal range recorded for that group, with the admitted group's row first. Label the rows 'admitted to the hospital' for the Admission = '+' group and 'followed at the outpatient clinic' for the Admission = '-' group. Every laboratory measurement recorded for those patients across the whole study period counts. Nothing else is needed.

Evidence：The normal range for lactate dehydrogenase means a value below 500.

Gold SQL（離線）：
```sql
SELECT CASE WHEN P.Admission = '+' THEN 'admitted to the hospital' ELSE 'followed at the outpatient clinic' END AS patient_group, COUNT(*) AS normal_ldh_measurements FROM Patient AS P JOIN Laboratory AS L ON P.ID = L.ID WHERE P.Admission IN ('+', '-') AND L.LDH < 500 GROUP BY 1 ORDER BY CASE P.Admission WHEN '+' THEN 0 ELSE 1 END
```

Agent SQL：
```sql
SELECT
    CASE p.Admission
        WHEN '+' THEN 'admitted to the hospital'
        WHEN '-' THEN 'followed at the outpatient clinic'
    END AS patient_group,
    COUNT(l.LDH) AS normal_lactate_dehydrogenase_measurements
FROM Patient AS p
JOIN Laboratory AS l ON l.ID = p.ID
WHERE lower(p.Diagnosis) LIKE '%aps%'
  AND p.Admission IN ('+', '-')
  AND l.LDH < 500
GROUP BY p.Admission
ORDER BY CASE p.Admission WHEN '+' THEN 1 WHEN '-' THEN 2 END;
```

觀察：model replies=13、tool attempts=14、SQL attempts=10、latency=37.100s；stop=final_sql_ready。



<a id="q439"></a>

## [Q439](failure-case-review.md#q439) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R4／附加cohort條件。

額外加入 Examination.Thrombosis>0，題目只需female同lab記錄PT／RNP條件。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm trying to size a subgroup in the thrombosis cohort: how many female patients had a normal prothrombin time (below 14 seconds) along with an elevated anti-ribonuclear protein level (16 or higher)? Please use the prothrombin time and anti-ribonuclear protein level from the same laboratory record for each patient. I just need the count of such female patients.

Evidence：Normal prothrombin time: below 14 seconds. Elevated anti-ribonuclear protein: a measured level of 16 or higher.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT T1.ID) AS patient_count FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE T1.SEX = 'F' AND T2.PT < 14 AND CAST(T2.RNP AS REAL) >= 16
```

Agent SQL：
```sql
SELECT COUNT(DISTINCT l.ID) AS patient_count
FROM Laboratory AS l
JOIN Patient AS p ON p.ID = l.ID
WHERE p.SEX = 'F'
  AND EXISTS (
      SELECT 1
      FROM Examination AS e
      WHERE e.ID = p.ID
        AND e.Thrombosis > 0
  )
  AND l.PT < 14
  AND CAST(l.RNP AS REAL) >= 16;
```

觀察：model replies=15、tool attempts=16、SQL attempts=12、latency=44.880s；stop=final_sql_ready。



<a id="q441"></a>

## [Q441](failure-case-review.md#q441) · dev · thrombosis_prediction

狀態：sql_error；歷史轉變：歷史啱→本輪錯；主候選：R8／最終JSON修訂。

最後測試SQL可執行；最終改以replace拼JSON交json_each，原生SQLite報 malformed JSON。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I need to find lupus patients with liver lab abnormalities. Can you give me the ID and sex of every patient who has at least one total bilirubin (T-BIL) result at or above the upper normal limit of 1.2 mg/dL, and who has a confirmed diagnosis of systemic lupus erythematosus (SLE)? SLE counts if it's among the patient's confirmed diagnoses, even when other diseases are diagnosed or suspected alongside it, but a suspected SLE alone doesn't count. The diagnosis should be the patient's overall diagnosis, not something noted at a single examination. Please order results by sex, then patient ID, and return only the ID and sex.

Evidence：T-BIL: total bilirubin; SLE: systemic lupus erythematosus; susp.: suspected, not a confirmed diagnosis

Gold SQL（離線）：
```sql
SELECT p.ID, p.SEX FROM Patient AS p WHERE p.ID IN (SELECT ID FROM Laboratory WHERE "T-BIL" >= 1.2) AND instr(',' || REPLACE(p.Diagnosis, ' ', '') || ',', ',' || 'SLE' || ',') > 0 ORDER BY p.SEX, p.ID;
```

Agent SQL：
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

觀察：model replies=6、tool attempts=8、SQL attempts=4、latency=22.363s；stop=final_sql_ready。



<a id="q442"></a>

## [Q442](failure-case-review.md#q442) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／標籤大小寫。

care_setting改首字母大寫，Gold精確小寫標籤；年齡計法亦須對照。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing how often older female patients show elevated anti-RNP antibody results, split by whether they were admitted to the hospital or followed at the outpatient clinic. For female patients aged at least 50 as of 2026-10-09, please give me a two-row breakdown by care setting (admitted to the hospital vs. followed at the outpatient clinic), showing for each setting how many patients had at least one anti-RNP laboratory result of at least 4, and how many had no such result. A patient's admission marker of '+' counts as admitted to the hospital and '-' counts as followed at the outpatient clinic; patients with any other admission marker are out of scope. Order the two rows alphabetically by care setting.

Evidence：anti-RNP: anti-ribonuclear protein antibody, measured in laboratory results; admission marker: the patient's recorded admission sign.

Gold SQL（離線）：
```sql
SELECT CASE WHEN p.Admission = '+' THEN 'admitted to the hospital' ELSE 'followed at the outpatient clinic' END AS care_setting, SUM(CASE WHEN EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND CAST(l.RNP AS REAL) >= 4) THEN 1 ELSE 0 END) AS patients_with_rnp_at_least_4, SUM(CASE WHEN EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND CAST(l.RNP AS REAL) >= 4) THEN 0 ELSE 1 END) AS patients_without_such_result FROM Patient AS p WHERE p.SEX = 'F' AND p.Birthday <= (CAST(substr('2026-10-09',1,4) AS INTEGER) - 50) || substr('2026-10-09',5) AND p.Admission IN ('+','-') GROUP BY 1 ORDER BY care_setting
```

Agent SQL：
```sql
WITH eligible AS (
    SELECT ID,
           CASE Admission
               WHEN '+' THEN 'Admitted to the hospital'
               WHEN '-' THEN 'Followed at the outpatient clinic'
           END AS care_setting
    FROM Patient
    WHERE SEX = 'F'
      AND date(Birthday, '+50 years') <= '2026-10-09'
      AND Admission IN ('+', '-')
),
patient_results AS (
    SELECT e.ID,
           e.care_setting,
           MAX(CASE WHEN CAST(l.RNP AS REAL) >= 4 THEN 1 ELSE 0 END) AS has_elevated_rnp
    FROM eligible e
    LEFT JOIN Laboratory l ON l.ID = e.ID
    GROUP BY e.ID, e.care_setting
)
SELECT care_setting,
       SUM(has_elevated_rnp) AS patients_with_at_least_one_result_at_least_4,
       COUNT(*) - SUM(has_elevated_rnp) AS patients_with_no_such_result
FROM patient_results
GROUP BY care_setting
ORDER BY care_setting;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=23.147s；stop=final_sql_ready。



<a id="q443"></a>

## [Q443](failure-case-review.md#q443) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／先篩後排名。

先排最新Lab才看IGG，未先排除IGG NULL；最新Lab不等於最新IGG測量。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm putting together a cohort summary and need one number: how many patients followed at the outpatient clinic (admission marker '-') have a most recent IgG lab result of 2000 or higher? By most recent, I mean the IgG measurement with the greatest laboratory date for that patient - since a patient has at most one lab record per date, there should be no ambiguity.

Evidence：

Gold SQL（離線）：
```sql
WITH latest_igg AS (SELECT ID, MAX(Date) AS LastDate FROM Laboratory WHERE IGG IS NOT NULL GROUP BY ID) SELECT COUNT(*) AS patient_count FROM Patient AS p JOIN latest_igg AS li ON li.ID = p.ID JOIN Laboratory AS l ON l.ID = li.ID AND l.Date = li.LastDate WHERE p.Admission = '-' AND l.IGG >= 2000
```

Agent SQL：
```sql
WITH latest AS (
    SELECT ID, IGG, ROW_NUMBER() OVER (PARTITION BY ID ORDER BY Date DESC) AS rn
    FROM Laboratory
)
SELECT COUNT(*)
FROM Patient AS p
JOIN latest AS l ON l.ID = p.ID AND l.rn = 1
WHERE p.Admission = '-'
  AND l.IGG >= 2000;
```

觀察：model replies=4、tool attempts=5、SQL attempts=1、latency=13.289s；stop=final_sql_ready。



<a id="q445"></a>

## [Q445](failure-case-review.md#q445) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／附加cohort條件。

額外inner JOIN Examination並限Thrombosis=1，Gold納每個care setting全部Patient。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For our thrombosis study cohort, I'd like to know how often patients have a normal IgG status at their most recent check, broken down by care setting. Please give me, for patients admitted to the hospital and for patients followed at the outpatient clinic, the percentage of that setting's patients whose most recent IgG measurement was normal. The percentage should be out of every patient in that setting, so patients who never had an IgG measurement count toward the denominator but not the numerator. Please round to one decimal place, and label the two results exactly as 'admitted to the hospital' and 'followed at the outpatient clinic'.

Evidence：An IgG measurement is considered normal when it is above 900 and below 2000.

Gold SQL（離線）：
```sql
WITH latest AS (SELECT ID, IGG, ROW_NUMBER() OVER (PARTITION BY ID ORDER BY Date DESC) AS rn FROM Laboratory WHERE IGG IS NOT NULL) SELECT CASE WHEN p.Admission = '+' THEN 'admitted to the hospital' ELSE 'followed at the outpatient clinic' END AS care_setting, ROUND(100.0 * SUM(CASE WHEN l.IGG > 900 AND l.IGG < 2000 THEN 1 ELSE 0 END) / COUNT(p.ID), 1) AS patient_share FROM Patient AS p LEFT JOIN latest AS l ON l.ID = p.ID AND l.rn = 1 WHERE p.Admission IN ('+', '-') GROUP BY 1 ORDER BY 1
```

Agent SQL：
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

觀察：model replies=11、tool attempts=14、SQL attempts=10、latency=38.319s；stop=final_sql_ready。



<a id="q448"></a>

## [Q448](failure-case-review.md#q448) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／診斷字串。

NOT LIKE '%susp%' 排除任何疾病被懷疑的整筆診斷，Gold只排'SLE susp'。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a capacity report for the lupus service. Among the patients whose profile lists a confirmed SLE diagnosis (not just suspected), I need: (1) how many were admitted to the hospital as inpatients, (2) how many were followed at the outpatient clinic, and (3) what percentage of the confirmed-SLE patients who were in one of these two care settings were inpatients. Please round the percentage to two decimals.

Evidence：SLE means systemic lupus erythematosus. A disease name followed by 'susp' (e.g., 'SLE susp') means only suspected, not confirmed, and does not count.

Gold SQL（離線）：
```sql
SELECT SUM(CASE WHEN Admission = '+' THEN 1 ELSE 0 END) AS inpatients, SUM(CASE WHEN Admission = '-' THEN 1 ELSE 0 END) AS outpatients, ROUND(100.0 * SUM(CASE WHEN Admission = '+' THEN 1 ELSE 0 END) / SUM(CASE WHEN Admission IN ('+', '-') THEN 1 ELSE 0 END), 2) AS inpatient_pct FROM Patient WHERE Diagnosis LIKE '%SLE%' AND Diagnosis NOT LIKE '%SLE susp%'
```

Agent SQL：
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

觀察：model replies=6、tool attempts=9、SQL attempts=5、latency=20.756s；stop=final_sql_ready。



<a id="q452"></a>

## [Q452](failure-case-review.md#q452) · test · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／年齡排序。

Birthday ASC挑最老，題目youngest／Gold應DESC；亦過度排所有susp診斷。

診斷改寫：2次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm reviewing confirmed SLE cases for a study of neurologic involvement. Among patients whose examination lists SLE among the diagnosed diseases and who have a symptom recorded at such an examination, I need the case detail of the youngest such patient. Please send me the symptom recorded at that qualifying examination and that patient's overall diagnosis (their overall diagnosis, not the diagnosis written at the examination). If two patients share the same birth date, use the one with the smaller patient ID; and if that patient has more than one qualifying examination, use the most recent one.

Evidence：SLE is systemic lupus erythematosus. A disease name followed by 'susp' means the disease was only suspected, not diagnosed.

Gold SQL（離線）：
```sql
WITH target AS (SELECT 'SLE' AS d) SELECT e.Symptoms, p.Diagnosis AS overall_diagnosis FROM Patient AS p JOIN Examination AS e ON e.ID = p.ID WHERE p.Birthday IS NOT NULL AND e.Symptoms IS NOT NULL AND TRIM(e.Symptoms) <> '' AND EXISTS (SELECT 1 FROM target WHERE REPLACE(',' || REPLACE(e.Diagnosis, ' ', '') || ',', ',' || d || ',', '') <> ',' || REPLACE(e.Diagnosis, ' ', '') || ',') ORDER BY p.Birthday DESC, p.ID, e.`Examination Date` DESC LIMIT 1
```

Agent SQL：
```sql
SELECT e.Symptoms, p.Diagnosis
FROM Patient AS p
JOIN Examination AS e ON e.ID = p.ID
WHERE e.Diagnosis LIKE '%SLE%'
  AND e.Diagnosis NOT LIKE '%susp%'
  AND e.Symptoms IS NOT NULL
  AND TRIM(e.Symptoms) <> ''
ORDER BY p.Birthday ASC, p.ID ASC, e.`Examination Date` DESC
LIMIT 1;
```

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=28.268s；stop=final_sql_ready。



<a id="q456"></a>

## [Q456](failure-case-review.md#q456) · test · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／標籤值。

輸出male/female文字，Gold為原始M/F代碼。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I need to size a comparison group for my study of liver-enzyme abnormalities. How many patients in the registry have never had an ALT result above the normal range? Please give me the count broken down by sex: the number of male patients and the number of female patients. Every patient in the registry counts, including patients with no laboratory results at all, since they have never had an abnormal result. The report should cover exactly the two sexes, male and female.

Evidence：ALT is measured by the GPT laboratory value; a GPT result of 60 or higher exceeds the normal range.

Gold SQL（離線）：
```sql
SELECT P.SEX AS sex, COUNT(*) AS patient_count FROM Patient P WHERE P.SEX IN ('M','F') AND NOT EXISTS (SELECT 1 FROM Laboratory L WHERE L.ID = P.ID AND L.GPT >= 60) GROUP BY P.SEX ORDER BY P.SEX
```

Agent SQL：
```sql
SELECT
  CASE SEX WHEN 'M' THEN 'male' WHEN 'F' THEN 'female' END AS sex,
  COUNT(*) AS patient_count
FROM Patient AS p
WHERE SEX IN ('M', 'F')
  AND NOT EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.GPT >= 60
  )
GROUP BY SEX
ORDER BY CASE SEX WHEN 'M' THEN 1 WHEN 'F' THEN 2 END;
```

觀察：model replies=6、tool attempts=6、SQL attempts=3、latency=23.229s；stop=final_sql_ready。



<a id="q458"></a>

## [Q458](failure-case-review.md#q458) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R7／標籤值。

輸出Female/Male而非原始F/M代碼。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among the patients who have laboratory test records on file, how many are female and how many are male? Please give me one line for the female patients and one line for the male patients, each showing the sex and the number of patients of that sex.

Evidence：

Gold SQL（離線）：
```sql
SELECT p.SEX AS sex, COUNT(DISTINCT p.ID) AS patient_count FROM Patient p JOIN Laboratory l ON l.ID = p.ID WHERE p.SEX IN ('F','M') GROUP BY p.SEX
```

Agent SQL：
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

觀察：model replies=6、tool attempts=6、SQL attempts=3、latency=17.813s；stop=final_sql_ready。



<a id="q459"></a>

## [Q459](failure-case-review.md#q459) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／診斷字串。

Diagnosis='SJS'漏掉SJS已確診並同時其他疾病的token組合。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm studying antiphospholipid antibodies in Sjögren's syndrome (SJS). Could you tell me the average anti-cardiolipin IgM concentration among SJS patients, rounded to two decimal places? To clarify: use only patients with an established SJS diagnosis recorded at the patient level (a diagnosis marked 'susp', such as 'SJS susp', is only a suspicion and those patients should not be included). Include every examination recorded for these patients regardless of date. A recorded anti-cardiolipin IgM value of 0 means the antibody was not detected at that examination, so treat it as no measurement and leave it out of the average - count only examinations where a concentration was detected.

Evidence：SJS is the abbreviation used for Sjögren's syndrome; a diagnosis marked 'susp' (e.g. 'SJS susp') is only a suspicion of the disease, not an established diagnosis.

Gold SQL（離線）：
```sql
WITH RECURSIVE tokens AS (SELECT ID, '' AS tok, COALESCE (Diagnosis, '') || ',' AS rest FROM Patient UNION ALL SELECT ID, trim(substr(rest, 1, instr(rest, ',') - 1)), substr(rest, instr(rest, ',') + 1) FROM tokens WHERE rest <> '') SELECT ROUND(AVG(CASE WHEN e."aCL IgM" > 0 THEN e."aCL IgM" END), 2) AS avg_aCL_IgM FROM Examination AS e WHERE e.ID IN (SELECT ID FROM tokens WHERE tok = 'SJS')
```

Agent SQL：
```sql
SELECT ROUND(AVG(e."aCL IgM"), 2)
FROM Examination AS e
JOIN Patient AS p ON p.ID = e.ID
WHERE p.Diagnosis = 'SJS'
  AND e."aCL IgM" IS NOT NULL
  AND e."aCL IgM" <> 0;
```

觀察：model replies=5、tool attempts=7、SQL attempts=3、latency=15.450s；stop=final_sql_ready。



<a id="q464"></a>

## [Q464](failure-case-review.md#q464) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R5／年齡定義。

用julianday/365.2425連續年齡，Gold完成年齡整數，再平均。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：In our autoimmune-cohort registry, I'm profiling young patients with strongly positive anti-RNP findings. What is the average age, in years, of the patients who were younger than 70 as of 2026-10-09 and who have at least one anti-RNP result of 64 or higher? Please give the average as a single number to one decimal place.

Evidence：anti-ribonuclear protein (anti-RNP) result: the reading recorded for a patient's anti-RNP test in the laboratory record

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(CAST(substr('2026-10-09',1,4) AS INTEGER) - CAST(substr(p.Birthday,1,4) AS INTEGER) - (substr('2026-10-09',6) < substr(p.Birthday,6))), 1) AS average_age FROM Patient AS p WHERE (CAST(substr('2026-10-09',1,4) AS INTEGER) - CAST(substr(p.Birthday,1,4) AS INTEGER) - (substr('2026-10-09',6) < substr(p.Birthday,6))) < 70 AND EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND CAST(l.RNP AS REAL) >= 64)
```

Agent SQL：
```sql
SELECT ROUND(AVG((julianday('2026-10-09') - julianday(p.Birthday)) / 365.2425), 1)
FROM Patient AS p
WHERE p.Birthday IS NOT NULL
  AND (julianday('2026-10-09') - julianday(p.Birthday)) / 365.2425 < 70
  AND EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND CAST(l.RNP AS REAL) >= 64
  );
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=17.608s；stop=final_sql_ready。



<a id="q466"></a>

## [Q466](failure-case-review.md#q466) · dev · thrombosis_prediction

狀態：missing_sql；歷史轉變：歷史啱→本輪錯；主候選：R8／最終修訂語法。

工具測試SQL成功，最終別名改為未引用women's_percentage，單引號破壞SQL，parser拒收。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：As part of our clinical audit I'm profiling patients born between 1936 and 1956 inclusive who never had a creatinine phosphokinase (CPK) result above the normal range. A CPK of 250 or higher counts as above the normal range, and patients with no CPK results on record count as never having exceeded it. For that group, please give me the women's percentage of the group's men and women, rounded to one decimal place.

Evidence：Creatinine phosphokinase (CPK) of 250 or higher is above the normal range.

Gold SQL（離線）：
```sql
SELECT ROUND(CAST(SUM(CASE WHEN SEX = 'F' THEN 1 ELSE 0 END) AS REAL) * 100 / SUM(CASE WHEN SEX IN ('M','F') THEN 1 ELSE 0 END), 1) AS percentage FROM Patient WHERE STRFTIME('%Y', Birthday) BETWEEN '1936' AND '1956' AND NOT EXISTS (SELECT 1 FROM Laboratory WHERE Laboratory.ID = Patient.ID AND Laboratory.CPK >= 250)
```

Agent SQL：
```sql
None
```

觀察：model replies=7、tool attempts=8、SQL attempts=4、latency=23.310s；stop=invalid_final_answer。



<a id="q467"></a>

## [Q467](failure-case-review.md#q467) · dev · thrombosis_prediction

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R4／附加有效性條件。

age BETWEEN0 AND49額外排除負年齡記錄，Gold只要求age<50；日期上界及TRIM亦不同。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm preparing a case series on early renal involvement and need to size my cohort. How many patients were under age 50 on the day of a laboratory test performed between 1 January 1981 and 31 December 1986 inclusive, had a platelet count from 100 through 400 at that test, and showed proteinuria at that test? Age means completed years on the day of the test, so under 50 is strictly below 50. The platelet range is inclusive. I just need the number of patients satisfying all conditions.

Evidence：A patient showed proteinuria at a test when that test's dipstick reading reports protein: a dash or zero means no protein was found, a number is the amount of protein found, TR stands for trace protein, and a reading written in percent signs is the dipstick saturated, the strongest reading.

Gold SQL（離線）：
```sql
SELECT COUNT(DISTINCT p.ID) AS patient_count FROM Patient AS p JOIN Laboratory AS l ON l.ID = p.ID WHERE SUBSTR(l.Date, 1, 4) BETWEEN '1981' AND '1986' AND l.PLT BETWEEN 100 AND 400 AND p.Birthday IS NOT NULL AND (CAST(SUBSTR(l.Date, 1, 4) AS INTEGER) - CAST(SUBSTR(p.Birthday, 1, 4) AS INTEGER) - CASE WHEN SUBSTR(l.Date, 6, 5) < SUBSTR(p.Birthday, 6, 5) THEN 1 ELSE 0 END) < 50 AND l."U-PRO" IS NOT NULL AND l."U-PRO" NOT IN ('-', '0')
```

Agent SQL：
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

觀察：model replies=6、tool attempts=7、SQL attempts=3、latency=23.266s；stop=final_sql_ready。



<a id="q474"></a>

## [Q474](failure-case-review.md#q474) · test · toxicology

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R1／元素編碼。

元素用大寫P/N，資料Gold為小寫p/n；另多輸出molecule_id,bond_type。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：What are the bonds that have phosphorus and nitrogen as their atom elements?

Evidence：

Gold SQL（離線）：
```sql
SELECT T2.bond_id FROM atom AS T1 INNER JOIN connected AS T2 ON T1.atom_id = T2.atom_id WHERE T2.bond_id IN (SELECT T3.bond_id FROM connected AS T3 INNER JOIN atom AS T4 ON T3.atom_id = T4.atom_id WHERE T4.element = 'p') AND T1.element = 'n'
```

Agent SQL：
```sql
SELECT DISTINCT b.bond_id, b.molecule_id, b.bond_type
FROM bond AS b
JOIN connected AS c ON c.bond_id = b.bond_id
JOIN atom AS a1 ON a1.atom_id = c.atom_id
JOIN atom AS a2 ON a2.atom_id = c.atom_id2
WHERE (a1.element = 'P' AND a2.element = 'N')
   OR (a1.element = 'N' AND a2.element = 'P');
```

觀察：model replies=6、tool attempts=7、SQL attempts=1、latency=25.800s；stop=final_sql_ready。



<a id="q479"></a>

## [Q479](failure-case-review.md#q479) · test · toxicology

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R7／輸出形狀。

Agent依bond_group兩行，Gold兩個diff欄單行；無bond分組政策亦不同。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I want to know whether molecular saturation is associated with carcinogenicity in our compound library. Please report, for molecules in which every bond is a single bond: the number of carcinogenic molecules minus the number of non-carcinogenic molecules. And for all other molecules: the same difference (carcinogenic count minus non-carcinogenic count). Rules: label '+' means the molecule is carcinogenic; label '-' means non-carcinogenic; bond type '-' denotes a single bond; each molecule belongs to exactly one of the two groups.

Evidence：In the labels, '+' indicates a carcinogenic molecule and '-' indicates a non-carcinogenic molecule; for bond types, '-' indicates a single bond.

Gold SQL（離線）：
```sql
SELECT (SELECT SUM(CASE WHEN m.label = '+' THEN 1 ELSE -1 END) FROM molecule m WHERE NOT EXISTS (SELECT 1 FROM bond b WHERE b.molecule_id = m.molecule_id AND b.bond_type <> '-')) AS diff_molecules_with_only_single_bonds, (SELECT SUM(CASE WHEN m.label = '+' THEN 1 ELSE -1 END) FROM molecule m WHERE EXISTS (SELECT 1 FROM bond b WHERE b.molecule_id = m.molecule_id AND b.bond_type <> '-')) AS diff_other_molecules
```

Agent SQL：
```sql
WITH molecule_bond_group AS (
  SELECT
    m.molecule_id,
    m.label,
    CASE
      WHEN COUNT(b.bond_id) > 0
       AND SUM(CASE WHEN b.bond_type = '-' THEN 1 ELSE 0 END) = COUNT(b.bond_id)
      THEN 'all_single'
      ELSE 'other'
    END AS bond_group
  FROM molecule AS m
  LEFT JOIN bond AS b
    ON b.molecule_id = m.molecule_id
  GROUP BY m.molecule_id, m.label
)
SELECT
  bond_group,
  SUM(CASE WHEN label = '+' THEN 1 ELSE 0 END)
    - SUM(CASE WHEN label = '-' THEN 1 ELSE 0 END) AS difference
FROM molecule_bond_group
GROUP BY bond_group;
```

觀察：model replies=5、tool attempts=6、SQL attempts=2、latency=26.582s；stop=final_sql_ready。



<a id="q480"></a>

## [Q480](failure-case-review.md#q480) · dev · toxicology

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R6／鍵端點限制。

只計所有carcinogenic double bonds，缺少兩端均carbon及去除雙向重複限制。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：In our toxicology library, how many carbon-carbon pairs joined by a double bond are there in total across the carcinogenic compounds? I want a single number for the whole library.

Evidence：A compound is carcinogenic when its label is '+' and non-carcinogenic when its label is '-'. In the bond notation, '-' is a single bond, '=' is a double bond, and '#' is a triple bond.

Gold SQL（離線）：
```sql
SELECT COUNT(*) AS num_pairs FROM connected AS c JOIN bond AS b ON b.bond_id = c.bond_id JOIN molecule AS m ON m.molecule_id = b.molecule_id JOIN atom AS a1 ON a1.atom_id = c.atom_id JOIN atom AS a2 ON a2.atom_id = c.atom_id2 WHERE m.label = '+' AND b.bond_type = '=' AND a1.element = 'c' AND a2.element = 'c' AND c.atom_id < c.atom_id2
```

Agent SQL：
```sql
SELECT COUNT(*)
FROM bond AS b
JOIN molecule AS m ON m.molecule_id = b.molecule_id
WHERE m.label = '+'
  AND b.bond_type = '=';
```

觀察：model replies=6、tool attempts=10、SQL attempts=3、latency=19.926s；stop=final_sql_ready。



<a id="q481"></a>

## [Q481](failure-case-review.md#q481) · dev · toxicology

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／分子定義。

挑最常見元素後，percentage numerator仍用bonded count，Gold需該元素全部atoms數。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：Among the molecules labeled '+' (carcinogenic), which chemical element is the most common among the atoms that take part in at least one bond? Also give the percentage of all atoms in those '+' molecules that this element accounts for, rounded to two decimal places. Count the percentage over every atom of the '+' molecules, whether or not it takes part in a bond. If several elements tie for most common, report each of them.

Evidence：

Gold SQL（離線）：
```sql
WITH plus_atoms AS (SELECT a.atom_id, a.element FROM atom a JOIN molecule m ON m.molecule_id = a.molecule_id WHERE m.label = '+'), bonded AS (SELECT atom_id, element FROM plus_atoms WHERE atom_id IN (SELECT atom_id FROM connected) OR atom_id IN (SELECT atom_id2 FROM connected)), bonded_counts AS (SELECT element, COUNT(*) AS n FROM bonded GROUP BY element), top AS (SELECT MAX(n) AS mx FROM bonded_counts), all_counts AS (SELECT element, COUNT(*) AS na FROM plus_atoms GROUP BY element), total AS (SELECT COUNT(*) AS tot FROM plus_atoms) SELECT bc.element, ROUND(100.0 * ac.na / t.tot, 2) AS pct FROM bonded_counts bc JOIN top ON bc.n = top.mx JOIN all_counts ac ON ac.element = bc.element CROSS JOIN total t ORDER BY bc.element
```

Agent SQL：
```sql
WITH bonded_atoms AS (
    SELECT atom_id FROM connected
    UNION
    SELECT atom_id2 FROM connected
),
plus_atoms AS (
    SELECT a.atom_id, a.element
    FROM atom AS a
    JOIN molecule AS m ON m.molecule_id = a.molecule_id
    WHERE m.label = '+'
),
all_atom_count AS (
    SELECT COUNT(*) AS total
    FROM plus_atoms
),
bonded_element_counts AS (
    SELECT p.element, COUNT(*) AS atom_count
    FROM plus_atoms AS p
    JOIN bonded_atoms AS b ON b.atom_id = p.atom_id
    GROUP BY p.element
),
ranked AS (
    SELECT element, atom_count,
           DENSE_RANK() OVER (ORDER BY atom_count DESC) AS rank
    FROM bonded_element_counts
)
SELECT element,
       ROUND(100.0 * atom_count / (SELECT total FROM all_atom_count), 2) AS percentage
FROM ranked
WHERE rank = 1
ORDER BY element;
```

觀察：model replies=5、tool attempts=10、SQL attempts=4、latency=20.974s；stop=final_sql_ready。



<a id="q486"></a>

## [Q486](failure-case-review.md#q486) · dev · toxicology

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R6／存在條件範圍。

unique element條件綁定該bond端點，Gold只要求該molecule任何atom具unique element即可列全部bonds。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm compiling bond records of unusual carcinogenic molecules for a structural alert review. Please find the bonds that belong to carcinogenic molecules (labelled '+') that contain an element recorded for no other molecule in the dataset. Note that this search covers the whole dataset, so an element counts as belonging to no other molecule when no molecule other than the one at hand records it. For each such bond, return only the bond id and molecule id.

Evidence：A '+' label means carcinogenic.

Gold SQL（離線）：
```sql
SELECT T1.bond_id, T1.molecule_id FROM bond AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id WHERE T2.label = '+' AND EXISTS (SELECT 1 FROM atom AS a WHERE a.molecule_id = T1.molecule_id AND a.element IN (SELECT element FROM atom GROUP BY element HAVING COUNT(DISTINCT molecule_id) = 1))
```

Agent SQL：
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

觀察：model replies=7、tool attempts=9、SQL attempts=3、latency=21.290s；stop=final_sql_ready。



<a id="q493"></a>

## [Q493](failure-case-review.md#q493) · test · toxicology

狀態：incorrect_result；歷史轉變：歷史啱→本輪錯；主候選：R2／圖度數量度。

bonds/atoms不是每atom degree平均；每bond連兩端且零degree也須納入。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：As part of a connectivity review, I'd like to know how heavily atoms are connected in molecule TR397: what is the average number of bonds an atom of TR397 has? Please give me just that one number, rounded to two decimal places.

Evidence：

Gold SQL（離線）：
```sql
SELECT ROUND(AVG(cnt), 2) AS avg_bonds_per_atom FROM (SELECT a.atom_id, COUNT(DISTINCT c.bond_id) AS cnt FROM atom a LEFT JOIN connected c ON (c.atom_id = a.atom_id OR c.atom_id2 = a.atom_id) WHERE a.molecule_id = 'TR397' GROUP BY a.atom_id)
```

Agent SQL：
```sql
SELECT ROUND(
    1.0 * (SELECT COUNT(*) FROM bond WHERE molecule_id = 'TR397') /
    (SELECT COUNT(*) FROM atom WHERE molecule_id = 'TR397'),
    2
) AS average_bonds_per_atom;
```

觀察：model replies=6、tool attempts=9、SQL attempts=4、latency=24.546s；stop=final_sql_ready。



<a id="q494"></a>

## [Q494](failure-case-review.md#q494) · dev · toxicology

狀態：sql_error；歷史轉變：兩次均錯；主候選：R8／欄位別名歧義。

原生SQLite報 ambiguous column name: element；GROUP BY element改GROUP BY1後即與Gold四行結果一致。

診斷改寫：1次，1次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm studying bond patterns in compounds that are not carcinogenic. For each element, how many double or triple bonds join a carbon atom to an atom of that element, across all non-carcinogenic molecules? Give me one row per element with the element and its count of such bonds—nothing else.

Evidence：A molecule labeled '-' is not carcinogenic; a molecule labeled '+' is carcinogenic.

Gold SQL（離線）：
```sql
SELECT a2.element AS element, COUNT(DISTINCT c.bond_id) AS bond_count FROM connected c JOIN bond b ON c.bond_id = b.bond_id JOIN atom a1 ON c.atom_id = a1.atom_id JOIN atom a2 ON c.atom_id2 = a2.atom_id JOIN molecule m ON b.molecule_id = m.molecule_id WHERE m.label = '-' AND a1.element = 'c' AND b.bond_type != '-' GROUP BY a2.element ORDER BY a2.element
```

Agent SQL：
```sql
WITH bonds_by_element AS (
    SELECT
        CASE
            WHEN a.element = 'c' THEN a2.element
            ELSE a.element
        END AS element,
        COUNT(DISTINCT b.bond_id) AS bond_count
    FROM connected AS c
    JOIN atom AS a ON a.atom_id = c.atom_id
    JOIN atom AS a2 ON a2.atom_id = c.atom_id2
    JOIN bond AS b ON b.bond_id = c.bond_id
    JOIN molecule AS m ON m.molecule_id = b.molecule_id
    WHERE m.label = '-'
      AND b.bond_type IN ('=', '#')
      AND (a.element = 'c' OR a2.element = 'c')
    GROUP BY element
)
SELECT element, bond_count
FROM bonds_by_element;
```

觀察：model replies=13、tool attempts=17、SQL attempts=11、latency=41.719s；stop=final_sql_ready。



<a id="q497"></a>

## [Q497](failure-case-review.md#q497) · dev · toxicology

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／零次群組。

WHERE只保留saturated atoms，漏掉應以0列出之element；Gold排任何非'-'bond，Agent只排'='/'#'。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：I'm profiling the compound library and want to size the fully saturated portion of each element's atom population - atoms attached only by single bonds behave differently from unsaturated sites. For each element symbol in the database, how many atoms are connected only by single bonds and never part of any multiple bond? Please give me one row per element symbol with the element symbol and the number of such atoms, sorted alphabetically by element symbol. This should cover all compounds in the database. Note that an atom with no bonds at all doesn't count as being connected by single bonds, so exclude those.

Evidence：A single bond is a bond between two atoms sharing exactly one electron pair, denoted by the bond-type symbol '-'. A multiple bond is a double or triple bond, i.e. a bond between two atoms sharing more than one electron pair.

Gold SQL（離線）：
```sql
WITH per_atom AS (SELECT a.atom_id AS atom_id, a.element AS element, CASE WHEN EXISTS (SELECT 1 FROM connected AS c WHERE c.atom_id = a.atom_id) AND NOT EXISTS (SELECT 1 FROM connected AS c JOIN bond AS b ON b.bond_id = c.bond_id WHERE c.atom_id = a.atom_id AND b.bond_type <> '-') THEN 1 ELSE 0 END AS saturated FROM atom AS a) SELECT element, SUM(saturated) AS atoms FROM per_atom GROUP BY element ORDER BY element
```

Agent SQL：
```sql
SELECT
    a.element,
    COUNT(*) AS atom_count
FROM atom AS a
WHERE EXISTS (
    SELECT 1
    FROM connected AS c
    JOIN bond AS b ON b.bond_id = c.bond_id
    WHERE c.atom_id = a.atom_id
      AND b.bond_type = '-'
)
AND NOT EXISTS (
    SELECT 1
    FROM connected AS c
    JOIN bond AS b ON b.bond_id = c.bond_id
    WHERE c.atom_id = a.atom_id
      AND b.bond_type IN ('=', '#')
)
GROUP BY a.element
ORDER BY a.element;
```

觀察：model replies=8、tool attempts=12、SQL attempts=6、latency=26.428s；stop=final_sql_ready。



<a id="q498"></a>

## [Q498](failure-case-review.md#q498) · dev · toxicology

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R2／統計範圍。

只計三鍵參與atom的molecules，Gold先選元素再計該元素所有molecules。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：In the toxicology compound database, which elements take part in a triple bond, and how widely are they distributed across the tested compounds? For each such element, give me its element symbol and the number of molecules that contain that element. Order the results from the most widespread element to the least; where two elements have equal counts, list them alphabetically by element symbol.

Evidence：The '#' bond-type symbol denotes a triple bond.

Gold SQL（離線）：
```sql
SELECT a.element AS element, COUNT(DISTINCT a.molecule_id) AS n_molecules FROM atom AS a WHERE a.element IN (SELECT at.element FROM bond AS b JOIN connected AS c ON b.bond_id = c.bond_id JOIN atom AS at ON c.atom_id = at.atom_id WHERE b.bond_type = '#') GROUP BY a.element ORDER BY n_molecules DESC, a.element
```

Agent SQL：
```sql
SELECT a.element AS element_symbol,
       COUNT(DISTINCT a.molecule_id) AS molecule_count
FROM connected AS c
JOIN bond AS b ON b.bond_id = c.bond_id
JOIN atom AS a ON a.atom_id = c.atom_id
WHERE b.bond_type = '#'
GROUP BY a.element
ORDER BY molecule_count DESC, element_symbol ASC;
```

觀察：model replies=8、tool attempts=10、SQL attempts=3、latency=24.522s；stop=final_sql_ready。



<a id="q499"></a>

## [Q499](failure-case-review.md#q499) · dev · toxicology

狀態：incorrect_result；歷史轉變：兩次均錯；主候選：R3／零次群組。

EXISTS先排無bond atoms，漏掉在TR397有atoms但bonded_count=0的element群組。

診斷改寫：0次，0次符合Gold。未做成功改寫的個案只支持差異假設；詳見原始診斷。

Question：For molecule TR397, I want to see which elements form the bonding skeleton. For each element present among its atoms, how many atoms of that element take part in at least one bond? Please report two things per row: the element symbol (e.g. c, h, o) and the number of that element's atoms in TR397 that take part in a bond. One row per element, ordered alphabetically by element symbol. Only atoms belonging to TR397 should count.

Evidence：Takes part in a bond: the atom is one of the two atoms a bond joins.

Gold SQL（離線）：
```sql
SELECT a.element, COUNT(DISTINCT CASE WHEN c.bond_id IS NOT NULL THEN a.atom_id END) AS bonded_atoms FROM atom a LEFT JOIN connected c ON (c.atom_id = a.atom_id OR c.atom_id2 = a.atom_id) WHERE a.molecule_id = 'TR397' GROUP BY a.element ORDER BY a.element
```

Agent SQL：
```sql
SELECT a.element, COUNT(DISTINCT a.atom_id) AS atom_count
FROM atom AS a
WHERE a.molecule_id = 'TR397'
  AND EXISTS (
    SELECT 1
    FROM connected AS c
    WHERE c.atom_id = a.atom_id
       OR c.atom_id2 = a.atom_id
  )
GROUP BY a.element
ORDER BY a.element;
```

觀察：model replies=5、tool attempts=8、SQL attempts=2、latency=19.703s；stop=final_sql_ready。




> Repository archive: raw traces and local HTML viewers are intentionally excluded. Trace links above point to local-reproduction guidance; full local review artifacts remain preserved separately.
