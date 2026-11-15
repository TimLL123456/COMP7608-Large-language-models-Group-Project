# Scryfall Oracle identifier

Type: column
Table: cards
Scope: scryfallOracleId
Summary: TEXT identifier shared across card records; observed matching-name reprints share identifiers, but universal distinct-card semantics remain unverified.
Keywords: scryfalloracleid, card identity, oracle, printing, identifier
Status: provisional
Sources: schema:cards.scryfallOracleId TEXT; values:cards records grouped by frameVersion 2015/future show differing distinct name, scryfallOracleId, scryfallId, and uuid counts

## Business Meaning
Text field labeled as a Scryfall Oracle identifier and associated with a stored card record. External-system semantics are Unknown / Not verified.
## Business Usage
Identical identifiers group multiple stored card records in observed data, but whether the field consistently defines a distinct card across all cases is Unknown / Not verified. It is not interchangeable with distinct names or row UUIDs.
## Value Meaning
TEXT; values can be absent, and identifier uniqueness/coverage semantics are Unknown / Not verified. Observed modern-frame subsets have materially different counts by name, Oracle ID, Scryfall ID, and row UUID, confirming these are different grouping choices.
## Calculation Meaning
N/A: source/pass-through field.
