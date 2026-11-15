# NCES school identification number

Type: column
Table: schools
Scope: NCESSchool
Summary: Nullable TEXT field for the 5-digit NCES school identifier; description states it combines with NCESDist to form a 12-digit ID.
Keywords: nces, school identifier, ncesschool, education statistics
Status: provisional
Sources: schema:schools.NCESSchool; description:schools.csv:3

## Business Meaning
NCES school-level identification number, represented as TEXT and nullable in the directory schema. Source description explicitly says it is a 5-digit school identification number.
## Business Usage
Identifies the school component of an NCES identifier; description says NCESSchool combined with NCESDist forms a 12-digit ID for each school.
## Value Meaning
Text identifier intended to contain five digits; retain leading zeros. Other value conventions are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
