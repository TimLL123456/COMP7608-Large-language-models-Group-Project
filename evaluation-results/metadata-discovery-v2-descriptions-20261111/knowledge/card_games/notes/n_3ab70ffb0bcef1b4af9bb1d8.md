# Ruling issue date

Type: column
Table: rulings
Scope: date
Summary: Calendar date stored for a ruling record; the column is declared DATE, but nullability and source coverage are not documented.
Keywords: ruling, date, calendar
Status: provisional
Sources: schema:rulings DDL date DATE

## Business Meaning
Date associated with a stored ruling record; whether it denotes issue, effective, or publication date is Unknown / Not verified.
## Business Usage
Can group ruling records by stored date when summarizing rulings.
## Value Meaning
DATE column; specific date conventions or code interpretations are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
