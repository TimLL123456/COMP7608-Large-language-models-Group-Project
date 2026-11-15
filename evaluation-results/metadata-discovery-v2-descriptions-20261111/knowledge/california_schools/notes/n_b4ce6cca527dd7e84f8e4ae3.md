# Mailing street address

Type: column
Table: schools
Scope: MailStreet
Summary: Nullable TEXT field described as unabbreviated mailing address for a school, district, or administrative authority.
Keywords: mailstreet, mailing address, street address, unabbreviated, schools
Status: provisional
Sources: schema:schools.MailStreet; description:schools.csv:13

## Business Meaning
Nullable TEXT field for the unabbreviated mailing address of the school, district, or administrative authority.
## Business Usage
Represents the mailing street component, distinct from the physical-location Street field; source cautions data can be absent for some entities.
## Value Meaning
N/A; no special code/value interpretation applies.
## Calculation Meaning
N/A; source/pass-through field.
