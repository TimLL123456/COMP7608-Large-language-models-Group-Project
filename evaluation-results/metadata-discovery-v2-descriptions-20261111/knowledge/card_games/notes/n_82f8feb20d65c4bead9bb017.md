# Card type line

Type: column
Table: cards
Scope: type
Summary: Text field describing card types as visible, including supertypes and subtypes, per the source description.
Keywords: type, creature, type line, card
Status: provisional
Sources: schema:cards DDL type TEXT; description:cards.csv:70

## Business Meaning
Card type line as visible, including any supertypes and subtypes, per source description.
## Business Usage
May be used to classify records by card type; observed examples include Creature and Legendary Creature.
## Value Meaning
TEXT; observed values are type-line strings. Exact full domain is Not verified.
## Calculation Meaning
N/A; source/pass-through field.
