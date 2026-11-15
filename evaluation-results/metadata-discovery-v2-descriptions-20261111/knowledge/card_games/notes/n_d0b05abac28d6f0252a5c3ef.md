# Base set size

Type: column
Table: sets
Scope: baseSetSize
Summary: Source-documented number of cards in a set; size relates to base-set counts, while set-type exclusion rules require care.
Keywords: base set size, card count, sets
Status: provisional
Sources: schema:sets DDL baseSetSize INTEGER; description:sets.csv:2 baseSetSize is number of cards in the set; values:sets sampled promo records have type promo and baseSetSize 1

## Business Meaning
The number of cards in a set, according to the source description.
## Business Usage
May provide the base card count of a set; to total base sizes across sets, sum this source field over the selected set records. Set selection/exclusion criteria are a separate decision; sampled promo records have type promo and may carry baseSetSize 1.
## Value Meaning
INTEGER field; no special code/value interpretation applies.
## Calculation Meaning
N/A; source/pass-through field. Any derived aggregation is the sum of baseSetSize over selected records; exact relationship to totalSetSize is Unknown / Not verified.
