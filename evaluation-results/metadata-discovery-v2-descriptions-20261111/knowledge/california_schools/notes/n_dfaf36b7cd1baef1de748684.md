# Average mathematics score

Type: column
Table: satscores
Scope: AvgScrMath
Summary: Nullable INTEGER SAT-record average score in Math; underlying averaging method and total-score status are unverified.
Keywords: sat, mathematics, average score, component
Status: provisional
Sources: schema:satscores.AvgScrMath; schema:satscores.cds; description:satscores.csv:9

## Business Meaning
Nullable INTEGER average score in Math in a SAT score-table record, as stated by source description.
## Business Usage
Can be used as a reported SAT component average; `cds` links the record to `schools.CDSCode` by declared foreign key.
## Value Meaning
Math average as represented in dataset; scale and null interpretation are Unknown / Not verified.
## Calculation Meaning
Pre-reported average field; underlying method Unknown / Not verified. Summing sections is not confirmed by source as official total.
