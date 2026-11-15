# Examination table definition

Type: table
Table: Examination
Scope: table_definition
Summary: Patient-linked examination rows include date, symptoms and diagnosis; repeated patient records occur and no row key or cohort definition is declared.
Keywords: examination, patient, repeated records, diagnosis, date, symptoms
Status: provisional
Sources: schema:Examination DDL has nullable ID/date/results, no declared primary key, and foreign key ID to Patient.ID; values:patients occur on multiple Examination rows; description:Examination.csv:1-2 documents ID and examination date

## Business Summary
Stores patient-linked examination attributes, including examination date, symptoms, diagnosis and thrombosis degree.
## Business Use Cases
ID links to Patient.ID; row-level findings can be studied against patient profiles. No cohort membership rule is established by the schema.
## Data Granularity
One examination record per row; repeated rows per patient occur. No unique key is declared in the inspected schema.
## Data Scope & Exclusions
Columns are nullable and population scope is Unknown / Not verified. Row date is recorded; no date-based scope restriction is inherent in the table.
