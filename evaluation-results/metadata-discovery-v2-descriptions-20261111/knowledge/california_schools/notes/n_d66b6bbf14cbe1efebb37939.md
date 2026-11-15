# Grade span offered

Type: column
Table: schools
Scope: GSoffered
Summary: Nullable TEXT field recording grades offered; distinct from enrolled grades, with observed preschool-prefixed and grade-number spans.
Keywords: gsoffered, grades offered, schools, grade span, preschool
Status: provisional
Sources: schema:schools.GSoffered; values:schools.GSoffered for NCESDist 0632640

## Business Meaning
`GSoffered` records the grade range offered at a school directory record; exact source definition is Unknown / Not verified.
## Business Usage
Use to identify grades offered; distinct from `GSserved`, which identifies grades with student enrollment.
## Value Meaning
Observed district 0632640 forms include `K-2`, `K-6`, `K-8`, `P-6`, and null. The question-supplied evidence says `P` stands for preschool. Other conventions are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
