# Transaction bank code

Type: column
Table: trans
Scope: bank
Summary: Nullable bank code on transfer transactions; observed codes pair with recipient account but external-bank classification remains undocumented.
Keywords: transaction, bank, recipient, transfer, code, nullable
Status: provisional
Sources: schema:trans.bank TEXT NULL; values:trans grouped by type and operation; values:trans VYDAJ/PREVOD NA UCET bank/account completeness

## Business Meaning
Nullable bank-related code on a transaction; precise role and bank identity mapping are not defined by the schema.
## Business Usage
On observed VYDAJ/PREVOD NA UCET rows, bank pairs with trans.account for the recipient. 208,282 of 208,283 such rows had a nonnull bank and account; one row had both null. No evidence establishes which codes identify banks external to the institution, so external classification is Unknown / Not verified.
## Value Meaning
TEXT nullable. Observed nonnull codes: AB, CD, EF, GH, IJ, KL, MN, OP, QR, ST, UV, WX, YZ. Full code dictionary and external/internal mapping Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
