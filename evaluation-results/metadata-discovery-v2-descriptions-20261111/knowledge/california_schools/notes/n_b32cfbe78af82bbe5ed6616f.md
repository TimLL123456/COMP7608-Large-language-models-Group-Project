# School funding type

Type: column
Table: schools
Scope: FundingType
Summary: Optional TEXT directory funding classification; observed categories include Directly funded and Locally funded.
Keywords: fundingtype, charter, direct, local
Status: provisional
Sources: schema:schools.FundingType; values:schools FundingType counts; values:schools active status/funding counts

## Business Meaning
FundingType is a nullable TEXT funding classification field in the schools directory; authoritative definitions are Unknown / Not verified.
## Business Usage
Supports grouping directory records by funding category. Observed values include Directly funded and Locally funded.
## Value Meaning
Observed values include Directly funded, Locally funded and Not in CS funding model, with null also present; category definitions are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
