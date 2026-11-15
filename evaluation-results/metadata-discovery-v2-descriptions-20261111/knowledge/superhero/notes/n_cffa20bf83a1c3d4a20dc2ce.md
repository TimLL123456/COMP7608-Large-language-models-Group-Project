# Attribute lookup identifier

Type: column
Table: attribute
Scope: id
Summary: Non-null integer primary key identifying an attribute lookup row; referenced by hero_attribute.attribute_id.
Keywords: attribute, id, primary key, lookup, hero attribute
Status: provisional
Sources: schema:attribute DDL primary key id; schema:hero_attribute foreign key attribute_id to attribute.id

## Business Meaning
Integer identifier for a superhero attribute lookup record.
## Business Usage
Join to hero_attribute.attribute_id to identify the attribute associated with a hero-attribute row.
## Value Meaning
INTEGER primary key and NOT NULL; particular ID-to-name assignments are dataset-specific.
## Calculation Meaning
N/A; source/pass-through field.
