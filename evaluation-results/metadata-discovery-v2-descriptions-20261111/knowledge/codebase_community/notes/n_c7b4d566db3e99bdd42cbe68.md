# votes.VoteTypeId

Type: column
Table: votes
Scope: VoteTypeId
Summary: Nullable integer vote classification; code labels are unverified, and inspected user-attributed votes have codes 5 and 8.
Keywords: votes, vote type, classification, integer
Status: provisional
Sources: schema:votes DDL; description:votes.csv:3; values:votes grouped by VoteTypeId and non-null UserId observations

## Business Meaning
Integer identifier classifying a vote record; the specific meaning of each code is Unknown / Not verified.
## Business Usage
Can distinguish vote record types. Which code represents an up-vote is Unknown / Not verified.
## Value Meaning
Nullable INTEGER. Observed codes include 1, 2, 3, 5, 8, 9, 10, 11, 15 and 16; only 5 and 8 occur among records with non-null UserId in inspected data. These observations do not establish labels.
## Calculation Meaning
N/A; source/pass-through field.
