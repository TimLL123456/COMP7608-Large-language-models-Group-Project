# Constructor race standings

Type: table
Table: constructorStandings
Scope: table_definition
Summary: Constructor standings snapshots linked to constructors and races; points and ranking fields represent values recorded at a race event.
Keywords: constructorstandings, constructor, race, cumulative points, position, wins
Status: provisional
Sources: schema:constructorStandings DDL and foreign keys; schema:races DDL; values:constructorStandings points and rounds for Ferrari 2016 and Italian constructor rows across years

## Business Summary
Stores constructor standings values associated with constructors and race events.
## Business Use Cases
Track constructor points, position, and wins over race events; races.year supports grouping by calendar year.
## Data Granularity
One row per constructorStandingsId primary key. Rows reference constructorId and raceId; uniqueness of constructor/race combinations is Unknown / Not verified.
## Data Scope & Exclusions
Schema includes non-null points REAL (default 0), nullable position and positionText, and non-null wins INTEGER (default 0). Observed points change across races in a year and increase in later rounds in sampled records, consistent with cumulative standings snapshots. The year-end row can be identified by the highest race round in a year where a record exists; coverage and behavior in all seasons are Unknown / Not verified.
