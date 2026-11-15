# Loan duration

Type: column
Table: loan
Scope: duration
Summary: Loan repayment-term duration recorded as an integer number of months.
Keywords: loan, duration, term, months, repayment
Status: provisional
Sources: schema:loan.duration (INTEGER NOT NULL); description:loan.csv:5 (duration, unit month); description:question evidence (term starts approval day, includes last day)

## Business Meaning
Duration of a loan's repayment term; field description identifies the unit as months.
## Business Usage
Used with approval date to determine the period the loan is being repaid. Supplied task evidence says the term starts on approval day and includes its last day; exact month-boundary handling remains Unknown / Not verified.
## Value Meaning
INTEGER NOT NULL; unit is months per field description. No special code interpretation applies.
## Calculation Meaning
Stored duration is a source/pass-through value. Exact inclusive last-day calculation from approval date is not established; month-end handling Unknown / Not verified.
