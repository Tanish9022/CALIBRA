# CALIBRA — Testing & Verification Guide

## 1. Automated Test Suites

CALIBRA is rigorously tested against an independent reference implementation (`tests/independent_reference.py`) to guarantee zero calculation discrepancies.

### 1.1 Golden Test Suite & Boundary Tests
File: `tests/golden_test_suite.py`  
Executes 34 high-precision test cases covering:
- Class I, II, III, and IIII step boundaries
- Transition points at $m = 500e$, $m = 2000e$, $m = 10000e$
- Exact boundary limits ($\text{limit} - \epsilon$, $\text{limit}$, $\text{limit} + \epsilon$)
- In-service verification multiplier ($2.0 \times \text{MPE}$)
- Metamorphic unit conversions ($\text{mg} \leftrightarrow \text{g} \leftrightarrow \text{kg} \leftrightarrow \text{t}$)
- Turning point arithmetic $P = I + 0.5e - \Delta L$
- Zero-load error subtraction $E_c = E - E_0$

### 1.2 Metrological Validation Suite
File: `validate_calibra.py`  
Runs 25 boundary and negative-case validations against the independent OIML reference engine.

### 1.3 Gravity & Coverage Gate Unit Tests
File: `tests/test_gravity_and_context.py`  
Tests Somigliana formula accuracy, free-air gradient reduction, transferability classification, and CoverageGate blocking conditions.

---

### 1.4 Metrological Throughput & Latency Benchmarks
Directory: [`benchmarks/`](file:///c:/Users/tanish/OneDrive/Tài liệu/Desktop/oiml/benchmarks/README.md)  
Executes 100,000 iterations per core subsystem to verify sub-microsecond determinism:
- Somigliana 1980 / WGS84 Geodetic Gravity Calculation (~295k ops/s)
- 34-Digit Decimal Metrology Core Turning Point & MPE derivation (~422k eval/s)
- Clause 3.9.2 Location Transferability Decision Matrix (~72k eval/s)
- Dynamic OIML Test Plan Compiler (~195k plans/s)
- Coverage Gate Multi-Point Verification (~185k checks/s)
- FIPS 180-4 Cryptographic SHA-256 Report Hashing (~8k rep/s, 988 MB/s)

---

## 2. Running the Test & Benchmark Suites

Execute from repository root:

```bash
# 1. Run Complete Metrological Performance Benchmark Suite
python benchmarks/run_benchmarks.py

# 2. Run 34 Golden Test Cases (Independent Differential Oracle)
python backend/tests/golden_test_suite.py

# 3. Run 25 Comparative Boundary Validations
python backend/validate_calibra.py

# 4. Run Pytest Suite (Gravity, Context, & Coverage Gate)
cmd /c "cd backend && set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && python -m pytest tests/test_gravity_and_context.py tests/test_report_consistency.py"
```

All suites execute in under 5 seconds with 100% pass rates. Direct benchmarks link: [`benchmarks/`](file:///c:/Users/tanish/OneDrive/Tài liệu/Desktop/oiml/benchmarks/README.md)
