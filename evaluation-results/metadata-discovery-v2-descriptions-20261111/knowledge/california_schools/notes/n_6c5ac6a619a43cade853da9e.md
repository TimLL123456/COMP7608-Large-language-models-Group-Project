# School SAT score records

Type: table
Table: satscores
Scope: table_definition
Summary: SAT score summaries keyed by CDS; includes school and district-type entries, score counts/averages, and required rtype classification.
Keywords: satscores, sat, cds, school, district, rtype, test takers, score
Status: provisional
Sources: schema:satscores; schema:satscores.cds; schema:satscores.rtype; schema:satscores.NumGE1500; values:satscores rtype counts

## Business Summary
Contains SAT score-summary records with CDS identifier, record classification (`rtype`), grade-12 enrollment, test-taker count, average reading/math/writing scores, and count scoring >=1500.
## Business Use Cases
Supports school-linked SAT analysis. `cds` is a declared foreign key to `schools.CDSCode`; use `rtype='S'` for observed individual school rows, distinguishing these from D-class rows.
## Data Granularity
One row per `cds` by declared primary key, corroborated by 2,269 rows and 2,269 distinct CDS values in inspected extract. Observed rtype counts: S=1,749, D=520; all S map to nonblank directory School names, while D map to blank/null School names.
## Data Scope & Exclusions
SAT temporal coverage remains Unknown / Not verified; schema has no academic-year field. Formal meanings of rtype codes and record inclusion rules are Unknown / Not verified. No active PctGE1500 column in DDL.
