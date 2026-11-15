# FRPM lowest grade served

Type: column
Table: frpm
Scope: Low Grade
Summary: Nullable TEXT label for lowest grade served; observed P, K, grades 1–12 and Adult; grade ordering is source-described only by label and user-provided ordering.
Keywords: frpm, low grade, grade served, p, k, school
Status: provisional
Sources: schema:frpm.`Low Grade`; values:frpm.`Low Grade` observed distinct values

## Business Meaning
Nullable TEXT field labeled `Low Grade` in an FRPM school record. Source schema does not define the precise concept beyond its field label; its relation to starting grade in K-12 enrollment is plausible but not independently documented.
## Business Usage
Used to categorize records by reported lower grade; apply an explicitly defined grade order rather than lexical string ordering.
## Value Meaning
Observed values include `P`, `K`, grade strings `1` through `12`, and `Adult`. The question defines P as pre-kindergarten, K as kindergarten, then grades 1–12; this semantic order is user-provided, not separately verified in source documentation. Adult is outside that sequence.
## Calculation Meaning
N/A; source/pass-through field.
