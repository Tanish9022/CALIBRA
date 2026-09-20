# CALIBRA — Metrological Operational Verification Guide

This document details the complete end-to-end operational verification workflow for CALIBRA as an enterprise Legal Metrology compliance engine compliant with OIML R-76-1:2006 and OIML R-76-2:2012.

---

## End-to-End Operational Workflow

### STEP 1: Architectural Verification & Dashboard Overview
- Navigate to `http://localhost:5174/`.
- Inspect the active system status:
  - 3 Profiling Instrument types (Class I, II, III, IIII)
  - 100% Deterministic decimal precision (arbitrary-precision Decimal arithmetic, 0% LLM hallucination risk)
  - Active test sessions and cryptographically sealed reports
  - Quick access to all core subsystems via the **Metrological Operations Hub**

---

### STEP 2: Geographical Gravity Screening & Transferability (Clause 3.9.2)
- Navigate to the **Gravity Screening Hub** (`/compliance-context`).
- Select or enter baseline verification conditions:
  - **Baseline Verification Center**: New Delhi Central Laboratory ($g = 9.7912 \text{ m/s}^2$).
  - **Intended Installation Location**: Leh Ladakh High-Altitude Facility ($g = 9.7744 \text{ m/s}^2$, elevation 3500 m).
- Examine the mathematical evaluation per OIML R76-1 Clause 3.9.2:
  - Calculated Relative Gravity Shift: $\frac{\Delta g}{g} = \mathbf{1715\text{ ppm}}$.
  - Maximum Permissible Error at Max Capacity: $\mathbf{500\text{ ppm}}$.
  - Legal Transferability Threshold: $\frac{1}{3} \text{ MPE} = \mathbf{166.7\text{ ppm}}$.
- System Determination:  
  $$\mathbf{RE\text{-}TEST\ /\ LOCATION\text{-}SPECIFIC\ EVALUATION\ REQUIRED}$$
- Test Self-Calibration Exemption:
  - Toggle the **"Internal Auto-Calibration Weight"** control.
  - The system dynamically updates the decision to **`TRANSFERABLE`** with explicit OIML R76 exemption citations.

---

### STEP 3: Test Workspace, Turning Point Derivation, & "WHY?" Explainability
- Navigate to **Test Workspace** (`/workspace`).
- Enter observation parameters:
  - Reference Standard Load ($L$): `10.0 kg`
  - Observed Indication ($I$): `10.018 kg`
  - Small Additional Weights to Turning Point ($\Delta L$): `4.0 g`
  - Prior Zero Error ($E_0$): `2.0 g`
- Click **"Evaluate Observation"**:
  - The compliance engine renders: **`FAIL`** ($E_c = +17\text{ g} > \text{MPE } \pm 10\text{ g}$).
- Click **"WHY? (Explain Decision)"**:
  - Step 1: Pre-rounding turning point $P = I + 0.5e - \Delta L = 10.018 + 5 - 4 = 10.019\text{ kg}$.
  - Step 2: Raw error $E = P - L = +19\text{ g}$.
  - Step 3: Corrected error $E_c = E - E_0 = +17\text{ g}$.
  - Step 4: OIML Table 6 lookup at $m = 1000e \implies \text{MPE } \pm 10\text{ g}$.
  - Step 5: Comparison $|+17\text{ g}| > 10\text{ g} \implies \mathbf{FAIL}$.

---

### STEP 4: Standards Traceability & Coverage Gate Enforcement
- Navigate to **Test Standards & Weights** (`/equipment`).
- Inspect reference mass standards: Class E2, F1, and M1 weights with traceable calibration certificates.
- Observe expired equipment handling (e.g. standard `EQ-EXP-004`).
- Open **Coverage Gate Status** on an active session:
  - The Coverage Gate verifies:
    1. Mandatory load point distribution (Min, 500e, 2000e, Max).
    2. Repeatability repetitions ($n \ge 3$).
    3. Eccentricity off-center load points ($4$ or $5$ points depending on load receptor shape).
    4. Test equipment calibration validity.
  - If any prerequisite fails, the system enforces a hard freeze preventing report finalization.

---

### STEP 5: Standardized OIML Report & Cryptographic Compliance Replay
- Navigate to **Reports** (`/reports`).
- Generate and download the standardized OIML R76-2 certificate:
  - Validates full context metadata, equipment traceability numbers, load point matrices, and SHA-256 integrity seal.
- Navigate to **Compliance Replay** (`/replay`):
  - Step through the complete 5-stage reconstructed audit pipeline:
    `Input → Context → Ruleset → Test Plan → Observation → Calculation → MPE → Decision`.
  - Verify the **SHA-256 Tamper Verification Hash**.
  - All decisions are deterministic, context-aware, explainable, and replayable decades later by regulatory authorities.
