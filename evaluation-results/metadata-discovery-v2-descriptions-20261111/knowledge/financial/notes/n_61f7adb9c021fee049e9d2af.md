# Loan approval date

Type: column
Table: loan
Scope: date
Summary: Loan date field is described as the date the loan was granted; stored as non-null DATE.
Keywords: loan, date, approval, granted, term
Status: provisional
Sources: schema:loan.date (DATE NOT NULL); description:loan.csv:3 (loan approval date); description:question evidence (term starts on approval day)

## Business Meaning
Date the loan was granted, per the loan field description.
## Business Usage
Can serve as the start of the loan repayment term; supplied task evidence specifies that term includes the approval day.
## Value Meaning
DATE NOT NULL. No special code/value interpretation applies.
## Calculation Meaning
Source/pass-through date. Term-end calculation requires the duration in months; the exact month-boundary convention is Unknown / Not verified.
