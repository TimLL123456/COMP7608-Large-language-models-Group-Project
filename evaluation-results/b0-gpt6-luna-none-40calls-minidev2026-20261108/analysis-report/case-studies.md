# KORA — Mini-Dev 2026 B0 Failure Case Studies
> Companion evidence appendix to [Chinese analysis](baseline-analysis-zh-HK.md) / [English analysis](baseline-analysis-en.md). Covers **114 representative SQL-compared or reference-QA Development cases** (97 original plus 17 added on 2026-11-09). The [failure inventory](failure-inventory.csv) now contains a provisional Gold/Agent SQL-difference review for **all 165 Development failures**: 153 candidate primary causes and 12 unresolved. The 51 cases without a dedicated case-study entry remain summarized in the inventory.
>
> **Source policy:** Only official pinned Mini-Dev 2026 Gold SQL was used. Gold SQL excerpts here are for **offline research/evaluator inspection only**; do **not** feed this appendix into the B0 inference context, schema retrieval, demo RAG corpus, or agent tool filesystem.
>
> **Evidence labels:** "Observed" = stored Score/SQL/Trace; "Candidate" = plausible failure mechanism from comparison; "Reference QA candidate" = a possible difference between question language and official Gold, **not a proven annotation defect**. No fresh SQLite rescoring or repaired-query rerun was performed.

## How to read this appendix

Each case has its official Question/Evidence, Gold and Agent SQL (full for high-signal cases; abbreviated for others), and an observable summary of tool calls. **Successful SQL execution does not validate semantics**. Several cases have more than one plausible issue. All Result labels refer to the archived EX scorer. A direct SQL feature mismatch is not automatically the cause of EX=0.

### Priority reading routes

