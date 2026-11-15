# Qualifying record identifier

Type: column
Table: qualifying
Scope: qualifyId
Summary: INTEGER primary key identifying a qualifying record; does not by itself establish a race-driver uniqueness rule.
Keywords: qualifying, qualifyid, record identifier, primary key
Status: provisional
Sources: schema:qualifying DDL (qualifyId INTEGER primary key autoincrement)

## Business Meaning
Identifier assigned to a qualifying record.
## Business Usage
Distinguishes qualifying rows; related race, driver, and constructor are represented by separate IDs.
## Value Meaning
INTEGER primary key.
## Calculation Meaning
N/A; source/pass-through field.
