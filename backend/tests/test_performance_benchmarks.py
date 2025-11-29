"""
Phase 5: Quality Assurance & Optimization - Performance Benchmarks

Performance benchmarking tests to measure and validate:
- Geometry generation speed
- Export format conversion speed
- Memory usage
- File size optimization
"""

from __future__ import annotations

import time
import pytest

from app.pipelines.geometry import build_step_solid, export_mesh, build_artifacts

# Simple test polygon (rectangular room)
SIMPLE_ROOM = [[[0, 0], [5000, 0], [5000, 4000], [0, 4000]]]

# Complex polygon (L-shaped room with many points)
L_SHAPED_ROOM = [
    [
        [0, 0],
        [8000, 0],
        [8000, 5000],
        [3000, 5000],
        [3000, 3000],
        [0, 3000],
    ]
]

# Very complex polygon (multi-room layout)
MULTI_ROOM = [
    [[0, 0], [5000, 0], [5000, 4000], [0, 4000]],  # Room 1
    [[6000, 0], [10000, 0], [10000, 4000], [6000, 4000]],  # Room 2
    [[0, 5000], [5000, 5000], [5000, 9000], [0, 9000]],  # Room 3
]


def test_performance_simple_room_step_generation():
    """
    Benchmark: STEP generation for simple rectangular room

    Success Criteria: <500ms for 5m×4m room
    """
    start = time.perf_counter()

    step_bytes = build_step_solid(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(step_bytes, bytes)
    assert len(step_bytes) > 0

    print(f"\nSimple room STEP generation: {duration_ms:.2f}ms, size: {len(step_bytes)} bytes")

    # Success criterion: <500ms
    assert duration_ms < 500, f"Simple STEP generation too slow: {duration_ms:.2f}ms"


def test_performance_complex_room_step_generation():
    """
    Benchmark: STEP generation for complex L-shaped room

    Success Criteria: <1000ms for L-shaped room
    """
    start = time.perf_counter()

    step_bytes = build_step_solid(
        polygons=L_SHAPED_ROOM, height=3000, wall_thickness=200
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(step_bytes, bytes)
    assert len(step_bytes) > 0

    print(f"\nL-shaped room STEP generation: {duration_ms:.2f}ms, size: {len(step_bytes)} bytes")

    # Success criterion: <1000ms
    assert duration_ms < 1000, f"Complex STEP generation too slow: {duration_ms:.2f}ms"


def test_performance_multi_room_step_generation():
    """
    Benchmark: STEP generation for multi-room layout

    Success Criteria: <2000ms for 3-room layout
    """
    start = time.perf_counter()

    step_bytes = build_step_solid(
        polygons=MULTI_ROOM, height=3000, wall_thickness=200
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(step_bytes, bytes)
    assert len(step_bytes) > 0

    print(f"\nMulti-room STEP generation: {duration_ms:.2f}ms, size: {len(step_bytes)} bytes")

    # Success criterion: <2000ms
    assert duration_ms < 2000, f"Multi-room STEP generation too slow: {duration_ms:.2f}ms"


def test_performance_obj_export():
    """
    Benchmark: OBJ export conversion speed

    Success Criteria: <100ms for simple room
    """
    start = time.perf_counter()

    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj", tolerance=0.1
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(obj_bytes, bytes)
    assert len(obj_bytes) > 0

    print(f"\nOBJ export: {duration_ms:.2f}ms, size: {len(obj_bytes)} bytes")

    # Success criterion: <100ms
    assert duration_ms < 100, f"OBJ export too slow: {duration_ms:.2f}ms"


def test_performance_stl_export():
    """
    Benchmark: STL export conversion speed

    Success Criteria: <100ms for simple room
    """
    start = time.perf_counter()

    stl_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="stl", tolerance=0.1
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(stl_bytes, bytes)
    assert len(stl_bytes) > 0

    print(f"\nSTL export: {duration_ms:.2f}ms, size: {len(stl_bytes)} bytes")

    # Success criterion: <100ms
    assert duration_ms < 100, f"STL export too slow: {duration_ms:.2f}ms"


def test_performance_glb_export():
    """
    Benchmark: GLB export conversion speed

    Success Criteria: <150ms for simple room
    """
    start = time.perf_counter()

    glb_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="glb", tolerance=0.1
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(glb_bytes, bytes)
    assert len(glb_bytes) > 0

    print(f"\nGLB export: {duration_ms:.2f}ms, size: {len(glb_bytes)} bytes")

    # Success criterion: <150ms
    assert duration_ms < 150, f"GLB export too slow: {duration_ms:.2f}ms"


def test_performance_build_artifacts():
    """
    Benchmark: Full artifact generation (DXF + STEP)

    Success Criteria: <1500ms for simple room with both formats
    """
    start = time.perf_counter()

    dxf_bytes, step_bytes = build_artifacts(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200
    )

    duration_ms = (time.perf_counter() - start) * 1000

    assert isinstance(dxf_bytes, bytes)
    assert isinstance(step_bytes, bytes)
    assert len(dxf_bytes) > 0
    assert len(step_bytes) > 0

    print(
        f"\nFull artifact generation: {duration_ms:.2f}ms, "
        f"DXF: {len(dxf_bytes)} bytes, STEP: {len(step_bytes)} bytes"
    )

    # Success criterion: <1500ms
    assert duration_ms < 1500, f"Artifact generation too slow: {duration_ms:.2f}ms"


def test_performance_tessellation_quality_vs_speed():
    """
    Benchmark: Tessellation tolerance impact on speed and file size

    Compares different tolerance values: 0.05 (high quality), 0.1 (default), 0.5 (low quality)
    """
    tolerances = [0.05, 0.1, 0.5]
    results = []

    for tol in tolerances:
        start = time.perf_counter()

        obj_bytes = export_mesh(
            polygons=L_SHAPED_ROOM, height=3000, wall_thickness=200, format="obj", tolerance=tol
        )

        duration_ms = (time.perf_counter() - start) * 1000

        results.append((tol, duration_ms, len(obj_bytes)))

        print(f"\nTolerance={tol}: {duration_ms:.2f}ms, size: {len(obj_bytes)} bytes")

    # Verify that lower tolerance = more time + larger file (generally)
    assert results[0][1] >= results[2][1] * 0.8  # High quality takes more time
    assert results[0][2] >= results[2][2]  # High quality produces larger files


def test_performance_solid_vs_hollow():
    """
    Benchmark: Solid extrusion vs hollow rooms (with wall thickness)

    Compares performance difference between solid and hollow geometry
    """
    # Solid extrusion (no wall thickness)
    start = time.perf_counter()
    step_solid = build_step_solid(polygons=SIMPLE_ROOM, height=3000, wall_thickness=0)
    solid_time_ms = (time.perf_counter() - start) * 1000

    # Hollow room (with wall thickness)
    start = time.perf_counter()
    step_hollow = build_step_solid(polygons=SIMPLE_ROOM, height=3000, wall_thickness=200)
    hollow_time_ms = (time.perf_counter() - start) * 1000

    print(
        f"\nSolid extrusion: {solid_time_ms:.2f}ms, size: {len(step_solid)} bytes"
    )
    print(
        f"Hollow room: {hollow_time_ms:.2f}ms, size: {len(step_hollow)} bytes"
    )

    # Hollow should take longer (boolean subtraction)
    assert hollow_time_ms >= solid_time_ms * 0.9

    # Both should complete reasonably fast
    assert solid_time_ms < 500
    assert hollow_time_ms < 1000


def test_file_size_optimization():
    """
    Benchmark: File size comparison across formats

    Validates that mesh formats are smaller than STEP
    """
    # Generate all formats
    step_bytes = build_step_solid(polygons=SIMPLE_ROOM, height=3000, wall_thickness=200)

    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj"
    )

    stl_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="stl"
    )

    glb_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="glb"
    )

    sizes = {
        "STEP": len(step_bytes),
        "OBJ": len(obj_bytes),
        "STL": len(stl_bytes),
        "GLB": len(glb_bytes),
    }

    print("\nFile sizes:")
    for fmt, size in sizes.items():
        print(f"  {fmt}: {size:,} bytes")

    # Mesh formats should generally be smaller than STEP
    # (STEP includes parametric data, meshes are just triangles)
    assert sizes["OBJ"] < sizes["STEP"] * 2  # Allow some margin
    assert sizes["GLB"] < sizes["STEP"] * 2


