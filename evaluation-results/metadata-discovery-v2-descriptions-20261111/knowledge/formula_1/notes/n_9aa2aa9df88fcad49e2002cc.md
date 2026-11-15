# Qualifying constructor identifier

Type: column
Table: qualifying
Scope: constructorId
Summary: Constructor ID associated with a qualifying record; schema foreign key references constructors.constructorId.
Keywords: qualifying, constructorid, constructor, foreign key
Status: provisional
Sources: schema:qualifying DDL constructorId INTEGER default 0 not null; schema:qualifying foreign key to constructors.constructorId

## Business Meaning
Identifier of the constructor associated with a qualifying record.
## Business Usage
Links qualifying entries to constructors through the declared foreign key.
## Value Meaning
INTEGER, NOT NULL, default 0; foreign key references constructors.constructorId.
## Calculation Meaning
N/A; source/pass-through field.
