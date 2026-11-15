# Attribute reference in hero-attribute association

Type: column
Table: hero_attribute
Scope: attribute_id
Summary: Nullable integer foreign key identifying the attribute lookup associated with a superhero's attribute value.
Keywords: attribute id, hero attribute, foreign key, superhero
Status: provisional
Sources: schema:hero_attribute.attribute_id INTEGER default NULL; schema:hero_attribute foreign key attribute_id to attribute.id

## Business Meaning
Integer reference identifying the attribute represented by an association row.
## Business Usage
Join to attribute.id to determine the named attribute for a hero_attribute row.
## Value Meaning
Nullable INTEGER; references attribute.id according to the schema. Special codes are Unknown / Not verified.
## Calculation Meaning
N/A; source/pass-through field.
