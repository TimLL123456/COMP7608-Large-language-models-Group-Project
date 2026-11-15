# Superhero gender reference

Type: column
Table: superhero
Scope: gender_id
Summary: Nullable foreign-key lookup ID for a hero's gender; join gender.id for category labels including Male.
Keywords: gender, gender_id, superhero, lookup
Status: provisional
Sources: schema:superhero.gender_id INTEGER nullable foreign key to gender.id; schema:gender.gender TEXT; values:gender observed labels Female, Male, N/A

## Business Meaning
Lookup reference for the gender category associated with a superhero record.
## Business Usage
Join superhero.gender_id to gender.id to categorize superhero records by gender label.
## Value Meaning
Nullable INTEGER foreign key to gender.id; observed labels in gender include Female, Male, and N/A.
## Calculation Meaning
N/A; source/pass-through field.