def test_performance_concurrent_exports():
    """
    Benchmark: Multiple concurrent export operations

    Simulates converting to multiple formats simultaneously
    """
    import concurrent.futures

    formats = ["obj", "stl", "ply", "glb"]

    def export_format(fmt):
        start = time.perf_counter()
        result = export_mesh(
            polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format=fmt
        )
        duration_ms = (time.perf_counter() - start) * 1000
        return fmt, duration_ms, len(result)

    # Run exports concurrently
    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(export_format, formats))

    total_duration_ms = (time.perf_counter() - start) * 1000

    print(f"\nConcurrent export of {len(formats)} formats: {total_duration_ms:.2f}ms")
    for fmt, duration, size in results:
        print(f"  {fmt.upper()}: {duration:.2f}ms, {size} bytes")

    # Concurrent should be faster than sequential
    # (at least 25% faster with 4 cores)
    sequential_estimate = sum(r[1] for r in results)
    speedup = sequential_estimate / total_duration_ms

    print(f"Speedup: {speedup:.2f}x")

    # Should see some parallelization benefit
    assert speedup > 1.25, f"Poor parallelization: {speedup:.2f}x speedup"


def test_performance_memory_usage():
    """
    Benchmark: Memory usage for geometry generation

    Tests that memory usage is reasonable for typical workloads
    """
    try:
        import psutil
        import os
    except ImportError:
        pytest.skip("psutil not installed")

    process = psutil.Process(os.getpid())

    # Get baseline memory
    baseline_mb = process.memory_info().rss / 1024 / 1024

    # Generate geometry
    step_bytes = build_step_solid(
        polygons=MULTI_ROOM, height=3000, wall_thickness=200
    )

    # Measure peak memory
    peak_mb = process.memory_info().rss / 1024 / 1024
    memory_increase_mb = peak_mb - baseline_mb

    print(f"\nMemory usage: baseline={baseline_mb:.1f}MB, peak={peak_mb:.1f}MB, "
          f"increase={memory_increase_mb:.1f}MB")

    # Memory increase should be reasonable (<100MB for 3 rooms)
    assert memory_increase_mb < 100, f"Excessive memory usage: {memory_increase_mb:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
