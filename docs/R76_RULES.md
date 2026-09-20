# CALIBRA — OIML R76 Metrological Rules & Formulas

## 1. Scope & Standard Baseline
- **Primary International Standards:**
  - **OIML R 76-1 Edition 2006 (E):** Metrological and technical requirements — Non-automatic weighing instruments.
  - **OIML R 76-2 Edition 2006 (E):** Pattern evaluation report format.

---

## 2. Accuracy Classes (Clause 3.2 & Table 3)

| Accuracy Class | Symbol | Verification Interval $e$ | Minimum Capacity $\text{Min}$ | Number of Intervals $n = \text{Max} / e$ |
| :--- | :---: | :---: | :---: | :---: |
| Special | **I** | $0.001\text{ g} \le e$ | $100 e$ | $50,000 \le n$ (no upper limit) |
| High | **II** | $0.001\text{ g} \le e \le 0.05\text{ g}$<br>$0.1\text{ g} \le e$ | $20 e$<br>$50 e$ | $100 \le n \le 100,000$<br>$5,000 \le n \le 100,000$ |
| Medium | **III** | $0.1\text{ g} \le e \le 2\text{ g}$<br>$5\text{ g} \le e$ | $20 e$ | $100 \le n \le 10,000$<br>$500 \le n \le 10,000$ |
| Ordinary | **IIII** | $5\text{ g} \le e$ | $10 e$ | $100 \le n \le 1,000$ |

---

## 3. Maximum Permissible Errors (MPE) (Clause 3.5.1 & Table 6)

### 3.1 Initial Verification MPE Table (in units of $e$)

| Accuracy Class | $m$ range for $\text{MPE} = \pm 0.5 e$ | $m$ range for $\text{MPE} = \pm 1.0 e$ | $m$ range for $\text{MPE} = \pm 1.5 e$ |
| :---: | :--- | :--- | :--- |
| **Class I** | $0 \le m \le 50,000 e$ | $50,000 e < m \le 200,000 e$ | $200,000 e < m$ |
| **Class II** | $0 \le m \le 5,000 e$ | $5,000 e < m \le 20,000 e$ | $20,000 e < m \le 100,000 e$ |
| **Class III** | $0 \le m \le 500 e$ | $500 e < m \le 2,000 e$ | $2,000 e < m \le 10,000 e$ |
| **Class IIII** | $0 \le m \le 50 e$ | $50 e < m \le 200 e$ | $200 e < m \le 1,000 e$ |

### 3.2 In-Service Inspection (Clause 3.5.2)
For in-service verification, MPE is double the initial verification tolerance:
$$\text{MPE}_{\text{in-service}} = 2.0 \times \text{MPE}_{\text{initial}}$$

---

## 4. Deterministic Calculation Trace (Annex A.4.4)

### 4.1 Digital Turning Point (Clause A.4.4.3)
For digital scale displays, the indication prior to rounding $P$ is determined by applying fractional weights $\Delta L$ until the indication reliably steps to $I + e$:

$$P = I + \frac{1}{2} e - \Delta L$$

### 4.2 Raw Indication Error (Clause A.4.4.1)
$$E = P - L$$

### 4.3 Zero Error & Corrected Error (Clause A.4.4.3)
Zero-load error $E_0$ is measured prior to load application:
$$E_c = E - E_0$$

### 4.4 Compliance Verdict
$$\text{Status} = \begin{cases} \mathbf{PASS} & \text{if } |E_c| \le \text{MPE} \\ \mathbf{FAIL} & \text{if } |E_c| > \text{MPE} \end{cases}$$

---

## 5. Capacity Boundaries & Prohibitions

1. **Negative Load Rejection (Clause 4.1):** Applied load $L < 0$ is physically impossible for legal weighing tests and triggers $\mathbf{INVALID}$.
2. **Overload Cutoff (Clause 4.1.2.6):** No indication may be evaluated above $\text{Max} + 9e$. Loads exceeding this limit are strictly rejected.
3. **Verification Scale Interval:** $e > 0$. Zero or negative intervals are rejected.
