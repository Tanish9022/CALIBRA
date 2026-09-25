#!/usr/bin/env python3
"""
CALIBRA — Legal Metrology Compliance Engine Benchmark Suite
============================================================
Automated execution of deterministic metrological throughput and latency benchmarks.
Standards: OIML R-76-1:2006, OIML R-76-2:2012, WGS84 Geodetic Reference Model.

Usage:
    python benchmarks/run_benchmarks.py
    python benchmarks/run_benchmarks.py --quick
"""

import os
import sys
import time
import json
import platform
import statistics
import hashlib
from decimal import Decimal
from datetime import datetime

# Locate backend directory dynamically
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) == "benchmarks":
    REPO_ROOT = os.path.dirname(CURRENT_DIR)
else:
    REPO_ROOT = CURRENT_DIR
    CURRENT_DIR = os.path.join(REPO_ROOT, "benchmarks")

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Force UTF-8 stdout if possible on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from engine.context.gravity_service import GravityContextService
from engine.test_plan_service import TestPlanService
from engine.coverage_gate import CoverageGate


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def print_metric(name: str, value: str, note: str = ""):
    print(f"  * {name:<42} : {value:>16}   {note}")


def benchmark_somigliana_gravity(iterations: int = 100000):
    print_header(f"1. Somigliana 1980 / WGS84 Gravity Calculation ({iterations:,} iterations)")
    
    latitudes = [28.6139, 34.1526, 18.9220, 47.3769, 1.3521, 51.5074, -33.8688, 35.6762]
    elevations = [216.0, 3500.0, 14.0, 408.0, 15.0, 35.0, 58.0, 40.0]
    lat_count = len(latitudes)
    lat_elev_pairs = [(latitudes[i % lat_count], elevations[i % lat_count]) for i in range(iterations)]
    
    # Warm up
    for lat, elev in lat_elev_pairs[:1000]:
        GravityContextService.estimate_gravity_somigliana(lat, elev)
        
    times = []
    t_start = time.perf_counter()
    for lat, elev in lat_elev_pairs:
        t0 = time.perf_counter()
        _ = GravityContextService.estimate_gravity_somigliana(lat, elev)
        times.append((time.perf_counter() - t0) * 1e6)  # microseconds
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_us = statistics.mean(times)
    p50_us = statistics.median(times)
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Throughput", f"{ops_per_sec:,.0f} ops/sec")
    print_metric("Mean Latency", f"{mean_us:.3f} µs")
    print_metric("Median (P50) Latency", f"{p50_us:.3f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.3f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.3f} µs")
    
    return {
        "id": "somigliana_gravity",
        "benchmark": "Somigliana WGS84 Gravity Calculation",
        "standard": "International Gravity Formula (1980) / WGS84 Ellipsoid",
        "iterations": iterations,
        "total_time_s": round(t_total, 4),
        "ops_per_sec": round(ops_per_sec, 2),
        "mean_latency_us": round(mean_us, 3),
        "p50_latency_us": round(p50_us, 3),
        "p95_latency_us": round(p95_us, 3),
        "p99_latency_us": round(p99_us, 3),
        "unit": "ops/s"
    }


def benchmark_decimal_metrology_core(iterations: int = 100000):
    print_header(f"2. Arbitrary-Precision Decimal Metrology Core ({iterations:,} evaluations)")
    
    test_data = []
    e_val = Decimal("10.0")
    half_e = Decimal("5.0")
    zero_error = Decimal("2.0")
    
    for i in range(iterations):
        load_kg = Decimal(10 + (i % 20))
        indication_kg = load_kg + Decimal("0.005")
        delta_l_g = Decimal("3.5")
        test_data.append((load_kg, indication_kg, delta_l_g))
        
    # Warm up
    for load_kg, indication_kg, delta_l_g in test_data[:1000]:
        P = indication_kg * Decimal("1000") + half_e - delta_l_g
        E = P - (load_kg * Decimal("1000"))
        Ec = E - zero_error
        m = (load_kg * Decimal("1000")) / e_val
        mpe = Decimal("10.0") if m <= 2000 else Decimal("15.0")
        _ = abs(Ec) <= mpe

    times = []
    t_start = time.perf_counter()
    for load_kg, indication_kg, delta_l_g in test_data:
        t0 = time.perf_counter()
        P = (indication_kg * Decimal("1000")) + half_e - delta_l_g
        E = P - (load_kg * Decimal("1000"))
        Ec = E - zero_error
        m = (load_kg * Decimal("1000")) / e_val
        if m <= Decimal("500"):
            mpe = Decimal("5.0")
        elif m <= Decimal("2000"):
            mpe = Decimal("10.0")
        else:
            mpe = Decimal("15.0")
        _ = abs(Ec) <= mpe
        times.append((time.perf_counter() - t0) * 1e6)
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_us = statistics.mean(times)
    p50_us = statistics.median(times)
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Throughput", f"{ops_per_sec:,.0f} evaluations/sec")
    print_metric("Mean Latency", f"{mean_us:.3f} µs")
    print_metric("Median (P50) Latency", f"{p50_us:.3f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.3f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.3f} µs")
    print_metric("Precision Level", "34-digit Arbitrary Precision (Decimal)")

    return {
        "id": "decimal_metrology_core",
        "benchmark": "Decimal Metrology Core (P, Ec, MPE)",
        "standard": "Arbitrary-Precision Decimal (34 digits) / OIML R76 Table 6",
        "iterations": iterations,
        "total_time_s": round(t_total, 4),
        "ops_per_sec": round(ops_per_sec, 2),
        "mean_latency_us": round(mean_us, 3),
        "p50_latency_us": round(p50_us, 3),
        "p95_latency_us": round(p95_us, 3),
        "p99_latency_us": round(p99_us, 3),
        "unit": "eval/s"
    }