- **Value/sentinel and encoded values:** [Q345](#q345), [Q363](#q363), [Q389](#q389), [Q472](#q472).
- **Measure source, grain, denominator:** [Q65](#q65), [Q79](#q79), [Q128](#q128), [Q217](#q217), [Q320](#q320), [Q379](#q379), [Q481](#q481).
- **Extra filters or temporal interpretation:** [Q33](#q33), [Q332](#q332), [Q398](#q398), [Q412](#q412), [Q443](#q443).
- **Final query / output contract:** [Q2](#q2), [Q165](#q165), [Q325](#q325), [Q327](#q327), [Q335](#q335).
- **Gold-reference interpretation checks:** [Q235](#q235), [Q255](#q255), [Q325](#q325).

## Case index

| DB | Reviewed IDs (links) |
| --- | --- |
| `california_schools` | [Q2](#q2), [Q5](#q5), [Q21](#q21), [Q33](#q33) |
| `card_games` | [Q52](#q52), [Q62](#q62), [Q65](#q65), [Q66](#q66), [Q72](#q72), [Q78](#q78), [Q79](#q79), [Q82](#q82), [Q83](#q83), [Q96](#q96), [Q100](#q100), [Q105](#q105) |
| `codebase_community` | [Q120](#q120), [Q128](#q128), [Q130](#q130), [Q139](#q139), [Q145](#q145) |
| `debit_card_specializing` | [Q152](#q152), [Q155](#q155), [Q157](#q157), [Q162](#q162) |
| `european_football_2` | [Q165](#q165), [Q173](#q173), [Q175](#q175), [Q177](#q177), [Q189](#q189), [Q191](#q191) |
| `financial` | [Q201](#q201), [Q205](#q205), [Q213](#q213), [Q217](#q217), [Q224](#q224), [Q227](#q227), [Q230](#q230), [Q235](#q235) |
| `formula_1` | [Q242](#q242), [Q245](#q245), [Q251](#q251), [Q255](#q255), [Q259](#q259), [Q277](#q277), [Q294](#q294) |
| `student_club` | [Q300](#q300), [Q320](#q320), [Q321](#q321), [Q325](#q325), [Q327](#q327), [Q329](#q329), [Q331](#q331) |
| `superhero` | [Q332](#q332), [Q335](#q335), [Q339](#q339), [Q342](#q342), [Q345](#q345), [Q348](#q348), [Q350](#q350), [Q355](#q355), [Q356](#q356), [Q357](#q357), [Q358](#q358), [Q359](#q359), [Q360](#q360), [Q363](#q363), [Q365](#q365), [Q366](#q366), [Q367](#q367), [Q368](#q368), [Q370](#q370), [Q371](#q371), [Q374](#q374), [Q377](#q377), [Q378](#q378), [Q379](#q379), [Q380](#q380), [Q381](#q381) |
| `thrombosis_prediction` | [Q389](#q389), [Q398](#q398), [Q400](#q400), [Q411](#q411), [Q412](#q412), [Q417](#q417), [Q430](#q430), [Q438](#q438), [Q443](#q443), [Q447](#q447) |
| `toxicology` | [Q472](#q472), [Q478](#q478), [Q480](#q480), [Q481](#q481), [Q487](#q487), [Q488](#q488), [Q494](#q494), [Q498](#q498) |

## Source links and methodology

- [Dev scores](../dev/scores/per_question.jsonl), [predicted SQL](../dev/predictions.jsonl), [structured trace events](../dev/traces.jsonl), [run configuration](../configuration.json).
- [Pinned official Gold SQL](https://huggingface.co/datasets/birdsql/bird_mini_dev/blob/5b256b5a9c17478f06ed6912612e9a14d17065c8/data/mini_dev_sqlite.jsonl); [dataset identity](../dataset_manifest.json).
- SQL excerpts preserve the source SQL (possibly truncated with an explicit marker); text transformations in summary only make trace JSON legible. A zero-row or NULL result can still be meaningful; no inference is made from a mere lack of tool errors.

## Database: `california_schools`

<a id="q2"></a>
### Q2 — moderate · incorrect_result

**Question:** For the five schools with ownership code 66 and the largest K-12 free-or-reduced-price meal counts, give each school's K-12 eligible meal rate rounded to six decimal places.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(1.0 * f."FRPM Count (K-12)" / NULLIF(f."Enrollment (K-12)", 0), 6) FROM frpm AS f JOIN schools AS s ON s.CDSCode = f.CDSCode WHERE s.SOC = '66' AND f."FRPM Count (K-12)" IS NOT NULL AND f."Enrollment (K-12)" > 0 ORDER BY f."FRPM Count (K-12)" DESC, s.CDSCode LIMIT 5
```

**Agent final SQL:**

```sql
SELECT
    s.School,
    ROUND(f."Percent (%) Eligible FRPM (K-12)", 6) AS k12_eligible_meal_rate
FROM frpm AS f
JOIN schools AS s ON s.CDSCode = f.CDSCode
WHERE s.SOC = '66'
ORDER BY f."FRPM Count (K-12)" DESC
LIMIT 5;
```

**Assessment (CANDIDATE ROOT CAUSE):** Output contract: the requested result contains only the eligible-meal rate; the agent adds School and uses a stored percentage instead of the reference ratio.

**Observed trace:** 7 model calls; 6 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT f."Academic Year", s.SOC, s.SOCType, COUNT(*) AS n FROM frpm f JOIN schools s ON s.CDSCode=f.CDSCode GROUP BY f."Academic Year", s.SOC, s.SOCType OR` → {"columns":["Academic Year","SOC","SOCType","n"],"rows":[["2014-2015",null,null,45],["2014-2015","08","Preschool",2]],"truncated":false}  
Call 3: `SELECT s.School, ROUND(f."Percent (%) Eligible FRPM (K-12)", 6) AS k12_eligible_meal_rate FROM frpm f JOIN schools s ON s.CDSCode=f.CDSCode WHERE s.SOC='66` → {"columns":["School","k12_eligible_meal_rate"],"rows":[["Paramount High",0.917948],["Calexico High",0.999329]],"truncated":false}


<a id="q5"></a>
### Q5 — challenging · incorrect_result

**Question:** How many non-charter schools in Los Angeles County have a K-12 free-meal percentage below 0.18%?

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(T2.School) FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Los Angeles' AND T2.Charter = 0 AND CAST(T1.`Free Meal Count (K-12)` AS REAL) * 100 / T1.`Enrollment (K-12)` < 0.18
```

**Agent final SQL:**

```sql
SELECT COUNT(*) AS school_count
FROM frpm
WHERE `County Name` = 'Los Angeles'
  AND `Charter School (Y/N)` = 0
  AND `Percent (%) Eligible Free (K-12)` < 0.18;
```

**Assessment (CANDIDATE ROOT CAUSE):** Measure/semantic mismatch: the target is K-12 free-meal percentage and non-charter status; the agent uses similarly named FRPM columns from a different table.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(*) AS school_count FROM frpm WHERE `County Name` = 'Los Angeles' AND `Charter School (Y/N)` = 0 AND `Percent (%) Eligible Free (K-12)` < 0.18;` → {"columns":["school_count"],"rows":[[201]],"truncated":false}


<a id="q21"></a>
### Q21 — challenging · incorrect_result

**Question:** For the 2014-2015 academic year, what was the average number of enrolled students aged 5 to 17 eligible for free or reduced price meals per Youth Authority school? Count every Youth Authority school regardless of its status (active, closed, or merged), and treat a Youth Authority school with no meal-program record as zero. Please give me just that one number, rounded to two decimal places.

**Evidence:** A Youth Authority school is a school the state directory classifies as a Youth Authority Facility.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(SUM(COALESCE(T1.`FRPM Count (Ages 5-17)`, 0.0)) * 1.0 / COUNT(T2.CDSCode), 2) AS avg_frpm_ages_5_17 FROM schools AS T2 LEFT JOIN frpm AS T1 ON T1.CDSCode = T2.CDSCode WHERE T2.SOCType LIKE '%Youth Authority%'
```

**Agent final SQL:**

```sql
SELECT ROUND(
    1.0 * SUM(COALESCE(f.`FRPM Count (Ages 5-17)`, 0)) / COUNT(*),
    2
) AS average_eligible_students
FROM schools AS s
LEFT JOIN frpm AS f
    ON f.CDSCode = s.CDSCode
   AND f.`Academic Year` = '2014-2015'
WHERE s.EdOpsName = 'Youth Authority School';
```

**Assessment (CANDIDATE ROOT CAUSE):** Filter drift: the reference identifies Youth Authority facilities using SOCType; the agent filters EdOpsName to a narrower/different label.

**Observed trace:** 11 model calls; 11 tool calls; 8 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT s.StatusType, COUNT(*) FROM schools s WHERE s.DOCType = 'Youth Authority Facility' GROUP BY s.StatusType;` → {"columns":["StatusType","COUNT(*)"],"rows":[],"truncated":false}  
Call 8: `SELECT ROUND(1.0 * SUM(COALESCE(f.`FRPM Count (Ages 5-17)`, 0)) / COUNT(*), 2) AS avg_eligible FROM schools s LEFT JOIN frpm f ON f.CDSCode=s.CDSCode AND f` → {"columns":["avg_eligible"],"rows":[[0.83]],"truncated":false}


<a id="q33"></a>
### Q33 — challenging · incorrect_result

**Question:** I'm studying the 1980 growth of public schooling in San Diego County. What was the average number of schools per month that opened in San Diego County in 1980 under a school district's jurisdiction? I need just that single number. Please average over all 12 months of 1980 (months with no openings count as zero), and give me the exact average without rounding.

**Evidence:** A school district is a local education agency that runs K-12 public schools; it is an elementary school district, a high school district, or a unified school district.

**Official Gold SQL** (full unless noted):

```sql
SELECT CAST(COUNT(*) AS REAL) / 12 AS monthly_average FROM schools WHERE County = 'San Diego' AND strftime('%Y', OpenDate) = '1980' AND DOCType IN ('Elementary School District', 'High School District', 'Unified School District');
```

**Agent final SQL:**

```sql
SELECT 519.0 / 12;
```

**Assessment (CANDIDATE ROOT CAUSE):** The trace first computes 572/12 = 47.6667 using the district-type condition, then adds unsupported SOCType LIKE '%(Public)%', yields 519/12=43.25 and finally hardcodes 519.0/12.

**Observed trace:** 12 model calls; 12 tool calls; 9 SQL calls (1 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT DOCType, SOCType, COUNT(*) AS n FROM schools WHERE County = 'San Diego' AND OpenDate >= '1980-01-01' AND OpenDate < '1981-01-01' GROUP BY DOCType, S` → {"columns":["DOCType","SOCType","n"],"rows":[["Unified School District","Elementary Schools (Public)",204],["Elementary School District","Elementary Schools (Public)",155]],"truncated":true}  
Call 9: `WITH monthly AS (SELECT CAST(strftime('%m', OpenDate) AS INTEGER) AS month, COUNT(*) AS n FROM schools WHERE County='San Diego' AND OpenDate >= '1980-01-01` → {"columns":["total_openings","average_exact"],"rows":[[519,43.25]],"truncated":false}


## Database: `card_games`

<a id="q52"></a>
### Q52 — simple · incorrect_result

**Question:** What rules text is printed on Benalish Knight? Return the distinct text as one line.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT DISTINCT REPLACE(text, CHAR(10), ' ') FROM cards WHERE name = 'Benalish Knight' AND text IS NOT NULL
```

**Agent final SQL:**

```sql
SELECT DISTINCT text
FROM cards
WHERE name = 'Benalish Knight';
```

**Assessment (CANDIDATE ROOT CAUSE):** Output normalization: Gold replaces newline characters in the distinct card rules text with spaces; agent returns raw text.

**Observed trace:** 4 model calls; 3 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT DISTINCT text FROM cards WHERE name = 'Benalish Knight';` → {"columns":["text"],"rows":[["Flash (You may cast this spell any time you could cast an instant.)\nFirst strike (This creature deals combat damage before creatures without first strike.)"]],"truncated":false}


<a id="q62"></a>
### Q62 — challenging · incorrect_result

**Question:** I collect promotional printings and play Brawl. How many different creature cards that have a promotional printing can serve as a Brawl commander? I just want a single number back.

**Evidence:** A promotional printing is a printing of a card made as a promotion, as opposed to a regular set printing. Brawl is a Magic: The Gathering format; the deck's commander is the card that leads it, and only certain cards are legal as a Brawl commander.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(DISTINCT name) AS creature_cards_legal_brawl_commanders FROM cards WHERE isPromo = 1 AND instr(types, 'Creature') > 0 AND instr(leadershipSkills, '''brawl'': True') > 0
```

**Agent final SQL:**

```sql
SELECT COUNT(DISTINCT c.name)
FROM cards c
JOIN legalities l ON l.uuid = c.uuid
WHERE c.isPromo = 1
  AND c.types LIKE '%Creature%'
  AND l.format = 'brawl'
  AND l.status = 'Legal';
```

**Assessment (CANDIDATE ROOT CAUSE):** Value/metric semantics: the reference checks the encoded Brawl leadershipSkills flag on cards, while the agent checks a separate legalities relation.

**Observed trace:** 6 model calls; 7 tool calls; 3 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT format, status, COUNT(*) FROM legalities GROUP BY format, status ORDER BY format, status` → {"columns":["format","status","COUNT(*)"],"rows":[["brawl","Banned",34],["brawl","Legal",7664]],"truncated":true}  
Call 3: `SELECT COUNT(DISTINCT c.scryfallOracleId) AS count FROM cards c JOIN legalities l ON l.uuid=c.uuid WHERE l.format='brawl' AND l.status='Legal' AND c.isProm` → {"columns":["count"],"rows":[[278]],"truncated":false}


<a id="q65"></a>
### Q65 — challenging · incorrect_result

**Question:** I have the count of sets with fewer than five translations of their name — now I need the gap in cards to size the translation budget. Can you give me the total number of cards contained in those sets? A few things to keep in mind: 'fewer than five' is strict, so a set with exactly five translations doesn't count. All sets count regardless of type or release (core set, expansion, promotional, online-only, etc.). If two languages have the identical translated name string for a set, that's one translation, not two. And a set's card count should be its full size, including promotional and related supplemental printings.

**Evidence:** A 'translation of a set's name' means the localized name of the set in another language, e.g. its French or Simplified Chinese name.

**Official Gold SQL** (full unless noted):

```sql
SELECT SUM(totalSetSize) AS total_cards FROM sets WHERE (SELECT COUNT(DISTINCT translation) FROM set_translations WHERE setCode = sets.code) < 5
```

**Agent final SQL:**

```sql
SELECT COUNT(c.id) AS total_cards
FROM sets AS s
LEFT JOIN set_translations AS st ON st.setCode = s.code
LEFT JOIN cards AS c ON c.setCode = s.code
GROUP BY s.code
HAVING COUNT(DISTINCT st.translation) < 5
;
```

**Assessment (CANDIDATE ROOT CAUSE):** The reference SUMs sets.totalSetSize across qualifying sets; agent counts cards rows and GROUP BY set, violating both the metric definition and single-total output.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH translation_counts AS ( SELECT setCode, COUNT(DISTINCT translation) AS translation_count FROM set_translations WHERE translation IS NOT NULL GROUP BY ` → {"columns":["total_cards"],"rows":[[45630]],"truncated":false}


<a id="q66"></a>
### Q66 — challenging · incorrect_result

**Question:** I'm preparing a multilingual catalog and want to gauge how much localizable content exists per kind of set. For every set type, I need the number of sets of that type that have an officially translated name, and the total number of cards in those sets. Please include every set type in the results, even ones where no set has an officially translated name (show zero for both values in that case), and sort the results alphabetically by set type.

**Evidence:** Set type: the expansion type of a set, such as core, expansion or promo. Officially translated name: the set's name rendered in another language, such as Italian or Chinese Traditional.

**Official Gold SQL** (full unless noted):

```sql
SELECT s.type, SUM(CASE WHEN EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code) THEN 1 ELSE 0 END) AS sets_with_translation, SUM(CASE WHEN EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code) THEN s.totalSetSize ELSE 0 END) AS total_cards FROM sets s GROUP BY s.type ORDER BY s.type
```

**Agent final SQL:**

```sql
WITH translated_sets AS (
    SELECT DISTINCT setCode
    FROM set_translations
    WHERE translation IS NOT NULL
      AND TRIM(translation) <> ''
),
per_set AS (
    SELECT
        s.code,
        s.type,
        CASE WHEN ts.setCode IS NOT NULL THEN 1 ELSE 0 END AS is_translated,
        COUNT(c.id) AS card_count
    FROM sets AS s
    LEFT JOIN translated_sets AS ts ON ts.setCode = s.code
    LEFT JOIN cards AS c ON c.setCode = s.code
    GROUP BY s.code, s.type, ts.setCode
)
SELECT
    type,
    SUM(is_translated) AS translated_set_count,
    SUM(CASE WHEN is_translated = 1 THEN card_count ELSE 0 END) AS translated_set_card_count
FROM per_set
GROUP BY type
ORDER BY type;
```

**Assessment (CANDIDATE ROOT CAUSE):** The reference counts sets with any name translation and their totalSetSize per type, including zero groups; agent derives card_count from cards rows, potentially changing the metric.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT s.type, COUNT(DISTINCT s.code) AS translated_set_count, COUNT(c.id) AS card_count FROM sets s LEFT JOIN set_translations t ON t.setCode = s.code AND` → {"columns":["type","translated_set_count","card_count"],"rows":[["archenemy",5,1686],["box",27,5182]],"truncated":false}  
Call 2: `WITH translated_sets AS ( SELECT DISTINCT setCode FROM set_translations WHERE translation IS NOT NULL AND TRIM(translation) <> '' ), per_set AS ( SELECT s.` → {"columns":["type","translated_set_count","translated_set_card_count"],"rows":[["archenemy",1,151],["box",3,284]],"truncated":false}


<a id="q72"></a>
### Q72 — challenging · incorrect_result

**Question:** I'm brewing and looking for cards that combine two keyword abilities. How many cards in the collection have both Flying and Cycling? Note that each printing counts as its own card, and a card only counts if it has both keywords.

**Evidence:** Flying and Cycling are keyword abilities in Magic: The Gathering.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(*) AS card_count FROM cards WHERE instr(',' || keywords || ',', ',' || 'Flying' || ',') > 0 AND instr(',' || keywords || ',', ',' || 'Cycling' || ',') > 0
```

**Agent final SQL:**

```sql
SELECT COUNT(*) AS count_cards
FROM cards
WHERE keywords LIKE '%Flying%'
  AND keywords LIKE '%Cycling%';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold checks comma-separated keyword token membership; agent uses substring LIKE, which can match non-exact terms.

**Observed trace:** 4 model calls; 3 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(*) AS count_cards FROM cards WHERE keywords LIKE '%Flying%' AND keywords LIKE '%Cycling%';` → {"columns":["count_cards"],"rows":[[45]],"truncated":false}


<a id="q78"></a>
### Q78 — challenging · incorrect_result

**Question:** I'm preparing localized set icon assets and need to know the foreign-language name coverage of every Magic: The Gathering set released in 2020. For each set released in 2020 (meaning its release date falls within the calendar year 2020), please give me the set's name, its keyrune code, and the number of languages in which the set has an official translated name. Nothing else.

**Evidence:** keyrune code: the code for the set's image icon; official translated name: the set's name rendered in a foreign language by the game's publisher.

**Official Gold SQL** (full unless noted):

```sql
SELECT s.name, s.keyruneCode, COUNT(DISTINCT st.language) AS translated_languages FROM sets s LEFT JOIN set_translations st ON st.setCode = s.code AND st.translation IS NOT NULL WHERE strftime('%Y', s.releaseDate) = '2020' GROUP BY s.id, s.name, s.keyruneCode ORDER BY s.name
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** The reference counts languages only when translated set names are present; agent counts distinct st.language even when translation may be NULL.

**Observed trace:** 15 model calls; 15 tool calls; 12 SQL calls (0 tool errors, 10 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT s.name, s.keyruneCode, COUNT(DISTINCT st.language) AS language_count FROM sets s LEFT JOIN set_translations st ON st.setCode = s.code WHERE s.releas` → {"columns":["name","keyruneCode","language_count"],"rows":[["Judge Gift Cards 2020","PMEI",0],["MagicFest 2020","PMEI",0]],"truncated":true}  
Call 12: `SELECT s.name,s.keyruneCode,COUNT(DISTINCT st.language) language_count FROM sets s LEFT JOIN set_translations st ON st.setCode=s.code WHERE s.releaseDate >` → {"columns":["name","keyruneCode","language_count"],"rows":[["Judge Gift Cards 2020","PMEI",0],["MagicFest 2020","PMEI",0]],"truncated":true}


<a id="q79"></a>
### Q79 — challenging · incorrect_result

**Question:** I'm sizing a catalogue page of 2017 sets that were localized for international markets. How many cards were there in total across the Magic: The Gathering sets released in 2017 (between January 1 and December 31, 2017) that have a name in a language other than English? A set counts as localized if its name has a foreign-language translation. Include every card in each qualifying set, counting promotional and related supplemental printings as part of the set. I just need the single total across all qualifying sets, not per-set numbers.

**Evidence:** A foreign-language translation is a set's name rendered in a language other than English (e.g. Chinese Simplified, German, Spanish).

**Official Gold SQL** (full unless noted):

```sql
SELECT SUM(s.totalSetSize) AS total_cards FROM sets s WHERE s.releaseDate BETWEEN '2017-01-01' AND '2017-12-31' AND EXISTS (SELECT 1 FROM set_translations t WHERE t.setCode = s.code)
```

**Agent final SQL:**

```sql
SELECT COUNT(*) AS total_cards
FROM cards
WHERE setCode IN (
    SELECT s.code
    FROM sets AS s
    WHERE s.releaseDate >= '2017-01-01'
      AND s.releaseDate < '2018-01-01'
      AND EXISTS (
          SELECT 1
          FROM set_translations AS st
          WHERE st.setCode = s.code
            AND st.language <> 'English'
      )
);
```

**Assessment (CANDIDATE ROOT CAUSE):** Reference adds sets.totalSetSize for 2017 localized sets, agent counts rows in cards instead; supplemental size need not equal stored printings.

**Observed trace:** 9 model calls; 10 tool calls; 6 SQL calls (0 tool errors, 2 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT s.code,s.name,s.releaseDate,s.type, COUNT(DISTINCT st.language) AS translations, COUNT(c.id) AS cards FROM sets s JOIN set_translations st ON st.set` → {"columns":["code","name","releaseDate","type","translations","cards"],"rows":[["AER","Aether Revolt","2017-01-20","expansion",10,1970],["AKH","Amonkhet","2017-04-28","expansion",10,3020]],"truncated":false}  
Call 6: `SELECT COUNT(*) AS total_cards FROM cards WHERE setCode IN (SELECT s.code FROM sets s WHERE s.releaseDate >= '2017-01-01' AND s.releaseDate < '2018-01-01' ` → {"columns":["total_cards"],"rows":[[808]],"truncated":false}


<a id="q82"></a>
### Q82 — challenging · incorrect_result

**Question:** I'm going through my paper collection before sharing it publicly, and I want to check something about the cards Wizards of the Coast has flagged. How many different cards are there that carry a sensitive content warning, are available in paper form, and have never been available on Magic Online (MTGO)? I just need that one count.

**Evidence:** MTGO means Magic: The Gathering Online, the official online version of the game. A sensitive content warning means Wizards of the Coast has marked the card for having sensitive content.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(*) AS card_count FROM (SELECT name FROM cards WHERE hasContentWarning = 1 GROUP BY name HAVING MAX(CASE WHEN availability LIKE '%paper%' THEN 1 ELSE 0 END) = 1 AND MAX(CASE WHEN availability LIKE '%mtgo%' THEN 1 ELSE 0 END) = 0)
```

**Agent final SQL:**

```sql
SELECT COUNT(DISTINCT name) AS card_count
FROM cards
WHERE hasContentWarning = 1
  AND availability LIKE '%paper%'
  AND availability NOT LIKE '%mtgo%';
```

**Assessment (CANDIDATE ROOT CAUSE):** The reference checks a card name across all printings for paper availability and absence from MTGO; the agent applies NOT LIKE per printing and may misclassify a card that was on MTGO in another printing.

**Observed trace:** 6 model calls; 5 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(DISTINCT name) AS card_count FROM cards WHERE hasContentWarning = 1 AND availability LIKE '%paper%' AND (availability NOT LIKE '%mtgo%' OR mtg` → {"columns":["card_count"],"rows":[[7]],"truncated":false}  
Call 3: `SELECT COUNT(DISTINCT name) FROM cards WHERE hasContentWarning=1 AND availability LIKE '%paper%' AND availability NOT LIKE '%mtgo%';` → {"columns":["COUNT(DISTINCT name)"],"rows":[[7]],"truncated":false}


<a id="q83"></a>
### Q83 — challenging · incorrect_result

**Question:** Hi! I'm preparing a licensing brief for our Japanese partner about Magic: The Gathering localization coverage. Could you pull a report of every expansion type (core, expansion, promo, etc.), showing for each one how many sets of that type carry a Japanese name entry? A Japanese name entry means the set's name-translations include a Japanese-language entry giving the set's name in Japanese. Please include every expansion type in the report even if none of its sets have such an entry (show 0 for those), and sort the results alphabetically by expansion type. Nothing else needed - just the expansion type and the count.

**Evidence:** Japanese name entry: an entry in the set's name-translations whose language is Japanese and which gives the set's name in Japanese.

**Official Gold SQL** (full unless noted):

```sql
SELECT s.type AS expansion_type, COUNT(DISTINCT CASE WHEN st.language = 'Japanese' AND st.translation IS NOT NULL AND TRIM(st.translation) <> '' THEN s.code END) AS japanese_named_sets FROM sets s LEFT JOIN set_translations st ON st.setCode = s.code GROUP BY s.type ORDER BY s.type
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** The LEFT JOIN must count only sets with a nonempty Japanese translation; agent COUNT(DISTINCT s.id) counts all sets regardless of translation.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT s.type, COUNT(DISTINCT s.id) AS japanese_name_set_count FROM sets s LEFT JOIN set_translations st ON st.setCode = s.code AND st.language = 'Japanese` → {"columns":["type","japanese_name_set_count"],"rows":[["archenemy",5],["box",27]],"truncated":false}


<a id="q96"></a>
### Q96 — challenging · incorrect_result

**Question:** I'm cataloguing modern-frame printings. How many different cards that have a text box were printed with a frame version of 2015 or a later year? I just need that single count.

**Gold SQL preview:**

```sql
SELECT COUNT(DISTINCT name) AS number_of_cards FROM cards WHERE isTextless = 0 AND CAST(frameVersion AS INTEGER) >= 2015
```

**Agent SQL preview:**

```sql
SELECT COUNT(DISTINCT scryfallOracleId)
FROM cards
WHERE frameVersion IN ('2015', 'future')
  AND text IS NOT NULL
  AND TRIM(text) <> '';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold counts distinct card names with isTextless=0 and frame year >=2015; agent uses scryfallOracleId and tests nonempty text, which is a different entity/criterion.

**Observed trace:** 7 model calls; 6 tool calls; 4 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q100"></a>
### Q100 — challenging · incorrect_result

**Question:** I'm cataloguing European releases of Counterspell. How many of its printings were released with both a French and an Italian localization? I just need the count as a single number.

**Evidence:** A printing is one release of the card identified by its set and its card number in that set; 'Counterspell' is the English card name as catalogued.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(DISTINCT c.id) FROM cards AS c JOIN foreign_data AS f ON c.uuid = f.uuid WHERE c.name = 'Counterspell' AND f.language IN ('French','Italian') AND c.id IN (SELECT c2.id FROM cards AS c2 JOIN foreign_data AS f2 ON c2.uuid = f2.uuid WHERE c2.name = 'Counterspell' AND f2.language = 'French' INTERSECT SELECT c3.id FROM cards AS c3 JOIN foreign_data AS f3 ON c3.uuid = f3.uuid WHERE c3.name = 'Counterspell' AND f3.language = 'Italian')
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Question is about card printings with both French and Italian localizations in foreign_data; agent uses set_translations, a different table grain.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT c.setCode, c.number, s.name, s.releaseDate, s.type, s.isForeignOnly, GROUP_CONCAT(DISTINCT st.language) AS langs FROM cards c JOIN sets s ON s.code=` → {"columns":["setCode","number","name","releaseDate","type","isForeignOnly","langs"],"rows":[["LEA","54","Limited Edition Alpha","1993-08-05","core",0,null],["LEB","55","Limited Edition Beta","1993-10-04","core",0,null]],"truncated":true}  
Call 2: `SELECT COUNT(*) AS count FROM (SELECT c.setCode, c.number FROM cards c JOIN sets s ON s.code=c.setCode WHERE c.name='Counterspell' AND s.type NOT IN ('funn` → {"columns":["count"],"rows":[[12]],"truncated":false}


<a id="q105"></a>
### Q105 — challenging · incorrect_result

**Question:** We're planning translation work for upcoming set releases and want to know how extensively a recent release year was localized. What was the average number of languages in which sets released in 2016 had their names translated? By 'released in 2016' I mean the release date falls within calendar year 2016. Every set released in 2016 counts toward the average, including any whose names were translated into no language at all (those count as zero). A language counts for a set when the set's name is rendered in that language. Please give me just that one number, rounded to two decimals.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(n), 2) AS avg_languages FROM (SELECT s.id, COUNT(DISTINCT CASE WHEN st.translation IS NOT NULL AND TRIM(st.translation) <> '' THEN st.language END) AS n FROM sets s LEFT JOIN set_translations st ON s.code = st.setCode WHERE substr(s.releaseDate, 1, 4) = '2016' GROUP BY s.id)
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(language_count), 2) AS average_languages
FROM (
  SELECT s.code, COUNT(DISTINCT st.language) AS language_count
  FROM sets AS s
  LEFT JOIN set_translations AS st ON st.setCode = s.code
  WHERE s.releaseDate >= '2016-01-01'
    AND s.releaseDate < '2017-01-01'
  GROUP BY s.code
);
```

**Assessment (CANDIDATE ROOT CAUSE):** Count a language only when the set name has a nonempty translation; agent counts language tags without validating translation text.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

## Database: `codebase_community`

<a id="q120"></a>
### Q120 — challenging · incorrect_result

**Question:** What is the difference in percentage points between the 2010 and 2011 shares of all Student badges, taking the 2010 share minus the 2011 share?

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT CAST(SUM(IIF(STRFTIME('%Y', Date) = '2010', 1, 0)) AS REAL) * 100 / COUNT(Id) - CAST(SUM(IIF(STRFTIME('%Y', Date) = '2011', 1, 0)) AS REAL) * 100 / COUNT(Id) FROM badges WHERE Name = 'Student'
```

**Agent final SQL:**

```sql
SELECT
    100.0 * SUM(CASE WHEN strftime('%Y', Date) = '2010' AND Name = 'Student' THEN 1 ELSE 0 END)
        / SUM(CASE WHEN strftime('%Y', Date) = '2010' THEN 1 ELSE 0 END)
    - 100.0 * SUM(CASE WHEN strftime('%Y', Date) = '2011' AND Name = 'Student' THEN 1 ELSE 0 END)
        / SUM(CASE WHEN strftime('%Y', Date) = '2011' THEN 1 ELSE 0 END)
    AS percentage_point_difference
FROM badges
WHERE strftime('%Y', Date) IN ('2010', '2011');
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold compares the share of Student badges across all Student-badge records by year; agent uses all badge records per year as denominators. Gold interpretation is authoritative for EX, but wording should also be reviewed.

**Observed trace:** 4 model calls; 3 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT 100.0 * SUM(CASE WHEN strftime('%Y', Date) = '2010' AND Name = 'Student' THEN 1 ELSE 0 END) / SUM(CASE WHEN strftime('%Y', Date) = '2010' THEN 1 ELS` → {"columns":["percentage_point_difference"],"rows":[[-7.2785444458662045]],"truncated":false}


<a id="q128"></a>
### Q128 — challenging · incorrect_result

**Question:** I want to profile the users who drop links in comment threads. What is the average age of the users who posted a comment containing a website link? Please round it to two decimal places. That single value is all I need back.

**Evidence:** A comment counts as containing a website if its content contains 'http://'.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(AVG(T.Age), 2) AS average_age FROM (SELECT DISTINCT T2.Id, T2.Age FROM comments AS T1 INNER JOIN users AS T2 ON T1.UserId = T2.Id WHERE T1.Text LIKE '%http://%') AS T
```

**Agent final SQL:**

```sql
SELECT ROUND(AVG(u.Age), 2) AS average_age
FROM comments AS c
JOIN users AS u ON u.Id = c.UserId
WHERE c.Text LIKE '%http://%';
```

**Assessment (CANDIDATE ROOT CAUSE):** One user may post multiple URL comments; Gold deduplicates users before AVG(Age), whereas agent averages joined comment rows.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT ROUND(AVG(u.Age), 2) AS average_age FROM comments AS c JOIN users AS u ON u.Id = c.UserId WHERE c.Text LIKE '%http://%';` → {"columns":["average_age"],"rows":[[28.24]],"truncated":false}


<a id="q130"></a>
### Q130 — challenging · incorrect_result

**Question:** I'm putting together a report for the site owners on where people who started posting during 2010 were located, with a focus on India. Could you tell me how many of the users whose first post was created in 2010 are located in India? By 2010 I mean the calendar year 2010, and by India I mean the country itself, not any place whose name merely contains the word.

**Gold SQL preview:**

```sql
WITH RECURSIVE fp AS (SELECT OwnerUserId AS uid, MIN(CreaionDate) AS fdate FROM posts WHERE OwnerUserId IS NOT NULL GROUP BY OwnerUserId), locs AS (SELECT u.Id AS uid, u.Location AS loc FROM users u JOIN fp ON fp.uid = u.Id WHERE fp.fdate >= '2010-01-01' AND fp.fdate < '2011-01-01'), parts(uid, head, tail) AS (SELECT uid, CASE WHEN instr(loc, ',') > 0 THEN substr(loc, 1, instr(loc, ',') - 1) ELSE loc END, CASE WHEN instr(loc, ',') > 0 THEN substr
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

```sql
SELECT COUNT(*) AS user_count
FROM users AS u
WHERE lower(trim(u.Location)) = 'india'
  AND EXISTS (
    SELECT 1
    FROM posts AS p
    WHERE p.OwnerUserId = u.Id
      AND p.CreaionDate >= '2010-01-01'
      AND p.CreaionDate < '2011-01-01'
      AND NOT EXISTS (
        SELECT 1
        FROM posts AS earlier
        WHERE earlier.OwnerUserId = p.OwnerUserId
          AND (
            earlier.CreaionDate < p.CreaionDate
            OR (earlie
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold parses comma-separated location parts to identify country India; agent matches only literal 'india'.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q139"></a>
### Q139 — challenging · incorrect_result

**Question:** I'm preparing a report on international participation. How many users located in India had earned a Yearling badge before 2014? 'Before 2014' should mean before 1 January 2014. I just need the single count, nothing else.

**Gold SQL preview:**

```sql
SELECT COUNT(DISTINCT T1.UserId) AS user_count FROM badges AS T1 INNER JOIN users AS T2 ON T1.UserId = T2.Id WHERE T2.Location LIKE '%India%' AND T1.Name = 'Yearling' AND T1.Date < '2014-01-01'
```

**Agent SQL preview:**

```sql
SELECT COUNT(DISTINCT b.UserId) AS user_count
FROM badges AS b
JOIN users AS u ON u.Id = b.UserId
WHERE b.Name = 'Yearling'
  AND b.Date < '2014-01-01'
  AND u.Location = 'India';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold matches locations containing India, whereas agent requires exact Location='India'.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q145"></a>
### Q145 — challenging · incorrect_result

**Question:** I'm profiling our most active contributors of 2012. Among the users who created more than ten posts in 2012 (judged by each post's creation date), what is their average number of up-votes cast and their average age? Please give me a single row with both averages, each rounded to two decimal places.

**Evidence:** Up-vote: a vote a user cast in favor of a post.

**Official Gold SQL** (full unless noted):

```sql
WITH active AS (SELECT OwnerUserId FROM posts WHERE CreaionDate >= '2012-01-01' AND CreaionDate < '2013-01-01' GROUP BY OwnerUserId HAVING COUNT(*) > 10) SELECT ROUND(AVG(u.UpVotes), 2) AS avg_upvotes, ROUND(AVG(u.Age), 2) AS avg_age FROM active AS a JOIN users AS u ON u.Id = a.OwnerUserId
```

**Agent final SQL:**

```sql
WITH active_users AS (
    SELECT OwnerUserId
    FROM posts
    WHERE CreaionDate >= '2012-01-01'
      AND CreaionDate < '2013-01-01'
      AND OwnerUserId IS NOT NULL
    GROUP BY OwnerUserId
    HAVING COUNT(*) > 10
),
user_upvotes AS (
    SELECT UserId, COUNT(*) AS upvote_count
    FROM votes
    WHERE VoteTypeId = 2
      AND UserId IS NOT NULL
    GROUP BY UserId
)
SELECT
    ROUND(AVG(COALESCE(uu.upvote_count, 0)), 2) AS avg_upvotes_cast,
    ROUND(AVG(u.Age), 2) AS avg_age
FROM active_users AS a
JOIN users AS u ON u.Id = a.OwnerUserId
LEFT JOIN user_upvotes AS uu ON uu.UserId = u.Id;
```

**Assessment (CANDIDATE ROOT CAUSE):** Reference averages users.UpVotes across qualifying active users; agent recomputes from votes records, introducing a different measure.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT VoteTypeId, COUNT(*) AS n FROM votes GROUP BY VoteTypeId ORDER BY VoteTypeId` → {"columns":["VoteTypeId","n"],"rows":[[1,1451],[2,33323]],"truncated":false}  
Call 2: `WITH active AS (SELECT OwnerUserId FROM posts WHERE CreaionDate >= '2012-01-01' AND CreaionDate < '2013-01-01' AND OwnerUserId IS NOT NULL GROUP BY OwnerUs` → {"columns":["avg_upvotes_cast","avg_age"],"rows":[[0,36.14]],"truncated":false}


## Database: `debit_card_specializing`

<a id="q152"></a>
### Q152 — challenging · incorrect_result

**Question:** How many customers who pay in EUR and had gas consumption in 2012 also had gas consumption in 2013? I just need a single number: the count of such customers. By 2012 and 2013 I mean those calendar years, and gas consumption in any month of the year counts.

**Gold SQL preview:**

```sql
SELECT COUNT(*) AS customers FROM (SELECT CustomerID FROM yearmonth WHERE SUBSTR(Date,1,4) = '2012' AND CustomerID IN (SELECT CustomerID FROM customers WHERE Currency = 'EUR') INTERSECT SELECT CustomerID FROM yearmonth WHERE SUBSTR(Date,1,4) = '2013')
```

**Agent SQL preview:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Agent adds Consumption>0 where Gold only checks matching yearmonth rows and currency, potentially excluding valid reference records.

**Observed trace:** 5 model calls; 7 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q155"></a>
### Q155 — challenging · incorrect_result

**Question:** I want to gauge how spread out our high-value fuelling activity in the Czech Republic was over the recorded window. How many whole minutes elapsed from the first to the last fuel transaction at gas stations in the Czech Republic with a price over 1000? Please round down to whole minutes.

**Gold SQL preview:**

```sql
SELECT (strftime('%s', MAX(Date || ' ' || Time)) - strftime('%s', MIN(Date || ' ' || Time))) / (5 * 13 - 5) AS minutes FROM transactions_1k AS T1 INNER JOIN gasstations AS T2 ON T1.GasStationID = T2.GasStationID WHERE T2.Country = 'CZE' AND T1.Price > 1000
```

**Agent SQL preview:**

```sql
SELECT CAST(
    (julianday(MAX(datetime(t.Date || ' ' || t.Time))) -
     julianday(MIN(datetime(t.Date || ' ' || t.Time))) ) * 1440
    AS INTEGER
) AS elapsed_minutes
FROM transactions_1k AS t
JOIN gasstations AS g
    ON t.GasStationID = g.GasStationID
WHERE g.Country = 'CZE'
  AND t.Price > 1000;
```

**Assessment (CANDIDATE ROOT CAUSE):** The Gold calculation uses integer-second difference divided by 60, whereas agent uses floating julianday; investigate rounding near a whole-minute boundary before attributing failure.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q157"></a>
### Q157 — challenging · incorrect_result

**Question:** I'm putting together currency-specific pricing proposals and need a sense of typical quarterly fuel consumption. Among customers who have fuel consumption recorded in the second quarter of 2013 (April, May and June 2013), what is the average amount of fuel consumed over the whole quarter by an EUR-paying customer, and the same average for a CZK-paying customer? Please round both averages to two decimal places. By EUR-paying / CZK-paying I mean a customer whose account currency is EUR / CZK.

**Evidence:** EUR-paying / CZK-paying: a customer whose account currency is EUR / CZK

**Official Gold SQL** (full unless noted):

```sql
WITH q2 AS (SELECT CustomerID, SUM(Consumption) AS total FROM yearmonth WHERE Date BETWEEN '201304' AND '201306' GROUP BY CustomerID) SELECT ROUND(AVG(CASE WHEN c.Currency = 'EUR' THEN q2.total END), 2) AS eur_avg_quarter, ROUND(AVG(CASE WHEN c.Currency = 'CZK' THEN q2.total END), 2) AS czk_avg_quarter FROM customers c JOIN q2 ON q2.CustomerID = c.CustomerID
```

**Agent final SQL:**

```sql
SELECT c.Currency,
       ROUND(AVG(q.quarter_total), 2) AS avg_quarter_consumption
FROM (
    SELECT CustomerID, SUM(Consumption) AS quarter_total
    FROM yearmonth
    WHERE Date IN ('201304', '201305', '201306')
    GROUP BY CustomerID
) AS q
JOIN customers AS c ON c.CustomerID = q.CustomerID
WHERE c.Currency IN ('EUR', 'CZK')
GROUP BY c.Currency;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold outputs a single row with EUR and CZK average columns; agent outputs one row per Currency, changing result shape.

**Observed trace:** 6 model calls; 7 tool calls; 3 SQL calls (1 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT Date, Consumption FROM yearmonth ORDER BY Date LIMIT 12;` → {"columns":["Date","Consumption"],"rows":[["201112",29.24],["201112",60.14]],"truncated":false}  
Call 3: `SELECT c.Currency, COUNT(DISTINCT q.CustomerID) AS customers, ROUND(AVG(q.quarter_total), 2) AS avg_quarter_consumption FROM ( SELECT CustomerID, SUM(Consu` → {"columns":["Currency","customers","avg_quarter_consumption"],"rows":[["CZK",24959,44462.45],["EUR",1615,3627.03]],"truncated":false}


<a id="q162"></a>
### Q162 — challenging · incorrect_result

**Question:** For my February 2013 activity report: how many SME customers actually purchased gas in February 2013? Please give me just a single whole number - the count of SME customers who consumed gas during the calendar month of February 2013 (Feb 1-28, 2013).

**Evidence:** By "gas" I mean gasoline (motor fuel) purchases, not natural gas.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(DISTINCT T2.CustomerID) AS sme_gas_customers FROM customers AS T1 INNER JOIN yearmonth AS T2 ON T1.CustomerID = T2.CustomerID WHERE T1.Segment = 'SME' AND T2.Date = '201302' AND T2.Consumption > 0
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold uses yearmonth monthly Consumption>0 for SME customers in 201302; agent instead reconstructs gas transactions from transactions_1k and products.

**Observed trace:** 5 model calls; 12 tool calls; 7 SQL calls (0 tool errors, 2 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT DISTINCT Segment FROM customers` → {"columns":["Segment"],"rows":[["SME"],["LAM"]],"truncated":false}  
Call 7: `SELECT ProductID, Description FROM products ORDER BY ProductID` → {"columns":["ProductID","Description"],"rows":[[1,"Rucní zadání"],[2,"Nafta"]],"truncated":true}


## Database: `european_football_2`

<a id="q165"></a>
### Q165 — moderate · incorrect_result

**Question:** List the ten players taller than 180 cm with the highest mean recorded heading accuracy, highest first. Break mean ties by player API ID.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT p.player_name FROM Player AS p JOIN Player_Attributes AS a ON a.player_api_id = p.player_api_id WHERE p.height > 180 GROUP BY p.player_api_id, p.player_name ORDER BY AVG(a.heading_accuracy) DESC, p.player_api_id LIMIT 10
```

**Agent final SQL:**

```sql
SELECT
    p.player_api_id,
    p.player_name,
    AVG(pa.heading_accuracy) AS mean_heading_accuracy
FROM Player AS p
JOIN Player_Attributes AS pa
    ON pa.player_api_id = p.player_api_id
WHERE p.height > 180
GROUP BY p.player_api_id, p.player_name
ORDER BY mean_heading_accuracy DESC, p.player_api_id ASC
LIMIT 10;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold returns only ten player_name values; agent adds player_api_id and computed heading accuracy to the result.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT p.player_api_id, p.player_name, p.height, AVG(pa.heading_accuracy) AS mean_heading_accuracy FROM Player p JOIN Player_Attributes pa ON pa.player_api` → {"columns":["player_api_id","player_name","height","mean_heading_accuracy"],"rows":[[30699,"Michael Ballack",187,91.8],[33030,"Fernando Llorente",195,91.52380952380952]],"truncated":false}


<a id="q173"></a>
### Q173 — challenging · incorrect_result

**Question:** I'm sizing up how defensive-minded the young generation is. Among players born after 1990 (i.e., born in 1991 or later) who have a defensive work rate rating, what share are rated high? A player counts as rated high if they've been rated high at any point in their career. Give me that share as a percentage rounded to two decimal places - nothing else.

**Gold SQL preview:**

```sql
SELECT ROUND(100.0 * (SELECT COUNT(DISTINCT pa.player_api_id) FROM Player p JOIN Player_Attributes pa ON pa.player_api_id = p.player_api_id WHERE CAST(STRFTIME('%Y', p.birthday) AS INTEGER) > 1990 AND pa.defensive_work_rate = 'high') / (SELECT COUNT(DISTINCT pa.player_api_id) FROM Player p JOIN Player_Attributes pa ON pa.player_api_id = p.player_api_id WHERE CAST(STRFTIME('%Y', p.birthday) AS INTEGER) > 1990 AND pa.defensive_work_rate IN ('low','
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

```sql
WITH young AS (
    SELECT p.player_api_id
    FROM Player p
    WHERE p.birthday >= '1991-01-01'
),
rated AS (
    SELECT DISTINCT
        y.player_api_id,
        MAX(CASE WHEN LOWER(TRIM(pa.defensive_work_rate)) = 'high' THEN 1 ELSE 0 END)
            OVER (PARTITION BY y.player_api_id) AS ever_high
    FROM young y
    JOIN Player_Attributes pa
        ON pa.player_api_id = y.player_api_id
    WHERE pa.defensive_work_rate IS NOT NULL
)
SELECT
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold denominator includes valid low/medium/high grades; agent counts every non-NULL defensive_work_rate, which may include non-grade values.

**Observed trace:** 5 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q175"></a>
### Q175 — challenging · incorrect_result

**Question:** What is the average height in centimeters of players whose current defensive work rate grade is not medium? Use each player's most recent rating record to determine their current grade, and round the result to two decimal places. I just need that single number.

**Evidence:** Defensive work rate grades run low, medium and high.

**Official Gold SQL** (full unless noted):

```sql
WITH latest AS (SELECT player_api_id, defensive_work_rate, ROW_NUMBER() OVER (PARTITION BY player_api_id ORDER BY date DESC, id DESC) AS rn FROM Player_Attributes) SELECT ROUND(AVG(p.height), 2) AS average_height FROM latest l JOIN Player p ON p.player_api_id = l.player_api_id WHERE l.rn = 1 AND l.defensive_work_rate IN ('low', 'high')
```

**Agent final SQL:**

```sql
SELECT ROUND(AVG(p.height), 2) AS average_height_cm
FROM Player AS p
JOIN (
    SELECT player_api_id, defensive_work_rate,
           ROW_NUMBER() OVER (
               PARTITION BY player_api_id
               ORDER BY date DESC, id DESC
           ) AS rn
    FROM Player_Attributes
) AS latest
    ON latest.player_api_id = p.player_api_id
WHERE latest.rn = 1
  AND LOWER(TRIM(latest.defensive_work_rate)) <> 'medium';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold allows only latest grade low/high; agent uses <> 'medium', which also admits other non-medium values.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH ranked AS ( SELECT player_api_id, defensive_work_rate, ROW_NUMBER() OVER (PARTITION BY player_api_id ORDER BY date DESC, id DESC) AS rn FROM Player_At` → {"columns":["average_height_cm"],"rows":[[180.93]],"truncated":false}


<a id="q177"></a>
### Q177 — challenging · incorrect_result

**Question:** I want to gauge how tall the current medium-defensive-work players from the 1990-1995 birth cohort are. Please find the average height, in centimetres, of players born from 1990 through 1995 inclusive whose defensive work rating is medium, and round the average to two decimals. A player's rating is the grade on their most recent record that carries a grade.

**Gold SQL preview:**

```sql
WITH latest_grade AS (SELECT player_api_id, defensive_work_rate, ROW_NUMBER() OVER (PARTITION BY player_api_id ORDER BY date DESC, id DESC) AS rn FROM Player_Attributes WHERE defensive_work_rate IN ('low', 'medium', 'high')) SELECT ROUND(AVG(p.height), 2) AS average_height FROM Player p JOIN latest_grade g ON g.player_api_id = p.player_api_id AND g.rn = 1 WHERE SUBSTR(p.birthday, 1, 4) BETWEEN '1990' AND '1995' AND g.defensive_work_rate = 'medium
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

```sql
WITH latest AS (
    SELECT
        player_api_id,
        defensive_work_rate,
        ROW_NUMBER() OVER (
            PARTITION BY player_api_id
            ORDER BY date DESC, id DESC
        ) AS rn
    FROM Player_Attributes
    WHERE defensive_work_rate IS NOT NULL
)
SELECT ROUND(AVG(p.height), 2) AS average_height_cm
FROM Player AS p
JOIN latest AS l
    ON l.player_api_id = p.player_api_id
   AND l.rn = 1
WHERE l.defensive_work_rate = 'me
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Reference chooses latest record among valid low/medium/high defensive grades; agent ranks all non-NULL entries, potentially selecting an invalid value.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q189"></a>
### Q189 — challenging · incorrect_result

**Question:** What percentage of left-footed players currently has a low attacking work rate? Use each player's most recent attribute record. Only count left-footed players whose current record includes an attacking work rate rating - those without one should be left out of the share. Give me a single percentage, rounded to one decimal place.

**Evidence:** Attacking work rate: how much effort a player puts into attacking plays, rated low, medium or high.

**Official Gold SQL** (full unless noted):

```sql
WITH latest AS (SELECT player_api_id, MAX(date) AS d FROM Player_Attributes GROUP BY player_api_id) SELECT ROUND(100.0 * COUNT(DISTINCT CASE WHEN pa.attacking_work_rate = 'low' THEN pa.player_api_id END) / COUNT(DISTINCT CASE WHEN pa.attacking_work_rate IN ('low','medium','high') THEN pa.player_api_id END), 1) AS pct FROM Player_Attributes pa JOIN latest l ON pa.player_api_id = l.player_api_id AND pa.date = l.d WHERE pa.preferred_foot = 'left'
```

**Agent final SQL:**

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
),
eligible AS (
    SELECT preferred_foot, attacking_work_rate
    FROM ranked
    WHERE rn = 1
      AND preferred_foot = 'left'
      AND attacking_work_rate IS NOT NULL
      AND TRIM(attacking_work_rate) <> ''
)
SELECT ROUND(
    100.0 * SUM(CASE WHEN LOWER(attacking_work_rate) = 'low' THEN 1 ELSE 0 END) / COUNT(*),
    1
) AS percentage
FROM eligible;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold's denominator is current records with explicit low/medium/high work rate; agent accepts all nonempty rated values.

**Observed trace:** 4 model calls; 3 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH ranked AS ( SELECT player_api_id, preferred_foot, attacking_work_rate, ROW_NUMBER() OVER (PARTITION BY player_api_id ORDER BY date DESC, id DESC) AS r` → {"columns":["percentage"],"rows":[[3.7]],"truncated":false}


<a id="q191"></a>
### Q191 — challenging · incorrect_result

**Question:** How many players had a jumping score of 80 or higher in the player fitness assessments made between 22 February 2007 and 30 August 2007, with both of those dates included in the period? For clarity, the jumping score is the player's jumping assessment on a 1-100 scale.

**Gold SQL preview:**

```sql
SELECT COUNT(DISTINCT player_api_id) AS player_count FROM Player_Attributes WHERE jumping >= 80 AND date(date) BETWEEN '2007-02-22' AND '2007-08-30'
```

**Agent SQL preview:**

```sql
SELECT COUNT(DISTINCT player_api_id) AS player_count
FROM Player_Attributes
WHERE date >= '2007-02-22'
  AND date <= '2007-08-30'
  AND jumping >= 80;
```

**Assessment (CANDIDATE ROOT CAUSE):** Potential date-boundary mismatch: the agent compares timestamp text to the end date string, while Gold applies date(date) to include the full last day.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

## Database: `financial`

<a id="q201"></a>
### Q201 — challenging · incorrect_result

**Question:** For loans dated in 1996 and 1997 across accounts owned by male clients, what was the percentage growth in total loan amount from 1996 to 1997?

**Gold SQL preview:**

```sql
SELECT CAST((SUM(CASE WHEN STRFTIME('%Y', T1.date) = '1997' THEN T1.amount ELSE 0 END) - SUM(CASE WHEN STRFTIME('%Y', T1.date) = '1996' THEN T1.amount ELSE 0 END)) AS REAL) * 100 / SUM(CASE WHEN STRFTIME('%Y', T1.date) = '1996' THEN T1.amount ELSE 0 END) FROM loan AS T1 INNER JOIN account AS T2 ON T1.account_id = T2.account_id INNER JOIN disp AS T3 ON T3.account_id = T2.account_id INNER JOIN client AS T4 ON T4.client_id = T3.client_id WHERE T4.ge
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

```sql
SELECT
  100.0 * (
    SUM(CASE WHEN strftime('%Y', date) = '1997' THEN amount ELSE 0 END) -
    SUM(CASE WHEN strftime('%Y', date) = '1996' THEN amount ELSE 0 END)
  ) /
  SUM(CASE WHEN strftime('%Y', date) = '1996' THEN amount ELSE 0 END) AS percentage_growth
FROM loan
WHERE strftime('%Y', date) IN ('1996', '1997')
  AND EXISTS (
    SELECT 1
    FROM disp
    JOIN client USING (client_id)
    WHERE disp.account_id = loan.account_id
      AND c
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** The Gold joins disp with type='OWNER'; agent EXISTS checks any male client linked to the account, potentially changing ownership semantics.

**Observed trace:** 5 model calls; 7 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q205"></a>
### Q205 — challenging · incorrect_result

**Question:** Among the bank's five most populous districts (the five with the largest numbers of inhabitants), which carries the heaviest active-lending burden relative to the account base it serves? For each of those five districts, please give me the district name and the average active loan per account, rounded to the nearest whole koruna. An active loan is a running loan contract with status 'C' (repaid OK so far) or status 'D' (client in debt). The average should be taken over every account held in the district, not just accounts with loans, and accounts and their loans count toward the district of the branch that holds the account, not the client's district. If several districts tie for the highest average, list them all.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH populous AS (SELECT district_id FROM district ORDER BY CAST(A4 AS INTEGER) DESC LIMIT 5), per_district AS (SELECT d.A2 AS district_name, SUM(CASE WHEN l.status IN ('C','D') THEN l.amount ELSE 0 END) * 1.0 / COUNT(a.account_id) AS raw_avg FROM district d JOIN account a ON a.district_id = d.district_id LEFT JOIN loan l ON l.account_id = a.account_id WHERE d.district_id IN (SELECT district_id FROM populous) GROUP BY d.district_id, d.A2) SELECT district_name, ROUND(raw_avg, 0) AS avg_active_loan_per_account FROM per_district ORDER BY raw_avg DESC, district_name
```

**Agent final SQL:**

```sql
WITH top_districts AS (
  SELECT district_id, A2 AS district_name
  FROM district
  ORDER BY CAST(A4 AS INTEGER) DESC
  LIMIT 5
),
district_averages AS (
  SELECT
    td.district_id,
    td.district_name,
    ROUND(
      COALESCE(SUM(CASE WHEN l.status IN ('C', 'D') THEN l.amount ELSE 0 END), 0) * 1.0
      / COUNT(a.account_id)
    ) AS average_active_loan_per_account
  FROM top_districts td
  JOIN account a ON a.district_id = td.district_id
  LEFT JOIN loan l ON l.account_id = a.account_id
  GROUP BY td.district_id, td.district_name
)
SELECT district_name, average_active_loan_per_account
FROM district_averages
WHERE average_active_loan_per_account = (
  SELECT MAX(average_active_loan_per_account)
  FROM district_averages
)
ORDER BY district_name;
```

**Assessment (CANDIDATE ROOT CAUSE):** The reference returns all five most populous districts with their averages; agent filters output to only those with the maximum average.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH top_districts AS ( SELECT d.district_id, d.A2 AS district_name, d.A4 AS inhabitants FROM district d ORDER BY CAST(d.A4 AS INTEGER) DESC LIMIT 5 ), per` → {"columns":["district_name","avg_active_loan"],"rows":[["Brno - mesto",27752]],"truncated":false}


<a id="q213"></a>
### Q213 — challenging · incorrect_result

**Question:** I'm profiling our gold-card customers for a regional campaign, split by gender. For women first, then men, look at gold-card holders whose card's account has an average balance over 1,000. Among the branch districts holding those accounts, keep only the districts with over 100,000 inhabitants. For each gender, tell me: the number of those districts; which of them has the most inhabitants, with its inhabitants figure - if two districts tie, list both, one row per district; the average salary across those districts, rounded to two decimals; and the average ratio of urban inhabitants across those districts, rounded to two decimals. Nothing else. Please note: 'over' means strictly greater than, and an account's average balance is the mean of its balances after each transaction.

**Gold SQL preview:**

```sql
WITH gold_holder AS (SELECT d.account_id, cl.gender FROM card c JOIN disp d ON c.disp_id = d.disp_id JOIN client cl ON d.client_id = cl.client_id WHERE c.type = 'gold' AND d.type = 'OWNER'), acct_bal AS (SELECT account_id, AVG(balance) AS avg_balance FROM trans GROUP BY account_id), holder_district AS (SELECT DISTINCT gh.gender, a.district_id FROM gold_holder gh JOIN account a ON gh.account_id = a.account_id JOIN acct_bal ab ON ab.account_id = a.
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

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
        ON c.client_id
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Output mismatch: the reference reports district name plus requested gender and metrics; agent reports district_id and replaces F/M values with women/men.

**Observed trace:** 4 model calls; 8 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q217"></a>
### Q217 — challenging · incorrect_result

**Question:** I'm reviewing our presence in central Bohemia. Please tell me: the names of the three most populous districts of central Bohemia (largest by inhabitants), the number of crimes committed in 1996 in each of them, the average 1996 crime count across those three districts, the average 1996 crime count across all districts in the country, and the difference between the three-district average and the overall average (three-district average minus overall average). Rank districts by inhabitants, breaking ties by district name alphabetically (ignoring accents). Round all averages and the difference to 2 decimal places. The overall average should cover every district in the country, whether or not it has any accounts.

**Evidence:** Central Bohemia is the region of the Czech Republic surrounding Prague.

**Official Gold SQL** (full unless noted):

```sql
WITH ranked AS ( SELECT d.A2 AS district_name, CAST(d.A4 AS INTEGER) AS inhabitants, d.A16 AS crimes_1996 FROM district d WHERE d.A3 = 'central Bohemia' ORDER BY CAST(d.A4 AS INTEGER) DESC, d.A2 LIMIT 3 ) SELECT r.district_name, r.crimes_1996, ROUND((SELECT AVG(crimes_1996) FROM ranked), 2) AS avg_crimes_top3_1996, ROUND((SELECT AVG(A16) FROM district), 2) AS avg_crimes_all_districts_1996, ROUND((SELECT AVG(crimes_1996) FROM ranked) - (SELECT AVG(A16) FROM district), 2) AS difference FROM ranked r ORDER BY r.inhabitants DESC, r.district_name
```

**Agent final SQL:**

```sql
WITH district_crimes AS (
    SELECT
        d.district_id,
        d.A2 AS district_name,
        d.A3 AS region,
        CAST(d.A4 AS INTEGER) AS inhabitants,
        COUNT(t.trans_id) AS crimes_1996
    FROM district AS d
    LEFT JOIN account AS a ON a.district_id = d.district_id
    LEFT JOIN trans AS t
        ON t.account_id = a.account_id
       AND t.date >= '1996-01-01'
       AND t.date < '1997-01-01'
    GROUP BY d.district_id, d.A2, d.A3, d.A4
),
ranked_central AS (
    SELECT
        district_name,
        inhabitants,
        crimes_1996,
        ROW_NUMBER() OVER (
            ORDER BY inhabitants DESC, lower(district_name) ASC
        ) AS rank
    FROM district_crimes
    WHERE region = 'central Bohemia'
),
averages AS (
    SELECT
        (SELECT AVG(crimes_1996)
         FROM ranked_central
         WHERE rank <= 3) AS top_three_average,
        (SELECT AVG(crimes_1996)
         FROM district_crimes) AS overall_average
)
SELECT
    MAX(CASE WHEN r.rank = 1 THEN r.district_name END) AS first_district,
    MAX(CASE WHEN r.rank = 1 THEN r.crimes_1996 END) AS first_district_crimes_1996,
    MAX(CASE WHEN r.rank = 2 THEN r.district_name END) AS second_district,
    MAX(CASE WHEN r.rank = 2 THEN r.crimes_1996 END) AS second_district_crimes_1996,
    MAX(CASE WHEN r.rank = 3 THEN r.district_name END) AS third_district,
    MAX(CASE WHEN r.rank = 3 THEN r.crimes_1996 END) AS third_district_crimes_1996,
    ROUND(a.top_three_average, 2) AS top_three_average_crimes_1996,
    ROUND(a.overall_average, 2) AS overall_average_crimes_1996,
    ROUND(a.top_three_average - a.overall_average, 2) AS average_difference
FROM ranked_central AS r
CROSS JOIN averages AS a
WHERE r.rank <= 3;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold's 1996 crime count comes from district.A16; agent counts banking trans records as if they were crimes.

**Observed trace:** 10 model calls; 11 tool calls; 7 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT * FROM district LIMIT 3` → {"columns":["district_id","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12","A13","A14","A15","A16"],"rows":[[1,"Hl.m. Praha","Prague","1204953","0","0","0",1,1,100,12541,0.2,0.43,167,85677,99107],[2,"Benesov","central Bohemia","88884","80","26","6",2,5,46.7,8507,1.6,1.85,132,2159,2674]],"tr  
Call 7: `SELECT d.A2, d.A3, CAST(d.A4 AS INTEGER) inhabitants, COUNT(t.trans_id) AS crimes_1996 FROM district d LEFT JOIN account a ON a.district_id=d.district_id L` → {"columns":["A2","A3","inhabitants","crimes_1996"],"rows":[["Kladno","central Bohemia",149893,2175],["Mlada Boleslav","central Bohemia",112065,2482]],"truncated":false}


<a id="q224"></a>
### Q224 — challenging · incorrect_result

**Question:** For a regional risk review, I need to look at our largest 24-month loans. Please find the ten loans with the largest approved amount among loans with a 24-month duration on accounts that have weekly statement issuance. For each of these ten loans, give me: the district of the branch servicing the account, the approved amount, the approval date, and the account balance at the end of the day the loan was approved. Two rules: if two loans have the same approved amount, the one approved earlier counts as larger; and if several transactions share that last day, the one with the higher transaction id counts as the later one. List the results from the largest approved amount down.

**Evidence:** Weekly statement issuance means statement frequency is 'POPLATEK TYDNE'; loan duration is stated in months.

**Official Gold SQL** (full unless noted):

```sql
WITH top_loans AS (SELECT l.loan_id, l.account_id, l.amount, l.date AS loan_date, d.A2 AS district_name FROM loan l JOIN account a ON a.account_id = l.account_id JOIN district d ON d.district_id = a.district_id WHERE l.duration = 24 AND a.frequency = 'POPLATEK TYDNE' ORDER BY l.amount DESC, l.date ASC, l.loan_id ASC LIMIT 10) SELECT district_name, amount AS approved_amount, loan_date AS approval_date, (SELECT t.balance FROM trans t WHERE t.account_id = top_loans.account_id AND t.date <= top_loans.loan_date ORDER BY t.date DESC, t.trans_id DESC LIMIT 1) AS balance_at_approval FROM top_loans ORDER BY approved_amount DESC
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** As-of balance: Gold chooses latest transaction on or before loan approval date; agent selects only transactions on the exact approval date.

**Observed trace:** 5 model calls; 7 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT l.loan_id, d.A2 AS district, l.amount AS approved_amount, l.date AS approval_date, t.balance AS approval_day_end_balance FROM loan l JOIN account a ` → {"columns":["loan_id","district","approved_amount","approval_date","approval_day_end_balance"],"rows":[[5176,"Strakonice",192552,"1994-11-12",14203],[6589,"Prachatice",189696,"1996-01-01",null]],"truncated":false}  
Call 2: `SELECT l.loan_id,l.account_id,l.date,l.amount, (SELECT COUNT(*) FROM trans t WHERE t.account_id=l.account_id AND date(t.date)=date(l.date)) AS same_day_cou` → {"columns":["loan_id","account_id","date","amount","same_day_count","next_trans_day"],"rows":[[5176,1106,"1994-11-12",192552,1,"1994-11-14"],[6589,7815,"1996-01-01",189696,0,"1996-01-03"]],"truncated":false}


<a id="q227"></a>
### Q227 — challenging · incorrect_result

**Question:** The loan of 98832 approved on January 3rd, 1996 has one applicant account. For that account, list every counterparty it had paid before January 3rd, 1996. A counterparty means a specific account number at a specific bank, so give me one row per bank code and account number combination. For each counterparty I need the bank code, the account number, the number of outgoing payments made to them, and the total amount paid to them. Count only outgoing payments (VYDAJ, i.e. debits) made before January 3rd, 1996, and sort the counterparties by total amount paid, largest first.

**Gold SQL preview:**

```sql
SELECT t.bank AS bank_code, t.account AS counterparty_account, COUNT(*) AS payment_count, SUM(t.amount) AS total_paid FROM trans t WHERE t.account_id = (SELECT l.account_id FROM loan l WHERE l.date = '1996-01-03' AND l.amount = 98832) AND t.type = 'VYDAJ' AND t.date < '1996-01-03' AND t.account > 0 GROUP BY t.bank, t.account ORDER BY total_paid DESC
```

**Agent SQL preview:**

```sql
SELECT
    t.bank AS bank_code,
    t.account AS account_number,
    COUNT(*) AS outgoing_payment_count,
    SUM(t.amount) AS total_amount_paid
FROM loan AS l
JOIN disp AS d
    ON d.account_id = l.account_id
JOIN trans AS t
    ON t.account_id = d.account_id
WHERE l.loan_id = 5999
  AND l.date = '1996-01-03'
  AND d.type = 'OWNER'
  AND t.type = 'VYDAJ'
  AND t.date < '1996-01-03'
GROUP BY t.bank, t.account
ORDER BY total_amount_paid DESC;
```

**Assessment (CANDIDATE ROOT CAUSE):** Reference identifies loan by date and amount; agent hardcodes loan_id and adds OWNER join, without the Gold t.account>0 condition.

**Observed trace:** 10 model calls; 12 tool calls; 7 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q230"></a>
### Q230 — challenging · incorrect_result

**Question:** I need to profile our three largest loans held by female clients. Please report for each of these loans: the client id, loan amount, duration in months, total payments, interest paid, loan status, the district and region of the branch where the loan's account is held, the account's transaction count and total deposits, an income category, the number of loans the bank has granted in that region, the average of the average salaries of that region's districts, and the client's completed age on 2026-10-09. A few notes: the three largest loans are the three highest approved loan amounts, and if amounts tie, include all tied loans. Total payments is the monthly payment times the duration, and interest paid is total payments minus the approved amount; round money figures to two decimals. The income category is High Income if total deposits exceed twice the loan amount, Medium Income if they exceed the loan amount, and Low Income otherwise. Loans in a region counts every loan the bank has granted in that region for all clients, not only female clients. The region's average salary is the average of the average salaries of the districts in that region, rounded to two decimals. For the age, use the completed age on 2026-10-09, subtracting one if the birthday hasn't occurred by that date.

**Evidence:** Female means client gender = 'F'. Deposits are transactions recorded as PRIJEM (credits to the account). District average salary is the district's average salary figure.

**Official Gold SQL** (full unless noted):

```sql
WITH female_loans AS (SELECT c.client_id, c.birth_date, d.account_id, l.loan_id, l.amount, l.duration, l.payments, l.status, a.district_id, RANK() OVER (ORDER BY l.amount DESC) AS rnk FROM client c JOIN disp d ON c.client_id = d.client_id AND d.type = 'OWNER' JOIN loan l ON d.account_id = l.account_id JOIN account a ON l.account_id = a.account_id WHERE c.gender = 'F'), region_loans AS (SELECT da.A3 AS region, COUNT(*) AS loans_in_region FROM loan l JOIN account a ON l.account_id = a.account_id JOIN district da ON a.district_id = da.district_id GROUP BY da.A3), region_salary AS (SELECT A3 AS region, ROUND(AVG(A11), 2) AS avg_district_salary FROM district GROUP BY A3), acct_trans AS (SELECT account_id, COUNT(*) AS transaction_count, SUM(CASE WHEN type = 'PRIJEM' THEN amount ELSE 0 END) AS total_credits FROM trans GROUP BY account_id) SELECT fl.client_id, fl.amount AS loan_amount, fl.duration AS loan_duration_months, ROUND(fl.payments * fl.duration, 2) AS total_payments, ROUND(fl.payments * fl.duration - fl.amount, 2) AS interest_paid, fl.status AS loan_status, di.A2 AS branch_district, di.A3 AS region, at.transaction_count, at.total_credits AS total_deposits, CASE WHEN at.total_credits > fl.amount * 2 THEN 'High Income' WHEN at.total_credits > fl.amount THEN 'Medium Income' ELSE 'Low Income' END AS income_category, rl.loans_in_region, rs.avg_district_salary AS region_avg_district_salary, STRFTIME('%Y', '2026-10-09') - STRFTIME('%Y', fl.birth_date) - CASE WHEN STRFTIME('%m-%d', '2026-10-09') < STRFTIME('%m-%d', fl.birth_date) THEN 1 ELSE 0 END AS client_age FROM female_loans fl JOIN district di ON fl.district_id = di.district_id JOIN region_loans rl ON di.A3 = rl.region JOIN region_salary rs ON di.A3 = rs.region LEFT JOIN acct_trans at ON fl.account_id = at.account_id WHERE fl.rnk <= 3 ORDER BY fl.amount DESC
```

**Agent final SQL:**

```sql
WITH top_amount AS (
    SELECT amount
    FROM loan
    ORDER BY amount DESC
    LIMIT 3
),
deposits AS (
    SELECT
        account_id,
        COUNT(*) AS transaction_count,
        SUM(CASE WHEN type = 'PRIJEM' THEN amount ELSE 0 END) AS total_deposits
    FROM trans
    GROUP BY account_id
),
regions AS (
    SELECT A3 AS region, ROUND(AVG(A11), 2) AS avg_district_salary
    FROM district
    GROUP BY A3
),
loans_by_region AS (
    SELECT d.A3 AS region, COUNT(*) AS regional_loan_count
    FROM loan l
    JOIN account a ON a.account_id = l.account_id
    JOIN district d ON d.district_id = a.district_id
    GROUP BY d.A3
)
SELECT
    c.client_id,
    l.amount AS loan_amount,
    l.duration AS duration_months,
    ROUND(l.payments * l.duration, 2) AS total_payments,
    ROUND(l.payments * l.duration - l.amount, 2) AS interest_paid,
    l.status AS loan_status,
    branch.A2 AS branch_district,
    branch.A3 AS branch_region,
    COALESCE(dep.transaction_count, 0) AS transaction_count,
    ROUND(COALESCE(dep.total_deposits, 0), 2) AS total_deposits,
    CASE
        WHEN COALESCE(dep.total_deposits, 0) > 2 * l.amount THEN 'High Income'
        WHEN COALESCE(dep.total_deposits, 0) > l.amount THEN 'Medium Income'
        ELSE 'Low Income'
    END AS income_category,
    lbr.regional_loan_count,
    reg.avg_district_salary,
    CAST(strftime('%Y', '2026-10-09') AS INTEGER)
      - CAST(strftime('%Y', c.birth_date) AS INTEGER)
      - CASE WHEN strftime('%m-%d', c.birth_date) > '10-09' THEN 1 ELSE 0 END AS age
FROM loan l
JOIN account a ON a.account_id = l.account_id
JOIN disp dp ON dp.account_id = a.account_id AND dp.type = 'OWNER'
JOIN client c ON c.client_id = dp.client_id
JOIN district branch ON branch.district_id = a.district_id
JOIN deposits dep ON dep.account_id = a.account_id
JOIN regions reg ON reg.region = branch.A3
JOIN loans_by_region lbr ON lbr.region = branch.A3
WHERE c.gender = 'F'
  AND l.amount >= (SELECT MIN(amount) FROM top_amount);
```

**Assessment (CANDIDATE ROOT CAUSE):** Reference ranks the largest loans *among female owners* and includes amount ties; agent selects top-three loan amounts across all loans before applying female filter.

**Observed trace:** 8 model calls; 14 tool calls; 7 SQL calls (1 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT A2,A3,A11,A12,A13 FROM district LIMIT 5` → {"columns":["A2","A3","A11","A12","A13"],"rows":[["Hl.m. Praha","Prague",12541,0.2,0.43],["Benesov","central Bohemia",8507,1.6,1.85]],"truncated":false}  
Call 7: `WITH top_amount AS (SELECT amount FROM loan ORDER BY amount DESC LIMIT 3), deposits AS (SELECT account_id, COUNT(*) AS transaction_count, SUM(CASE WHEN typ` → {"columns":["client_id","loan_amount","duration_months","total_payments","interest_paid","loan_status","branch_district","branch_region","transaction_count","total_deposits","income_category","regional_loan_count","avg_district_salary","age"],"rows":[[10997,566640,60,566640,0,"C","Hl.m. Praha","Prag


<a id="q235"></a>
### Q235 — challenging · incorrect_result · Reference QA watchlist

**Question:** I'd like a district-by-district picture of where our classic-card-holding account owners send money outside the bank. For every district, give me: the district name, the number of clients who own an account and hold a classic credit card, the number of external accounts at other banks those clients paid through outgoing payments, and the total amount of those outgoing payments. A district means the district of the branch where the owned account is held — not the client's home district — and each client and every outgoing payment from the account they own counts toward that account's branch district. Include every district, even ones with no such clients or no such outgoing payments (show zeros). Use the whole recorded payment history. Order by total amount paid from highest to lowest, and alphabetically by district name when totals tie. Don't round the totals.

**Evidence:** An account owner is the client recorded as 'OWNER' on the account. An outgoing payment is a transaction recorded with type 'VYDAJ' (money paid out of the account). An external account is an account held at another bank to which the account holder sends money; the receiving bank together with the receiving account number identifies it.

**Official Gold SQL** (full unless noted):

```sql
WITH holders AS ( SELECT dp.client_id, dp.account_id, a.district_id FROM card c JOIN disp dp ON dp.disp_id = c.disp_id AND dp.type = 'OWNER' JOIN account a ON a.account_id = dp.account_id WHERE c.type = 'classic' ) SELECT d.A2 AS district, COUNT(DISTINCT h.client_id) AS classic_card_holders, COUNT(DISTINCT t.account) AS external_accounts_paid, COALESCE(SUM(t.amount), 0) AS total_amount_paid FROM district d LEFT JOIN holders h ON h.district_id = d.district_id LEFT JOIN trans t ON t.account_id = h.account_id AND t.type = 'VYDAJ' AND t.account > 0 GROUP BY d.district_id, d.A2 ORDER BY total_amount_paid DESC, district ASC
```

**Agent final SQL:**

```sql
WITH eligible_accounts AS (
    SELECT
        a.account_id,
        a.district_id,
        COUNT(DISTINCT d.client_id) AS classic_card_client_count
    FROM account AS a
    JOIN disp AS d
        ON d.account_id = a.account_id
       AND d.type = 'OWNER'
    JOIN card AS c
        ON c.disp_id = d.disp_id
       AND c.type = 'classic'
    GROUP BY a.account_id, a.district_id
),
district_totals AS (
    SELECT
        ea.district_id,
        SUM(ea.classic_card_client_count) AS client_count,
        COUNT(DISTINCT CASE
            WHEN t.type = 'VYDAJ'
             AND t.bank IS NOT NULL
             AND t.account IS NOT NULL
            THEN t.bank || ':' || t.account
        END) AS external_account_count,
        SUM(CASE WHEN t.type = 'VYDAJ' THEN t.amount ELSE 0 END) AS outgoing_payment_total
    FROM eligible_accounts AS ea
    LEFT JOIN trans AS t
        ON t.account_id = ea.account_id
    GROUP BY ea.district_id
)
SELECT
    d.A2 AS district_name,
    COALESCE(dt.client_count, 0) AS client_count,
    COALESCE(dt.external_account_count, 0) AS external_account_count,
    COALESCE(dt.outgoing_payment_total, 0) AS outgoing_payment_total
FROM district AS d
LEFT JOIN district_totals AS dt
    ON dt.district_id = d.district_id
ORDER BY outgoing_payment_total DESC, district_name ASC;
```

**Assessment (REFERENCE QA CANDIDATE):** Reference QA candidate: question defines counterparty as bank code + account number, but Gold counts DISTINCT t.account only. Do not change EX without data-level examination.

**Observed trace:** 5 model calls; 8 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT A2 FROM district LIMIT 1` → {"columns":["A2"],"rows":[["Hl.m. Praha"]],"truncated":false}


**Reference review discipline:** Do not change the Gold answer or EX based on this observation alone. Re-execute candidate interpretations on the pinned database and record exact result differences before filing an annotation issue.

## Database: `formula_1`

<a id="q242"></a>
### Q242 — moderate · incorrect_result

**Question:** Which driver won the most recorded races? Give their first name, last name, nationality, and highest recorded driver-standings points total.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH wins AS (SELECT driverId, COUNT(*) AS win_count FROM results WHERE positionOrder = 1 GROUP BY driverId), winner AS (SELECT driverId FROM wins ORDER BY win_count DESC, driverId LIMIT 1) SELECT d.forename, d.surname, d.nationality, (SELECT MAX(s.points) FROM driverStandings AS s WHERE s.driverId = d.driverId) FROM winner AS w JOIN drivers AS d ON d.driverId = w.driverId
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold identifies winners using positionOrder=1 and outputs four requested fields; agent filters position=1 and adds race_wins to output.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT d.forename, d.surname, d.nationality, COUNT(*) AS race_wins, (SELECT MAX(ds.points) FROM driverStandings ds WHERE ds.driverId = d.driverId) AS highe` → {"columns":["forename","surname","nationality","race_wins","highest_standings_points"],"rows":[["Michael","Schumacher","German",87,148]],"truncated":false}


<a id="q245"></a>
### Q245 — challenging · incorrect_result

**Question:** For each year before 1975 with recorded winner times, what was the mean race winner elapsed time in seconds? Round the exact mean to two decimal places; if it is exactly halfway, round away from zero. Order by year.

**Gold SQL preview:**

```sql
SELECT r.year, FLOOR((SUM(x.milliseconds) + 5 * COUNT(*)) / (10 * COUNT(*))) / 100.0 FROM results AS x JOIN races AS r ON r.raceId = x.raceId WHERE r.year < 1975 AND x.positionOrder = 1 AND x.milliseconds IS NOT NULL GROUP BY r.year ORDER BY r.year
```

**Agent SQL preview:**

```sql
SELECT
    r.year,
    printf('%.2f', AVG(res.milliseconds) / 1000.0) AS mean_elapsed_seconds
FROM races AS r
JOIN results AS res
    ON res.raceId = r.raceId
WHERE r.year < 1975
  AND res.positionOrder = 1
  AND res.milliseconds IS NOT NULL
GROUP BY r.year
ORDER BY r.year;
```

**Assessment (CANDIDATE ROOT CAUSE):** Agent printf('%.2f', ...) returns text whereas Gold applies a specified rounding arithmetic; evaluate exact numeric and halfway-rounding semantics.

**Observed trace:** 8 model calls; 8 tool calls; 5 SQL calls (0 tool errors, 3 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q251"></a>
### Q251 — challenging · incorrect_result

**Question:** I'm comparing pit stop activity at the newer Grand Prix weekends. Among the 2017 races that were not hosted in 2000, what was the average number of pit stops per race? Please take the average of all of those races and round it to two decimal places.

**Evidence:** Hosted in 2000 means the race was on the 2000 race calendar.

**Official Gold SQL** (full unless noted):

```sql
WITH cohort AS (SELECT raceId FROM races WHERE year = 2017 AND name NOT IN (SELECT name FROM races WHERE year = 2000)) SELECT ROUND(1.0 * (SELECT COUNT(*) FROM pitStops WHERE raceId IN (SELECT raceId FROM cohort)) / (SELECT COUNT(*) FROM cohort), 2) AS avg_pit_stops_per_race
```

**Agent final SQL:**

```sql
WITH calendar_2000 AS (
    SELECT raceId
    FROM races
    WHERE year = 2000
),
races_2017_not_2000 AS (
    SELECT raceId
    FROM races
    WHERE year = 2017
      AND raceId NOT IN (SELECT raceId FROM calendar_2000)
),
per_race AS (
    SELECT r.raceId, COUNT(p.stop) AS pit_stop_count
    FROM races_2017_not_2000 AS r
    LEFT JOIN pitStops AS p ON p.raceId = r.raceId
    GROUP BY r.raceId
)
SELECT ROUND(AVG(pit_stop_count), 2) AS average_pit_stops_per_race
FROM per_race;
```

**Assessment (CANDIDATE ROOT CAUSE):** Compare 2017 race names with 2000 race names; agent compares year-specific raceIds, which do not identify the same Grand Prix across years.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH calendar_2000 AS (SELECT raceId FROM races WHERE year = 2000), races_2017_not_2000 AS (SELECT raceId FROM races WHERE year = 2017 AND raceId NOT IN (S` → {"columns":["average_pit_stops_per_race"],"rows":[[25.95]],"truncated":false}


<a id="q255"></a>
### Q255 — challenging · incorrect_result · Reference QA watchlist

**Question:** Who set the fastest time in Q1 at the 1995 Japanese Grand Prix, and what was that time? Please give me the driver's forename and surname, and the Q1 time. By '1995 Japanese Grand Prix' I mean the race of the 1995 season named 'Japanese Grand Prix'. If two drivers tied for the fastest Q1 time, list them all.

**Evidence:** Q1: the time a driver set in the first qualifying session.

**Official Gold SQL** (full unless noted):

```sql
SELECT d.forename, d.surname, q.q1 FROM qualifying AS q JOIN drivers AS d ON d.driverId = q.driverId JOIN races AS r ON r.raceId = q.raceId WHERE r.year = 1995 AND r.name = 'Japanese Grand Prix' AND q.q1 IS NOT NULL ORDER BY CAST(SUBSTR(q.q1, 1, INSTR(q.q1, ':') - 1) AS INTEGER) ASC, CAST(SUBSTR(q.q1, INSTR(q.q1, ':') + 1) AS REAL) ASC LIMIT 1;
```

**Agent final SQL:**

```sql
SELECT d.forename, d.surname, q.q1
FROM races r
JOIN qualifying q ON q.raceId = r.raceId
JOIN drivers d ON d.driverId = q.driverId
WHERE r.year = 1995
  AND r.name = 'Japanese Grand Prix'
  AND q.q1 = (
      SELECT MIN(q2.q1)
      FROM qualifying q2
      WHERE q2.raceId = r.raceId
        AND q2.q1 IS NOT NULL
  );
```

**Assessment (REFERENCE QA CANDIDATE):** Reference QA candidate: question says to include all tied fastest Q1 drivers, while Gold LIMIT 1. Also compare textual MIN(q1) with numeric time ordering.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT d.forename, d.surname, q.q1 FROM races r JOIN qualifying q ON q.raceId = r.raceId JOIN drivers d ON d.driverId = q.driverId WHERE r.year = 1995 AND ` → {"columns":["forename","surname","q1"],"rows":[["Mark","Blundell","16:42.640"]],"truncated":false}


**Reference review discipline:** Do not change the Gold answer or EX based on this observation alone. Re-execute candidate interpretations on the pinned database and record exact result differences before filing an annotation issue.

<a id="q259"></a>
### Q259 — challenging · incorrect_result

**Question:** Who won the 2017 Azerbaijan Grand Prix? I'd like the winner's forename and surname, the local clock time (hours:minutes:seconds.milliseconds) at the circuit at which he crossed the finish line, and the url of his information page, so I can compare the moment the race ended with the TV coverage.

**Evidence:** A driver's race time is the duration from the start of the race to the moment he crosses the finish line.

**Official Gold SQL** (full unless noted):

```sql
SELECT d.forename, d.surname, time(r.time, '0' || res.time) || '.' || substr(res.time, -3) AS finish_time, d.url FROM races r JOIN results res ON res.raceId = r.raceId JOIN drivers d ON d.driverId = res.driverId WHERE r.year = 2017 AND r.name = 'Azerbaijan Grand Prix' AND res.positionOrder = 1
```

**Agent final SQL:**

```sql
SELECT d.forename, d.surname, r.url,
       time(
           (julianday(r.date || ' ' || r.time) +
            CAST(res.milliseconds AS REAL) / 86400000.0)
       ) || '.' || printf('%03d', res.milliseconds % 1000) AS finish_local_time
FROM races AS r
JOIN results AS res ON res.raceId = r.raceId
JOIN drivers AS d ON d.driverId = res.driverId
WHERE r.year = 2017
  AND r.name = 'Azerbaijan Grand Prix'
  AND res.positionOrder = 1;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold requests driver information URL and local finish time; agent outputs race URL and a different column order.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT races.name, races.time AS scheduled_time, results.time AS race_duration, results.milliseconds, results.position, results.positionOrder, drivers.fore` → {"columns":["name","scheduled_time","race_duration","milliseconds","position","positionOrder","forename","surname","url"],"rows":[["Azerbaijan Grand Prix","13:00:00","2:03:55.573",7435573,1,1,"Daniel","Ricciardo","http://en.wikipedia.org/wiki/Daniel_Ricciardo"],["Azerbaijan Grand Prix","13:00:00","+


<a id="q277"></a>
### Q277 — challenging · incorrect_result

**Question:** For the 1995 season (races held in the calendar year 1995), how many drivers set a Q1 lap time of more than two minutes - i.e., strictly longer than 2:00.000? I just need the number of drivers.

**Gold SQL preview:**

```sql
SELECT COUNT(DISTINCT T1.driverId) FROM qualifying AS T1 INNER JOIN races AS T2 ON T2.raceId = T1.raceId WHERE T2.year = 1995 AND (length(T1.q1) > length('2:00.000') OR T1.q1 > '2:00.000')
```

**Agent SQL preview:**

```sql
SELECT COUNT(DISTINCT q.driverId) AS driver_count
FROM qualifying AS q
JOIN races AS r ON r.raceId = q.raceId
WHERE r.year = 1995
  AND q.q1 IS NOT NULL
  AND TRIM(q.q1) <> ''
  AND (
    CAST(SUBSTR(TRIM(q.q1), 1, INSTR(TRIM(q.q1), ':') - 1) AS INTEGER) * 60
    + CAST(SUBSTR(TRIM(q.q1), INSTR(TRIM(q.q1), ':') + 1, 2) AS INTEGER)
  ) > 120;
```

**Assessment (CANDIDATE ROOT CAUSE):** Reference counts Q1 times strictly greater than 2:00.000; agent converts only minutes and integer seconds and therefore excludes times 2:00.xxx.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q294"></a>
### Q294 — challenging · incorrect_result

**Question:** For the 1957 British Grand Prix, what percentage of the drivers who took part in the race were classified finishers, rounded to two decimals? By classified finisher I mean a driver whose race record shows them finishing the race, whether on the lead lap or one or more laps behind the winner. I just need the one percentage figure.

**Gold SQL preview:**

```sql
SELECT ROUND(100.0 * COUNT(DISTINCT CASE WHEN x.position IS NOT NULL THEN x.driverId END) / COUNT(DISTINCT x.driverId), 2) AS finisher_percentage FROM races r JOIN results x ON x.raceId = r.raceId WHERE r.year = 1957 AND r.name = 'British Grand Prix'
```

**Agent SQL preview:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold uses non-NULL results.position as classified finisher; agent uses status category strings, which may not be equivalent.

**Observed trace:** 6 model calls; 7 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

## Database: `student_club`

<a id="q300"></a>
### Q300 — moderate · incorrect_result

**Question:** List the name of students that have attended more than 7 events.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT T1.first_name, T1.last_name FROM member AS T1 INNER JOIN attendance AS T2 ON T1.member_id = T2.link_to_member GROUP BY T2.link_to_member HAVING COUNT(T2.link_to_event) > 7
```

**Agent final SQL:**

```sql
SELECT m.first_name || ' ' || m.last_name AS name
FROM member AS m
JOIN attendance AS a ON a.link_to_member = m.member_id
GROUP BY m.member_id
HAVING COUNT(DISTINCT a.link_to_event) > 7;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold outputs first_name and last_name as two columns; agent concatenates them into one name.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT m.first_name || ' ' || m.last_name AS name FROM member AS m JOIN attendance AS a ON a.link_to_member = m.member_id GROUP BY m.member_id HAVING COUNT` → {"columns":["name"],"rows":[["Grant Gilmour"],["Luisa Guidi"]],"truncated":true}


<a id="q320"></a>
### Q320 — challenging · incorrect_result

**Question:** I'm putting together a recruitment report for the colleges and want to know which parts of the university our club's membership actually draws from. For every person on the roster-regardless of their position in the club-look at their major, and the college that houses the department offering that major. Which college or colleges do the most majors on our roster come from, and how many majors is that? If there's a tie at the top, give me every college tied at that count. Please list the colleges in alphabetical order by college name, and return just each college's name and its number of majors.

**Evidence:** Major: a field of study offered by a department housed in a college.

**Official Gold SQL** (full unless noted):

```sql
WITH cnt AS (SELECT mj.college AS college, COUNT(DISTINCT mj.major_id) AS majors FROM member m JOIN major mj ON mj.major_id = m.link_to_major GROUP BY mj.college) SELECT college, majors FROM cnt WHERE majors = (SELECT MAX(majors) FROM cnt) ORDER BY college
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold counts DISTINCT major_id per college, agent counts all member rows; entity grain changes from majors to members.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH college_counts AS ( SELECT ma.college, COUNT(*) AS major_count FROM "member" AS me JOIN major AS ma ON me.link_to_major = ma.major_id GROUP BY ma.coll` → {"columns":["college","major_count"],"rows":[["College of Education & Human Services",8]],"truncated":false}


<a id="q321"></a>
### Q321 — challenging · incorrect_result

**Question:** I want to review what the money actually went on for the well-funded events, by venue. For events that had a budget line of more than forty dollars, how many different things were bought for them at each location? Please give me, for each location, the location of the event and the number of different things bought for such events at that location, and nothing else. Note that a budget line of more than forty dollars means a single budgeted amount strictly over 40 dollars, and all qualifying events held at a location should be pooled together.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH RECURSIVE split(item, rest, loc) AS (SELECT '', x.expense_description || ',', e.location FROM expense x JOIN budget b ON b.budget_id = x.link_to_budget JOIN event e ON e.event_id = b.link_to_event WHERE b.amount > 40 UNION ALL SELECT trim(substr(rest, 1, instr(rest, ',') - 1)), substr(rest, instr(rest, ',') + 1), loc FROM split WHERE rest <> '') SELECT loc AS location, COUNT(DISTINCT item) AS things_bought FROM split WHERE item <> '' GROUP BY loc ORDER BY loc
```

**Agent final SQL:**

```sql
SELECT ev.location,
       COUNT(DISTINCT ex.expense_description) AS different_things_bought
FROM event AS ev
JOIN budget AS b ON b.link_to_event = ev.event_id
JOIN expense AS ex ON ex.link_to_budget = b.budget_id
WHERE b.amount > 40
GROUP BY ev.location;
```

**Assessment (CANDIDATE ROOT CAUSE):** Expense descriptions may contain several comma-delimited items; agent counts distinct full expense_description rather than individual items.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT ev.location, COUNT(DISTINCT ex.expense_description) AS different_things_bought FROM event AS ev JOIN budget AS b ON b.link_to_event = ev.event_id JO` → {"columns":["location","different_things_bought"],"rows":[["Campus Common",1],["MU 215",7]],"truncated":false}


<a id="q325"></a>
### Q325 — challenging · sql_error · Reference QA watchlist

**Question:** For our year-end review, I want to know which event formats bring in the most people. Looking at our whole club year (every event from September 2019 through May 2020), which event type was attended by the most members, and how many members attended that type's events? If several event types tie for the most, list every one of them. Just give me the event type and the number of members for it - nothing else.

**Evidence:** By "attended" I mean a member coming to an event; event type is the kind of event, e.g. Meeting, Social, Game, Election, Community Service.

**Official Gold SQL** (full unless noted):

```sql
WITH member_counts AS (SELECT e.type AS event_type, COUNT(DISTINCT a.link_to_member) AS members FROM event e LEFT JOIN attendance a ON a.link_to_event = e.event_id GROUP BY e.type) SELECT event_type, members FROM member_counts WHERE members = (SELECT MAX(members) FROM member_counts) ORDER BY event_type
```

**Agent final SQL:**

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

**Assessment (REFERENCE QA CANDIDATE):** Final SQL uses >= ALL(subquery), unsupported in SQLite; scored sql_error. QA watchlist: Gold does not explicitly filter the date window in the question.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / sql_error**. 

Call 1: `SELECT type, COUNT(*) AS member_count FROM event e JOIN attendance a ON a.link_to_event=e.event_id WHERE date(e.event_date) >= date('2019-09-01') AND date(` → {"columns":["type","member_count"],"rows":[["Meeting",109],["Guest Speaker",83]],"truncated":false}


**Reference review discipline:** Do not change the Gold answer or EX based on this observation alone. Re-execute candidate interpretations on the pinned database and record exact result differences before filing an annotation issue.

<a id="q327"></a>
### Q327 — challenging · sql_error

**Question:** I'm wrapping up the October Meeting and need the final numbers broken down by what we actually bought, not just by budget category. For every item bought with approved money for the October Meeting, can you give me: the item's name, the budget category of the purchase that included the item, and the total cost in dollars of the approved October Meeting purchases that included the item? Only expenses marked as approved count - an expense without an approval mark doesn't. If an item was included in approved purchases recorded under more than one budget category, give me one row per category. Costs should be plain sums in US dollars with no rounding, and please sort the list by category and then by item name.

**Evidence:** An item is a single thing bought with club money, such as water, pizza or posters. A purchase is an expense recorded for the event.

**Official Gold SQL** (full unless noted):

```sql
WITH RECURSIVE split AS (SELECT link_to_budget AS bid, cost, '' AS item, expense_description || ',' AS rest FROM expense WHERE approved = 'true' UNION ALL SELECT bid, cost, trim(substr(rest, 1, instr(rest, ',') - 1)), substr(rest, instr(rest, ',') + 1) FROM split WHERE rest <> '') SELECT s.item AS item, b.category AS category, SUM(s.cost) AS total_cost FROM split s JOIN budget b ON s.bid = b.budget_id JOIN event e ON b.link_to_event = e.event_id WHERE s.item <> '' AND e.event_name = 'October Meeting' GROUP BY s.item, b.category ORDER BY b.category, s.item
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Final SQL json_each(...) attempts TRIM(item), but the json_each virtual table returns value, not item; scored final sql_error.

**Observed trace:** 6 model calls; 9 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / sql_error**. 

Call 1: `SELECT expense_id, expense_description, cost, approved, budget.category, event.event_name FROM expense JOIN budget ON expense.link_to_budget=budget.budget_` → {"columns":["expense_id","expense_description","cost","approved","category","event_name"],"rows":[["recJnyr7Z1CjAlHgA","Posters",54.25,"true","Advertisement","October Meeting"],["recTUt9QxJ0Sp3H3m","Water, chips, cookies",69.33,"true","Food","October Meeting"]],"truncated":false}  
Call 3: `SELECT expense_description, cost, approved, budget.category FROM expense JOIN budget ON expense.link_to_budget=budget.budget_id JOIN event ON budget.link_t` → {"columns":["expense_description","cost","approved","category"],"rows":[["Posters",54.25,"true","Advertisement"],["Water, chips, cookies",69.33,"true","Food"]],"truncated":false}


<a id="q329"></a>
### Q329 — challenging · incorrect_result

**Question:** I'm preparing the year-end audit of club spending. For each item Sacha Harrison bought with club money, I need the item name and how many times she bought it. Can you give me that list?

**Gold SQL preview:**

```sql
WITH RECURSIVE split(rest, item) AS (SELECT expense_description || ',', '' FROM expense WHERE link_to_member = (SELECT member_id FROM member WHERE first_name = 'Sacha' AND last_name = 'Harrison') UNION ALL SELECT substr(rest, instr(rest, ',') + 1), trim(substr(rest, 1, instr(rest, ',') - 1)) FROM split WHERE rest <> '') SELECT item, COUNT(*) AS times FROM split WHERE item <> '' GROUP BY item ORDER BY item
```

**Agent SQL preview:**

```sql
SELECT e.expense_description AS item_name, COUNT(*) AS times_bought
FROM expense AS e
JOIN member AS m ON e.link_to_member = m.member_id
WHERE m.first_name = 'Sacha'
  AND m.last_name = 'Harrison'
GROUP BY e.expense_description
ORDER BY e.expense_description;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold recursively splits comma-separated expense descriptions into items, whereas agent treats each entire description as one item.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q331"></a>
### Q331 — challenging · incorrect_result

**Question:** For our department report, I need to know how many different fields of study our club members from the Political Science Department represent. Only count members of the Political Science Department - members from other departments don't count. Just give me the number of different majors studied by those members.

**Gold SQL preview:**

```sql
SELECT COUNT(DISTINCT T2.major_id) AS different_majors FROM member AS T1 INNER JOIN major AS T2 ON T1.link_to_major = T2.major_id WHERE T2.department = 'Political Science Department'
```

**Agent SQL preview:**

```sql
SELECT COUNT(DISTINCT major.major_name) AS different_majors
FROM member
JOIN major ON member.link_to_major = major.major_id
WHERE major.department = 'Political Science';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold filters department='Political Science Department', agent uses 'Political Science'.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

## Database: `superhero`

<a id="q332"></a>
### Q332 — moderate · incorrect_result

**Question:** Among Marvel Comics superheroes with a known eye colour, rank the eye colours by number of superheroes. Give each colour, its hero count, and its rank, most common first; break display-order ties alphabetically.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH colour_counts AS (SELECT c.colour AS eye_colour, COUNT(*) AS hero_count FROM superhero AS s JOIN colour AS c ON c.id = s.eye_colour_id JOIN publisher AS p ON p.id = s.publisher_id WHERE p.publisher_name = 'Marvel Comics' AND c.colour <> 'No Colour' GROUP BY c.colour) SELECT eye_colour, hero_count, RANK() OVER (ORDER BY hero_count DESC) AS popularity_rank FROM colour_counts ORDER BY hero_count DESC, eye_colour
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold includes Marvel heroes regardless of alignment and excludes No Colour; agent adds alignment='Good' and does not exclude No Colour.

**Observed trace:** 8 model calls; 10 tool calls; 3 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT c.colour, COUNT(*) AS hero_count, RANK() OVER (ORDER BY COUNT(*) DESC) AS rank FROM superhero s JOIN colour c ON s.eye_colour_id = c.id JOIN publish` → {"columns":["colour","hero_count","rank"],"rows":[["Blue",91,1],["Brown",60,2]],"truncated":false}  
Call 3: `SELECT id, alignment FROM alignment;` → {"columns":["id","alignment"],"rows":[[1,"Good"],[2,"Bad"]],"truncated":false}


<a id="q335"></a>
### Q335 — challenging · incorrect_result

**Question:** Between Marvel Comics and DC Comics, which publisher has more superheroes, and by how many?

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH counts AS ( SELECT SUM(CASE WHEN p.publisher_name = 'Marvel Comics' THEN 1 ELSE 0 END) AS marvel_count, SUM(CASE WHEN p.publisher_name = 'DC Comics' THEN 1 ELSE 0 END) AS dc_count FROM superhero AS s JOIN publisher AS p ON p.id = s.publisher_id ) SELECT CASE WHEN marvel_count > dc_count THEN 'Marvel Comics' WHEN dc_count > marvel_count THEN 'DC Comics' ELSE 'Tie' END, ABS(marvel_count - dc_count) FROM counts
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold returns winning publisher and absolute difference; agent returns publisher, count and signed difference (three fields).

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT p.publisher_name, COUNT(*) AS superhero_count FROM superhero s JOIN publisher p ON p.id=s.publisher_id WHERE p.publisher_name IN ('Marvel Comics','D` → {"columns":["publisher_name","superhero_count"],"rows":[["DC Comics",224],["Marvel Comics",387]],"truncated":false}


<a id="q339"></a>
### Q339 — challenging · incorrect_result

**Question:** List superheroes whose known eye, hair and skin colours are all the same, along with any recorded publisher name.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT s.superhero_name, p.publisher_name FROM superhero AS s LEFT JOIN publisher AS p ON p.id = s.publisher_id JOIN colour AS c ON c.id = s.eye_colour_id WHERE s.eye_colour_id = s.hair_colour_id AND s.eye_colour_id = s.skin_colour_id AND c.colour <> 'No Colour'
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes colour category 'No Colour'; agent checks FK equality/NULL only.

**Observed trace:** 4 model calls; 7 tool calls; 1 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT s.superhero_name, p.publisher_name FROM superhero s LEFT JOIN publisher p ON p.id = s.publisher_id WHERE s.eye_colour_id IS NOT NULL AND s.hair_colo` → {"columns":["superhero_name","publisher_name"],"rows":[["Agent Zero","Marvel Comics"],["Alex Mercer","Wildstorm"]],"truncated":true}


<a id="q342"></a>
### Q342 — challenging · incorrect_result

**Question:** Which publisher has more superheroes, DC Comics or Marvel Comics, and by how many? Return Tie if their counts are equal.

**Gold SQL preview:**

```sql
WITH counts AS (SELECT SUM(CASE WHEN p.publisher_name = 'DC Comics' THEN 1 ELSE 0 END) AS dc, SUM(CASE WHEN p.publisher_name = 'Marvel Comics' THEN 1 ELSE 0 END) AS marvel FROM superhero AS s JOIN publisher AS p ON p.id = s.publisher_id) SELECT CASE WHEN dc > marvel THEN 'DC Comics' WHEN marvel > dc THEN 'Marvel Comics' ELSE 'Tie' END, ABS(dc - marvel) FROM counts
```

**Agent SQL preview:**

```sql
SELECT CASE
         WHEN SUM(CASE WHEN p.publisher_name = 'DC Comics' THEN 1 ELSE 0 END) =
              SUM(CASE WHEN p.publisher_name = 'Marvel Comics' THEN 1 ELSE 0 END)
           THEN 'Tie'
         WHEN SUM(CASE WHEN p.publisher_name = 'DC Comics' THEN 1 ELSE 0 END) >
              SUM(CASE WHEN p.publisher_name = 'Marvel Comics' THEN 1 ELSE 0 END)
           THEN 'DC Comics by ' || (
             SUM(CASE WHEN p.publisher_name = 'DC Comic
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold returns two values (winner or Tie, absolute count difference); agent formats winner and margin as one string.

**Observed trace:** 5 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q345"></a>
### Q345 — challenging · incorrect_result

**Question:** I'm setting a typical weight for a green-skinned creature class. Can you tell me the average weight in kg of the heroes with green skin? Count only heroes whose weight is known, and give me one number rounded to one decimal place.

**Evidence:** Green skin means the hero's skin colour is green.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(AVG(T1.weight_kg), 1) AS average_weight_kg FROM superhero AS T1 INNER JOIN colour AS T2 ON T1.skin_colour_id = T2.id WHERE T2.colour = 'Green' AND T1.weight_kg > 0
```

**Agent final SQL:**

```sql
SELECT ROUND(AVG(s.weight_kg), 1) AS average_weight_kg
FROM superhero AS s
JOIN colour AS c ON c.id = s.skin_colour_id
WHERE LOWER(c.colour) = 'green'
  AND s.weight_kg IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes weight_kg<=0; agent excludes only NULL, then executes and submits a successful query returning 967.6.

**Observed trace:** 5 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT ROUND(AVG(s.weight_kg), 1) AS average_weight_kg FROM superhero AS s JOIN colour AS c ON c.id = s.skin_colour_id WHERE LOWER(c.colour) = 'green' AND ` → {"columns":["average_weight_kg"],"rows":[[967.6]],"truncated":false}


<a id="q348"></a>
### Q348 — challenging · incorrect_result

**Question:** I want to profile the cohort of heroes whose Intelligence score matches Abomination's Intelligence score. What is their average measured weight in kg? Please round the average to two decimals.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END), 2) AS average_weight_kg FROM superhero s JOIN hero_attribute ha ON ha.hero_id = s.id JOIN attribute a ON a.id = ha.attribute_id WHERE a.attribute_name = 'Intelligence' AND ha.attribute_value = (SELECT abom_ha.attribute_value FROM superhero abom JOIN hero_attribute abom_ha ON abom_ha.hero_id = abom.id JOIN attribute abom_a ON abom_a.id = abom_ha.attribute_id WHERE abom.superhero_nam
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(s.weight_kg), 2) AS avg_weight_kg
FROM superhero AS s
JOIN hero_attribute AS ha ON ha.hero_id = s.id
JOIN attribute AS a ON a.id = ha.attribute_id
WHERE a.attribute_name = 'Intelligence'
  AND ha.attribute_value = (
      SELECT ha2.attribute_value
      FROM superhero AS ab
      JOIN hero_attribute AS ha2 ON ha2.hero_id = ab.id
      JOIN attribute AS a2 ON a2.id = ha2.attribute_id
      WHERE ab.superhero_name = 'Abomination'
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold computes average only over positive measured weights; agent AVG(weight_kg) includes zero sentinel values.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q350"></a>
### Q350 — challenging · incorrect_result

**Question:** I'm putting together a comparison of the heaviest brick-strength characters. What is the average weight, in kilograms, of all superheroes whose Strength score equals the Hulk's? I just need a single integer rounded to the nearest kilogram. Include every superhero in the database, no restrictions on publisher or alignment. If a hero's weight is unknown, leave them out and average only over the heroes whose weight has actually been measured.

**Evidence:** Strength is one of the six measured hero attributes, each scored on a 1-100 scale; the Hulk is the superhero named 'Hulk'; weight is the superhero's weight in kilograms.

**Official Gold SQL** (full unless noted):

```sql
SELECT CAST(ROUND(AVG(s.weight_kg)) AS INTEGER) AS average_weight_kg FROM superhero s INNER JOIN hero_attribute ha ON ha.hero_id = s.id INNER JOIN attribute a ON a.id = ha.attribute_id WHERE a.attribute_name = 'Strength' AND ha.attribute_value = (SELECT ha2.attribute_value FROM superhero s2 INNER JOIN hero_attribute ha2 ON ha2.hero_id = s2.id INNER JOIN attribute a2 ON a2.id = ha2.attribute_id WHERE s2.superhero_name = 'Hulk' AND a2.attribute_name = 'Strength') AND s.weight_kg > 0
```

**Agent final SQL:**

```sql
SELECT ROUND(AVG(s.weight_kg)) AS average_weight_kg
FROM superhero AS s
JOIN hero_attribute AS ha ON ha.hero_id = s.id
JOIN attribute AS a ON a.id = ha.attribute_id
WHERE a.attribute_name = 'Strength'
  AND ha.attribute_value = (
      SELECT hha.attribute_value
      FROM superhero AS h
      JOIN hero_attribute AS hha ON hha.hero_id = h.id
      JOIN attribute AS hattr ON hattr.id = hha.attribute_id
      WHERE h.superhero_name = 'Hulk'
        AND hattr.attribute_name = 'Strength'
  )
  AND s.weight_kg IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold requires weight_kg>0 when averaging Hulk-strength peers; agent uses IS NOT NULL instead.

**Observed trace:** 8 model calls; 8 tool calls; 4 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT id, attribute_name FROM attribute WHERE lower(attribute_name) LIKE '%strength%'` → {"columns":["id","attribute_name"],"rows":[[2,"Strength"]],"truncated":false}  
Call 4: `SELECT ROUND(AVG(s.weight_kg)) AS average_weight_kg FROM superhero s JOIN hero_attribute ha ON ha.hero_id = s.id JOIN attribute a ON a.id = ha.attribute_id` → {"columns":["average_weight_kg"],"rows":[[1571582]],"truncated":false}


<a id="q355"></a>
### Q355 — challenging · incorrect_result

**Question:** What is the average weight in kilograms of the DC Comics heroes whose eye colour is also shared by at least one Marvel Comics hero? Leave out any heroes whose weight is unknown, round the result to the nearest kilogram, and treat 'No Colour' as an eye colour like any other when matching between publishers. I just want that single number.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END)) AS average_weight_kg FROM superhero AS s JOIN publisher AS p ON s.publisher_id = p.id WHERE p.publisher_name = 'DC Comics' AND s.eye_colour_id IN (SELECT s2.eye_colour_id FROM superhero AS s2 JOIN publisher AS p2 ON s2.publisher_id = p2.id WHERE p2.publisher_name = 'Marvel Comics')
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(s.weight_kg)) AS average_weight_kg
FROM superhero AS s
JOIN publisher AS d ON d.id = s.publisher_id
WHERE d.publisher_name = 'DC Comics'
  AND s.weight_kg IS NOT NULL
  AND EXISTS (
      SELECT 1
      FROM superhero AS m
      JOIN publisher AS p ON p.id = m.publisher_id
      WHERE p.publisher_name = 'Marvel Comics'
        AND m.eye_colour_id = s.eye_colour_id
  );
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes zero/unknown weights; agent lacks matching >0 condition.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q356"></a>
### Q356 — challenging · incorrect_result

**Question:** I'm researching heroes like A-Bomb. What is the average height in centimetres of the superheroes in A-Bomb's group? Please give me just that single number, rounded to one decimal place. Note that A-Bomb itself belongs to its group and should be included, and only heroes whose height is actually on record should count toward the average-anyone without a recorded height should be left out rather than counted as some height.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(CASE WHEN height_cm > 0 THEN height_cm END), 1) AS average_height_cm FROM superhero WHERE race_id = (SELECT race_id FROM superhero WHERE superhero_name = 'A-Bomb')
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(CAST(height_cm AS REAL)), 1)
FROM superhero
WHERE race_id = (
    SELECT race_id
    FROM superhero
    WHERE superhero_name = 'A-Bomb'
)
AND height_cm IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes unrecorded heights via height_cm>0; agent uses height_cm IS NOT NULL.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q357"></a>
### Q357 — challenging · incorrect_result

**Question:** What is the average weight, in kg, of the heroes who belong to races in which no hero is female? Heroes whose weight is not recorded should not count toward the average. I just need that single value.

**Gold SQL preview:**

```sql
SELECT AVG(T1.weight_kg) AS average_weight_kg FROM superhero AS T1 INNER JOIN race AS T2 ON T1.race_id = T2.id WHERE T1.weight_kg > 0 AND NOT EXISTS (SELECT 1 FROM superhero AS T3 INNER JOIN gender AS T4 ON T3.gender_id = T4.id WHERE T3.race_id = T2.id AND T4.gender = 'Female')
```

**Agent SQL preview:**

```sql
SELECT AVG(s.weight_kg)
FROM superhero AS s
WHERE s.weight_kg IS NOT NULL
  AND s.race_id IN (
      SELECT r.id
      FROM race AS r
      WHERE NOT EXISTS (
          SELECT 1
          FROM superhero AS f
          JOIN gender AS g ON g.id = f.gender_id
          WHERE f.race_id = r.id
            AND LOWER(g.gender) = 'female'
      )
  );
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes weight_kg<=0; agent uses IS NOT NULL.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q358"></a>
### Q358 — challenging · incorrect_result

**Question:** I'm writing a piece about which real publishing companies have put out very tall heroes. How many publishers in the database have released at least one hero taller than 200 cm? Note that taller than 200 cm means strictly more than 200 cm, and it counts if even one of their heroes is that tall. I just need the number of publishers, nothing else.

**Gold SQL preview:**

```sql
SELECT COUNT(DISTINCT T1.publisher_id) AS publisher_count FROM superhero AS T1 INNER JOIN publisher AS T2 ON T1.publisher_id = T2.id WHERE T1.height_cm > 200 AND T2.publisher_name <> ''
```

**Agent SQL preview:**

```sql
SELECT COUNT(DISTINCT publisher_id) AS publisher_count
FROM superhero
WHERE height_cm > 200
  AND publisher_id IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold joins publisher and excludes blank publisher names; agent counts publisher_id without checking publisher_name.

**Observed trace:** 5 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q359"></a>
### Q359 — challenging · incorrect_result

**Question:** For a licensing survey of non-DC heroic characters, I need a single total count of superheroes whose alignment is Good and who are not published by DC Comics. Just that one number, please.

**Gold SQL preview:**

```sql
SELECT COUNT(*) AS hero_count FROM superhero AS T1 INNER JOIN alignment AS T2 ON T1.alignment_id = T2.id WHERE T2.alignment = 'Good' AND NOT EXISTS (SELECT 1 FROM publisher AS T3 WHERE T3.id = T1.publisher_id AND T3.publisher_name = 'DC Comics')
```

**Agent SQL preview:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold uses NOT EXISTS to preserve NULL publisher semantics; agent uses NOT IN, which excludes NULL publisher_id.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q360"></a>
### Q360 — challenging · incorrect_result

**Question:** I'm comparing superhero body weights to typical human weights for an article. What is the average weight in kilograms of superheroes published by DC Comics, rounded to one decimal place, and how many DC Comics superheroes is that average based on? Only superheroes with a known weight should count toward the average, so the count should be the number of superheroes it's based on. DC Comics means the publisher named DC Comics.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(s.weight_kg), 1) AS avg_weight_kg, COUNT(*) AS hero_count FROM superhero s JOIN publisher p ON s.publisher_id = p.id WHERE p.publisher_name = 'DC Comics' AND s.weight_kg > 0
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(s.weight_kg), 1) AS average_weight_kg,
       COUNT(s.weight_kg) AS superhero_count
FROM superhero AS s
JOIN publisher AS p ON s.publisher_id = p.id
WHERE p.publisher_name = 'DC Comics'
  AND s.weight_kg IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold averages and counts only positive weight_kg; agent checks non-NULL.

**Observed trace:** 5 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q363"></a>
### Q363 — challenging · incorrect_result

**Question:** What is the average weight in kg of the Female heroes in the database? Round it to two decimal places, and skip any heroes whose weight is unknown. I just need that single number.

**Evidence:** kg: kilograms

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(AVG(weight_kg), 2) AS average_weight_kg FROM superhero WHERE gender_id = (SELECT id FROM gender WHERE gender = 'Female') AND weight_kg > 0
```

**Agent final SQL:**

```sql
SELECT ROUND(AVG(s.weight_kg), 2) AS average_weight_kg
FROM superhero AS s
JOIN gender AS g ON s.gender_id = g.id
WHERE g.gender = 'Female'
  AND s.weight_kg IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes zero weight; agent checks only IS NOT NULL.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT ROUND(AVG(s.weight_kg), 2) AS average_weight_kg FROM superhero AS s JOIN gender AS g ON s.gender_id = g.id WHERE g.gender = 'Female' AND s.weight_kg` → {"columns":["average_weight_kg"],"rows":[[60.78]],"truncated":false}


<a id="q365"></a>
### Q365 — challenging · incorrect_result

**Question:** I'm comparing how power-rich male and female heroes are. For all male heroes and all female heroes that have a documented real full name, what is the average number of superpowers per hero for each gender? Please compute each average over the entire hero population of that gender, not just the heroes that happen to have power records. Give me both averages, each rounded to two decimal places, and nothing else.

**Evidence:** Full name: the hero's real, full personal name (first name plus last name, and optionally middle names); single names such as mononyms or aliases are not a full name.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(CAST(SUM(CASE WHEN g.gender = 'Male' THEN COALESCE(pc.cnt, 0) ELSE 0 END) AS REAL) / SUM(CASE WHEN g.gender = 'Male' THEN 1 ELSE 0 END), 2) AS avg_superpowers_male, ROUND(CAST(SUM(CASE WHEN g.gender = 'Female' THEN COALESCE(pc.cnt, 0) ELSE 0 END) AS REAL) / SUM(CASE WHEN g.gender = 'Female' THEN 1 ELSE 0 END), 2) AS avg_superpowers_female FROM superhero AS s INNER JOIN gender AS g ON s.gender_id = g.id LEFT JOIN (SELECT hero_id, COUNT(*) AS cnt FROM hero_power GROUP BY hero_id) AS pc ON pc.hero_id = s.id WHERE s.full_name LIKE '% %'
```

**Agent final SQL:**

```sql
SELECT g.gender,
       ROUND(AVG(COALESCE(p.power_count, 0)), 2) AS average_superpowers_per_hero
FROM superhero AS s
JOIN gender AS g ON g.id = s.gender_id
LEFT JOIN (
    SELECT hero_id, COUNT(DISTINCT power_id) AS power_count
    FROM hero_power
    GROUP BY hero_id
) AS p ON p.hero_id = s.id
WHERE LOWER(g.gender) IN ('male', 'female')
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> ''
  AND INSTR(TRIM(s.full_name), ' ') > 0
GROUP BY g.gender;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold outputs two aggregate columns (male, female) in one row; agent emits one row per gender. Reference COUNT uses all relevant heroes, with zero powers included.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT g.gender, COUNT(*) AS heroes, ROUND(AVG(COALESCE(p.power_count, 0)), 2) AS avg_powers FROM superhero s JOIN gender g ON g.id = s.gender_id LEFT JOIN` → {"columns":["gender","heroes","avg_powers"],"rows":[["Female",133,6.87],["Male",306,7.87]],"truncated":false}


<a id="q366"></a>
### Q366 — challenging · incorrect_result

**Question:** I'm putting together a physical profile of the green-skinned villain corner of the universe for a fan wiki page. Could you tell me the average height in centimetres and the average weight in kilograms of the green-skinned villains? Please average only over the characters whose measurement is actually on record - a character with no recorded height or weight shouldn't drag the average down - and round each average to two decimals. I just need those two numbers.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(CASE WHEN T1.height_cm > 0 THEN T1.height_cm END), 2) AS avg_height_cm, ROUND(AVG(CASE WHEN T1.weight_kg > 0 THEN T1.weight_kg END), 2) AS avg_weight_kg FROM superhero AS T1 INNER JOIN alignment AS T2 ON T1.alignment_id = T2.id INNER JOIN colour AS T3 ON T1.skin_colour_id = T3.id WHERE T2.alignment = 'Bad' AND T3.colour = 'Green'
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(s.height_cm), 2) AS avg_height_cm,
       ROUND(AVG(s.weight_kg), 2) AS avg_weight_kg
FROM superhero AS s
JOIN alignment AS a ON s.alignment_id = a.id
JOIN colour AS c ON s.skin_colour_id = c.id
WHERE a.alignment = 'Bad'
  AND c.colour = 'Green';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold separately excludes nonpositive height and weight from each average; agent AVG over raw values includes 0.

**Observed trace:** 5 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q367"></a>
### Q367 — challenging · incorrect_result

**Question:** I'm profiling publisher rosters and now want to look at the physical build of George Lucas's heroes. What is the average height of the heroes he created, in centimetres, and their average weight, in kilograms? Please round each average to one decimal place, and only include heroes whose height (for the height average) or weight (for the weight average) is actually known.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(CASE WHEN s.height_cm > 0 THEN s.height_cm END), 1) AS average_height_cm, ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END), 1) AS average_weight_kg FROM superhero AS s INNER JOIN publisher AS p ON s.publisher_id = p.id WHERE p.publisher_name = 'George Lucas'
```

**Agent SQL preview:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes nonpositive heights and weights; agent excludes NULL only.

**Observed trace:** 5 model calls; 5 tool calls; 2 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q368"></a>
### Q368 — challenging · incorrect_result

**Question:** I'd like to know how tall the heroes are who share at least one superpower with 3-D Man. Can you give me the average height in centimetres of those heroes, rounded to one decimal place? Please leave 3-D Man himself out of it, and don't count heroes whose height isn't known.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(s.height_cm), 1) AS avg_height_cm FROM superhero AS s WHERE s.height_cm > 0 AND s.id <> (SELECT id FROM superhero WHERE superhero_name = '3-D Man') AND s.id IN (SELECT hp2.hero_id FROM hero_power AS hp2 WHERE hp2.power_id IN (SELECT power_id FROM hero_power WHERE hero_id = (SELECT id FROM superhero WHERE superhero_name = '3-D Man')))
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(CAST(h.height_cm AS REAL)), 1) AS average_height_cm
FROM superhero h
WHERE h.height_cm IS NOT NULL
  AND h.superhero_name <> '3-D Man'
  AND EXISTS (
      SELECT 1
      FROM hero_power hp
      JOIN hero_power hp3 ON hp.power_id = hp3.power_id
      JOIN superhero man ON man.id = hp3.hero_id
      WHERE hp.hero_id = h.id
        AND man.superhero_name = '3-D Man'
  );
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes height_cm<=0, agent excludes only NULL.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q370"></a>
### Q370 — challenging · incorrect_result

**Question:** I'm doing a physical-profile breakdown of the George Lucas catalogue. For the heroes published by George Lucas that have at least one superpower in the database, what is their average weight in kilograms, counting only the heroes whose weight is recorded? Please give me just that one number, rounded to two decimal places.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(CASE WHEN s.weight_kg > 0 THEN s.weight_kg END), 2) AS avg_weight_kg FROM superhero AS s INNER JOIN publisher AS p ON s.publisher_id = p.id WHERE p.publisher_name = 'George Lucas' AND EXISTS (SELECT 1 FROM hero_power AS hp WHERE hp.hero_id = s.id)
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(CAST(s.weight_kg AS REAL)), 2)
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

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes weight_kg<=0, agent excludes only NULL.

**Observed trace:** 4 model calls; 6 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q371"></a>
### Q371 — challenging · incorrect_result

**Question:** For the article I'm writing on heroic female characters, I'd like a physique stat for the trivia box: what is the average weight in kilograms of female superheroes whose alignment is good? Only count superheroes whose weight is known. Please round the result to two decimal places.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(s.weight_kg), 2) AS average_weight_kg FROM superhero AS s JOIN gender AS g ON g.id = s.gender_id JOIN alignment AS a ON a.id = s.alignment_id WHERE g.gender = 'Female' AND a.alignment = 'Good' AND s.weight_kg > 0
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(CAST(s.weight_kg AS REAL)), 2) AS average_weight_kg
FROM superhero AS s
JOIN gender AS g ON s.gender_id = g.id
JOIN alignment AS a ON s.alignment_id = a.id
WHERE g.gender = 'Female'
  AND a.alignment = 'Good'
  AND s.weight_kg IS NOT NULL;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes weight_kg<=0, agent excludes only NULL.

**Observed trace:** 6 model calls; 9 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q374"></a>
### Q374 — challenging · incorrect_result

**Question:** I want to know about the lightest superhero whose weight has actually been recorded. Among all heroes sharing that lightest weight, give me the largest number of superpowers any of them has. If such a hero has no powers, that counts as 0. Please return just that one number.

**Gold SQL preview:**

```sql
SELECT MAX(cnt) AS power_count FROM (SELECT COUNT(hp.power_id) AS cnt FROM superhero AS h LEFT JOIN hero_power hp ON h.id = hp.hero_id WHERE h.weight_kg = (SELECT MIN(weight_kg) FROM superhero WHERE weight_kg > 0) GROUP BY h.id)
```

**Agent SQL preview:**

```sql
WITH lightest AS (
    SELECT MIN(weight_kg) AS min_weight
    FROM superhero
    WHERE weight_kg IS NOT NULL
)
SELECT COALESCE(MAX(power_count), 0)
FROM (
    SELECT s.id, COUNT(DISTINCT hp.power_id) AS power_count
    FROM superhero AS s
    JOIN lightest AS l ON s.weight_kg = l.min_weight
    LEFT JOIN hero_power AS hp ON hp.hero_id = s.id
    GROUP BY s.id
);
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold finds minimum positive measured weight; agent finds MIN(weight_kg) among non-NULL values (potentially zero).

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q377"></a>
### Q377 — challenging · incorrect_result

**Question:** I'm looking at how designers pair hair and eye colours. For every eye colour that appears on at least one brown-haired hero, how many heroes have that eye colour while their hair is NOT brown? Just give me each eye colour and that count, listing the eye colour with the highest count first. If two eye colours have the same count, the one whose name comes first alphabetically should come first.

**Gold SQL preview:**

```sql
WITH cohort AS (SELECT DISTINCT s.eye_colour_id AS eid FROM superhero AS s INNER JOIN colour AS h ON s.hair_colour_id = h.id WHERE h.colour = 'Brown') SELECT c.colour AS eye_colour, COUNT(CASE WHEN h.colour <> 'Brown' THEN 1 END) AS heroes FROM cohort AS t INNER JOIN colour AS c ON c.id = t.eid LEFT JOIN superhero AS s ON s.eye_colour_id = t.eid LEFT JOIN colour AS h ON h.id = s.hair_colour_id GROUP BY c.colour ORDER BY heroes DESC, eye_colour
```

**Agent SQL preview:**

```sql
SELECT eye.colour AS eye_colour, COUNT(*) AS hero_count
FROM superhero AS h
JOIN colour AS hair ON hair.id = h.hair_colour_id
JOIN colour AS eye ON eye.id = h.eye_colour_id
WHERE h.eye_colour_id IN (
    SELECT DISTINCT brown_hair_hero.eye_colour_id
    FROM superhero AS brown_hair_hero
    JOIN colour AS brown_hair ON brown_hair.id = brown_hair_hero.hair_colour_id
    WHERE brown_hair.colour = 'Brown'
)
AND hair.colour <> 'Brown'
GROUP BY h.eye_
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold retains eye-colour groups even when the not-brown count is zero; agent filters before GROUP BY and can drop zero groups.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q378"></a>
### Q378 — challenging · incorrect_result

**Question:** I'm preparing a report on Marvel's roster and want to gauge how heroic their catalogued heroes are. Among Marvel Comics superheroes whose civilian full name is documented, what percentage are good? Please give me just that single percentage, rounded to two decimal places. Note: the percentage should be taken over all Marvel Comics superheroes with a known full name - those whose moral alignment is unknown still count toward the total, just not as good.

**Evidence:** Good refers to alignment = 'Good'. A full name means the hero's real-world civilian identity, i.e. an actual person's name such as 'Charles Chandler' or 'Richard Milhouse Jones'.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(CAST(SUM(CASE WHEN T3.alignment = 'Good' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*), 2) AS percentage FROM superhero AS T1 INNER JOIN publisher AS T2 ON T1.publisher_id = T2.id LEFT JOIN alignment AS T3 ON T1.alignment_id = T3.id WHERE T2.publisher_name = 'Marvel Comics' AND T1.full_name IS NOT NULL AND T1.full_name <> '-'
```

**Agent final SQL:**

```sql
SELECT ROUND(100.0 * SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) / COUNT(*), 2) AS percentage
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
LEFT JOIN alignment AS a ON a.id = s.alignment_id
WHERE p.publisher_name = 'Marvel Comics'
  AND s.full_name IS NOT NULL
  AND TRIM(s.full_name) <> '';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes full_name='-' as unknown name; agent checks only NULL/blank.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT p.publisher_name, a.alignment, COUNT(*) AS n FROM superhero s JOIN publisher p ON s.publisher_id=p.id LEFT JOIN alignment a ON s.alignment_id=a.id W` → {"columns":["publisher_name","alignment","n"],"rows":[["Marvel Comics",null,3],["Marvel Comics","Bad",105]],"truncated":false}  
Call 2: `SELECT 100.0 * SUM(CASE WHEN a.alignment='Good' THEN 1 ELSE 0 END) / COUNT(*) AS pct FROM superhero s JOIN publisher p ON s.publisher_id=p.id LEFT JOIN ali` → {"columns":["pct"],"rows":[[64.19753086419753]],"truncated":false}


<a id="q379"></a>
### Q379 — challenging · incorrect_result

**Question:** What percentage of Marvel Comics superheroes with a recorded superpower are classified as good? Round the percentage to two decimal places, and give me just that single value.

**Evidence:** Good means alignment 'Good'; superpower refers to a hero's recorded power.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(CAST(SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*), 2) AS good_percentage FROM superhero s JOIN publisher p ON s.publisher_id = p.id LEFT JOIN alignment a ON s.alignment_id = a.id WHERE p.publisher_name = 'Marvel Comics' AND EXISTS (SELECT 1 FROM hero_power hp WHERE hp.hero_id = s.id)
```

**Agent final SQL:**

```sql
SELECT ROUND(
    100.0 * SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) / COUNT(*),
    2
)
FROM superhero AS s
JOIN publisher AS p ON p.id = s.publisher_id
JOIN alignment AS a ON a.id = s.alignment_id
WHERE p.publisher_name = 'Marvel Comics'
  AND EXISTS (
      SELECT 1
      FROM hero_power AS hp
      WHERE hp.hero_id = s.id
  );
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold uses LEFT JOIN alignment to retain unknown alignment in denominator; agent INNER JOIN excludes such heroes.

**Observed trace:** 4 model calls; 7 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT ROUND(100.0 * SUM(CASE WHEN a.alignment = 'Good' THEN 1 ELSE 0 END) / COUNT(DISTINCT s.id), 2) AS percentage FROM superhero s JOIN publisher p ON p.` → {"columns":["percentage"],"rows":[[64.97]],"truncated":false}


<a id="q380"></a>
### Q380 — challenging · incorrect_result

**Question:** I'm comparing the builds of heroes whose power sets overlap with 3-D Man's. What is the average weight in kg of the heroes other than 3-D Man that share at least one superpower with him? Please round it to two decimal places, leave out any heroes whose weight isn't recorded, and return just that single number.

**Gold SQL preview:**

```sql
SELECT ROUND(AVG(weight_kg), 2) AS average_weight_kg FROM superhero WHERE superhero_name <> '3-D Man' AND weight_kg > 0 AND id IN (SELECT hero_id FROM hero_power WHERE power_id IN (SELECT power_id FROM hero_power WHERE hero_id = (SELECT id FROM superhero WHERE superhero_name = '3-D Man')))
```

**Agent SQL preview:**

```sql
SELECT ROUND(AVG(s.weight_kg), 2)
FROM superhero AS s
WHERE s.weight_kg IS NOT NULL
  AND s.id <> (SELECT id FROM superhero WHERE superhero_name = '3-D Man')
  AND EXISTS (
    SELECT 1
    FROM hero_power AS hp
    JOIN hero_power AS h3 ON h3.power_id = hp.power_id
    WHERE hp.hero_id = s.id
      AND h3.hero_id = (SELECT id FROM superhero WHERE superhero_name = '3-D Man')
  );
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold excludes weight_kg<=0, agent excludes only NULL.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q381"></a>
### Q381 — challenging · incorrect_result

**Question:** Among superheroes whose weight is not recorded, how many more have the 'No Colour' eye category than have blue eyes? I want a single whole number: the count of 'No Colour' eyes minus the count of blue eyes in that group - it can be negative if blue is more common. Please give me just that one number, with no other results or breakdowns.

**Gold SQL preview:**

```sql
SELECT SUM(CASE WHEN co.colour = 'No Colour' THEN 1 ELSE 0 END) - SUM(CASE WHEN co.colour = 'Blue' THEN 1 ELSE 0 END) AS diff FROM superhero AS s JOIN colour AS co ON co.id = s.eye_colour_id WHERE s.weight_kg = 0 OR s.weight_kg IS NULL
```

**Agent SQL preview:**

```sql
SELECT
    (SELECT COUNT(*)
     FROM superhero s
     JOIN colour c ON c.id = s.eye_colour_id
     WHERE s.weight_kg IS NULL AND c.colour = 'No Colour')
  - (SELECT COUNT(*)
     FROM superhero s
     JOIN colour c ON c.id = s.eye_colour_id
     WHERE s.weight_kg IS NULL AND c.colour = 'Blue') AS difference;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold defines missing weight as weight_kg=0 OR NULL; agent tests NULL only.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

## Database: `thrombosis_prediction`

<a id="q389"></a>
### Q389 — challenging · incorrect_result

**Question:** How many distinct female patients have a normal anti-Scl-70 result and no recorded non-null symptom on any examination?

**Evidence:** Normal anti-Scl-70 is recorded as 'negative' or '0'.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(*) FROM Patient AS p WHERE p.SEX = 'F' AND EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.SC170 IN ('negative', '0')) AND NOT EXISTS (SELECT 1 FROM Examination AS e WHERE e.ID = p.ID AND e.Symptoms IS NOT NULL)
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold uses Patient.SEX='F', while agent filters text 'female' (encoded value mismatch).

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(DISTINCT p.ID) AS patient_count FROM Patient p WHERE lower(trim(p.SEX)) = 'female' AND EXISTS ( SELECT 1 FROM Laboratory l WHERE l.ID = p.ID A` → {"columns":["patient_count"],"rows":[[0]],"truncated":false}


<a id="q398"></a>
### Q398 — challenging · incorrect_result

**Question:** Among the thrombosis registry patients followed at the outpatient clinic, how many have a non-normal hematocrit and an anti-ribonuclear protein measurement above 16? I need a single count. A patient counts if they have at least one hematocrit reading outside the normal range, regardless of test date, and at least one anti-ribonuclear protein reading above 16, regardless of test date. Include every patient in the registry, not only those with a recorded thrombosis event.

**Evidence:** Hematocrit is normal when the value lies strictly between 29 and 52; outside that range it is abnormal. A negative anti-ribonuclear protein result means none was detected.

**Official Gold SQL** (full unless noted):

```sql
WITH cohort AS (SELECT DISTINCT p.ID FROM Patient p JOIN Laboratory l ON p.ID = l.ID WHERE p.Admission = '-' AND (l.HCT >= 52 OR l.HCT <= 29)) SELECT COUNT(DISTINCT l.ID) AS patient_count FROM Laboratory l WHERE l.ID IN (SELECT ID FROM cohort) AND l.RNP IS NOT NULL AND CAST(l.RNP AS REAL) > 16
```

**Agent final SQL:**

```sql
SELECT COUNT(*)
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
      AND l.RNP IS NOT NULL
      AND l.RNP <> 'negative'
      AND CAST(l.RNP AS REAL) > 16
);
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold requires p.Admission='-' for outpatient, but agent omits admission filter.

**Observed trace:** 12 model calls; 13 tool calls; 9 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT DISTINCT Admission FROM Patient` → {"columns":["Admission"],"rows":[["+"],["-"]],"truncated":false}  
Call 9: `SELECT COUNT(DISTINCT p.ID) FROM Patient p WHERE EXISTS (SELECT 1 FROM Laboratory l WHERE l.ID=p.ID AND l.HCT IS NOT NULL AND (l.HCT <= 29 OR l.HCT >= 52))` → {"columns":["COUNT(DISTINCT p.ID)"],"rows":[[4]],"truncated":false}


<a id="q400"></a>
### Q400 — challenging · incorrect_result

**Question:** I'm studying patients who carry exactly the rheumatoid arthritis and Sjögren's syndrome overlap. Please look at each patient's own record and find those whose record names exactly rheumatoid arthritis and Sjögren's syndrome, in either order, and no other disease – a disease recorded only as suspected does not count as a diagnosis. For those patients, considering their whole recorded laboratory history regardless of date, I need two numbers: how many have had at least one laboratory result showing a normal platelet level, and how many have never had a laboratory result showing a normal platelet level – count a patient with no laboratory results at all as never having had a normal platelet result.

**Gold SQL preview:**

```sql
SELECT SUM(CASE WHEN EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.PLT > 100 AND l.PLT < 400) THEN 1 ELSE 0 END) AS had_normal_platelet_result, SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.PLT > 100 AND l.PLT < 400) THEN 1 ELSE 0 END) AS never_normal_platelet_result FROM Patient AS p WHERE LENGTH(LOWER(REPLACE(p.Diagnosis, ' ', ''))) - LENGTH(REPLACE(LOWER(REPLACE(p.Diagnosis, ' ', '')), ',', '')
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Agent SQL preview:**

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
WHERE REPLACE(REPLACE(TRIM(p.Diagnosis), ' ', ''), ',
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold requires an exact two-diagnosis RA/SJS overlap after normalization; agent uses a narrower set of capitalization/string variants.

**Observed trace:** 10 model calls; 10 tool calls; 6 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q411"></a>
### Q411 — challenging · incorrect_result

**Question:** In our autoimmune disease cohort, what percentage of thrombosis patients were diagnosed with SLE at the examination visit? I need the percentage on a 0-100 scale, rounded to two decimal places. Please use the diagnosis recorded at the examination visit, not the diagnosis on the patient's overall file. This is for a write-up on which diagnoses accompany thrombotic events in this cohort.

**Evidence:** SLE: systemic lupus erythematosus, an autoimmune disease; thrombosis: formation of a blood clot within a blood vessel

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(CAST(COUNT(DISTINCT CASE WHEN Diagnosis LIKE '%SLE%' THEN ID END) AS REAL) * 100 / COUNT(DISTINCT ID), 2) AS percentage FROM Examination WHERE Thrombosis > 0
```

**Agent final SQL:**

```sql
SELECT ROUND(
    100.0 * SUM(CASE WHEN Diagnosis LIKE 'SLE%' THEN 1 ELSE 0 END) / COUNT(*),
    2
) AS percentage
FROM Examination
WHERE Thrombosis > 0;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold counts distinct patient IDs; agent counts Examination rows, shifting percentage denominator.

**Observed trace:** 8 model calls; 9 tool calls; 5 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT Diagnosis, Thrombosis, COUNT(*) AS n FROM Examination GROUP BY Diagnosis, Thrombosis ORDER BY Diagnosis, Thrombosis` → {"columns":["Diagnosis","Thrombosis","n"],"rows":[[null,0,23],[null,2,1]],"truncated":true}  
Call 5: `SELECT COUNT(*) AS total_thrombosis_examinations, SUM(CASE WHEN Diagnosis = 'SLE' THEN 1 ELSE 0 END) AS sle_exact, SUM(CASE WHEN Diagnosis LIKE 'SLE%' THEN` → {"columns":["total_thrombosis_examinations","sle_exact","sle_prefixed"],"rows":[[12,4,6]],"truncated":false}


<a id="q412"></a>
### Q412 — challenging · incorrect_result

**Question:** For the thrombosis cohort, I need to describe how long admitted patients typically wait from their first hospital visit until their first examination. Please give me the average delay in days across admitted patients, based on each patient's own first visit and first examination, rounded to the nearest whole number. A patient counts as admitted whenever her admission entry carries a plus sign, regardless of anything else in that entry.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(AVG(gap), 0) AS average_days FROM (SELECT T1.ID, MIN(JULIANDAY(T3.`Examination Date`)) - JULIANDAY(T1.`First Date`) AS gap FROM Patient AS T1 INNER JOIN Examination AS T3 ON T1.ID = T3.ID WHERE T1.Admission LIKE '%+%' GROUP BY T1.ID)
```

**Agent final SQL:**

```sql
SELECT CAST(ROUND(AVG(julianday(first_exam) - julianday("First Date"))) AS INTEGER) AS average_delay_days
FROM (
    SELECT p.ID,
           p."First Date",
           MIN(e."Examination Date") AS first_exam
    FROM Patient AS p
    JOIN Examination AS e ON e.ID = p.ID
    WHERE p.Admission LIKE '%+%'
      AND e.Thrombosis = 1
      AND p."First Date" IS NOT NULL
    GROUP BY p.ID
);
```

**Assessment (CANDIDATE ROOT CAUSE):** Agent adds Examination.Thrombosis=1 absent from Gold population, instead of using every admitted patient's first examination.

**Observed trace:** 16 model calls; 16 tool calls; 12 SQL calls (0 tool errors, 3 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT p.ID, p.Admission, p.Diagnosis, p."First Date", min(e."Examination Date") AS first_exam FROM Patient p LEFT JOIN Examination e ON e.ID=p.ID GROUP BY` → {"columns":["ID","Admission","Diagnosis","First Date","first_exam"],"rows":[[2110,"+","RA susp.","1993-02-10",null],[11408,"+","PSS","1973-01-01",null]],"truncated":false}  
Call 12: `SELECT p.ID,p."First Date", min(e."Examination Date") first_exam, julianday(min(e."Examination Date"))-julianday(p."First Date") delay FROM Patient p JOIN ` → {"columns":["ID","First Date","first_exam","delay"],"rows":[[3192610,"1994-01-13","1995-07-07",540]],"truncated":false}


<a id="q417"></a>
### Q417 — challenging · incorrect_result

**Question:** In this cohort, I want to compare the most extreme total cholesterol (T-CHO) readings between patients admitted to the hospital and those followed at the outpatient clinic. Please give me, for each of the two groups, the single highest T-CHO reading, along with the admission status ('+' admitted, '-' outpatient) and the patient ID whose reading is the group's highest. List the admitted group's row first, then the outpatient group's. If several patients tie at a group's highest reading, list each of them.

**Gold SQL preview:**

```sql
SELECT l.`T-CHO` AS `T-CHO`, p.Admission AS status, p.ID FROM Patient p JOIN Laboratory l ON l.ID = p.ID JOIN (SELECT p2.Admission AS adm, MAX(l2.`T-CHO`) AS mx FROM Patient p2 JOIN Laboratory l2 ON l2.ID = p2.ID WHERE p2.Admission IN ('+', '-') GROUP BY p2.Admission) t ON t.adm = p.Admission AND t.mx = l.`T-CHO` ORDER BY CASE p.Admission WHEN '+' THEN 0 ELSE 1 END, p.ID
```

**Agent SQL preview:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold output order is T-CHO, Admission status, Patient ID; agent returns Admission, T-CHO, Patient ID. Verify scoring shape.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q430"></a>
### Q430 — challenging · incorrect_result

**Question:** In the thrombosis and autoimmune-disease cohort, I want to compare how often lactate dehydrogenase stays in the normal range between patients admitted to the hospital and patients followed at the outpatient clinic. Please give me one row per patient group showing the number of lactate dehydrogenase measurements within the normal range recorded for that group, with the admitted group's row first. Label the rows 'admitted to the hospital' for the Admission = '+' group and 'followed at the outpatient clinic' for the Admission = '-' group. Every laboratory measurement recorded for those patients across the whole study period counts. Nothing else is needed.

**Evidence:** The normal range for lactate dehydrogenase means a value below 500.

**Official Gold SQL** (full unless noted):

```sql
SELECT CASE WHEN P.Admission = '+' THEN 'admitted to the hospital' ELSE 'followed at the outpatient clinic' END AS patient_group, COUNT(*) AS normal_ldh_measurements FROM Patient AS P JOIN Laboratory AS L ON P.ID = L.ID WHERE P.Admission IN ('+', '-') AND L.LDH < 500 GROUP BY 1 ORDER BY CASE P.Admission WHEN '+' THEN 0 ELSE 1 END
```

**Agent final SQL:**

```sql
SELECT
    CASE p.Admission
        WHEN '+' THEN 'admitted to the hospital'
        WHEN '-' THEN 'followed at the outpatient clinic'
    END AS patient_group,
    COUNT(*) AS normal_ldh_measurements
FROM Patient AS p
JOIN Laboratory AS l ON l.ID = p.ID
WHERE p.Admission IN ('+', '-')
  AND (
      p.Diagnosis LIKE '%APS%'
      OR p.Diagnosis LIKE '%MCTD%'
      OR p.Diagnosis LIKE '%SLE%'
  )
  AND l.LDH < 500
GROUP BY p.Admission
ORDER BY CASE p.Admission WHEN '+' THEN 1 WHEN '-' THEN 2 END;
```

**Assessment (CANDIDATE ROOT CAUSE):** Agent adds APS/MCTD/SLE Diagnosis filters that the question and Gold do not require.

**Observed trace:** 11 model calls; 12 tool calls; 8 SQL calls (0 tool errors, 4 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT Diagnosis, Admission, COUNT(*) AS patients FROM Patient GROUP BY Diagnosis, Admission ORDER BY Diagnosis, Admission` → {"columns":["Diagnosis","Admission","patients"],"rows":[["","-",1],["AGA","+",1]],"truncated":true}  
Call 8: `SELECT p.Admission, COUNT(*) AS n FROM Patient p JOIN Laboratory l ON l.ID=p.ID WHERE l.LDH < 500 AND (p.Diagnosis LIKE '%APS%' OR p.Diagnosis LIKE '%MCTD%` → {"columns":["Admission","n"],"rows":[["+",2093],["-",1893]],"truncated":false}


<a id="q438"></a>
### Q438 — challenging · incorrect_result

**Question:** I'm reviewing patients with an elevated anti-ribonuclear protein result. Among patients who ever had an anti-ribonuclear protein result of 16 or higher, I want to follow up the three whose liver enzymes stayed in the normal range. The normal range for GPT is below 60. For each patient, take their highest GPT value among their laboratory tests that fall in the normal range. Rank patients from that highest value down; if two patients share the same value, the one with the smaller patient ID comes first. Please return exactly three patients, one row per patient, with only each patient's Birthday.

**Gold SQL preview:**

```sql
SELECT T1.Birthday FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE T2.GPT < 60 AND T1.ID IN (SELECT ID FROM Laboratory WHERE CAST(RNP AS REAL) >= 16) GROUP BY T1.ID ORDER BY MAX(T2.GPT) DESC, T1.ID ASC LIMIT 3
```

**Agent SQL preview:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold takes MAX(GPT) among tests with GPT<60; agent requires all GPT tests be normal, excluding patients with any abnormal test.

**Observed trace:** 6 model calls; 7 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q443"></a>
### Q443 — challenging · incorrect_result

**Question:** I'm putting together a cohort summary and need one number: how many patients followed at the outpatient clinic (admission marker '-') have a most recent IgG lab result of 2000 or higher? By most recent, I mean the IgG measurement with the greatest laboratory date for that patient - since a patient has at most one lab record per date, there should be no ambiguity.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH latest_igg AS (SELECT ID, MAX(Date) AS LastDate FROM Laboratory WHERE IGG IS NOT NULL GROUP BY ID) SELECT COUNT(*) AS patient_count FROM Patient AS p JOIN latest_igg AS li ON li.ID = p.ID JOIN Laboratory AS l ON l.ID = li.ID AND l.Date = li.LastDate WHERE p.Admission = '-' AND l.IGG >= 2000
```

**Agent final SQL:**

```sql
SELECT COUNT(*) AS patient_count
FROM Patient AS p
WHERE p.Admission = '-'
  AND EXISTS (
    SELECT 1
    FROM Laboratory AS l
    WHERE l.ID = p.ID
      AND l.Date = (
        SELECT MAX(l2.Date)
        FROM Laboratory AS l2
        WHERE l2.ID = p.ID
      )
      AND l.IGG >= 2000
  );
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold selects latest Laboratory date with a non-NULL IGG measurement, agent finds latest date among all lab rows.

**Observed trace:** 4 model calls; 4 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(*) AS patient_count FROM Patient AS p WHERE p.Admission = '-' AND EXISTS ( SELECT 1 FROM Laboratory AS l WHERE l.ID = p.ID AND l.Date = (SELEC` → {"columns":["patient_count"],"rows":[[11]],"truncated":false}


<a id="q447"></a>
### Q447 — challenging · incorrect_result

**Question:** In the thrombosis prediction cohort, I want to gauge how often the most recent anti-ribonuclear protein measurement among female patients was markedly elevated while CPK stayed low at that same measurement. Please give me a single integer: the number of female patients whose most recent anti-ribonuclear protein titer was above 64 and whose CPK from that same laboratory record was below 250. Above 64 means strictly greater than 64, and below 250 means strictly less than 250.

**Evidence:** Anti-ribonuclear protein is an autoantibody measured as a titer in the blood; a negative result means the antibody was not detected.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(DISTINCT p.ID) AS female_patients FROM Patient AS p JOIN Laboratory AS l ON l.ID = p.ID WHERE p.SEX = 'F' AND l.RNP IS NOT NULL AND l.Date = (SELECT MAX(l2.Date) FROM Laboratory AS l2 WHERE l2.ID = p.ID AND l2.RNP IS NOT NULL) AND CAST(l.RNP AS REAL) > 64 AND l.CPK < 250
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold selects latest non-NULL RNP measurement; agent selects latest lab row regardless of RNP.

**Observed trace:** 5 model calls; 6 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT RNP, COUNT(*) AS n FROM Laboratory GROUP BY RNP ORDER BY n DESC LIMIT 30;` → {"columns":["RNP","n"],"rows":[[null,13765],["0",72]],"truncated":false}  
Call 2: `SELECT COUNT(*) FROM (SELECT l.ID, l.RNP, l.CPK, ROW_NUMBER() OVER (PARTITION BY l.ID ORDER BY l.Date DESC) rn FROM Laboratory l JOIN Patient p ON p.ID=l.I` → {"columns":["COUNT(*)"],"rows":[[0]],"truncated":false}


## Database: `toxicology`

<a id="q472"></a>
### Q472 — challenging · incorrect_result

**Question:** Among carcinogenic molecules, what percentage contain no fluorine atoms? Round to two decimal places.

**Evidence:** A '+' carcinogenicity label means carcinogenic.

**Official Gold SQL** (full unless noted):

```sql
SELECT ROUND(100.0 * SUM(CASE WHEN NOT EXISTS ( SELECT 1 FROM atom AS a WHERE a.molecule_id = m.molecule_id AND a.element = 'f' ) THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) FROM molecule AS m WHERE m.label = '+'
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Toxicology stores fluorine as lowercase element='f'; agent checks uppercase 'F'.

**Observed trace:** 4 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(*) AS carcinogenic_count, SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM atom a WHERE a.molecule_id=m.molecule_id AND a.element='F') THEN 1 ELSE 0 EN` → {"columns":["carcinogenic_count","no_fluorine_count","percentage"],"rows":[[152,152,100]],"truncated":false}


<a id="q478"></a>
### Q478 — challenging · incorrect_result

**Question:** What fraction of all atoms in molecule TR006 are hydrogen? Give the fraction and the molecule's recorded carcinogenicity label.

**Gold SQL preview:**

```sql
WITH SubQuery AS (SELECT DISTINCT T1.atom_id, T1.element, T1.molecule_id, T2.label FROM atom AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id WHERE T2.molecule_id = 'TR006') SELECT CAST(COUNT(CASE WHEN element = 'h' THEN atom_id ELSE NULL END) AS REAL) / (CASE WHEN COUNT(atom_id) = 0 THEN NULL ELSE COUNT(atom_id) END) AS ratio, label FROM SubQuery GROUP BY label
```

**Agent SQL preview:**

```sql
SELECT
  SUM(CASE WHEN LOWER(a.element) = 'h' THEN 1 ELSE 0 END) || '/' || COUNT(*) AS hydrogen_fraction,
  m.label AS carcinogenicity_label
FROM atom AS a
JOIN molecule AS m ON m.molecule_id = a.molecule_id
WHERE m.molecule_id = 'TR006'
GROUP BY m.molecule_id, m.label;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold outputs a numeric hydrogen fraction; agent produces a text fraction like 'x/y', changing result value/type.

**Observed trace:** 7 model calls; 8 tool calls; 4 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q480"></a>
### Q480 — challenging · incorrect_result

**Question:** In our toxicology library, how many carbon-carbon pairs joined by a double bond are there in total across the carcinogenic compounds? I want a single number for the whole library.

**Gold SQL preview:**

```sql
SELECT COUNT(*) AS num_pairs FROM connected AS c JOIN bond AS b ON b.bond_id = c.bond_id JOIN molecule AS m ON m.molecule_id = b.molecule_id JOIN atom AS a1 ON a1.atom_id = c.atom_id JOIN atom AS a2 ON a2.atom_id = c.atom_id2 WHERE m.label = '+' AND b.bond_type = '=' AND a1.element = 'c' AND a2.element = 'c' AND c.atom_id < c.atom_id2
```

**Agent SQL preview:**

```sql
SELECT COUNT(*) AS cc_double_bonds
FROM bond b
JOIN molecule m ON m.molecule_id = b.molecule_id
WHERE m.label = '+'
  AND b.bond_type = '='
  AND EXISTS (
    SELECT 1
    FROM connected c
    JOIN atom a ON a.atom_id = c.atom_id
    WHERE c.bond_id = b.bond_id
      AND LOWER(a.element) = 'c'
  )
  AND EXISTS (
    SELECT 1
    FROM connected c
    JOIN atom a ON a.atom_id = c.atom_id2
    WHERE c.bond_id = b.bond_id
      AND LOWER(a.element) =
-- [Excerpt cut; consult linked authoritative source for full SQL.]
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold requires both endpoints of a carbon-carbon double bond and canonical connected pair c.atom_id<c.atom_id2; agent counts bonds via EXISTS on ends without that pair condition.

**Observed trace:** 7 model calls; 9 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

<a id="q481"></a>
### Q481 — challenging · incorrect_result

**Question:** Among the molecules labeled '+' (carcinogenic), which chemical element is the most common among the atoms that take part in at least one bond? Also give the percentage of all atoms in those '+' molecules that this element accounts for, rounded to two decimal places. Count the percentage over every atom of the '+' molecules, whether or not it takes part in a bond. If several elements tie for most common, report each of them.

**Evidence:** _(no additional evidence)_

**Official Gold SQL** (full unless noted):

```sql
WITH plus_atoms AS (SELECT a.atom_id, a.element FROM atom a JOIN molecule m ON m.molecule_id = a.molecule_id WHERE m.label = '+'), bonded AS (SELECT atom_id, element FROM plus_atoms WHERE atom_id IN (SELECT atom_id FROM connected) OR atom_id IN (SELECT atom_id2 FROM connected)), bonded_counts AS (SELECT element, COUNT(*) AS n FROM bonded GROUP BY element), top AS (SELECT MAX(n) AS mx FROM bonded_counts), all_counts AS (SELECT element, COUNT(*) AS na FROM plus_atoms GROUP BY element), total AS (SELECT COUNT(*) AS tot FROM plus_atoms) SELECT bc.element, ROUND(100.0 * ac.na / t.tot, 2) AS pct FROM bonded_counts bc JOIN top ON bc.n = top.mx JOIN all_counts ac ON ac.element = bc.element CROSS JOIN total t ORDER BY bc.element
```

**Agent final SQL:**

```sql
WITH plus_atoms AS (
    SELECT a.atom_id, a.element
    FROM atom AS a
    JOIN molecule AS m ON m.molecule_id = a.molecule_id
    WHERE m.label = '+'
),
bonded_atoms AS (
    SELECT DISTINCT pa.atom_id, pa.element
    FROM plus_atoms AS pa
    WHERE EXISTS (
        SELECT 1
        FROM connected AS c
        WHERE c.atom_id = pa.atom_id OR c.atom_id2 = pa.atom_id
    )
),
element_counts AS (
    SELECT element, COUNT(*) AS bonded_atom_count
    FROM bonded_atoms
    GROUP BY element
)
SELECT element,
       ROUND(100.0 * bonded_atom_count / (SELECT COUNT(*) FROM plus_atoms), 2)
           AS percent_of_all_plus_atoms
FROM element_counts
WHERE bonded_atom_count = (SELECT MAX(bonded_atom_count) FROM element_counts);
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold numerator uses bonded-atom frequency to select the top element, then computes percentage using that element's count across all positive-molecule atoms; agent uses bonded count in numerator.

**Observed trace:** 6 model calls; 9 tool calls; 3 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `WITH plus_atoms AS ( SELECT a.atom_id, a.element, a.molecule_id FROM atom a JOIN molecule m ON m.molecule_id=a.molecule_id WHERE m.label='+' ), bonded_atom` → {"columns":["element","bonded_atom_count","pct_all_plus_atoms"],"rows":[["h",1568,42.47]],"truncated":false}  
Call 3: `SELECT element, COUNT(*) FROM atom GROUP BY element ORDER BY COUNT(*) DESC LIMIT 20` → {"columns":["element","COUNT(*)"],"rows":[["h",4034],["c",3433]],"truncated":false}


<a id="q487"></a>
### Q487 — challenging · incorrect_result

**Question:** I'm building a control group of nitrogen-containing structures for a carcinogenicity review. How many molecules in the database contain at least one nitrogen atom, where none of those nitrogen atoms takes part in a double bond or a triple bond? A nitrogen held only by single bonds is fine; any nitrogen in a double or triple bond disqualifies the molecule. Molecules with no nitrogen at all don't count. I just need the single number of such molecules.

**Evidence:** Nitrogen refers to the element code 'n'; '=' denotes a double bond; '#' denotes a triple bond; '-' denotes a single bond.

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(*) AS number_of_molecules FROM molecule AS m WHERE EXISTS (SELECT 1 FROM atom AS a WHERE a.molecule_id = m.molecule_id AND a.element = 'n') AND NOT EXISTS (SELECT 1 FROM atom AS a2 INNER JOIN connected AS c ON c.atom_id = a2.atom_id OR c.atom_id2 = a2.atom_id INNER JOIN bond AS b ON b.bond_id = c.bond_id WHERE a2.molecule_id = m.molecule_id AND a2.element = 'n' AND b.bond_type <> '-')
```

**Agent final SQL:**

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

**Assessment (CANDIDATE ROOT CAUSE):** Gold checks a double/triple bond incident to nitrogen atoms; agent joins bonds at molecule granularity, potentially rejecting a molecule for bonds not involving nitrogen.

**Observed trace:** 5 model calls; 9 tool calls; 4 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(DISTINCT molecule_id) AS count FROM atom WHERE element = 'n'` → {"columns":["count"],"rows":[[187]],"truncated":false}  
Call 4: `SELECT COUNT(*) FROM molecule m WHERE EXISTS (SELECT 1 FROM atom a WHERE a.molecule_id=m.molecule_id AND a.element='n') AND NOT EXISTS (SELECT 1 FROM atom ` → {"columns":["COUNT(*)"],"rows":[[6]],"truncated":false}


<a id="q488"></a>
### Q488 — challenging · incorrect_result

**Question:** In the toxicology database, how many atoms are bonded to chlorine atoms, taken across all molecules? I want a single number. By chlorine I mean the element 'cl'.

**Evidence:** cl: chlorine

**Official Gold SQL** (full unless noted):

```sql
SELECT COUNT(DISTINCT T1.atom_id) AS bonded_atom_count FROM connected AS T1 INNER JOIN atom AS T2 ON T1.atom_id2 = T2.atom_id WHERE T2.element = 'cl'
```

**Agent final SQL:**

```sql
SELECT COUNT(*) AS atoms_bonded_to_chlorine
FROM connected c
JOIN atom chlorine ON chlorine.atom_id = c.atom_id
WHERE LOWER(chlorine.element) = 'cl';
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold checks chlorine as connected.atom_id2 and DISTINCT connected.atom_id; agent reverses the endpoint and counts rows.

**Observed trace:** 6 model calls; 5 tool calls; 1 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT COUNT(*) AS atoms_bonded_to_chlorine FROM connected c JOIN atom cl_atom ON cl_atom.atom_id = c.atom_id JOIN atom bonded_atom ON bonded_atom.atom_id ` → {"columns":["atoms_bonded_to_chlorine"],"rows":[[314]],"truncated":false}


<a id="q494"></a>
### Q494 — challenging · incorrect_result

**Question:** I'm studying bond patterns in compounds that are not carcinogenic. For each element, how many double or triple bonds join a carbon atom to an atom of that element, across all non-carcinogenic molecules? Give me one row per element with the element and its count of such bonds—nothing else.

**Evidence:** A molecule labeled '-' is not carcinogenic; a molecule labeled '+' is carcinogenic.

**Official Gold SQL** (full unless noted):

```sql
SELECT a2.element AS element, COUNT(DISTINCT c.bond_id) AS bond_count FROM connected c JOIN bond b ON c.bond_id = b.bond_id JOIN atom a1 ON c.atom_id = a1.atom_id JOIN atom a2 ON c.atom_id2 = a2.atom_id JOIN molecule m ON b.molecule_id = m.molecule_id WHERE m.label = '-' AND a1.element = 'c' AND b.bond_type != '-' GROUP BY a2.element ORDER BY a2.element
```

**Agent final SQL:**

```sql
SELECT a2.element AS element, COUNT(*) AS bond_count
FROM connected c
JOIN atom a1 ON a1.atom_id = c.atom_id
JOIN atom a2 ON a2.atom_id = c.atom_id2
JOIN bond b ON b.bond_id = c.bond_id
JOIN molecule m ON m.molecule_id = b.molecule_id
WHERE m.label = '-'
  AND a1.element = 'c'
  AND b.bond_type IN ('=', '#')
GROUP BY a2.element
ORDER BY a2.element;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold COUNT(DISTINCT c.bond_id); agent COUNT(*) and restricts exact bond-type literals, which can change count.

**Observed trace:** 11 model calls; 14 tool calls; 8 SQL calls (0 tool errors, 1 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT name FROM sqlite_master WHERE type='table';` → {"columns":["name"],"rows":[["atom"],["bond"]],"truncated":false}  
Call 8: `SELECT a1.element AS e1, a2.element AS e2, b.bond_type, COUNT(*) AS n FROM connected c JOIN atom a1 ON a1.atom_id=c.atom_id JOIN atom a2 ON a2.atom_id=c.at` → {"columns":["e1","e2","bond_type","n"],"rows":[["c","c","=",1106],["c","n","#",2]],"truncated":false}


<a id="q498"></a>
### Q498 — challenging · incorrect_result

**Question:** In the toxicology compound database, which elements take part in a triple bond, and how widely are they distributed across the tested compounds? For each such element, give me its element symbol and the number of molecules that contain that element. Order the results from the most widespread element to the least; where two elements have equal counts, list them alphabetically by element symbol.

**Evidence:** The '#' bond-type symbol denotes a triple bond.

**Official Gold SQL** (full unless noted):

```sql
SELECT a.element AS element, COUNT(DISTINCT a.molecule_id) AS n_molecules FROM atom AS a WHERE a.element IN (SELECT at.element FROM bond AS b JOIN connected AS c ON b.bond_id = c.bond_id JOIN atom AS at ON c.atom_id = at.atom_id WHERE b.bond_type = '#') GROUP BY a.element ORDER BY n_molecules DESC, a.element
```

**Agent final SQL:**

```sql
SELECT a.element AS element_symbol,
       COUNT(DISTINCT a.molecule_id) AS molecule_count
FROM atom AS a
JOIN bond AS b
  ON a.molecule_id = b.molecule_id
WHERE b.bond_type = '#'
  AND a.element IS NOT NULL
GROUP BY a.element
ORDER BY molecule_count DESC, element_symbol ASC;
```

**Assessment (CANDIDATE ROOT CAUSE):** Gold first identifies chemical elements involved in triple bonds, then counts molecules containing each element anywhere; agent counts all elements in any molecule with triple bond.

**Observed trace:** 5 model calls; 7 tool calls; 2 SQL calls (0 tool errors, 0 truncated SQL results). Final score: **EX=0 / incorrect_result**. 

Call 1: `SELECT bond_type, COUNT(*) FROM bond GROUP BY bond_type` → {"columns":["bond_type","COUNT(*)"],"rows":[["#",5],["-",7743]],"truncated":false}  
Call 2: `SELECT a.element, COUNT(DISTINCT a.molecule_id) AS molecule_count FROM atom a JOIN bond b ON a.molecule_id = b.molecule_id WHERE b.bond_type = '#' AND a.el` → {"columns":["element","molecule_count"],"rows":[["c",2],["cl",2]],"truncated":false}



---

## Appendix B — Additional Mini-Dev 2026 SQL & Trace Reviews (2026-11-09)

**Method:** 17 new cases below supplement the 97 earlier case studies. These are directly compared with the **same pinned official 2026 Gold SQL**, archived final Agent SQL and observable structured tool calls. The remaining 51 new/previous cases without a standalone case-study section are summarized in the [full 165-case inventory](failure-inventory.csv). Reference SQL is **offline research only** and must never enter agent prompts or retrieval.

| Database | Newly documented cases |
| --- | --- |
| `california_schools` | [Q4](#q4), [Q6](#q6) |
| `card_games` | [Q67](#q67), [Q86](#q86), [Q115](#q115) |
| `codebase_community` | [Q131](#q131) |
| `debit_card_specializing` | [Q153](#q153) |
| `european_football_2` | [Q172](#q172) |
| `financial` | [Q203](#q203), [Q216](#q216), [Q223](#q223) |
| `formula_1` | [Q258](#q258) |
| `superhero` | [Q354](#q354) |
| `thrombosis_prediction` | [Q406](#q406), [Q420](#q420) |
| `toxicology` | [Q497](#q497), [Q499](#q499) |

<a id="q4"></a>
### Q4 — california_schools · Unsupported/missing filter (candidate)

**Official question:** What are the mailing street address and name of the school with the seventh-highest recorded average mathematics score?

**Evidence:** _(none supplied)_

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT sc.MailStreet, sc.School FROM satscores AS sat JOIN schools AS sc ON sc.CDSCode = sat.cds WHERE sat.rtype = 'S' AND sat.AvgScrMath IS NOT NULL ORDER BY sat.AvgScrMath DESC, sat.cds LIMIT 1 OFFSET 6
```

**Archived Agent final SQL:**

```sql
SELECT s.MailStreet, s.School
FROM satscores AS sat
JOIN schools AS s ON sat.cds = s.CDSCode
WHERE sat.AvgScrMath IS NOT NULL
ORDER BY sat.AvgScrMath DESC
LIMIT 1 OFFSET 6;
```

**Observed difference / candidate mechanism:** Omitted SAT school-level rtype=S restriction and deterministic tie-break. This is not a proven causal repair.

**Observable trace:** 4 model calls, 4 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(satscores) → inspect_table(schools) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["MailStreet","School","AvgScrMath"],"rows":[["25 Churchill Avenue",null,671]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q6"></a>
### Q6 — california_schools · Measure source/grain (candidate)

**Official question:** Which schools served a grade span of Kindergarten to 9th grade in the county of Los Angeles and what is its Percent (%) Eligible FRPM (Ages 5-17)?

**Evidence:** FRPM eligibility percentage is free-or-reduced-price meal recipients divided by same-age-band enrollment, times 100.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT T2.School, T1.`FRPM Count (Ages 5-17)` * 100 / T1.`Enrollment (Ages 5-17)` FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Los Angeles' AND T2.GSserved = 'K-9'
```

**Archived Agent final SQL:**

```sql
SELECT s.School, f."Percent (%) Eligible FRPM (Ages 5-17)"
FROM schools AS s
JOIN frpm AS f ON s.CDSCode = f.CDSCode
WHERE s.County = 'Los Angeles'
  AND s.GSserved = 'K-9';
```

**Observed difference / candidate mechanism:** Used stored eligibility percentage instead of specified FRPM count / enrollment * 100. This is not a proven causal repair.

**Observable trace:** 4 model calls, 4 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(schools) → inspect_table(frpm) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["School","GSserved","Percent (%) Eligible FRPM (Ages 5-17)"],"rows":[["White Oak Elementary","K-9",0.0375586854460094],["The Accelerated","K-9",0.976388888888889]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q67"></a>
### Q67 — card_games · Aggregation/population (candidate)

**Official question:** How many rulings were issued for Mishra's Factory on the latest date any ruling for it exists? By "latest date" I mean the most recent calendar date on which any ruling for the card exists, and by Mishra's Factory I mean the card by that name across all of its printings. I only want that count.

**Evidence:** ruling: an official rules statement issued for a card on a given date

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT COUNT(DISTINCT T2.text) AS ruling_count FROM cards AS T1 INNER JOIN rulings AS T2 ON T1.uuid = T2.uuid WHERE T1.name = 'Mishra''s Factory' AND T2.date = (SELECT MAX(T4.date) FROM cards AS T3 INNER JOIN rulings AS T4 ON T3.uuid = T4.uuid WHERE T3.name = 'Mishra''s Factory')
```

**Archived Agent final SQL:**

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

**Observed difference / candidate mechanism:** COUNT(*) across printings vs distinct ruling texts on latest date. This is not a proven causal repair.

**Observable trace:** 5 model calls, 4 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(rulings) → inspect_table(cards) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["date","ruling_count"],"rows":[["2016-06-08",46]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q86"></a>
### Q86 — card_games · Value/encoded semantics (candidate)

**Official question:** Among the Commander-leadable cards that the Card Kingdom catalog lists for both a foil printing and a regular non-foil printing – cards listed for only one of the two printings don't count – I want the single most recent card frame year (the latest calendar year among the frame versions), and the count of cards in that group whose frame version is that year. Please return just that one row: the frame year and its card count.

**Evidence:** A card 'may lead a Commander deck' if it can be the deck's commander – the one card that leads the deck and sets its color identity – not merely be included among the deck's other cards.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH cmd AS (SELECT frameVersion, substr(leadershipSkills, instr(leadershipSkills, 'commander')) AS tail FROM cards WHERE cardKingdomId IS NOT NULL AND cardKingdomFoilId IS NOT NULL) SELECT frameVersion AS frame_year, COUNT(*) AS card_count FROM cmd WHERE substr(tail, length('commander') + length('True'), length('True')) = 'True' GROUP BY frameVersion ORDER BY CAST(frameVersion AS INTEGER) DESC LIMIT 1
```

**Archived Agent final SQL:**

```sql
SELECT '2015' AS frame_year, COUNT(*) AS card_count
FROM cards
WHERE leadershipSkills LIKE '%commander%'
  AND leadershipSkills LIKE '%True%'
  AND cardKingdomFoilId IS NOT NULL
  AND cardKingdomId IS NOT NULL
  AND frameVersion = '2015';
```

**Observed difference / candidate mechanism:** Hardcodes year 2015 and matches leadershipSkills with broad LIKE rather than field-specific semantics. This is not a proven causal repair.

**Observable trace:** 10 model calls, 9 tool calls, 7 SQL calls; 1 SQL-tool errors. list_tables → inspect_table(cards) → execute_sql → execute_sql → execute_sql → execute_sql → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["name","type","setCode","frameVersion","cardKingdomFoilId","cardKingdomId","leadershipSkills"],"rows":[["Oriss, Samite Guardian","Legendary Creature — Human Cleric","FUT","future","122545","122365","{'brawl': False, 'commander': True, 'oathbreaker': False}"],["Linessa, Zephyr Mage","Legendary Creature — Human Wizard","FUT","future","122568","122388","{'brawl': False, 'commander': True, 'oathbreaker': False}"],["Korlash, Heir to Blackblade","Legendary Creature — Zombie Warrior","FUT",

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q115"></a>
### Q115 — card_games · Measure source/grain (candidate)

**Official question:** Among the Commander-type expansion sets released in calendar year 2020 (1 January 2020 to 31 December 2020), I need the one with the highest total card count, so we can plan translation work. Please send me the set's id from the sets listing, its name, and the number of official languages it was released in. The total card count should include promotional and related supplemental products, but exclude Alchemy modifications. If two sets tie for the highest total card count, list each of them, ordered by set id ascending.

**Evidence:** Commander: a multiplayer expansion type of the game. Alchemy modifications: online-only variant versions of cards.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH cohort AS (SELECT * FROM sets WHERE type = 'commander' AND releaseDate >= '2020-01-01' AND releaseDate <= '2020-12-31') SELECT c.id, c.name, COUNT(DISTINCT st.language) AS languages FROM cohort c LEFT JOIN set_translations st ON st.setCode = c.code WHERE c.totalSetSize = (SELECT MAX(totalSetSize) FROM cohort) GROUP BY c.id, c.name ORDER BY c.id ASC
```

**Archived Agent final SQL:**

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

**Observed difference / candidate mechanism:** Recalculates total card count from card rows rather than sets.totalSetSize; adds output column, LIMIT 1. This is not a proven causal repair.

**Observable trace:** 11 model calls, 10 tool calls, 6 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(sets) → inspect_table(set_translations) → inspect_table(cards) → execute_sql → execute_sql → execute_sql → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["id","name","code","total_card_count","official_language_count"],"rows":[[44,"Commander 2020","C20",323,0]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q131"></a>
### Q131 — codebase_community · Aggregation/population (candidate)

**Official question:** I'm profiling the authors behind poorly received R posts to see if they tend to be low-reputation members. Can you give me the average reputation of the users who own posts tagged with the R tag that have a score below 20? Just the single number, rounded to the nearest whole number.

**Evidence:** 'r' is the tag used on this site for the R programming language for statistical computing.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT ROUND(AVG(u.Reputation)) AS avg_reputation FROM users u WHERE u.Id IN (SELECT p.OwnerUserId FROM posts p WHERE p.Score < 20 AND p.Tags LIKE '%' || '<' || 'r' || '>' || '%')
```

**Archived Agent final SQL:**

```sql
SELECT ROUND(AVG(u.Reputation)) AS average_reputation
FROM posts p
JOIN users u ON u.Id = p.OwnerUserId
WHERE p.Score < 20
  AND p.Tags LIKE '%<r>%';
```

**Observed difference / candidate mechanism:** AVG reputation per matching post instead of distinct matching user. This is not a proven causal repair.

**Observable trace:** 4 model calls, 5 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(posts) → inspect_table(tags) → inspect_table(users) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["average_reputation"],"rows":[[499]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q153"></a>
### Q153 — debit_card_specializing · Unsupported/missing filter (candidate)

**Official question:** I'm reviewing our 2012 performance and want to see which client segments hold our small-scale customers. For each client segment, can you tell me how many customers had total consumption below 30,000 over the whole of 2012? Please count only customers who used their cards at some point during 2012, and treat 30,000 as a strict limit - someone at exactly 30,000 doesn't count. I just need the client segment and the number of such customers per segment.

**Evidence:** Consumption means the amount spent through a customer's fuel cards.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH yearly AS (SELECT CustomerID, SUM(Consumption) AS total_consumption FROM yearmonth WHERE Date >= '201201' AND Date <= '201212' GROUP BY CustomerID HAVING SUM(Consumption) < 30000) SELECT c.Segment AS segment, COUNT(*) AS customers FROM yearly AS y INNER JOIN customers AS c ON c.CustomerID = y.CustomerID GROUP BY c.Segment ORDER BY c.Segment
```

**Archived Agent final SQL:**

```sql
WITH active_customers AS (
    SELECT DISTINCT CustomerID
    FROM transactions_1k
    WHERE Date >= '2012-01-01'
      AND Date < '2013-01-01'
),
customer_consumption AS (
    SELECT CustomerID, SUM(Consumption) AS total_consumption
    FROM yearmonth
    WHERE Date >= '201201'
      AND Date < '201301'
    GROUP BY CustomerID
)
SELECT c.Segment, COUNT(*) AS customer_count
FROM active_customers a
JOIN customer_consumption cc ON cc.CustomerID = a.CustomerID
JOIN customers c ON c.CustomerID = a.CustomerID
WHERE cc.total_consumption < 30000
GROUP BY c.Segment
ORDER BY c.Segment;
```

**Observed difference / candidate mechanism:** Adds sampled transactions_1k activity cohort when Gold only checks yearmonth; may exclude customers. This is not a proven causal repair.

**Observable trace:** 5 model calls, 7 tool calls, 3 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(customers) → inspect_table(transactions_1k) → inspect_table(yearmonth) → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["Segment","customer_count"],"rows":[["KAM",20],["LAM",82],["SME",202]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q172"></a>
### Q172 — european_football_2 · Aggregation/population (candidate)

**Official question:** What is the average height, in centimetres, of the players taller than 180 cm who have appeared in the home team's number-3 lineup slot? This should cover the whole recorded match history with no season or date restriction. 'Taller than 180' means strictly taller than 180 cm. Please round the final average to two decimal places and return just that single value.

**Evidence:** Number-3 lineup slot: each match records a home team's starting eleven as eleven ordered player slots; the number-3 slot is the home team's third slot.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT ROUND(AVG(height), 2) AS avg_height FROM (SELECT p.height AS height FROM Player p JOIN Match m ON m.home_player_3 = p.player_api_id WHERE p.height > 180 GROUP BY p.player_api_id)
```

**Archived Agent final SQL:**

```sql
SELECT ROUND(AVG(p.height), 2) AS average_height_cm
FROM "Match" AS m
JOIN Player AS p ON p.player_api_id = m.home_player_3
WHERE p.height > 180;
```

**Observed difference / candidate mechanism:** Weights player height by number of match appearances instead of unique players. This is not a proven causal repair.

**Observable trace:** 4 model calls, 4 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(Match) → inspect_table(Player) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["average_height_cm"],"rows":[[187.05]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q203"></a>
### Q203 — financial · Output contract/representation (candidate)

**Official question:** We're reviewing our first month of operations. Looking at the districts where we opened at least one account during that first month, which district had the largest population, and how many inhabitants does it have? If several districts tie for the largest population, list all of them with their populations.

**Evidence:** The bank's first month of operation is the calendar month in which its earliest account was opened.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH first_month AS (SELECT strftime('%Y-%m', MIN(date)) AS ym FROM account), first_month_districts AS (SELECT DISTINCT district_id FROM account WHERE strftime('%Y-%m', date) = (SELECT ym FROM first_month)), cohort AS (SELECT d.A2 AS district_name, CAST(d.A4 AS INTEGER) AS inhabitants FROM district d JOIN first_month_districts f ON d.district_id = f.district_id) SELECT district_name, inhabitants FROM cohort WHERE inhabitants = (SELECT MAX(inhabitants) FROM cohort)
```

**Archived Agent final SQL:**

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

**Observed difference / candidate mechanism:** Returns TEXT population (observed "1204953") whereas Gold CASTs inhabitants to INTEGER. This is not a proven causal repair.

**Observable trace:** 4 model calls, 4 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(account) → inspect_table(district) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["district","population"],"rows":[["Hl.m. Praha","1204953"]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q216"></a>
### Q216 — financial · Measure source/grain (candidate)

**Official question:** I'm planning a regional campaign for female customers who hold a credit card and a loan, and I need a demographic profile per region. For each region, please give me: the region, the average district salary of the districts where these female clients live, and the average 1996 district unemployment rate of those same districts – both averages rounded to 2 decimal places. I also want the name of the most populous district among those districts in each region, so I know where to focus local advertising. A few rules: count only female clients who own the account (disposition type OWNER) and who have at least one credit card and at least one loan on that account. 'Most populous' means the district with the largest number of inhabitants; if two tie, take the one whose name comes first alphabetically. One row per region, and include every region that has at least one such client – nothing else.

**Evidence:** Disposition type OWNER means the client owns the account. Unemployment rate in 1996 is the district's unemployment rate for 1996; average salary is the district's average salary.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH cohort AS ( SELECT DISTINCT c.district_id FROM client c JOIN disp d ON d.client_id = c.client_id AND d.type = 'OWNER' WHERE c.gender = 'F' AND d.disp_id IN (SELECT disp_id FROM card) AND d.account_id IN (SELECT account_id FROM loan) ) SELECT di.A3 AS region, ROUND(AVG(di.A11), 2) AS average_district_salary, ROUND(AVG(di.A13), 2) AS average_unemployment_rate_1996, (SELECT di2.A2 FROM district di2 WHERE di2.district_id IN (SELECT district_id FROM cohort) AND di2.A3 = di.A3 ORDER BY CAST(di2.A4 AS INTEGER) DESC, di2.A2 LIMIT 1) AS most_populous_district FROM district di WHERE di.district_id IN (SELECT district_id FROM cohort) GROUP BY di.A3 ORDER BY di.A3
```

**Archived Agent final SQL:**

```sql
WITH eligible_districts AS (
    SELECT DISTINCT c.district_id
    FROM client AS c
    JOIN disp AS dp
        ON dp.client_id = c.client_id
    WHERE c.gender = 'F'
      AND dp.type = 'OWNER'
      AND EXISTS (
          SELECT 1
          FROM card AS ca
          WHERE ca.disp_id = dp.disp_id
      )
      AND EXISTS (
          SELECT 1
          FROM loan AS lo
          WHERE lo.account_id = dp.account_id
      )
)
SELECT
    d.A3 AS region,
    ROUND(AVG(d.A11), 2) AS avg_district_salary,
    ROUND(AVG(d.A13), 2) AS avg_unemployment_rate_1996,
    (
        SELECT d2.A2
        FROM district AS d2
        JOIN eligible_districts AS ed2
            ON ed2.district_id = d2.district_id
        WHERE d2.A3 = d.A3
        ORDER BY d2.A9 DESC, d2.A2 ASC
        LIMIT 1
    ) AS most_populous_district
FROM district AS d
JOIN eligible_districts AS ed
    ON ed.district_id = d.district_id
GROUP BY d.A3;
```

**Observed difference / candidate mechanism:** Uses A9 instead of A4 as district population for most-populous district. This is not a proven causal repair.

**Observable trace:** 5 model calls, 9 tool calls, 2 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(client) → inspect_table(disp) → inspect_table(account) → inspect_table(card) → inspect_table(loan) → inspect_table(district) → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["region","avg_salary","avg_unemployment_1996","most_populous_district"],"rows":[["Prague",12541,0.43,"Hl.m. Praha"],["central Bohemia",9318.3,3.18,"Mlada Boleslav"],["east Bohemia",8614.25,3.27,"Nachod"]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q223"></a>
### Q223 — financial · Aggregation/population (candidate)

**Official question:** I'm doing a lending review by account-opening year for my region. For accounts opened in the central Bohemia region from 1 January 1996 onward, broken down by the calendar year of the account creation date (as a text string like '1996', not an integer), I need: the number of accounts opened that year in the region, the total amount lent on those accounts, and the average across the districts of the amount lent per account opened in that district, rounded to two decimals. An account with no loan counts as having lent nothing.

**Evidence:** Central Bohemia is the region value recorded for districts in the region data; the amount lent on an account is the total of the loans granted on that account.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH cba AS ( SELECT a.account_id, a.district_id, STRFTIME('%Y', a.date) AS y FROM account a INNER JOIN district d ON a.district_id = d.district_id WHERE d.A3 = 'central Bohemia' AND a.date >= '1996-01-01' ), branch AS ( SELECT cba.y, cba.district_id, SUM(COALESCE(l.amount, 0)) * 1.0 / COUNT(DISTINCT cba.account_id) AS lent_per_account FROM cba LEFT JOIN loan l ON l.account_id = cba.account_id GROUP BY cba.y, cba.district_id ) SELECT yt.y AS opening_year, yt.accounts_opened, yl.total_lent, ROUND(b.avg_lent, 2) AS avg_amount_lent_per_account FROM ( SELECT y, COUNT(DISTINCT account_id) AS accounts_opened FROM cba GROUP BY y ) yt INNER JOIN ( SELECT y, SUM(l.amount) AS total_lent FROM cba LEFT JOIN loan l ON l.account_id = cba.account_id GROUP BY y ) yl ON yl.y = yt.y INNER JOIN ( SELECT y, AVG(lent_per_account) AS avg_lent FROM branch GROUP BY y ) b ON b.y = yt.y ORDER BY yt.y
```

**Archived Agent final SQL:**

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

**Observed difference / candidate mechanism:** Averages district lending rates after joining to each account, weighting districts by accounts. This is not a proven causal repair.

**Observable trace:** 5 model calls, 6 tool calls, 2 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(account) → inspect_table(district) → inspect_table(loan) → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["year","accounts_opened","total_amount_lent","avg_district_amount_lent_per_account"],"rows":[["1996",191,4887024,25586.51],["1997",114,1971468,17293.58]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q258"></a>
### Q258 — formula_1 · Aggregation/population (candidate)

**Official question:** I'm writing an article about the Italian Grand Prix and want to know which first names recur among the drivers who finished second in that race. For every forename carried by two or more runners-up of the Italian Grand Prix across all its editions in the data, please give me one row with the forename and the number of runners-up who carried it. Order the rows from the most runners-up to the fewest, and alphabetically by forename when two forenames are tied. Leave out any forename held by only one runner-up.

**Evidence:** A runner-up is the driver who finished second in an edition of the Italian Grand Prix.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT d.forename AS forename, COUNT(DISTINCT d.driverId) AS runner_ups FROM races AS r INNER JOIN results AS x ON x.raceId = r.raceId INNER JOIN drivers AS d ON d.driverId = x.driverId WHERE r.name = 'Italian Grand Prix' AND x.position = 2 GROUP BY d.forename HAVING COUNT(DISTINCT d.driverId) > 1 ORDER BY runner_ups DESC, d.forename
```

**Archived Agent final SQL:**

```sql
SELECT d.forename, COUNT(*) AS runner_up_count
FROM races AS ra
JOIN results AS re ON re.raceId = ra.raceId
JOIN drivers AS d ON d.driverId = re.driverId
WHERE ra.name = 'Italian Grand Prix'
  AND re.position = 2
GROUP BY d.forename
HAVING COUNT(*) >= 2
ORDER BY runner_up_count DESC, d.forename ASC;
```

**Observed difference / candidate mechanism:** COUNT(*) of runner-up results vs distinct driver IDs. This is not a proven causal repair.

**Observable trace:** 5 model calls, 6 tool calls, 2 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(races) → inspect_table(results) → inspect_table(drivers) → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["name","n"],"rows":[["Italian Grand Prix",1724]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q354"></a>
### Q354 — superhero · Entity/relationship/join (candidate)

**Official question:** For my cryokinesis page, I want to know how broad the power portfolios are around ice-powered heroes. Consider all heroes who share at least one superpower with a cryokinesis holder - including the cryokinesis holders themselves, since they share cryokinesis with each other. What is the average number of superpowers these heroes have, rounded to one decimal place? Please send back just that single number.

**Evidence:** Cryokinesis is the superpower to generate and control ice.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH sharers AS (SELECT DISTINCT hp2.hero_id FROM hero_power hp1 JOIN hero_power hp2 ON hp2.power_id = hp1.power_id WHERE hp1.hero_id IN (SELECT hero_id FROM hero_power WHERE power_id = (SELECT id FROM superpower WHERE power_name = 'Cryokinesis'))), counts AS (SELECT hero_id, COUNT(*) AS cnt FROM hero_power WHERE hero_id IN (SELECT hero_id FROM sharers) GROUP BY hero_id) SELECT ROUND(AVG(cnt), 1) AS avg_superpower_count FROM counts
```

**Archived Agent final SQL:**

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

**Observed difference / candidate mechanism:** Final query only shares Cryokinesis itself, not any power with a Cryokinesis holder; earlier executed SQL used broader relation. This is not a proven causal repair.

**Observable trace:** 4 model calls, 5 tool calls, 1 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(superpower) → inspect_table(hero_power) → inspect_table(superhero) → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["average_superpowers"],"rows":[[9.1]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q406"></a>
### Q406 — thrombosis_prediction · Output contract/representation (candidate)

**Official question:** I'm looking at patients whose anti-ribonuclear protein antibody measurement came out higher than 32. Of those patients, how many were women and how many were men? Note that 'higher than 32' means strictly above 32, not equal to it, and a patient qualifies if any of their laboratory measurements exceeded 32.

**Evidence:** A woman means a patient recorded as F, and a man means a patient recorded as M.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT COUNT(DISTINCT CASE WHEN T1.SEX = 'F' THEN T1.ID END) AS women, COUNT(DISTINCT CASE WHEN T1.SEX = 'M' THEN T1.ID END) AS men FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE CAST(T2.RNP AS REAL) > 32
```

**Archived Agent final SQL:**

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
GROUP BY p.SEX
ORDER BY p.SEX;
```

**Observed difference / candidate mechanism:** Two rows grouped by SEX rather than one row with women and men columns. This is not a proven causal repair.

**Observable trace:** 6 model calls, 7 tool calls, 3 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(Examination) → inspect_table(Laboratory) → inspect_table(Patient) → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["SEX","patient_count"],"rows":[["F",12]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q420"></a>
### Q420 — thrombosis_prediction · Output contract/representation (candidate)

**Official question:** I'm putting together a care-setting summary of severe SLE cases for the rheumatology department. Among patients diagnosed with SLE, considering only those whose only diagnosis is SLE and who had abnormally high proteinuria, how many were admitted to the hospital and how many were followed at the outpatient clinic? Please count each patient based on their full history at the hospital.

**Evidence:** Abnormally high proteinuria means a proteinuria level of 30 or higher.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT COUNT(DISTINCT CASE WHEN T1.Admission = '+' THEN T1.ID END) AS admitted_to_hospital, COUNT(DISTINCT CASE WHEN T1.Admission = '-' THEN T1.ID END) AS followed_at_outpatient_clinic FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE T1.Diagnosis = 'SLE' AND CAST(T2.`U-PRO` AS REAL) >= 30
```

**Archived Agent final SQL:**

```sql
SELECT
    CASE
        WHEN p.Admission = '+' THEN 'Hospital'
        WHEN p.Admission = '-' THEN 'Outpatient clinic'
    END AS care_setting,
    COUNT(DISTINCT p.ID) AS patient_count
FROM Patient AS p
WHERE p.Diagnosis = 'SLE'
  AND p.Admission IN ('+', '-')
  AND EXISTS (
      SELECT 1
      FROM Laboratory AS l
      WHERE l.ID = p.ID
        AND CASE
                WHEN l."U-PRO" = '>=1000' THEN 1000
                WHEN l."U-PRO" LIKE '>=%' THEN CAST(SUBSTR(l."U-PRO", 3) AS REAL)
                WHEN l."U-PRO" LIKE '+%(%' THEN CAST(
                    SUBSTR(
                        l."U-PRO",
                        INSTR(l."U-PRO", '(') + 1,
                        INSTR(l."U-PRO", ')') - INSTR(l."U-PRO", '(') - 1
                    ) AS REAL
                )
                WHEN l."U-PRO" GLOB '[0-9]*' THEN CAST(l."U-PRO" AS REAL)
                ELSE NULL
            END >= 30
  )
GROUP BY p.Admission
ORDER BY p.Admission DESC;
```

**Observed difference / candidate mechanism:** Returns care-setting rows rather than two counts as columns; custom U-PRO parsing differs from Gold CAST. This is not a proven causal repair.

**Observable trace:** 8 model calls, 9 tool calls, 5 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(Examination) → inspect_table(Laboratory) → inspect_table(Patient) → execute_sql → execute_sql → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["Admission","COUNT(*)"],"rows":[["",1],["+",13],["-",1]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.

<a id="q497"></a>
### Q497 — toxicology · Unresolved; further comparison needed (candidate)

**Official question:** I'm profiling the compound library and want to size the fully saturated portion of each element's atom population - atoms attached only by single bonds behave differently from unsaturated sites. For each element symbol in the database, how many atoms are connected only by single bonds and never part of any multiple bond? Please give me one row per element symbol with the element symbol and the number of such atoms, sorted alphabetically by element symbol. This should cover all compounds in the database. Note that an atom with no bonds at all doesn't count as being connected by single bonds, so exclude those.

**Evidence:** A single bond is a bond between two atoms sharing exactly one electron pair, denoted by the bond-type symbol '-'. A multiple bond is a double or triple bond, i.e. a bond between two atoms sharing more than one electron pair.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
WITH per_atom AS (SELECT a.atom_id AS atom_id, a.element AS element, CASE WHEN EXISTS (SELECT 1 FROM connected AS c WHERE c.atom_id = a.atom_id) AND NOT EXISTS (SELECT 1 FROM connected AS c JOIN bond AS b ON b.bond_id = c.bond_id WHERE c.atom_id = a.atom_id AND b.bond_type <> '-') THEN 1 ELSE 0 END AS saturated FROM atom AS a) SELECT element, SUM(saturated) AS atoms FROM per_atom GROUP BY element ORDER BY element
```

**Archived Agent final SQL:**

```sql
SELECT a.element, COUNT(DISTINCT a.atom_id) AS atom_count
FROM atom AS a
WHERE EXISTS (
    SELECT 1
    FROM connected AS c
    JOIN bond AS b ON b.bond_id = c.bond_id
    WHERE (c.atom_id = a.atom_id OR c.atom_id2 = a.atom_id)
      AND b.bond_type = '-'
)
AND NOT EXISTS (
    SELECT 1
    FROM connected AS c
    JOIN bond AS b ON b.bond_id = c.bond_id
    WHERE (c.atom_id = a.atom_id OR c.atom_id2 = a.atom_id)
      AND b.bond_type <> '-'
)
GROUP BY a.element
ORDER BY a.element;
```

**Observed difference / candidate mechanism:** Gold checks only connected.atom_id; agent checks both endpoints; reference/semantics QA needed. This is not a proven causal repair.

**Observable trace:** 7 model calls, 9 tool calls, 3 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(atom) → inspect_table(bond) → inspect_table(element) → inspect_table(connected) → inspect_table(molecule) → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["element","atom_count"],"rows":[["br",46],["c",1142],["cl",314]],"truncated":false}

**Review disposition:** Reference-QA candidate, unresolved: check source data and annotation before calling either SQL wrong.

<a id="q499"></a>
### Q499 — toxicology · Output contract/representation (candidate)

**Official question:** For molecule TR397, I want to see which elements form the bonding skeleton. For each element present among its atoms, how many atoms of that element take part in at least one bond? Please report two things per row: the element symbol (e.g. c, h, o) and the number of that element's atoms in TR397 that take part in a bond. One row per element, ordered alphabetically by element symbol. Only atoms belonging to TR397 should count.

**Evidence:** Takes part in a bond: the atom is one of the two atoms a bond joins.

**Official Gold SQL (pinned 2026 revision; offline evaluation only):**

```sql
SELECT a.element, COUNT(DISTINCT CASE WHEN c.bond_id IS NOT NULL THEN a.atom_id END) AS bonded_atoms FROM atom a LEFT JOIN connected c ON (c.atom_id = a.atom_id OR c.atom_id2 = a.atom_id) WHERE a.molecule_id = 'TR397' GROUP BY a.element ORDER BY a.element
```

**Archived Agent final SQL:**

```sql
SELECT a.element, COUNT(DISTINCT a.atom_id) AS bonded_atom_count
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

**Observed difference / candidate mechanism:** Agent omits elements with zero bonded atoms whereas Gold includes them with zero counts. This is not a proven causal repair.

**Observable trace:** 8 model calls, 10 tool calls, 4 SQL calls; 0 SQL-tool errors. list_tables → inspect_table(atom) → inspect_table(bond) → inspect_table(element) → inspect_table(molecule) → inspect_table(connected) → execute_sql → execute_sql → execute_sql → execute_sql. Last SQL tool result (not necessarily the submitted final SQL): {"columns":["element","bonded_atom_count"],"rows":[["c",34],["h",24],["n",6]],"truncated":false}

**Review disposition:** Provisional SQL/trace comparison; no fresh SQLite counterfactual execution.
