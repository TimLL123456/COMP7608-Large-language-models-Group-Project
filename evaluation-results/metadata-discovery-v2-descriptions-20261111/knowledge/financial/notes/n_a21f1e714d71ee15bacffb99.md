# District records

Type: table
Table: district
Scope: table_definition
Summary: District rows identify a district by district_id and include its name (A2), region label (A3), and other district attributes.
Keywords: district, location, name, region, branch
Status: provisional
Sources: schema:district DDL district_id primary key and A2/A3 required columns; schema:account.district_id foreign key to district.district_id; description:district.csv:2 name; values:district.A3 observed region labels

## Business Summary
Stores district-level records with identifier, human-readable name, region label and additional attributes.
## Business Use Cases
Supports attaching account branch-location district_id values to district names and regions for geographic reporting.
## Data Granularity
One row per district_id, declared INTEGER primary key.
## Data Scope & Exclusions
account.district_id references district.district_id; source descriptions identify A2 as district name and A3 as region. Meanings of other attributes and any historical changes are Unknown / Not verified.