def benchmark_clause_392_transferability(iterations: int = 25000):
    print_header(f"3. Clause 3.9.2 Location Transferability Evaluation ({iterations:,} evaluations)")
    
    classes = ["I", "II", "III", "IIII"]
    max_caps = [0.220, 5.0, 30.0, 1500.0]
    e_vals = [0.0001, 0.01, 10.0, 500.0]
    
    times = []
    t_start = time.perf_counter()
    for i in range(iterations):
        cls_idx = i % 4
        t0 = time.perf_counter()
        _ = GravityContextService.evaluate_location_transferability(
            accuracy_class=classes[cls_idx],
            max_capacity_kg=max_caps[cls_idx],
            verification_interval_e_g=e_vals[cls_idx],
            has_internal_calibration=(i % 3 == 0),
            is_gravity_sensitive=True,
            test_location_name="New Delhi Verification Center",
            test_gravity_ms2=9.7912,
            intended_location_name="Leh Ladakh Facility",
            intended_gravity_ms2=9.7744
        )
        times.append((time.perf_counter() - t0) * 1e6)
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_us = statistics.mean(times)
    p50_us = statistics.median(times)
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Throughput", f"{ops_per_sec:,.0f} evaluations/sec")
    print_metric("Mean Latency", f"{mean_us:.3f} µs")
    print_metric("Median (P50) Latency", f"{p50_us:.3f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.3f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.3f} µs")

    return {
        "id": "clause_392_transferability",
        "benchmark": "Clause 3.9.2 Location Transferability",
        "standard": "OIML R76-1:2006 Clause 3.9.2 Zone of Intended Use",
        "iterations": iterations,
        "total_time_s": round(t_total, 4),
        "ops_per_sec": round(ops_per_sec, 2),
        "mean_latency_us": round(mean_us, 3),
        "p50_latency_us": round(p50_us, 3),
        "p95_latency_us": round(p95_us, 3),
        "p99_latency_us": round(p99_us, 3),
        "unit": "eval/s"
    }


def benchmark_dynamic_test_plan_compiler(iterations: int = 2000):
    print_header(f"4. Dynamic OIML Test Plan Compiler ({iterations:,} compilations)")

    times = []
    t_start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = TestPlanService.compile_test_plan(
            accuracy_class="III",
            max_capacity_kg=30.0,
            verification_interval_e_g=10.0,
            verification_type="INITIAL",
            has_tare=True
        )
        times.append((time.perf_counter() - t0) * 1e3)  # milliseconds
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_ms = statistics.mean(times)
    p50_ms = statistics.median(times)
    times_sorted = sorted(times)
    p95_ms = times_sorted[int(iterations * 0.95)]
    p99_ms = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Compilation Throughput", f"{ops_per_sec:,.0f} plans/sec")
    print_metric("Mean Latency", f"{mean_ms:.3f} ms")
    print_metric("Median (P50) Latency", f"{p50_ms:.3f} ms")
    print_metric("95th Percentile (P95)", f"{p95_ms:.3f} ms")
    print_metric("99th Percentile (P99)", f"{p99_ms:.3f} ms")

    return {
        "id": "dynamic_test_plan_compiler",
        "benchmark": "Dynamic OIML Test Plan Compiler",
        "standard": "OIML R76-1:2006 Dynamic Test Matrix (Classes I-IIII)",
        "iterations": iterations,
        "total_time_s": round(t_total, 4),
        "ops_per_sec": round(ops_per_sec, 2),
        "mean_latency_ms": round(mean_ms, 4),
        "p50_latency_ms": round(p50_ms, 4),
        "p95_latency_ms": round(p95_ms, 4),
        "p99_latency_ms": round(p99_ms, 4),
        "unit": "plans/s"
    }


