# Printed mana cost

Type: column
Table: cards
Scope: manaCost
Summary: TEXT field described as the card's mana cost; observed bracketed mana-symbol strings and NULL, with {0} representing a zero cost.
Keywords: manacost, mana cost, printed cost, bracketed symbols
Status: provisional
Sources: schema:cards DDL manaCost TEXT; description:cards.csv:41 manaCost described as the card's mana cost wrapped in brackets for each value; values:cards grouped manaCost shows NULL and bracketed cost strings

## Business Meaning
The card's mana cost, as described by source field documentation.
## Business Usage
Can distinguish records with a non-NULL printed mana cost from those without one; observed formatting uses bracketed mana symbols, e.g. {1}{W} and {0}.
## Value Meaning
TEXT; observed values include NULL and bracketed mana-symbol strings. Exact complete value domain is Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
