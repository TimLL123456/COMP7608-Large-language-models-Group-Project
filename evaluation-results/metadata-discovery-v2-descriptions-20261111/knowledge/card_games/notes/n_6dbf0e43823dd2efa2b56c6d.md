# Card rules text

Type: column
Table: cards
Scope: text
Summary: TEXT field containing rules text; nonempty text is observable but not verified as an exact indicator of having a text box.
Keywords: text, rules text, card text, card ability, text box
Status: provisional
Sources: schema:cards.text TEXT; values:cards frameVersion 2015 grouped by isTextless and nonblank text: textless=1 had 13 nonblank of 13, textless=0 had 25,205 nonblank of 25,487

## Business Meaning
Text field for card rules text, demonstrated by card records containing abilities and reminder text; exact source convention is not documented.
## Business Usage
A non-NULL, nonblank value can filter records with text content, but is not verified as an exact indicator of having a text box. In observed frameVersion 2015 records marked isTextless=1, all 13 records had nonblank text; among isTextless=0 records, some had blank text. Thus neither field is an exact verified proxy for physical text-box presence.
## Value Meaning
Text content; special code interpretation does not apply. Null and blank values occur; exact distinction in source convention is Unknown / Not verified.
## Calculation Meaning
N/A: source/pass-through field.
