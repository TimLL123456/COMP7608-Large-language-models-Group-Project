# Patient.Diagnosis definition

Type: column
Table: Patient
Scope: Diagnosis
Summary: Nullable patient disease-name TEXT; values include comma-separated diagnoses and capitalization or suspicion variants.
Keywords: diagnosis, patient, disease names, psoriatic arthritis, comma-delimited
Status: provisional
Sources: schema:Patient DDL Diagnosis TEXT nullable; description:Patient.csv:7 labels Diagnosis as disease names; values:observed Patient.Diagnosis labels include capitalization variants and suspicion-marked labels

## Business Meaning
Patient-level text field described by the source as disease names; distinct from Examination.Diagnosis.
## Business Usage
Stores diagnosis labels associated with a patient profile. Observed values may contain multiple comma-delimited diagnoses; parsing/completeness and cohort membership are Unknown / Not verified.
## Value Meaning
Nullable TEXT. Observed labels include capitalization variants of Psoriatic Arthritis and suspicion-marked labels; full vocabulary and inclusion interpretation are Unknown / Not verified.
## Calculation Meaning
N/A; stored source/pass-through field.
