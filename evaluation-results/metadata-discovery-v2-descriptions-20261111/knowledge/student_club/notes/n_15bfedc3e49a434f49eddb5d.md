# Budget entry spent amount

Type: column
Table: budget
Scope: spent
Summary: REAL amount spent in a budget category, documented as expense spending summarized per event category; entries aggregate to events.
Keywords: budget, spent, expense, amount, dollar, event
Status: provisional
Sources: schema:budget.spent REAL; schema:budget.link_to_event REFERENCES event(event_id); schema:expense.link_to_budget REFERENCES budget(budget_id); description:Budget.csv:3; values:budget 52 rows spent non-NULL across 23 events; values:per-event budget.spent sums matched linked expense.cost sums for all observed expense-present groups, 12 event groups without linked expense records

## Business Meaning
Amount spent in the budgeted category for an event, per the Budget description.
## Business Usage
Supports category-level and event-level spending summaries. Budget rows link to events; multiple budget entries may belong to one event. The Expense table references budget entries.
## Value Meaning
REAL amount; documentation identifies dollars. In observed data all 52 budget rows have non-NULL spent values.
## Calculation Meaning
Documentation says this value is a total summarized from Expense, but exact calculation is unspecified. In the observed database, per-budget-entry sums of linked expense.cost match budget.spent for all event groups that have expenses; 12 of 23 event groups have no linked expenses, so this check does not establish spend calculation for all cases.
