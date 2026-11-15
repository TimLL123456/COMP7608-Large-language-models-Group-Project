# Laboratory.GOT definition

Type: column
Table: Laboratory
Scope: GOT
Summary: Nullable INTEGER AST glutamic oxaloacetic transaminase laboratory result; source describes normal range below 60.
Keywords: got, ast, glutamic oxaloacetic transaminase, laboratory, range
Status: provisional
Sources: schema:Laboratory DDL GOT nullable INTEGER; description:Laboratory.csv:3 AST glutamic oxaloacetic transaminase, normal range N < 60

## Business Meaning
GOT is the AST glutamic oxaloacetic transaminase laboratory result, per source description.
## Business Usage
Can be used to analyze recorded GOT results by patient and date; individual test semantics beyond the field are Unknown / Not verified.
## Value Meaning
Nullable INTEGER. Source description states normal range N < 60; other coding or units are Unknown / Not verified.
## Calculation Meaning
N/A; stored source/pass-through field. Normal-range classification using <60 is an externally stated interpretation, not a stored calculation.
