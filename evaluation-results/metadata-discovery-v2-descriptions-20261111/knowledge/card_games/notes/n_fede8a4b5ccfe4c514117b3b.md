# Ruling text

Type: column
Table: rulings
Scope: text
Summary: Free-text content of a stored ruling row; associated card is identified through rulings.uuid.
Keywords: ruling, text, card, uuid, content
Status: provisional
Sources: schema:rulings DDL text TEXT; schema:rulings DDL uuid references cards.uuid

## Business Meaning
Text content stored for a ruling associated with a card record; whether each row is an official ruling is Unknown / Not verified.
## Business Usage
Can be searched or reviewed as ruling prose and linked to a card record via rulings.uuid.
## Value Meaning
TEXT field; detailed content and source coverage are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
