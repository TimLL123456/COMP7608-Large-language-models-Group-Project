# Superhero publisher reference and creator ambiguity

Type: column
Table: superhero
Scope: publisher_id
Summary: Nullable foreign key to publisher.id; observed labels such as Marvel Comics filter dataset association, while creator or franchise semantics are not verified.
Keywords: superhero, publisher_id, publisher, foreign key, marvel comics
Status: provisional
Sources: schema:superhero.publisher_id foreign key to publisher.id; schema:publisher DDL; values:publisher.publisher_name includes Marvel Comics and George Lucas

## Business Meaning
Nullable integer association between a superhero record and a publisher record.
## Business Usage
Join superhero.publisher_id to publisher.id to filter records by associated publisher label, including observed Marvel Comics. This association is not independently established as creator attribution.
## Value Meaning
IDs reference publisher rows; NULL is allowed. The publisher table includes labels such as Marvel Comics and George Lucas; semantics beyond the stored label are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
