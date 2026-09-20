# CALIBRA — Gravity & Location Metrology Engine

## 1. Executive Summary

In legal metrology under **OIML R76-1:2006 Clause 3.9.2** (*"Metrological characteristics depending on gravity"*), non-automatic weighing instruments (NAWI) that utilize gravitational force to evaluate mass (such as strain-gauge load cells, vibrating-wire sensors, or mechanical springs) without automatic internal calibration adjustment are directly dependent on the local acceleration of gravity $g$.

CALIBRA treats **Compliance Context** as a first-class citizen rather than a cosmetic location string.

> **Metrological Safety Rule:**  
> CALIBRA does **not** physically alter the instrument's calibration or claim to physically improve machine performance. Instead, CALIBRA mathematically evaluates whether existing test evidence from an initial verification location can be legally transferred to an intended installation site under OIML R76.

---

## 2. Gravitational Models Implemented

### 2.1 Theoretical Acceleration (Somigliana 1980 / WGS84)
For locations where authoritative measured gravity is unavailable, CALIBRA estimates normal sea-level theoretical gravity $\gamma(\phi)$ using the Somigliana formula:

$$\gamma(\phi) = 9.780327 \times \left(1 + 0.0053024 \sin^2\phi - 0.0000058 \sin^2 2\phi\right) \text{ m/s}^2$$

Where $\phi$ is the geodetic latitude in degrees.

### 2.2 Free-Air Elevation Correction
Gravitational acceleration decreases with altitude above the geoid. CALIBRA applies the international free-air gradient:

$$\Delta g_{\text{elev}} = -3.086 \times 10^{-6} \times h \text{ m/s}^2$$

Where $h$ is the orthometric elevation in meters.

$$\hat{g}_{\text{local}} = \gamma(\phi) + \Delta g_{\text{elev}}$$

### 2.3 Prioritization Hierarchy
1. **DECLARED / MEASURED**: Authoritative local acceleration measured by gravimetry or published by national metrology institutes (e.g. CSIR-NPL in India). **Never silently overridden.**
2. **ESTIMATED**: Calculated via Somigliana + Free-Air. Explicitly watermarked as an estimate requiring on-site confirmation.

---

## 3. OIML R76 Clause 3.9.2 Location Transferability Evaluation

When an instrument tested at Location $A$ ($g_A$) is intended for use at Location $B$ ($g_B$), CALIBRA executes the following deterministic compliance check:

### 3.1 Self-Calibration Exemption
If the instrument possesses an internal automatic calibration weight system (common in Class I & II balances):
$$\text{Status} \rightarrow \mathbf{TRANSFERABLE}$$
Gravitational shifts are dynamically compensated on-site by the internal reference standard.

### 3.2 Transducer Sensitivity Check
If the instrument employs direct mass-to-mass comparison (e.g. beam balance with deadweights):
$$\text{Status} \rightarrow \mathbf{TRANSFERABLE}$$

### 3.3 Gravitational Shift vs MPE Tolerance
For gravity-sensitive instruments (load cells without internal calibration), CALIBRA computes the relative gravitational shift:

$$\frac{\Delta g}{g_A} = \frac{|g_A - g_B|}{g_A}$$

This dimensionless value (in parts per million, ppm) is compared against the instrument's Maximum Permissible Error (MPE) at maximum capacity $\text{Max}$:

$$\text{Relative MPE} = \frac{\text{MPE}(\text{Max})}{\text{Max}}$$

$$\text{Zone Allowance} = \frac{1}{3} \times \frac{\text{MPE}(\text{Max})}{\text{Max}}$$

| Relative Shift Condition | Decision Status | Regulatory Action |
| :--- | :--- | :--- |
| $\frac{\Delta g}{g_A} \le \frac{1}{3} \text{Relative MPE}$ | **TRANSFERABLE** | No further testing required. Original certificate valid. |
| $\frac{1}{3} \text{Relative MPE} < \frac{\Delta g}{g_A} \le \text{Relative MPE}$ | **CONDITIONAL** | Gravity zone markings or on-site span adjustment required. |
| $\frac{\Delta g}{g_A} > \text{Relative MPE}$ | **RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED** | Original testing cannot legally establish compliance at destination. Mandatory re-verification required at destination. |

---

## 4. Benchmark Demonstration: Delhi to Leh

- **Test Location:** New Delhi Central Laboratory ($g = 9.7912 \text{ m/s}^2$)
- **Intended Destination:** Leh, Ladakh ($3500\text{m elevation}, g = 9.7744 \text{ m/s}^2$)
- **Instrument:** Class III Commercial Scale, $\text{Max} = 30\text{ kg}$, $e = 10\text{ g}$, $n = 3000$.

### Calculations:
1. $\Delta g = 9.7912 - 9.7744 = 0.0168 \text{ m/s}^2$
2. Relative Shift $\frac{\Delta g}{g_A} = \frac{0.0168}{9.7912} \approx 1715.8 \text{ ppm}$
3. At $\text{Max} = 30\text{ kg} = 3000e$: $\text{MPE}(\text{Max}) = \pm 1.5e = \pm 15\text{ g}$.
4. Relative $\text{MPE} = \frac{15\text{ g}}{30000\text{ g}} = 500.0 \text{ ppm}$.
5. $\frac{1}{3} \text{ MPE Threshold} = 166.7 \text{ ppm}$.

### Conclusion:
$$1715.8 \text{ ppm} \gg 500.0 \text{ ppm} \implies \mathbf{RE\text{-}TEST\ REQUIRED}$$
The error induced solely by the altitude and latitude difference ($1715 \text{ ppm} \times 30\text{ kg} \approx 51.5\text{ g}$) is over **3 times larger** than the legal MPE ($\pm 15\text{ g}$).
CALIBRA intercepts this context change immediately and flags the test session as requiring location-specific re-evaluation.
