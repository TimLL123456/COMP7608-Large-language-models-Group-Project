# Gender lookup table definition

Type: table
Table: gender
Scope: table_definition
Summary: Lookup of gender IDs and nullable text labels referenced by superhero.gender_id.
Keywords: gender, lookup, superhero, gender_id
Status: provisional
Sources: schema:gender DDL; schema:superhero.gender_id foreign key to gender.id; values:gender grouped label values observed

## Business Summary
Lookup table containing gender identifiers and nullable text labels referenced by superhero records.
## Business Use Cases
Resolve superhero.gender_id to a gender label for categorizing records.
## Data Granularity
One row per gender lookup record; id is the primary key. Label uniqueness is Unknown / Not verified.
## Data Scope & Exclusions
Observed labels include Female, Male, and N/A. Exhaustiveness or broader interpretation is Unknown / Not verified.