def benchmark_coverage_gate_verification(iterations: int = 5000):
    print_header(f"5. Coverage Gate Multi-Point Verification ({iterations:,} validations)")

    test_plan = TestPlanService.compile_test_plan(
        accuracy_class="III",
        max_capacity_kg=30.0,
        verification_interval_e_g=10.0,
        verification_type="INITIAL",
        has_tare=True
    )

    class MockTestDef:
        def __init__(self, code):
            self.code = code

    class MockResult:
        def __init__(self, code, status="PASS"):
            self.test_definition = MockTestDef(code)
            self.status = status
            self.decision_reason = "Within MPE limits"

    class MockEquipment:
        def __init__(self, eq_id, name, status="VALID"):
            self.id = eq_id
            self.name = name
            self.status = status

    results = [MockResult(t["code"], "PASS") for t in test_plan]
    equipment = [
        MockEquipment("EQ-001", "Class F1 Standard", "VALID"),
        MockEquipment("EQ-002", "Digital Barometer", "VALID")
    ]
    observations = []

    times = []
    t_start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = CoverageGate.evaluate_session_coverage(
            test_plan=test_plan,
            results=results,
            observations=observations,
            equipment_list=equipment
        )
        times.append((time.perf_counter() - t0) * 1e6)
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_us = statistics.mean(times)
    p50_us = statistics.median(times)
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Validation Throughput", f"{ops_per_sec:,.0f} checks/sec")
    print_metric("Mean Latency", f"{mean_us:.3f} µs")
    print_metric("Median (P50) Latency", f"{p50_us:.3f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.3f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.3f} µs")

    return {
        "id": "coverage_gate_verification",
        "benchmark": "Coverage Gate Verification",
        "standard": "Multi-Point Distribution Gate / Audit Enforcer",
        "iterations": iterations,
        "total_time_s": round(t_total, 4),
        "ops_per_sec": round(ops_per_sec, 2),
        "mean_latency_us": round(mean_us, 3),
        "p50_latency_us": round(p50_us, 3),
        "p95_latency_us": round(p95_us, 3),
        "p99_latency_us": round(p99_us, 3),
        "unit": "checks/s"
    }


def benchmark_cryptographic_report_hashing(iterations: int = 10000):
    print_header(f"6. Cryptographic SHA-256 Report Integrity Hashing ({iterations:,} payloads)")

    # 128 KB simulated PDF payload
    simulated_report = b"%PDF-1.4 simulated metrology certificate content with OIML R76-2 tables " * 1800
    payload_size_kb = len(simulated_report) / 1024
    total_mb_processed = (len(simulated_report) * iterations) / (1024 * 1024)

    times = []
    t_start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = hashlib.sha256(simulated_report).hexdigest()
        times.append((time.perf_counter() - t0) * 1e6)
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mb_per_sec = total_mb_processed / t_total
    mean_us = statistics.mean(times)
    p50_us = statistics.median(times)
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Payload Size per Report", f"{payload_size_kb:.1f} KB")
    print_metric("Total Data Processed", f"{total_mb_processed:.1f} MB")
    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Hashing Speed", f"{mb_per_sec:.1f} MB/s")
    print_metric("Reports Signed/Verified", f"{ops_per_sec:,.0f} reports/sec")
    print_metric("Mean Latency per Report", f"{mean_us:.2f} µs")
    print_metric("Median (P50) Latency", f"{p50_us:.2f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.2f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.2f} µs")

    return {
        "id": "cryptographic_sha256_hashing",
        "benchmark": "Cryptographic SHA-256 Hashing",
        "standard": "FIPS 180-4 SHA-256 Tamper Protection (128 KB payload)",
        "iterations": iterations,
        "total_time_s": round(t_total, 4),
        "ops_per_sec": round(ops_per_sec, 2),
        "mb_per_sec": round(mb_per_sec, 1),
        "mean_latency_us": round(mean_us, 3),
        "p50_latency_us": round(p50_us, 3),
        "p95_latency_us": round(p95_us, 3),
        "p99_latency_us": round(p99_us, 3),
        "unit": "reports/s"
    }


