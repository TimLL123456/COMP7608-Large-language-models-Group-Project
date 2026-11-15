# Attendance event reference

Type: column
Table: attendance
Scope: link_to_event
Summary: Event identifier on an attendance record; references event.event_id and forms the attendance member-event pair.
Keywords: attendance, event, reference, identifier
Status: provisional
Sources: schema:attendance.link_to_event TEXT REFERENCES event(event_id); description:Attendance.csv:1

## Business Meaning
Event identifier associated with an attendance record.
## Business Usage
Joins attendance to event via event.event_id; paired with link_to_member in the composite primary key to represent an attendee-event association.
## Value Meaning
TEXT foreign-key reference to event.event_id; no special code interpretation is verified.
## Calculation Meaning
N/A; source/pass-through reference field.
