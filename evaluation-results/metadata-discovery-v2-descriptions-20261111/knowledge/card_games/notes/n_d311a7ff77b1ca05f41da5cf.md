# Translation language

Type: column
Table: set_translations
Scope: language
Summary: Language label attached to stored set-name translation records; dataset does not establish official card-printing status.
Keywords: translation, language, set localized name, set
Status: provisional
Sources: schema:set_translations.language TEXT; schema:set_translations.setCode references sets.code; values:set_translations.language ten observed labels

## Business Meaning
Language label associated with a stored set-name translation record.
## Business Usage
Can group or filter set translations by language; setCode references sets.code. Presence does not establish that cards in the set were officially printed in that language.
## Value Meaning
TEXT; observed labels are Chinese Simplified, Chinese Traditional, French, German, Italian, Japanese, Korean, Portuguese (Brazil), Russian, and Spanish. These are labels in this table, not verified official card-printing languages.
## Calculation Meaning
N/A; source/pass-through field.
