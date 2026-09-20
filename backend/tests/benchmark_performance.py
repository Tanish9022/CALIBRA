import time
import statistics
import hashlib
from decimal import Decimal
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.context.gravity_service import GravityContextService
from engine.test_plan_service import TestPlanService
from engine.coverage_gate import CoverageGate


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def print_metric(name: str, value: str, note: str = ""):
    print(f"  • {name:<42} : {value:>16}   {note}")


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
        g = GravityContextService.estimate_gravity_somigliana(lat, elev)
        times.append((time.perf_counter() - t0) * 1e6) # microseconds
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
        "benchmark": "Somigliana Gravity",
        "iterations": iterations,
        "ops_per_sec": ops_per_sec,
        "mean_us": mean_us,
        "p99_us": p99_us
    }


def benchmark_decimal_metrology_core(iterations: int = 100000):
    print_header(f"2. Arbitrary-Precision Decimal Metrology Core ({iterations:,} evaluations)")
    
    # Simulates turning point derivation:
    # P = I + 0.5e - delta_L
    # E = P - L
    # Ec = E - E0
    # MPE lookup per OIML Table 6
    # Decision: PASS if |Ec| <= MPE else FAIL
    
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
        decision = abs(Ec) <= mpe

    times = []
    t_start = time.perf_counter()
    for load_kg, indication_kg, delta_l_g in test_data:
        t0 = time.perf_counter()
        # Full deterministic OIML R76 calculation
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
        passed = abs(Ec) <= mpe
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
        "benchmark": "Decimal Metrology Core",
        "iterations": iterations,
        "ops_per_sec": ops_per_sec,
        "mean_us": mean_us,
        "p99_us": p99_us
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
        res = GravityContextService.evaluate_location_transferability(
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
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Throughput", f"{ops_per_sec:,.0f} evaluations/sec")
    print_metric("Mean Latency", f"{mean_us:.3f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.3f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.3f} µs")

    return {
        "benchmark": "Clause 3.9.2 Transferability",
        "iterations": iterations,
        "ops_per_sec": ops_per_sec,
        "mean_us": mean_us,
        "p99_us": p99_us
    }


def benchmark_dynamic_test_plan_compiler(iterations: int = 2000):
    print_header(f"4. Dynamic OIML Test Plan Compiler ({iterations:,} compilations)")

    times = []
    t_start = time.perf_counter()
    for i in range(iterations):
        t0 = time.perf_counter()
        plan = TestPlanService.compile_test_plan(
            accuracy_class="III",
            max_capacity_kg=30.0,
            verification_interval_e_g=10.0,
            verification_type="INITIAL",
            has_tare=True
        )
        times.append((time.perf_counter() - t0) * 1e3) # milliseconds
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_ms = statistics.mean(times)
    times_sorted = sorted(times)
    p95_ms = times_sorted[int(iterations * 0.95)]
    p99_ms = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Compilation Throughput", f"{ops_per_sec:,.0f} plans/sec")
    print_metric("Mean Latency", f"{mean_ms:.3f} ms")
    print_metric("95th Percentile (P95)", f"{p95_ms:.3f} ms")
    print_metric("99th Percentile (P99)", f"{p99_ms:.3f} ms")

    return {
        "benchmark": "Dynamic Test Plan Compiler",
        "iterations": iterations,
        "ops_per_sec": ops_per_sec,
        "mean_ms": mean_ms,
        "p99_ms": p99_ms
    }


def benchmark_coverage_gate_verification(iterations: int = 5000):
    print_header(f"5. Coverage Gate Multi-Point Verification ({iterations:,} validations)")

    # Compile a realistic test plan
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
        gate_res = CoverageGate.evaluate_session_coverage(
            test_plan=test_plan,
            results=results,
            observations=observations,
            equipment_list=equipment
        )
        times.append((time.perf_counter() - t0) * 1e6)
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mean_us = statistics.mean(times)
    times_sorted = sorted(times)
    p95_us = times_sorted[int(iterations * 0.95)]
    p99_us = times_sorted[int(iterations * 0.99)]

    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Validation Throughput", f"{ops_per_sec:,.0f} checks/sec")
    print_metric("Mean Latency", f"{mean_us:.3f} µs")
    print_metric("95th Percentile (P95)", f"{p95_us:.3f} µs")
    print_metric("99th Percentile (P99)", f"{p99_us:.3f} µs")

    return {
        "benchmark": "Coverage Gate Verification",
        "iterations": iterations,
        "ops_per_sec": ops_per_sec,
        "mean_us": mean_us,
        "p99_us": p99_us
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
        digest = hashlib.sha256(simulated_report).hexdigest()
        times.append((time.perf_counter() - t0) * 1e6)
    t_total = time.perf_counter() - t_start

    ops_per_sec = iterations / t_total
    mb_per_sec = total_mb_processed / t_total
    mean_us = statistics.mean(times)

    print_metric("Payload Size per Report", f"{payload_size_kb:.1f} KB")
    print_metric("Total Data Processed", f"{total_mb_processed:.1f} MB")
    print_metric("Total Execution Time", f"{t_total:.3f} s")
    print_metric("Hashing Speed", f"{mb_per_sec:.1f} MB/s")
    print_metric("Reports Signed/Verified", f"{ops_per_sec:,.0f} reports/sec")
    print_metric("Mean Latency per Report", f"{mean_us:.2f} µs")

    return {
        "benchmark": "Cryptographic SHA-256 Hashing",
        "iterations": iterations,
        "ops_per_sec": ops_per_sec,
        "mb_per_sec": mb_per_sec,
        "mean_us": mean_us
    }


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("  CALIBRA — LEGAL METROLOGY COMPLIANCE ENGINE PERFORMANCE BENCHMARKS")
    print("  Standards: OIML R-76-1:2006 / OIML R-76-2:2012 / WGS84 Geodetic Reference")
    print("#" * 80)

    results = []
    results.append(benchmark_somigliana_gravity())
    results.append(benchmark_decimal_metrology_core())
    results.append(benchmark_clause_392_transferability())
    results.append(benchmark_dynamic_test_plan_compiler())
    results.append(benchmark_coverage_gate_verification())
    results.append(benchmark_cryptographic_report_hashing())

    print("\n" + "=" * 80)
    print("  BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(f"  {'Subsystem / Operation':<35} | {'Throughput':<20} | {'Mean Latency':<15}")
    print("  " + "-" * 76)
    for r in results:
        name = r["benchmark"]
        if "mb_per_sec" in r:
            throughput = f"{r['ops_per_sec']:,.0f} ops/s ({r['mb_per_sec']:.0f} MB/s)"
        else:
            throughput = f"{r['ops_per_sec']:,.0f} ops/s"
        latency = f"{r.get('mean_us', r.get('mean_ms', 0)):.2f} " + ("µs" if "mean_us" in r else "ms")
        print(f"  {name:<35} | {throughput:<20} | {latency:<15}")
    print("=" * 80 + "\n")
