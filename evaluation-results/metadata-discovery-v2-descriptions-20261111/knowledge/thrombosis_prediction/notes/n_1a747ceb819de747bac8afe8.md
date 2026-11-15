# Laboratory.ALB definition

Type: column
Table: Laboratory
Scope: ALB
Summary: Nullable REAL laboratory field; source description identifies ALB as albumin, while units and calibration are not specified.
Keywords: alb, albumin, laboratory, measurement, nullable
Status: provisional
Sources: schema:Laboratory.ALB REAL nullable; description:Laboratory.csv ALB field identification

## Business Meaning
ALB is identified as albumin in the Laboratory source description.
## Business Usage
Can be used as an albumin measurement in laboratory-record analyses; a patient may have dated records over time.
## Value Meaning
REAL, nullable. Units, reference range, and special codes are Unknown / Not verified.
## Calculation Meaning
N/A; stored source/pass-through measurement. No source-defined derivation is specified.
