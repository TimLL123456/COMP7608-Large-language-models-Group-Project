# Foreign flavor text

Type: column
Table: foreign_data
Scope: flavorText
Summary: TEXT field on foreign_data for language-specific flavor text; row joins to cards by UUID, not directly to a printing.
Keywords: foreign data, flavor text, language, translation, uuid
Status: provisional
Sources: schema:foreign_data.flavorText TEXT and uuid references cards.uuid; description:foreign_data.csv:2 foreign flavor text field

## Business Meaning
Flavor text field on a foreign-language card-data row; source documentation describes this as foreign flavor text.
## Business Usage
May be paired with language and joined on foreign_data.uuid = cards.uuid to associate flavor text with a stored card record. Schema does not establish linkage to a specific set printing.
## Value Meaning
TEXT; nonempty values can identify stored flavor text. Null/blank conventions and completeness are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
