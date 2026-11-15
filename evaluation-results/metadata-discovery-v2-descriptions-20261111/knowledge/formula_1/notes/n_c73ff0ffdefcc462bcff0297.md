# Constructor nationality

Type: column
Table: constructors
Scope: nationality
Summary: Nullable TEXT nationality attribute on a constructor record; the observed Italian value is exactly 'Italian'.
Keywords: constructor, nationality, italian, team
Status: provisional
Sources: schema:constructors DDL; values:constructors nationality values and records with nationality='Italian'

## Business Meaning
Nationality attribute associated with a constructor/team; the schema does not define the convention behind it.
## Business Usage
Can filter constructor records by nationality. The observed Italian constructors have the literal value “Italian”; complete convention and coverage are Unknown / Not verified.
## Value Meaning
Nullable TEXT. The Italian value observed is exactly “Italian”; other value semantics are Unknown / Not verified.
## Calculation Meaning
N/A — source/pass-through field.
