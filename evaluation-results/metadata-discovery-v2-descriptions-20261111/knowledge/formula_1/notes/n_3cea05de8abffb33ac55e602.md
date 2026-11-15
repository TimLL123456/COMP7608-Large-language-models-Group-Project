# Driver abbreviation code

Type: column
Table: drivers
Scope: code
Summary: Nullable text field for a driver's abbreviated code; source description says null or empty means no code.
Keywords: drivers, code, abbreviation, identifier
Status: provisional
Sources: schema:drivers DDL (code TEXT); description:drivers.csv:4

## Business Meaning
Abbreviated code associated with a driver.
## Business Usage
May serve as a short driver label; interpretation of absence follows the source description.
## Value Meaning
TEXT nullable. Source description states that "null" or empty means the driver does not have a code; exact representation of literal text null versus SQL NULL is Not verified.
## Calculation Meaning
N/A; source/pass-through field.
