# badges.Name

Type: column
Table: badges
Scope: Name
Summary: Text badge name identifying the badge recorded; Yearling is an observed exact value.
Keywords: badges, name, badge type, yearling
Status: provisional
Sources: schema:badges.Name; description:badges.csv:3; values:badges.Name exact Yearling observed

## Business Meaning
The badge name the user obtained, per data description.
## Business Usage
Can categorize badge records by badge name; records with exact stored name `Yearling` are retrievable as that category.
## Value Meaning
Nullable TEXT. `Yearling` is an observed exact value; other names and code interpretations are not exhaustively verified.
## Calculation Meaning
N/A; source/pass-through field, no derived calculation verified.
