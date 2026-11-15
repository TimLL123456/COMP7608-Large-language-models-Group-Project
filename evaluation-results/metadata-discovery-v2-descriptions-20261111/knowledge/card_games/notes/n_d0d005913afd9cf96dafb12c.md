# Card power value

Type: column
Table: cards
Scope: power
Summary: TEXT card-power attribute; numeric values and symbolic expressions occur. Null/* are unknown and ∞ infinite; expression range treatment is unverified.
Keywords: power, numeric, symbolic, card
Status: provisional
Sources: schema:cards.power TEXT; description:cards.csv:55 identifies power and documents null/* as unknown and ∞ as infinite; values:cards power values include 2+*, *², ?, and ∞

## Business Meaning
Power attribute stored for a card record; source documentation calls it card power. Creature-only scope is Unknown / Not verified.
## Business Usage
Can classify records by power when numeric parsing and symbolic-value handling are specified.
## Value Meaning
TEXT field. Source description documents null and `*` as unknown and `∞` as infinite. Observed symbolic values include `2+*` and `*²`; their order or inclusion in numeric ranges is Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field. Numeric comparisons require an analysis rule, not stored calculation.
