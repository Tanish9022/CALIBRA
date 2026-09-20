# CALIBRA — Explainable Metrology Compliance Engine for NAWI (OIML R-76)

**Legal Metrology Platform:** Production-grade software system for Non-Automatic Weighing Instruments (NAWI) testing, verification, and legal test report generation compliant with OIML Recommendation R-76-1:2006 and R-76-2:2012.

---

## 1. Executive Summary

CALIBRA is **not** a generic CRUD form or simple PDF template.  
It is an **evidence-driven compliance engine** that transforms raw NAWI test observations into deterministic, context-aware, explainable, and auditable legal decisions:

$$\mathbf{Instrument\ Profile} \rightarrow \mathbf{Compliance\ Context} \rightarrow \mathbf{R76\ Compiler} \rightarrow \mathbf{Dynamic\ Test\ Plan} \rightarrow \mathbf{Test\ Observations} \rightarrow \mathbf{Decimal\ Calculation} \rightarrow \mathbf{R76\ Rules} \rightarrow \mathbf{PASS/FAIL/REVIEW} \rightarrow \mathbf{Explainable\ Trace} \rightarrow \mathbf{Coverage\ Gate} \rightarrow \mathbf{Standardized\ Report} \rightarrow \mathbf{Compliance\ Replay}$$

---

## 2. Core Architectural Highlights

1. **Deterministic Metrology Core:** Evaluates all observations using arbitrary-precision Python `Decimal` (34 digits of precision). Zero LLM involvement in PASS/FAIL/MPE calculations.
2. **First-Class Gravity Context Engine:** Implements the international Somigliana (WGS84) gravity formula with free-air elevation reduction. Evaluates OIML R76-1:2006 Clause 3.9.2 location transferability (e.g. proves mathematically why a test in New Delhi cannot be blindly transferred to Leh, Ladakh).
3. **Coverage Gate:** Strictly prevents official report finalization if mandatory tests, load points, or traceable test standards are missing or expired.
4. **Instant "WHY?" Explainability:** Every compliance decision provides a one-click mathematical lineage showing raw input, turning point $P = I + 0.5e - \Delta L$, raw error $E = P - L$, zero correction $E_c = E - E_0$, and OIML Table 6 MPE limits.
5. **Compliance Replay (`/replay`):** Allows regulatory auditors to step through the historical reasoning chain and inspect whether active rulesets differ from the historical ruleset used.
6. **Cryptographic SHA-256 Tamper Detection:** Standardized OIML R76-2 PDF reports are hashed upon generation. Any subsequent tampering is flagged immediately.

---

## 3. Setup Instructions & Environment Variables

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ and npm
- Windows / Linux / macOS

### Environment Variables (Optional defaults work out-of-the-box):
```env
# Optional environment variables
DATABASE_URL=sqlite:///./calibra.db   # For PostgreSQL: postgresql://user:pass@localhost:5432/calibra
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=*
SECRET_KEY=calibra-super-secret-metrology-audit-key
```

---

## 4. Quick Start Commands

### 4.1 Backend Setup & Seed
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python seed.py --force
```

### 4.2 Start Backend Server
```bash
# From backend/ directory
python -m uvicorn main:app --reload --port 8000
```
Backend API will be live at: `http://localhost:8000` (API documentation at `/docs`).

### 4.3 Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Open browser at: `http://localhost:5174/`

---

## 5. Automated Verification & Benchmark Commands

Execute from the `backend/` directory:

```bash
# 1. Run Complete Metrological Performance Benchmark Suite
python tests/benchmark_performance.py

# 2. Run 34 Golden Test Cases (Independent Differential Oracle)
python tests/golden_test_suite.py

# 3. Run 25 Comparative Boundary Validations
python validate_calibra.py

# 4. Run Pytest Suite (Gravity, Context, & Coverage Gate)
cmd /c "set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && python -m pytest tests/test_gravity_and_context.py tests/test_report_consistency.py"
```

---

## 6. Metrological Performance & Throughput Benchmarks

Empirical performance benchmark results measured on CALIBRA's deterministic computation engine:

| Subsystem / Metrological Engine | Throughput | Mean Latency | 99th Percentile (P99) | Precision / Standard |
| :--- | :--- | :--- | :--- | :--- |
| **Somigliana WGS84 Gravity Calculation** | **381,357 ops/s** | **2.50 µs** | **6.10 µs** | International Gravity Formula (1980) |
| **Decimal Metrology Core ($P, E_c, \text{MPE}$)** | **578,517 eval/s** | **1.60 µs** | **2.50 µs** | Arbitrary-Precision Decimal (34 digits) |
| **Clause 3.9.2 Location Transferability** | **132,906 eval/s** | **7.39 µs** | **12.90 µs** | OIML R76-1:2006 Clause 3.9.2 |
| **Dynamic OIML Test Plan Compiler** | **285,608 plans/s**| **0.003 ms** | **0.005 ms** | Classes I, II, III, IIII Dynamic Catalog |
| **Coverage Gate Verification** | **245,877 checks/s**| **3.95 µs** | **5.30 µs** | Multi-Point Mandatory Distribution Gate |
| **Cryptographic SHA-256 Report Hashing** | **11,451 rep/s (1.4 GB/s)** | **87.17 µs**| **120.5 µs** | FIPS 180-4 SHA-256 Tamper Protection |