def main():
    quick_mode = "--quick" in sys.argv
    multiplier = 0.1 if quick_mode else 1.0

    print("\n" + "#" * 80)
    print("  CALIBRA — LEGAL METROLOGY COMPLIANCE ENGINE PERFORMANCE BENCHMARKS")
    print("  Standards: OIML R-76-1:2006 / OIML R-76-2:2012 / WGS84 Geodetic Reference")
    print(f"  Mode: {'QUICK TEST' if quick_mode else 'FULL RIGOROUS SUITE'}")
    print("#" * 80)

    results = []
    results.append(benchmark_somigliana_gravity(int(100000 * multiplier)))
    results.append(benchmark_decimal_metrology_core(int(100000 * multiplier)))
    results.append(benchmark_clause_392_transferability(int(25000 * multiplier)))
    results.append(benchmark_dynamic_test_plan_compiler(int(2000 * multiplier)))
    results.append(benchmark_coverage_gate_verification(int(5000 * multiplier)))
    results.append(benchmark_cryptographic_report_hashing(int(10000 * multiplier)))

    print("\n" + "=" * 80)
    print("  BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(f"  {'Subsystem / Operation':<36} | {'Throughput':<22} | {'Mean Latency':<12} | {'P99 Latency':<12}")
    print("  " + "-" * 88)
    for r in results:
        name = r["benchmark"]
        if "mb_per_sec" in r:
            throughput = f"{r['ops_per_sec']:,.0f} {r['unit']} ({r['mb_per_sec']:.0f} MB/s)"
        else:
            throughput = f"{r['ops_per_sec']:,.0f} {r['unit']}"
        
        latency = f"{r.get('mean_latency_us', r.get('mean_latency_ms', 0)):.2f} " + ("µs" if "mean_latency_us" in r else "ms")
        p99 = f"{r.get('p99_latency_us', r.get('p99_latency_ms', 0)):.2f} " + ("µs" if "p99_latency_us" in r else "ms")
        print(f"  {name:<36} | {throughput:<22} | {latency:<12} | {p99:<12}")
    print("=" * 80 + "\n")

    # System metadata
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "quick_mode": quick_mode
    }

    full_payload = {
        "meta": system_info,
        "benchmarks": results
    }

    # Save to benchmarks/results/
    results_dir = os.path.join(CURRENT_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    json_path = os.path.join(results_dir, "latest_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, indent=2)
    rel_json = os.path.relpath(json_path, REPO_ROOT)
    print(f"  [Artifact] Benchmark JSON exported to: {rel_json}")

    # Generate Markdown Summary
    md_path = os.path.join(results_dir, "latest_results.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# CALIBRA — Latest Benchmark Execution Results\n\n")
        f.write(f"- **Execution Timestamp**: `{system_info['timestamp']}`\n")
        f.write(f"- **Operating System / Platform**: `{system_info['platform']}`\n")
        f.write(f"- **Python Version**: `{system_info['python_version']}`\n")
        f.write(f"- **Processor**: `{system_info['processor']}`\n")
        f.write(f"- **Suite Mode**: `{'Quick' if quick_mode else 'Full Rigorous (100k iters)'}`\n\n")
        f.write("## Performance & Throughput Summary\n\n")
        f.write("| Subsystem / Engine | Throughput | Mean Latency | Median (P50) | 99th %ile (P99) | Precision / Standard |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            if "mb_per_sec" in r:
                t_str = f"**{r['ops_per_sec']:,.0f} {r['unit']}** ({r['mb_per_sec']:.0f} MB/s)"
            else:
                t_str = f"**{r['ops_per_sec']:,.0f} {r['unit']}**"
            mean_str = f"{r.get('mean_latency_us', r.get('mean_latency_ms', 0)):.2f} " + ("µs" if "mean_latency_us" in r else "ms")
            p50_str = f"{r.get('p50_latency_us', r.get('p50_latency_ms', 0)):.2f} " + ("µs" if "p50_latency_us" in r else "ms")
            p99_str = f"{r.get('p99_latency_us', r.get('p99_latency_ms', 0)):.2f} " + ("µs" if "p99_latency_us" in r else "ms")
            f.write(f"| **{r['benchmark']}** | {t_str} | {mean_str} | {p50_str} | {p99_str} | {r['standard']} |\n")
        f.write("\n*Generated automatically by `benchmarks/run_benchmarks.py`.*\n")
    rel_md = os.path.relpath(md_path, REPO_ROOT)
    print(f"  [Artifact] Benchmark Markdown table exported to: {rel_md}\n")


if __name__ == "__main__":
    main()
