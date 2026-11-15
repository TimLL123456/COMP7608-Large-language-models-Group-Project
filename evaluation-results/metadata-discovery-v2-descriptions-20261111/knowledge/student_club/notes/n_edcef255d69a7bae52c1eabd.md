# Expense date

Type: column
Table: expense
Scope: expense_date
Summary: Text date associated with an expense record; observed October-November 2019 values use YYYY-MM-DD.
Keywords: expense, date, day
Status: provisional
Sources: schema:expense.expense_date TEXT; values:expense.expense_date observed YYYY-MM-DD examples including October-November 2019

## Business Meaning
Date associated with an expense record; whether it represents purchase/transaction date, entry date, or another date is Unknown / Not verified.
## Business Usage
Can filter expense records by date periods.
## Value Meaning
Stored as TEXT; observed sample values use YYYY-MM-DD format. Other formats are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through date field.
