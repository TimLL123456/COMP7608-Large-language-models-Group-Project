# Foreign-language type line

Type: column
Table: foreign_data
Scope: type
Summary: Localized card type line stored on foreign_data rows linked to cards by UUID; dataset meaning beyond the field label is unverified.
Keywords: foreign data, localized type, card type, language, uuid
Status: provisional
Sources: schema:foreign_data.type TEXT; schema:foreign_data.uuid references cards.uuid; description:foreign_data.csv:7

## Business Meaning
Type-line text associated with a foreign-language card-data row; exact source semantics beyond the field label are Unknown / Not verified.
## Business Usage
Join foreign_data.uuid to cards.uuid to associate localized type text with a card record; filter foreign_data.language for a language subset.
## Value Meaning
TEXT type-line strings; full domain and language coverage are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
