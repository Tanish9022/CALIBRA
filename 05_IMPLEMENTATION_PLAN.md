# CALIBRA — Implementation Plan

## Phase 1: Foundation (Core Backend & DB)
**Focus**: Setting up the data models, initial database schema, and core validation logic.
1. **Repository Setup**: Initialize the backend project (e.g., Python FastAPI or Node/Express).
2. **Database Schema**: Create PostgreSQL models for `Instrument`, `TestSession`, `Observation`, and `RuleSet` using an ORM like SQLAlchemy or Prisma.
3. **Instrument Service**: Build CRUD operations and profile validation API.
4. **Basic API Gateway**: Wire up endpoints for managing instruments and sessions.

## Phase 2: Rules & Calculation Engine
**Focus**: Implementing the deterministic heart of CALIBRA.
1. **Rule Engine Service**: Implement the parser and evaluator for JSON-defined R76 rules.
2. **Calculation Service**: Create robust unit normalization, margin calculation, and raw input preservation pipelines.
3. **Test Definitions**: Encode a small subset of fully-validated R76 tests (e.g., Weighing Performance, Eccentricity) to act as MVP rules.
4. **Evidence Generation**: Wire up the evidence lineage (Input -> Normalization -> Calculation -> Rule -> Decision) to persist into the database.

## Phase 3: Reporting & Auditing
**Focus**: Proving the workflow and closing the loop.
1. **Report Generator**: Create PDF/DOCX templates mapping to OIML R76-2 structural format.
2. **Report Engine**: Feed data from finalized `TestSession` objects and their `Evidence` graphs into the reporting templates.
3. **Audit Trail**: Ensure all state changes (especially PASS/FAIL decisions) create an immutable audit record tied to a user role.

## Phase 4: User Interface
**Focus**: Bringing the functionality to the user while keeping logic separated.
1. **Scaffold Frontend**: Setup React/Next.js dashboard.
2. **Implement Instrument Profiler & Workspace**: Create the forms for defining the instrument and inputting raw test observations.
3. **Evidence UI (The "WHY?" Screen)**: Build the visualization for the Evidence Graph to fulfill the "explainability" core value.
4. **Connect to Reporting**: Provide the UI elements to export and archive the generated test reports.

## Phase 5: Verification & Pilot Deployment
**Focus**: Assuring quality and regulatory adherence of the MVP.
1. **Unit Testing**: Run through the hand-verified test cases and boundary rules defined in `03_R76_RULES_AND_COMPLIANCE_SPEC.md`.
2. **Integration Testing**: Validate the full journey from "Create Instrument" to "Generate Report" programmatically.
3. **Demo Rehearsal**: Ensure the 'Killer Demo Flow' defined in `04_UI_UX_AND_DEMO_SPEC.md` executes flawlessly.
