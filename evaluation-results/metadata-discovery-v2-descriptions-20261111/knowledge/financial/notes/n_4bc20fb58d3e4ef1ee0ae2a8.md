# Client gender

Type: column
Table: client
Scope: gender
Summary: Gender attribute recorded for a client; description maps F to female and M to male.
Keywords: client, gender, female, male
Status: provisional
Sources: schema:client.gender (TEXT, NOT NULL); description:client.csv:2 (F female, M male)

## Business Meaning
Gender attribute associated with a client.
## Business Usage
Supports segmentation by recorded gender.
## Value Meaning
Dataset description maps F to female and M to male; column is non-null TEXT.
## Calculation Meaning
N/A; source/pass-through field.
