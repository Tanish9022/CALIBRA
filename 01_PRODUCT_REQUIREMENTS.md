# CALIBRA — Product Requirements

## Identity
**Project:** CALIBRA — Explainable Metrology Compliance Engine  
**SIH Problem Statement:** SIH26035  
**Domain:** Legal Metrology / Non-Automatic Weighing Instruments (NAWI)  
**Primary standard:** OIML R76  
**Primary output:** evidence-backed standardized test report

## Product thesis
CALIBRA converts:
Instrument profile → applicable test plan → observations → validation → calculations → rule evaluation → PASS/FAIL/REVIEW → evidence → report.

The differentiator is the compliance engine, not PDF generation.

## Problem
SIH26035 describes the current NAWI test-report workflow as largely spreadsheet/document-template based and identifies it as time-consuming, prone to calculation errors and lacking uniformity. The requested software includes test-data recording, validation, calculations, automatic compliance determination, standardized reporting, storage, search/dashboard capabilities and role-based access.

## Goals

### Must have
- Instrument profiles
- Test sessions
- Observation entry
- Unit normalization
- Required-field and consistency validation
- Deterministic calculations
- Versioned R76 rules
- PASS / FAIL / REVIEW / NOT_APPLICABLE
- Explainable results
- Standardized report generation
- Evidence storage
- Search/retrieval
- Role-based access
- Audit trail
- Rules replaceable without rewriting UI

### Should have
- CSV/Excel import
- Legacy report extraction
- Dashboard/analytics
- Digital signatures
- API integration
- Offline draft/sync
- Rule regression tests

### Future
- Instrument/test-device integration
- Remote testing
- Multiple OIML recommendation modules
- Jurisdiction overlays
- Ruleset publishing lifecycle
- Laboratory information-system integration

## Non-goals
Do not claim universal legal approval, OIML certification, autonomous AI legal decisions, or complete R76 coverage until every implemented procedure is actually validated.

## Personas
- Technician
- Reviewer
- Laboratory Administrator
- Auditor / Regulatory User

## Core journeys
1. **New instrument**: Login → Create instrument → Validate profile → Generate test plan → Start session.
2. **Execute test**: Open test → Enter observations → Validate → Calculate → View result → View evidence → Complete/review.
3. **Finish report**: Complete required tests → Resolve warnings → Reviewer approval → Generate report → Store evidence/report.

## Principles
- **Explainability first**: Every derived result exposes source input, normalization, calculation, applicable rule, threshold, comparison, result and ruleset version.
- **Deterministic compliance**: AI may assist with extraction/classification; final compliance decisions are explicit rules.
- **Version everything**: Every result/report stores the exact ruleset.
- **Fail safely**: Ambiguous or contradictory situations become REVIEW rather than forced PASS.
- **Preserve raw evidence**: Never overwrite original observations.

## Pilot metrics
Measure rather than invent:
- report preparation time
- manual corrections
- validation issues caught
- incomplete sessions
- evidence completeness
- reports per technician
- report-format consistency

## Demo
Use a controlled Class III example:
Class III | Max 30 kg | e 10 g | Load 10 kg | Indication 10.008 kg

Show:
- Profile
- Generated test plan
- Observation
- Calculation
- Result
- Why/evidence
- Deliberate failure
- Report generation

## Acceptance criteria
A feature is complete when backend validation, persistence, tests, reproducible workflow, explainability and required audit events are present.

## Compliance safety
CALIBRA is a prototype for automating a standards-based workflow. All formulas and rules must be validated against authoritative OIML/DoCA material before production/regulatory use.
