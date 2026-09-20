# CALIBRA - Operational Walkthrough Script

This document provides a guided walkthrough of CALIBRA as an explainable Legal Metrology compliance engine for Non-Automatic Weighing Instruments (NAWI) per OIML Recommendation R-76.

For the comprehensive technical operational guide, see [docs/OPERATIONAL_GUIDE.md](file:///c:/Users/tanish/OneDrive/Tài liệu/Desktop/oiml/docs/OPERATIONAL_GUIDE.md).

## Setup
1. Start the backend: `python -m uvicorn main:app --reload --port 8000` (from `backend/`).
2. Start the frontend: `npm run dev` (from `frontend/`).
3. Open `http://localhost:5174` in your browser.

## Step 1: The Metrology Dashboard
*(Start on the Dashboard)*
- The CALIBRA Dashboard displays live verification statistics across profiled instruments, test sessions, and issued certificates.
- The Metrological Operations Hub provides direct access to every core engine.

## Step 2: Instrument Profile & Test Plan Compilation
*(Navigate to Instruments)*
- Profiles Class I, II, III, and IIII weighing instruments.
- Dynamically compiles tailored test plans based on instrument capacity, verification intervals, and tare capabilities per OIML R76.

## Step 3: Test Workspace & Deterministic Evaluation
*(Navigate to Test Workspace)*
- Enter raw observations ($L, I, \Delta L, E_0$).
- Executes turning point derivation ($P = I + 0.5e - \Delta L$) and zero error correction ($E_c = E - E_0$).
- Click "WHY?" to inspect the step-by-step mathematical proof against OIML Table 6 Maximum Permissible Errors.

## Step 4: Geographical Gravity Screening & Transferability
*(Navigate to Gravity Hub)*
- Evaluates Somigliana 1980 WGS84 theoretical gravity and elevation lapse rates.
- Evaluates OIML R76-1 Clause 3.9.2 transferability (e.g. New Delhi to Leh Ladakh) and automatic internal calibration exemptions.

## Step 5: Reports & Compliance Replay
*(Navigate to Reports & Compliance Replay)*
- Issues tamper-resistant OIML R76-2 certificates with embedded SHA-256 hashes.
- Audits historical reasoning lineage with zero drift.
