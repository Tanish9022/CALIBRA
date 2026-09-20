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

## 2. Running the Test Suites

Execute from the `backend/` directory:

```bash
# 1. Run 34 Golden Test Cases (Independent Differential Oracle)
python tests/golden_test_suite.py

# 2. Run 25 Comparative Boundary Validations
python validate_calibra.py

# 3. Run Pytest Suite (Gravity, Context, & Coverage Gate)
cmd /c "set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && python -m pytest tests/test_gravity_and_context.py tests/test_report_consistency.py"
```

All suites execute in under 5 seconds with 100% pass rates.
