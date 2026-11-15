# Transaction amount

Type: column
Table: trans
Scope: amount
Summary: Required INTEGER transaction amount; observed amounts are positive on complete outgoing transfers, but denomination and unit scale are undocumented.
Keywords: transaction, amount, integer, payment, unit, aggregation
Status: provisional
Sources: schema:trans.amount INTEGER NOT NULL; values:trans amount range on VYDAJ/PREVOD NA UCET with bank and account populated

## Business Meaning
Numeric amount recorded for an account transaction.
## Business Usage
Can be aggregated as the recorded transaction measure; type and operation characterize transaction activity. Observed VYDAJ/PREVOD NA UCET rows with both recipient fields populated have positive amounts (range 1–14,882); amount semantics beyond recorded transaction amount are not verified.
## Value Meaning
INTEGER NOT NULL. Currency denomination and unit scale are Unknown / Not verified.
## Calculation Meaning
N/A; stored source/pass-through value. No conversion or rounding is verified.
