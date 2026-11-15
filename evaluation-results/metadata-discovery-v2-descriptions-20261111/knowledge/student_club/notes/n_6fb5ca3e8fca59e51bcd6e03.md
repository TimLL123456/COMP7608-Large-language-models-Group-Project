# Major identifier

Type: column
Table: major
Scope: major_id
Summary: TEXT primary-key identifier for records in major; referenced by member.link_to_major.
Keywords: major, major_id, identifier, member reference
Status: provisional
Sources: schema:major DDL major_id TEXT primary key; schema:member DDL link_to_major foreign key references major.major_id

## Business Meaning
Identifier for a major record; broader institutional identifier semantics are Unknown / Not verified.
## Business Usage
Connects member records through member.link_to_major to the represented major.
## Value Meaning
TEXT primary key for the major table.
## Calculation Meaning
N/A; source/pass-through identifier.
