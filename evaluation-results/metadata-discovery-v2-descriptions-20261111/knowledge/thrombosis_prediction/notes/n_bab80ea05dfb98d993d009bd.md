# Laboratory.ID definition

Type: column
Table: Laboratory
Scope: ID
Summary: Non-null patient identifier; part of Laboratory composite primary key and references Patient.ID.
Keywords: laboratory, patient identifier, foreign key, primary key
Status: provisional
Sources: schema:Laboratory DDL ID INTEGER NOT NULL, composite primary key (ID, Date), foreign key ID references Patient.ID; description:Laboratory.csv:1 ID identification of patient

## Business Meaning
Identifier linking a Laboratory record to a patient, as source description identifies ID as patient identification.
## Business Usage
Join to Patient.ID to access patient profile attributes; distinct IDs identify patients represented by laboratory rows.
## Value Meaning
INTEGER, non-null. Declared foreign key to Patient.ID and part of composite primary key with Date; uniqueness alone is not implied.
## Calculation Meaning
N/A; stored source/pass-through field.
