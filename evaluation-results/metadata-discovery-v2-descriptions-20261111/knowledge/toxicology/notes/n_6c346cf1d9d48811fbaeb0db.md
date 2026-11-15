# atom.molecule_id

Type: column
Table: atom
Scope: molecule_id
Summary: Optional text molecule identifier associates atom records with the molecule they belong to; foreign key to molecule.molecule_id.
Keywords: atom, molecule_id, association, foreign key
Status: provisional
Sources: schema:atom.molecule_id TEXT DEFAULT NULL; schema:atom foreign key to molecule.molecule_id; description:atom.csv:2

## Business Meaning
Identifier for the molecule to which an atom record belongs.
## Business Usage
Joins atom rows to molecule rows and supports grouping atoms by molecule.
## Value Meaning
Text value; schema permits NULL and declares a foreign key to molecule.molecule_id. Source description says TRXXX_i denotes the ith atom of molecule TRXXX.
## Calculation Meaning
N/A; source/pass-through field.
