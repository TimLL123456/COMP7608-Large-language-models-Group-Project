# Legality card UUID

Type: column
Table: legalities
Scope: uuid
Summary: Text UUID linking a legality row to the corresponding card record via cards.uuid foreign key.
Keywords: uuid, legalities, card, foreign key, join
Status: provisional
Sources: schema:legalities DDL uuid references cards.uuid; schema:cards DDL uuid TEXT NOT NULL UNIQUE

## Business Meaning
Text identifier for the card record to which the play-format legality row applies.
## Business Usage
Join legalities.uuid to cards.uuid; schema declares this foreign key reference.
## Value Meaning
No special code/value interpretation verified.
## Calculation Meaning
N/A; source/pass-through field.
