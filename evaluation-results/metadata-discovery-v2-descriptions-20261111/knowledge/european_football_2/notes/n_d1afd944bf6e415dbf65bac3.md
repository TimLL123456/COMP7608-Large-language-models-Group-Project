# League.name definition

Type: column
Table: League
Scope: name
Summary: Text name identifying a league or competition; declared unique in the schema.
Keywords: league name, competition
Status: provisional
Sources: schema:League.name; schema:League.id; schema:Match.league_id

## Business Meaning
Text name identifying a league or competition.
## Business Usage
Used as a human-readable league label; matches link via Match.league_id to League.id.
## Value Meaning
TEXT field, declared UNIQUE in the League schema; naming conventions are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
