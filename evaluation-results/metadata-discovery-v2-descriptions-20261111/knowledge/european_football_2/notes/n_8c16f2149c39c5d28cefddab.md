# Player_Attributes.heading_accuracy definition

Type: column
Table: Player_Attributes
Scope: heading_accuracy
Summary: Recorded integer player heading-accuracy rating in dated player attribute records.
Keywords: heading accuracy, player skill, attribute rating
Status: provisional
Sources: schema:Player_Attributes.heading_accuracy INTEGER; schema:Player_Attributes DDL foreign keys to Player API identifiers

## Business Meaning
Player heading-accuracy attribute recorded in Player_Attributes.
## Business Usage
Can be analyzed across player attribute records and averaged by player; join to Player using player_api_id. No date-selection rule is specified by the schema.
## Value Meaning
Integer-valued rating; scale, bounds, and special codes are not verified from schema.
## Calculation Meaning
Source/pass-through field; no calculation in the table schema.
