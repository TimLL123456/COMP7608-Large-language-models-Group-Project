# Race season year

Type: column
Table: races
Scope: year
Summary: Year associated with a race event; races.year references seasons.year and can scope event records by season.
Keywords: races, year, season, event
Status: provisional
Sources: schema:races DDL; description:races.csv:2

## Business Meaning
Season year associated with a race event.
## Business Usage
Scope race events by season; races.year references seasons.year, and races.name identifies the named event.
## Value Meaning
INTEGER NOT NULL with default 0; foreign key references seasons.year. Special value interpretation is Unknown / Not verified.
## Calculation Meaning
N/A — source/pass-through field.
