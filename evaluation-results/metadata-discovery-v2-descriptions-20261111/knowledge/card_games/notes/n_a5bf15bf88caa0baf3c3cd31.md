# Online-only card flag

Type: column
Table: cards
Scope: isOnlineOnly
Summary: INTEGER flag indicating whether the card record is associated with an online-only set/printing; detailed values require description verification.
Keywords: online-only, isonlineonly, card, printing, flag
Status: provisional
Sources: schema:cards DDL isOnlineOnly INTEGER default 0 not null

## Business Meaning
Flag associated with whether a card record is online-only; exact scope/definition is Unknown / Not verified.
## Business Usage
May be used to identify online-only card records; verify values and semantics before relying on it.
## Value Meaning
INTEGER, default 0 and NOT NULL according to schema; specific code meanings are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
