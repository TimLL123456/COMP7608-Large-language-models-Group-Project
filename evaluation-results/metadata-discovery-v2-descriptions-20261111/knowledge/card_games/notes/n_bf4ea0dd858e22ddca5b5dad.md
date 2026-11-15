# Card availability platforms

Type: column
Table: cards
Scope: availability
Summary: Comma-separated platform/printing-type values on card records; documentation lists paper and digital platforms, not localized releases.
Keywords: availability, arena, mtgo, paper, platforms, card
Status: provisional
Sources: schema:cards.availability TEXT; description:cards.csv:4 availability is a list of available printing types with examples arena, mtgo, paper, dreamcast, shandalar; values:cards grouped observed combinations and NULL

## Business Meaning
Lists platforms or printing types associated with a card record.
## Business Usage
Can filter records by platform membership; this field does not itself establish localized release availability.
## Value Meaning
TEXT serialized as comma-separated names. Documentation identifies arena, mtgo, paper, dreamcast, and shandalar; observed values include combinations and NULL.
## Calculation Meaning
N/A; source/pass-through field.
