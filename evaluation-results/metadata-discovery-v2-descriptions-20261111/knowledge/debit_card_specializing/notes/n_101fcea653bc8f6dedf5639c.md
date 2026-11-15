# Transaction amount field

Type: column
Table: transactions_1k
Scope: Amount
Summary: INTEGER Amount on transaction records; source describes total price as Amount × Price, but unit and business interpretation remain unverified.
Keywords: transaction, amount, price, calculation, unit
Status: provisional
Sources: schema:transactions_1k DDL Amount INTEGER; description:transactions_1k.csv:8; description:transactions_1k.csv:9

## Business Meaning
INTEGER field named Amount in a transaction record; precise business meaning and unit are Unknown / Not verified.
## Business Usage
Can be considered alongside Price in the source-described total price calculation.
## Value Meaning
N/A; no special code/value interpretation is verified.
## Calculation Meaning
Source description specifies total price = Amount × Price; whether Amount has a particular physical unit is Unknown / Not verified.
