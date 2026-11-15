# Event identifier

Type: column
Table: event
Scope: event_id
Summary: Declared TEXT primary key identifying an event record; budget.link_to_event references it.
Keywords: event, identifier, primary key, budget reference
Status: provisional
Sources: schema:event.event_id TEXT PRIMARY KEY; schema:budget.link_to_event TEXT REFERENCES event(event_id); schema:attendance.link_to_event REFERENCES event(event_id)

## Business Meaning
Identifier for an event record.
## Business Usage
Join key referenced by budget.link_to_event and attendance.link_to_event via declared foreign keys.
## Value Meaning
TEXT identifier; no special code interpretation verified.
## Calculation Meaning
N/A; source/pass-through identifier.
