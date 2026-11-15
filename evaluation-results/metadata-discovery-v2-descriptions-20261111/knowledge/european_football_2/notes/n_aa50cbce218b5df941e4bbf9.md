# Player_Attributes.date definition

Type: column
Table: Player_Attributes
Scope: date
Summary: Text snapshot timestamp; 2013-07-12 has one record per observed player, while other days may contain same-player duplicate dates.
Keywords: player attributes, date, temporal record, calendar day, duplicates
Status: provisional
Sources: schema:Player_Attributes.date TEXT; schema:Player_Attributes.id INTEGER PRIMARY KEY; values:Player_Attributes records grouped by player and calendar date show one 2013-07-12 row per observed player; values:Player_Attributes same-player same-date duplicates observed on other dates

## Business Meaning
Text timestamp associated with a player's attribute record; exact capture semantics are Unknown / Not verified.
## Business Usage
Supports ordering player attribute records by timestamp and filtering calendar days. Same-player duplicate date records occur elsewhere, so per-day selection may require a rule. For 2013-07-12, the observed records cover 346 distinct players, with one record each on that date; the schema alone does not establish a general uniqueness constraint.
## Value Meaning
TEXT values observed include timestamp-formatted date strings such as 2013-07-12 00:00:00.
## Calculation Meaning
N/A; source/pass-through field.
