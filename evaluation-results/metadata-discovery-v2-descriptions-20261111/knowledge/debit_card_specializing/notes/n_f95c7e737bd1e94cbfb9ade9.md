# Transaction records (limited sample)

Type: table
Table: transactions_1k
Scope: table_definition
Summary: Transaction rows with date, customer/card/product/station identifiers, amount and price; observed sample covers only four dates in August 2012.
Keywords: transaction, date, customer, product, amount, price
Status: provisional
Sources: schema:transactions_1k DDL columns and TransactionID primary key; values:transactions_1k row count and observed Date min/max/distinct count

## Business Summary
Stores transaction-like records with date/time, customer/card/station/product identifiers, Amount and Price; exact field units are Unknown / Not verified.
## Business Use Cases
Can describe recorded transactions and relate identifiers to catalogs by matching values. The table's data cannot establish 2013 purchase activity.
## Data Granularity
One row per TransactionID; schema declares TransactionID as an autoincrement primary key. Other uniqueness is Unknown / Not verified.
## Data Scope & Exclusions
The table contains 1,000 rows with observed dates 2012-08-23 through 2012-08-26 (four distinct dates); no 2013 transactions were observed. Broader transaction coverage and inclusion rules are Unknown / Not verified.
