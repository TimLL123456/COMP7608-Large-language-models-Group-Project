# Badges table definition

Type: table
Table: badges
Scope: table_definition
Summary: Records badges obtained by users, with badge name and date fields.
Keywords: badges, users, earned date, name
Status: provisional
Sources: schema:badges DDL and foreign key; description:badges.csv:1-4

## Business Summary
Stores badge records linked to users, with a badge name and obtained date.
## Business Use Cases
Can support examining badge records by user, badge name, or date. Other use cases are Unknown / Not verified.
## Data Granularity
One row per badge record; whether users can have repeated names or other uniqueness constraints is Unknown / Not verified.
## Data Scope & Exclusions
The table schema includes Id, UserId, Name, and Date. Temporal coverage and exclusions are Unknown / Not verified.
