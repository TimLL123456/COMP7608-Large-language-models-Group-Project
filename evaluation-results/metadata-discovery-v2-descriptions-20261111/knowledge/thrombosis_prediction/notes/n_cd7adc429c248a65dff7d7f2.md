# Laboratory.SM definition

Type: column
Table: Laboratory
Scope: SM
Summary: Nullable TEXT anti-SM result field; observed codes include 0, 1, 2, 8 and negative; clinical mapping is not fully verified.
Keywords: sm, anti-sm, laboratory, antibody, result
Status: provisional
Sources: schema:Laboratory DDL SM TEXT nullable; values:SELECT `SM`, COUNT(*) AS n FROM Laboratory GROUP BY `SM` ORDER BY `SM`

## Business Meaning
SM is a Laboratory serology result field corresponding to anti-SM per the source/table context.
## Business Usage
Can be used to find patient laboratory records with recorded SM results; retain raw text values.
## Value Meaning
Nullable TEXT. Inspected values include `0`, `1`, `2`, `8`, and `negative`. Clinical mapping of codes is Unknown / Not verified by source documentation; supplied-question normal categories are query-specific and not generalized here.
## Calculation Meaning
N/A; stored source/pass-through field.
