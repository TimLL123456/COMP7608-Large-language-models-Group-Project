# CDS school identifier

Type: column
Table: satscores
Scope: cds
Summary: Required TEXT primary key in SAT records and declared foreign key referencing schools.CDSCode; joins the FRPM school identifier via schools.CDSCode.
Keywords: cds, school identifier, sat, foreign key, join
Status: provisional
Sources: schema:satscores.cds; schema:schools.CDSCode; schema:frpm.CDSCode; values:satscores.cds matched frpm.CDSCode

## Business Meaning
`cds` is a required TEXT identifier for a SAT score row; schema declares it the primary key and a foreign key referencing `schools.CDSCode`.
## Business Usage
Links SAT records to directory entries and, via the shared schools.CDSCode key, to `frpm.CDSCode`. Inspected values confirmed direct matches between SAT and FRPM CDS identifiers.
## Value Meaning
Identifier values; specific encoding semantics are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
