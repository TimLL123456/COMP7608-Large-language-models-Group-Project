# Driver information-page URL

Type: column
Table: drivers
Scope: url
Summary: Driver-record URL stored as unique, non-null TEXT; page content/purpose beyond URL field is not verified.
Keywords: drivers, url, information page, link
Status: provisional
Sources: schema:drivers DDL (url TEXT default '' not null unique)

## Business Meaning
URL associated with the driver record; presumed page link based on the field name, specific destination details Unknown / Not verified.
## Business Usage
Can be returned as a driver-record link; content and availability of destination are Unknown / Not verified.
## Value Meaning
TEXT, default empty string, not null, and unique per schema. No special code interpretation applies.
## Calculation Meaning
N/A; source/pass-through field.
