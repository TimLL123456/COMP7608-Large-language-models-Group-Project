# Loan monthly payment amount

Type: column
Table: loan
Scope: payments
Summary: Loan payments field is documented as monthly payment; REAL stored value, denomination not documented in schema.
Keywords: loan, payments, monthly payment, installment, real
Status: provisional
Sources: schema:loan.payments REAL NOT NULL; description:loan.csv:6 (monthly payment)

## Business Meaning
Payment amount recorded for a loan; field documentation identifies it as the monthly payment.
## Business Usage
Can be multiplied by duration in months to derive a scheduled total-payment measure when that calculation is intended.
## Value Meaning
REAL NOT NULL; currency denomination or unit beyond monthly payment is Unknown / Not verified.
## Calculation Meaning
Source field is the recorded monthly payment. A total based on monthly payment times duration is a derived calculation, not the stored field.
