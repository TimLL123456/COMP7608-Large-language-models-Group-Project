# Patient.ID definition

Type: column
Table: Patient
Scope: ID
Summary: Non-null INTEGER patient identifier and declared primary key; referenced by Laboratory and Examination records.
Keywords: patient, id, identifier, primary key, laboratory, examination
Status: provisional
Sources: schema:Patient DDL ID INTEGER NOT NULL PRIMARY KEY; description:Patient.csv:1 ID identification of the patient; schema:Laboratory foreign key ID references Patient.ID; schema:Examination foreign key ID references Patient.ID

## Business Meaning
Identifier of the patient, according to the source description.
## Business Usage
Identifies patient profile records and links patient-level attributes to clinical records through matching ID fields, including Laboratory and Examination.
## Value Meaning
INTEGER, non-null and declared primary key in Patient; Laboratory.ID and Examination.ID reference Patient.ID. No additional coding scheme is verified.
## Calculation Meaning
N/A; stored source/pass-through field.
