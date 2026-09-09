# CALIBRA — R76 Rules and Compliance Specification

## Purpose
Define how CALIBRA represents, tests and executes OIML R76 requirements.

**IMPORTANT:** This engineering specification is not a substitute for the authoritative OIML document. Exact formulas, thresholds, exceptions and applicability conditions must be transcribed and validated from the exact R76 edition adopted for the MVP.

## Rule lifecycle
```
Authoritative OIML source
  |
  v
Rule interpretation
  |
  v
Machine-readable rule
  |
  v
Unit tests/reference cases
  |
  v
Peer review
  |
  v
Published ruleset
```
*Never silently edit a published ruleset.*

## Ruleset identity
- standard = OIML R76
- edition = <validated edition>
- version = <internal version>
- source_document = <authoritative reference>
- checksum = <hash>
- status = DRAFT | VALIDATED | PUBLISHED | RETIRED

## Rule categories
- Applicability rules
- Calculation rules
- Threshold/MPE rules
- Decision rules

## Calculation example
Use only after confirming the exact applicable authoritative rule.
```
Reference load = 10 kg
Observed indication = 10.008 kg
Error = observed indication - reference load = +0.008 kg = +8 g

If the verified applicable limit is ±10 g:
abs(+8 g) <= 10 g => PASS
```
Store:
- raw load
- raw indication
- units
- normalized values
- formula
- result
- rule
- ruleset version

## MPE decision pipeline
```
Instrument profile
  |
  v
Accuracy class
  |
  v
Load expressed in verification intervals
  |
  v
Applicable MPE region
  |
  v
Permissible error
  |
  v
Observed error comparison
  |
  v
Decision
```
*Never hard-code one MPE for every case.*

## Unit normalization
MVP may explicitly support: `mg`, `g`, `kg`

Store:
- raw unit
- normalized unit
- conversion factor
- conversion operation

*Unsupported or ambiguous units => REVIEW/validation error.*

## Validation
- **Structural**: missing mandatory fields, malformed numeric values, empty observations
- **Range**: values outside known input constraints
- **Cross-field**: observed load beyond declared capacity, e <= 0, incompatible configuration, contradictory metadata
- **Sequence**: Do not run dependent calculations until required observations exist.
- **Suspicious data**: Flag unusual/repeated patterns for review; do not accuse manipulation automatically.

## Decision policy
- **PASS**: All required data validated and applicable requirement satisfied.
- **FAIL**: All required data validated and deterministic requirement not satisfied.
- **REVIEW**: Ambiguous, contradictory, missing or explicitly human-review-required condition.
- **NOT_APPLICABLE**: Only when an approved applicability rule says so.

## Evidence chain
```
RAW INPUT
  |
  v
NORMALIZATION
  |
  v
CALCULATION
  |
  v
APPLICABLE RULE
  |
  v
THRESHOLD
  |
  v
DECISION
```

## Explainability API concept
```json
{
  "status": "PASS",
  "reason": "Observed value is within the applicable verified limit.",
  "inputs": {},
  "normalized_values": {},
  "calculation": {},
  "rule": {
    "standard": "OIML R76",
    "edition": "<validated edition>",
    "code": "<rule-code>"
  },
  "threshold": {},
  "evidence_id": "<id>"
}
```

## Unit tests for every rule
Each rule needs: normal passing case, boundary case, just-over-limit case, invalid-input case, unit-conversion case where applicable.
*Boundary semantics must come from the authoritative rule.*

## Reference corpus
Build: hand-verified examples, synthetic edge cases, malformed inputs, regression cases from software bugs.
*Synthetic cases validate code behavior; they do not prove legal correctness.*

## AI boundary
**AI may:**
- extract data from legacy reports
- classify free-text labels
- flag anomalies
- explain a deterministic result in natural language

**AI may not:**
- invent OIML requirements
- invent thresholds
- override deterministic rules
- declare legal compliance by itself

## Rule change workflow
```
Draft ↓ Source comparison ↓ Implementation ↓ Tests ↓ Peer review ↓ Publish ↓ Checksum/version
```
*Old finalized reports remain tied to their original ruleset.*

## MVP recommendation
Implement a small fully-validated subset first:
- instrument profile
- test plan
- 3–5 core tests
- calculations
- verified MPE/decision path
- evidence
- report

A verified small engine is better than an unverified claim of complete R76 coverage.
