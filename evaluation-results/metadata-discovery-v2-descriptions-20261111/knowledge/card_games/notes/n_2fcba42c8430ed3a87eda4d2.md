# Converted mana cost

Type: column
Table: cards
Scope: convertedManaCost
Summary: REAL field described as converted mana cost; documentation directs to manaValue, but equivalence and edge-case handling remain unverified.
Keywords: converted mana cost, mana value, cost
Status: provisional
Sources: schema:cards.convertedManaCost REAL; description:cards.csv:11 describes converted mana cost and states Use the manaValue property

## Business Meaning
Source describes this field as converted mana cost and directs users to manaValue. Exact equivalence to mana value for all records is Unknown / Not verified.
## Business Usage
Numeric field present for card records and usable for converted-cost analysis; for a mana-value request, documentation points to manaValue, not expressly to this field. Multi-face handling is Unknown / Not verified.
## Value Meaning
REAL; NULL and special-value semantics are Unknown / Not verified.
## Calculation Meaning
Unknown / Not verified; source does not establish whether this value is calculated or passed through.
