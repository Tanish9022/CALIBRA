# CALIBRA — System Architecture

```
                                      +---------------------------------------------+
                                      |             CALIBRA FRONTEND                |
                                      | React 19 + Vite + Tailwind + Lucide Icons  |
                                      +----------------------+----------------------+
                                                             | HTTP / JSON
                                                             v
+-------------------------------------------------------------------------------------------------------------------+
|                                                 FASTAPI BACKEND                                                   |
|                                                                                                                   |
|  +---------------------+   +---------------------+   +---------------------+   +-------------------------------+  |
|  |  Instruments Router |   | Context Router      |   | Compliance Router   |   | Reports Router                |  |
|  |  /instruments       |   | /compliance-context |   | /compliance         |   | /reports                      |  |
|  +---------------------+   +---------------------+   +---------------------+   +-------------------------------+  |
|                                                                                                                   |
|  +---------------------+   +---------------------+   +---------------------+   +-------------------------------+  |
|  |  Sessions Router    |   | Equipment Router    |   | Replay Router       |   | Demo Router                   |  |
|  |  /sessions          |   | /equipment          |   | /replay             |   | /demo                         |  |
|  +---------------------+   +---------------------+   +---------------------+   +-------------------------------+  |
|                                                                                                                   |
+----------------------------------------------------+--------------------------------------------------------------+
                                                     |
                                                     v
+-------------------------------------------------------------------------------------------------------------------+
|                                            CALIBRA COMPLIANCE ENGINE                                              |
|                                                                                                                   |
|  +----------------------------+  +----------------------------+  +----------------------------+                   |
|  | CalculationEngine (Decimal)|  | RuleEngine (OIML R76 Table)|  | GravityContextService      |                   |
|  | Turning Point P = I+0.5e-ΔL|  | Clause 3.5.1 MPE Steps     |  | Somigliana WGS84 + FreeAir |                   |
|  | Error Ec = (P-L) - E0      |  | Repeatability & Eccentric  |  | Clause 3.9.2 Transfer Eval |                   |
|  +----------------------------+  +----------------------------+  +----------------------------+                   |
|                                                                                                                   |
|  +----------------------------+  +----------------------------+  +----------------------------+                   |
|  | TestPlanService            |  | CoverageGate               |  | ComplianceReplayService    |                   |
|  | Dynamic R76 Test Compiler  |  | Traceability & Load Points |  | Reconstructed Audit Chain  |                   |
|  +----------------------------+  +----------------------------+  +----------------------------+                   |
|                                                                                                                   |
+----------------------------------------------------+--------------------------------------------------------------+
                                                     |
                                                     v
                                      +------------------------------+
                                      |      SQLITE / POSTGRESQL     |
                                      | SQLAlchemy ORM + Audit Trail |
                                      +------------------------------+
```

## Layer Responsibilities
1. **Frontend**: Pure reactive UI for technicians, auditors, and reviewers. Handles real-time input normalization, visual indicators, explainability modal, and the Metrological Operations Hub.
2. **Backend API**: FastAPI REST endpoints with strict Pydantic schemas, role-based access checking, and JSON serialization.
3. **Compliance Engine**: Metrology core utilizing Python `Decimal` (34 digits of precision). Completely isolated from AI to guarantee 100% deterministic reproducibility.
4. **Storage & Cryptographic Audit**: Immutable SQLite/PostgreSQL relational database with SHA-256 checksum verification on all generated reports.
