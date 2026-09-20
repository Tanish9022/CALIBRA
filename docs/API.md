# CALIBRA — API Specification

The CALIBRA backend exposes clean RESTful APIs designed for compliance verification, real-time calculation, gravity screening, and audit replay.

## Base URL: `http://localhost:8000`

---

## 1. Compliance Context & Gravity
- `GET /compliance-context/locations`  
  Returns all national reference metrological laboratories and testing stations (Delhi, Leh, Mumbai, Zurich, Singapore).
- `POST /compliance-context/estimate-gravity`  
  Computes theoretical local gravity using the Somigliana 1980 / WGS84 formula + free-air elevation reduction.  
  **Request Body:** `{"latitude_deg": 28.6139, "elevation_m": 216.0}`
- `POST /compliance-context/evaluate-transferability`  
  Evaluates location transferability under OIML R76-1:2006 Clause 3.9.2.  
  **Request Body:**
  ```json
  {
    "accuracy_class": "III",
    "max_capacity_kg": 30.0,
    "verification_interval_e_g": 10.0,
    "has_internal_calibration": false,
    "is_gravity_sensitive": true,
    "test_location_name": "New Delhi",
    "test_gravity_ms2": 9.7912,
    "intended_location_name": "Leh Ladakh",
    "intended_gravity_ms2": 9.7744
  }
  ```
  **Response:** `TRANSFERABLE` | `CONDITIONAL` | `RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED`.
- `POST /compliance-context/impact-analysis`  
  Analyzes the impact of a context or ruleset modification on active test plans.

---

## 2. Compliance Evaluation & Explainability
- `POST /compliance/evaluate_weighing/{observation_id}`  
  Executes deterministic calculation ($P = I + 0.5e - \Delta L$, $E = P - L$, $E_c = E - E_0$) and compares with Table 6 MPE. Persists immutable evidence record.
- `GET /compliance/explain/{evidence_id}`  
  Returns the exact step-by-step lineage, formula inputs, intermediate decimals, and Table 6 boundary comparison for the **"WHY?"** explainability drawer.
- `GET /compliance/coverage-gate/{session_id}`  
  Checks mandatory test completeness, load points, repeat weighings, and test equipment calibration status.

---

## 3. Standardized Reports & Replay
- `POST /reports/generate/{session_id}?force=false`  
  Enforces CoverageGate. Compiles standardized OIML R76-2 PDF report and registers cryptographic SHA-256 hash.
- `GET /reports/download/{session_id}`  
  Streams the generated PDF report.
- `GET /reports/{report_id}/verify`  
  Cryptographically verifies the physical file on disk against the stored SHA-256 database checksum.
- `GET /replay/session/{session_id}`  
  Reconstructs the full end-to-end historical audit timeline.

---

## 4. Test Equipment Traceability
- `GET /equipment`  
  Lists all calibrated standard weights (Class E2, F1, M1) and equipment.
- `POST /equipment`  
  Registers a new test standard with certificate number and calibration expiry.
- `GET /equipment/validate/{equipment_id}`  
  Checks if equipment calibration has expired.

---

## 5. Automated Verification Scenarios
- `POST /demo/gravity-scenario`  
  Triggers the Delhi $\rightarrow$ Leh geographical gravity shift test and returns mathematical proof.
- `POST /demo/expired-equipment-scenario`  
  Triggers the expired standard weights scenario demonstrating Coverage Gate BLOCK.
