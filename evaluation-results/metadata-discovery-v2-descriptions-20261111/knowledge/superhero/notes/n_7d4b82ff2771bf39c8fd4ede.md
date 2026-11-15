# Superhero skin colour reference

Type: column
Table: superhero
Scope: skin_colour_id
Summary: Nullable integer foreign key referencing the colour lookup record assigned to a superhero's skin colour.
Keywords: superhero, skin colour, colour id, foreign key
Status: provisional
Sources: schema:superhero.skin_colour_id foreign key to colour.id; description:colour.csv:2

## Business Meaning
Identifies the colour lookup record assigned to a superhero's skin colour.
## Business Usage
Join to colour.id and use colour.colour for the label; nullable by schema, though null occurrence in current data is unverified.
## Value Meaning
Integer references colour.id; no special code interpretation verified.
## Calculation Meaning
N/A; source/pass-through field.
