# Transaction date field

Type: column
Table: transactions_1k
Scope: Date
Summary: DATE transaction field observed in 2012 only from 2012-08-23 through 2012-08-26; narrow coverage does not verify 2013 customer-month fuel use.
Keywords: transaction, date, coverage, period, sample
Status: provisional
Sources: schema:transactions_1k DDL Date DATE; description:transactions_1k.csv:2; values:transactions_1k row count 1000, MIN/MAX Date and distinct-date count

## Business Meaning
Date records a date associated with a transaction; exact event timing semantics are Unknown / Not verified.
## Business Usage
Can support filtering or grouping transaction records by date. Its observed coverage is insufficient to establish all card use during 2013.
## Value Meaning
Declared DATE. The 1,000-row transactions_1k sample spans 2012-08-23 through 2012-08-26 across four distinct dates; full underlying transaction coverage is Unknown / Not verified.
## Calculation Meaning
N/A; stored source field with no derivation verified.
