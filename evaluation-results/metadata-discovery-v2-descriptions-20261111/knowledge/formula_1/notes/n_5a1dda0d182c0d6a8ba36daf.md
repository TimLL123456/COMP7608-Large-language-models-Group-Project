# Race results

Type: table
Table: results
Scope: table_definition
Summary: Race result entries link events, drivers and constructors; duplicate driver-race records and non-starters occur.
Keywords: results, race, driver, constructor, finish, position, participation, start
Status: provisional
Sources: schema:results DDL and foreign keys; values:results row and distinct-pair counts; values:duplicate driver-race status observations

## Business Summary
Stores race-result entries linking a race, driver, constructor and status with outcome fields.
## Business Use Cases
Join results to races and drivers to examine event participation and outcomes; position=1 identifies rows coded as race wins. Distinct raceId-driverId pairs count represented driver-race events, not necessarily starts.
## Data Granularity
One row per resultId primary key. Observed 23,179 rows and 23,090 distinct raceId-driverId pairs; 83 pairs have duplicates (maximum 3). Duplicates may reflect different statuses or constructor entries.
## Data Scope & Exclusions
Observed result rows include non-starters (e.g. Did not qualify, Did not prequalify). Grid values can be 0 or positive; grid alone is not verified as a definitive start criterion. Reliable rule for identifying every start is Unknown / Not verified.
