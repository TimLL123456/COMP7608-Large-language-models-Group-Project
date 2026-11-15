# Foreign card-data card UUID

Type: column
Table: foreign_data
Scope: uuid
Summary: UUID linking a language-specific card-data row to the corresponding cards.uuid; foreign key is declared in schema.
Keywords: foreign data, card uuid, link, translation
Status: provisional
Sources: schema:foreign_data.uuid references cards.uuid

## Business Meaning
Identifies the card record to which this foreign-language data row relates.
## Business Usage
Join foreign_data.uuid to cards.uuid to associate language-specific fields with a card record; filter language as needed.
## Value Meaning
N/A; source identifier value, with no special code interpretation verified.
## Calculation Meaning
N/A; source/pass-through field.
