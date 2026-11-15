# Promotional type labels

Type: column
Table: cards
Scope: promoTypes
Summary: Text field stores one or more comma-separated promotional type labels associated with a card record; examples include prerelease and release.
Keywords: promotypes, promotion, release, prerelease, cards
Status: provisional
Sources: schema:cards DDL promoTypes TEXT; description:cards.csv:57; values:cards promoTypes grouped values include release and prerelease

## Business Meaning
Stores promotional type label(s) associated with a card record.
## Business Usage
Useful for identifying kinds of promotional printings; test individual labels within the delimited value rather than treating the full string as one type.
## Value Meaning
TEXT; observed values include single and comma-separated labels, including `release`, `prerelease`, and `datestamped,release`. Exact controlled vocabulary and encoding specification are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
