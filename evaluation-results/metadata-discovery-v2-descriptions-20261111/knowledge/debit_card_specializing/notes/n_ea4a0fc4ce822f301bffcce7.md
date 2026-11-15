# Transaction gas station identifier

Type: column
Table: transactions_1k
Scope: GasStationID
Summary: INTEGER station reference on transactions; all 1,000 observed transaction rows matched a gasstations.GasStationID.
Keywords: transaction, gas station, identifier, join
Status: provisional
Sources: schema:transactions_1k DDL GasStationID INTEGER; schema:gasstations DDL GasStationID INTEGER PRIMARY KEY; values:transactions_1k LEFT JOIN gasstations on GasStationID, 1000/1000 matched

## Business Meaning
GasStationID identifies the gas station associated with a transaction; business semantics beyond this association are Unknown / Not verified.
## Business Usage
Can associate transaction records to gasstations using equal GasStationID values. All 1,000 observed transaction rows matched a gasstations key.
## Value Meaning
INTEGER station identifier; no special code interpretation verified.
## Calculation Meaning
N/A; stored source/pass-through field.
