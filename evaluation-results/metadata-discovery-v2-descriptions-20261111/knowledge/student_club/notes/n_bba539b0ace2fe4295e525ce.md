# Expense member reference

Type: column
Table: expense
Scope: link_to_member
Summary: Member identifier associated with an expense record and referencing member.member_id; its role as purchaser remains unverified.
Keywords: expense, member, reference, identifier, responsibility
Status: provisional
Sources: schema:expense.link_to_member TEXT REFERENCES member(member_id)

## Business Meaning
Member identifier associated with an expense record; schema establishes a foreign key to member.member_id, but whether it identifies the purchaser, submitter, or another responsible party is Unknown / Not verified.
## Business Usage
Can join an expense row to a member record; attribution specifically as a purchase is unverified.
## Value Meaning
Text foreign-key reference; no special code interpretation verified.
## Calculation Meaning
N/A; source/pass-through reference field.
