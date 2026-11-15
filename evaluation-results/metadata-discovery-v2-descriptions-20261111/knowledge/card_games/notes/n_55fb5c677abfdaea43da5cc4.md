# Card row ID

Type: column
Table: cards
Scope: id
Summary: Integer primary-key identifier for a stored card row; schema declares autoincrement and separates it from the UUID.
Keywords: id, card, primary key, identifier, autoincrement
Status: provisional
Sources: schema:cards DDL id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT; description:cards.csv:1

## Business Meaning
Integer identifier for a stored card row; the source description calls it the unique ID number identifying cards.
## Business Usage
Can identify a row in cards. Primary-key constraint and autoincrement declaration are verified; stability across data releases is Unknown / Not verified.
## Value Meaning
INTEGER value used as row identifier; numeric range and continuity are Unknown / Not verified.
## Calculation Meaning
N/A: source/pass-through field.
