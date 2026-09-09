# CALIBRA — UI/UX and Demo Specification

## Design objective
The interface should communicate:
**AUTOMATE. EXPLAIN. PROVE.**

It should feel like regulated laboratory software, not a generic AI dashboard.

## Navigation
- Dashboard
- Instruments
- Test Sessions
- Test Plans
- Results
- Reports
- Evidence
- Audit Logs
- Rulesets
- Administration

## Screen 1 — Dashboard
**Cards:** Active Tests, Pending Review, Completed Tests, Failed Tests
**Main panels:** recent sessions, attention-required items, report queue, throughput

## Screen 2 — Instrument Profile
**Fields:** manufacturer, model, instrument type, accuracy class, Max, Min, e, number of intervals, configuration, supporting document
**Actions:** Validate Profile, Generate Test Plan

## Screen 3 — Generated Test Plan
Example:
```
01 Administrative examination    REQUIRED
02 Construction examination      REQUIRED
03 Weighing performance          REQUIRED
04 Repeatability                 REQUIRED
05 Eccentricity                  REQUIRED
06 Zero return                   CONDITIONAL
...
```
*Each card shows status, required/conditional state, progress and “Why is this required?”.*

## Screen 4 — Test Workspace
**Desktop layout:**
- left: test list
- center: observation entry
- right: live validation/calculation

Example:
```
Reference Load | Observed
5 kg           | 5.006 kg
10 kg          | 10.008 kg
20 kg          | 20.014 kg
```
**Actions:** Save Draft, Validate, Calculate, Complete Test

## Screen 5 — Result
Large result: **PASS**
Show: observed error, applicable limit, margin, rule, evidence ID
**Buttons:** WHY?, VIEW EVIDENCE, REPORT

## Screen 6 — Why?
Evidence tree:
```
Raw Observation
  |
  v
Normalized Value
  |
  v
Calculation
  |
  v
Applicable R76 Rule
  |
  v
Threshold
  |
  v
Decision
```
*Each node opens metadata.*

## Screen 7 — Failure
Never show only FAIL.
Example:
```
FAIL
Observed error: +80 g
Permissible limit: ±10 g
Exceedance: 70 g
Reason: Observed absolute error exceeds the applicable verified limit.
[VIEW EVIDENCE]
```

## Screen 8 — REVIEW
```
REVIEW REQUIRED
Reason: Inconsistent instrument configuration.
Issue: Observed load > declared Max.
Action: Review instrument profile.
```

## Screen 9 — Report
**Preview:** report metadata, instrument identity, test conditions, test results, PASS/FAIL, remarks, reviewer, ruleset, evidence references
**Actions:** PDF, DOCX, Archive, Sign (future), Export

## Demo storyline
1. **Establish problem**: Observation -> Spreadsheet -> Manual calculation -> Template -> PDF
2. **Create instrument**: Class III, Max 30 kg, e 10 g
3. **Generate test plan**
4. **Enter valid data**: 10.000 kg, 10.008 kg
5. **Show result**: Error = +8 g, Result = PASS
6. **Click WHY**: Reveal input → calculation → rule → threshold → decision.
7. **Break the workflow**: Use a deliberately failing observation.
8. **Show explanation.**
9. **Generate report.**

## UI copy
**Prefer:** Why did this pass?, Why did this fail?, Review required, Applicable rule, Evidence chain, Ruleset version, Input validation
**Avoid:** AI says compliant, 100% accurate, Guaranteed approval, Legally valid everywhere

## Visual language
- technical blue primary
- green PASS
- red FAIL
- amber REVIEW
- white/light background
- restrained icons
- compact cards
- strong diagrams
*Do not rely on color alone for status.*

## Screenshot checklist
- [ ] Dashboard
- [ ] Test Data Entry
- [ ] PASS + explanation
- [ ] FAIL + explanation
- [ ] Evidence Graph
- [ ] Report
- [ ] Ruleset/version
- [ ] Global architectu ] Instrument Profile
- [ ] Auto Test Plan
- [re
