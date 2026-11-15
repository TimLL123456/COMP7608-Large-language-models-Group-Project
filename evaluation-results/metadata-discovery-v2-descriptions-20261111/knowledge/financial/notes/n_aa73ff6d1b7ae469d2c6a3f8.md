# Client identifier

Type: column
Table: client
Scope: client_id
Summary: INTEGER primary key for client records; referenced by disposition.client_id.
Keywords: client, identifier, primary key, disposition
Status: provisional
Sources: schema:client.client_id primary key; schema:disp.client_id foreign key references client.client_id

## Business Meaning
Identifier for a client record.
## Business Usage
Connects clients to dispositions through disp.client_id.
## Value Meaning
INTEGER NOT NULL primary key; no special code interpretation applies.
## Calculation Meaning
N/A; source/pass-through identifier.
