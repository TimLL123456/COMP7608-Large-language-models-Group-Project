# Disposition account ID

Type: column
Table: disp
Scope: account_id
Summary: Required account identifier on a disposition; references account.account_id and links clients to accounts.
Keywords: disposition, account id, foreign key, client account association
Status: provisional
Sources: schema:disp.account_id INTEGER NOT NULL REFERENCES account.account_id

## Business Meaning
Identifies the account associated with a disposition record.
## Business Usage
Joins disp records to account records; together with disp.client_id represents client-account associations.
## Value Meaning
INTEGER NOT NULL; foreign key to account.account_id.
## Calculation Meaning
N/A; source/pass-through identifier.
