# Client district identifier

Type: column
Table: client
Scope: district_id
Summary: Client district_id is a required FK to district; source label describes branch location, so home/residence semantics remain unverified.
Keywords: client, district, district_id, foreign key, branch, residence
Status: provisional
Sources: schema:client.district_id INTEGER NOT NULL REFERENCES district.district_id; description:client.csv:4

## Business Meaning
District identifier associated with a client record. The source field description says “location of branch”; whether this is a client's home/residential district is Unknown / Not verified.
## Business Usage
Joins a client to district attributes via district.district_id. Residence-based interpretation is unverified.
## Value Meaning
INTEGER NOT NULL foreign key to district.district_id.
## Calculation Meaning
N/A; source/pass-through identifier.