*All benchmarks executed over 100,000 iterations per test; see [`backend/tests/benchmark_performance.py`](file:///c:/Users/tanish/OneDrive/Tài liệu/Desktop/oiml/backend/tests/benchmark_performance.py).*

---

## 7. Pre-configured Metrological Roles & Operator Accounts

CALIBRA pre-configures 4 metrological roles:
- **Senior Inspector Verma** (`verma@calibra.gov.in`) — *Reviewer / Approver*
- **Inspector Sharma** (`sharma@calibra.gov.in`) — *Technician / Operator*
- **Laboratory Administrator** (`admin@calibra.gov.in`) — *Administrator*
- **Regulatory Auditor** (`auditor@doca.gov.in`) — *Auditor (Read-only replay)*

---

## 8. Operational Verification Workflow (Full Working System)

The complete end-to-end metrology workflow is accessible directly through the application interface:

1. **Dashboard & Metrological Operations Hub (`/`):** View profiled instruments across Class I, II, III, and IIII, test sessions, and issued certificates. Quick operational action cards allow direct navigation to every core metrological engine.
2. **Gravity & Geographical Screening Hub (`/compliance-context`):**
   - Implements the Somigliana 1980 WGS84 formula with free-air vertical gradient ($-3.086\ \mu\text{Gal/m}$).
   - Evaluates location transferability between verification centers (e.g. New Delhi at $g = 9.7912\text{ m/s}^2$ vs Leh Ladakh at $g = 9.7744\text{ m/s}^2$).
   - Demonstrates that $\frac{\Delta g}{g} = 1715\text{ ppm}$ exceeds the permissible $500\text{ ppm}$ MPE tolerance, issuing a mandatory **`RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED`** decision.
   - Toggling the internal calibration weight immediately applies the OIML R76 self-calibration exemption, updating the status to **`TRANSFERABLE`**.
3. **Deterministic Weighing Performance & "WHY?" Explainability (`/workspace`):**
   - Enter raw test observations ($L = 10\text{ kg}, I = 10.018\text{ kg}, \Delta L = 4\text{ g}, E_0 = 2\text{ g}$).
   - The engine deterministically calculates turning point $P = I + 0.5e - \Delta L$, raw error $E = P - L$, and zero-corrected error $E_c = E - E_0 = +17\text{ g}$.
   - Against OIML Table 6 MPE ($\pm 10\text{ g}$), the system renders **`FAIL`** with a one-click mathematical proof drawer.
4. **Standards Traceability & Coverage Gate (`/equipment`):**
   - Monitors reference mass standards (Classes E2, F1, M1) and automatic calibration expiry.
   - Hard blocks report generation whenever mandatory load points or standard calibrations are expired.
5. **Standardized OIML R76-2 Reports & Compliance Replay (`/reports` & `/replay`):**
   - Generates cryptographically signed OIML R76-2 verification reports with embedded SHA-256 integrity hash.
   - Allows regulatory auditors to replay the complete 5-stage reasoning chain decades later.

---

## 9. Known Limitations & Scope Boundaries

1. **Sensors Supported:** Focuses on Non-Automatic Weighing Instruments (NAWI) under OIML R76. Does not cover automatic catchweighers (OIML R51) or continuous totalizing weighers (OIML R50) in this prototype.
2. **Gravity Source:** Uses Somigliana WGS84 with free-air elevation reduction for estimation. While standard in geodetic screening, final statutory verification requires local gravimetry measurements or published national grid values.
3. **Environmental Testing:** Temperature and humidity limits are evaluated against R76 standard operating bands ($+10^\circ\text{C}$ to $+40^\circ\text{C}$ for Class III). Specialized temperature chambers are simulated.

---

## 10. Rules Requiring Expert Verification

Whenever an OIML clause allows jurisdictional discretion, CALIBRA flags it as requiring expert review:
1. **Clause 3.9.2 Zone Boundaries:** Jurisdictional regulations (e.g. EU WELMEC 2 vs Indian Legal Metrology Rules) differ on whether the allowable gravity threshold is $\frac{1}{3} \text{MPE}$ or $\frac{1}{2} \text{MPE}$. CALIBRA implements $\frac{1}{3} \text{MPE}$ by default and makes the coefficient configurable.
2. **Discrimination Thresholds:** The exact minimum displacement required for visual confirmation of turning points on continuous vs discrete displays requires laboratory visual verification.

---

## 11. Documentation Index

- [System Architecture](docs/ARCHITECTURE.md)
- [Gravity & Location Engine](docs/GRAVITY_CONTEXT.md)
- [OIML R76 Rules & Formulas](docs/R76_RULES.md)
- [REST API Specification](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Operational Verification Guide](docs/OPERATIONAL_GUIDE.md)
- [Testing & Validation Guide](docs/TESTING.md)
- [Security & Audit Integrity](docs/SECURITY.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
