# CALIBRA — Latest Benchmark Execution Results

- **Execution Timestamp**: `2026-09-25T13:01:22.171378`
- **Operating System / Platform**: `Windows-11-10.0.26200-SP0`
- **Python Version**: `3.12.10`
- **Processor**: `Intel64 Family 6 Model 154 Stepping 4, GenuineIntel`
- **Suite Mode**: `Full Rigorous (100k iters)`

## Performance & Throughput Summary

| Subsystem / Engine | Throughput | Mean Latency | Median (P50) | 99th %ile (P99) | Precision / Standard |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Somigliana WGS84 Gravity Calculation** | **295,501 ops/s** | 3.23 µs | 2.80 µs | 6.60 µs | International Gravity Formula (1980) / WGS84 Ellipsoid |
| **Decimal Metrology Core (P, Ec, MPE)** | **422,955 eval/s** | 2.20 µs | 1.90 µs | 5.00 µs | Arbitrary-Precision Decimal (34 digits) / OIML R76 Table 6 |
| **Clause 3.9.2 Location Transferability** | **71,692 eval/s** | 13.69 µs | 10.90 µs | 65.00 µs | OIML R76-1:2006 Clause 3.9.2 Zone of Intended Use |
| **Dynamic OIML Test Plan Compiler** | **195,817 plans/s** | 0.00 ms | 0.00 ms | 0.01 ms | OIML R76-1:2006 Dynamic Test Matrix (Classes I-IIII) |
| **Coverage Gate Verification** | **185,136 checks/s** | 5.13 µs | 4.50 µs | 11.90 µs | Multi-Point Distribution Gate / Audit Enforcer |
| **Cryptographic SHA-256 Hashing** | **7,993 reports/s** (988 MB/s) | 124.80 µs | 108.90 µs | 261.50 µs | FIPS 180-4 SHA-256 Tamper Protection (128 KB payload) |

*Generated automatically by `benchmarks/run_benchmarks.py`.*
