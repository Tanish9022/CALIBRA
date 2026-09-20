# CALIBRA — System Architecture

## System Architecture Diagram

```mermaid
graph TD
    subgraph PresentationLayer ["Layer 1: Presentation & Field UI (React 19 + Vite)"]
        Dashboard["Metrological Operations Hub<br/>/dashboard"]
        Workspace["Test Workspace & Observations<br/>/workspace"]
        ExplainDrawer["'WHY?' Explainability Modal<br/>5-Step Mathematical Lineage"]
        GravityUI["Gravity & Transferability Hub<br/>/compliance-context"]
        EquipUI["Standards Traceability Registry<br/>/equipment"]
        ReplayUI["Compliance Replay Timeline<br/>/replay"]
        ReportsUI["Standardized Report Center<br/>/reports"]
    end

    subgraph APILayer ["Layer 2: API & Validation Layer (FastAPI + Pydantic)"]
        RouterInst["Instruments Router<br/>/api/instruments"]
        RouterSess["Sessions Router<br/>/api/sessions"]
        RouterCtx["Context Router<br/>/api/context"]
        RouterComp["Compliance Router<br/>/api/compliance"]
        RouterEquip["Equipment Router<br/>/api/equipment"]
        RouterReplay["Replay Router<br/>/api/replay"]
        RouterRep["Reports Router<br/>/api/reports"]
    end

    subgraph CoreEngine ["Layer 3: Deterministic Metrology Core (34-Digit Decimal Precision)"]
        CalcEngine["Calculation Engine<br/>• Turning Point: P = I + 0.5e - ΔL<br/>• Raw Error: E = P - L<br/>• Corrected Error: Ec = E - E0"]
        RuleEngine["OIML R-76 Rules Engine<br/>• Table 6 MPE Tiered Step Function<br/>• Classes I, II, III, IIII Limits<br/>• Clause 3.5.2 In-Service Multipliers"]
        GravityEngine["Gravity Context Service<br/>• Somigliana 1980 / WGS84 Formula<br/>• Free-Air Gradient: -3.086 µGal/m<br/>• Clause 3.9.2 Transferability (1/3 MPE)"]
        TestPlanCompiler["Dynamic Test Plan Compiler<br/>• Catalog per Class & Capacity<br/>• Weighing, Tare, Eccentricity, Repeatability"]
        CoverageGate["Metrological Coverage Gate<br/>• Min, 500e, 2000e, Max Load Check<br/>• Standards Calibration Expiry Block<br/>• Repeatability (n>=3) & Off-Center Checks"]
        ReplayEngine["Compliance Replay Service<br/>• 5-Stage Reconstructed Audit Lineage<br/>• Historical Ruleset Version Drift Guard"]
        ReportEngine["Report Generator (OIML R76-2)<br/>• Structured PDF Verification Certificate<br/>• Cryptographic SHA-256 Tamper Seal"]
    end

    subgraph StorageLayer ["Layer 4: Storage & Cryptographic Audit (SQLAlchemy ORM)"]
        DB[("Relational Database<br/>SQLite / PostgreSQL")]
        AuditLog[("Immutable Audit Trail<br/>audit_events")]
    end

    Workspace --> RouterSess
    Workspace --> ExplainDrawer
    Dashboard --> RouterInst
    GravityUI --> RouterCtx
    EquipUI --> RouterEquip
    ReplayUI --> RouterReplay
    ReportsUI --> RouterRep

    RouterInst --> TestPlanCompiler
    RouterSess --> CalcEngine
    RouterComp --> RuleEngine
    RouterCtx --> GravityEngine
    RouterEquip --> CoverageGate
    RouterReplay --> ReplayEngine
    RouterRep --> ReportEngine

    CalcEngine --> RuleEngine
    RuleEngine --> CoverageGate
    CoverageGate --> ReportEngine
    ReportEngine --> ReplayEngine

    CalcEngine --> DB
    RuleEngine --> DB
    CoverageGate --> DB
    ReplayEngine --> AuditLog
    ReportEngine --> DB
```

## Layer Responsibilities
1. **Frontend**: Pure reactive UI for technicians, auditors, and reviewers. Handles real-time input normalization, visual indicators, explainability modal, and the Metrological Operations Hub.
2. **Backend API**: FastAPI REST endpoints with strict Pydantic schemas, role-based access checking, and JSON serialization.
3. **Compliance Engine**: Metrology core utilizing Python `Decimal` (34 digits of precision). Completely isolated from AI to guarantee 100% deterministic reproducibility.
4. **Storage & Cryptographic Audit**: Immutable SQLite/PostgreSQL relational database with SHA-256 checksum verification on all generated reports.
