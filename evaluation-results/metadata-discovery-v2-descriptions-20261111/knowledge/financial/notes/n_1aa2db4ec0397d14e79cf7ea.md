# Credit card records

Type: table
Table: card
Scope: table_definition
Summary: Stores card identifiers, disposition links, type and issue date; connects cards to account-client relationships via disposition.
Keywords: card, credit card, disposition, type, issued
Status: provisional
Sources: schema:card DDL primary key card_id and foreign key disp_id to disp.disp_id; description:card.csv:1,3,4

## Business Summary
Stores credit card records with card identifier, disposition link, card type and issue date.
## Business Use Cases
Links an issued card to a disposition and thereby an account-client association; supports grouping by recorded card class.
## Data Granularity
One row per card_id, declared primary key. Uniqueness of disposition/card combinations is Unknown / Not verified.
## Data Scope & Exclusions
card.disp_id references disp.disp_id. Type and issue date are required. Whether issue date defines continued active status or a valid-time interval is Unknown / Not verified.
