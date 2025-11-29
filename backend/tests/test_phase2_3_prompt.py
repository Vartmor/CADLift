#!/usr/bin/env python3
"""
Test suite for Phase 2.3 improvements - Prompt Pipeline.

Tests:
- Position-based layout (L-shaped, U-shaped, clusters)
- Custom polygon rooms (non-rectangular shapes)
- LLM response validation and retry logic
- Enhanced instruction schema validation
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def test_simple_rectangular_room():
    """Test 2.3: Simple rectangular room (auto-positioned)"""
    print("\n" + "="*60)
    print("Test 2.3: Simple Rectangular Room (Auto-Positioned)")
    print("="*60)

    from app.pipelines.prompt import _instructions_to_model, _validate_instruction_schema

    instructions = {
        "rooms": [
            {"name": "bedroom", "width": 4000, "length": 3000}
        ],
        "extrude_height": 3000,
        "wall_thickness": 200
    }

    try:
        # Validate schema
        _validate_instruction_schema(instructions)
        print("✅ Schema validation passed")

        # Convert to model
        model = _instructions_to_model(instructions, "Test prompt", {})

        print(f"✅ Model generated")
        print(f"   Contours: {len(model['contours'])}")
        print(f"   Polygon vertices: {len(model['contours'][0])}")

        # Verify polygon is at origin
        polygon = model['contours'][0]
        assert polygon[0] == [0.0, 0.0], "Should start at origin"
        assert polygon[1] == [4000.0, 0.0], "Width should be 4000"
        assert polygon[2] == [4000.0, 3000.0], "Length should be 3000"

        print("✅ Simple rectangular room works correctly")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_positioned_l_shaped_layout():
    """Test 2.3: Positioned rectangular rooms forming L-shape"""
    print("\n" + "="*60)
    print("Test 2.3: Positioned L-Shaped Layout")
    print("="*60)

    from app.pipelines.prompt import _instructions_to_model, _validate_instruction_schema

    # L-shaped layout: reception 8x5m, hallway 8x2m positioned below it
    instructions = {
        "rooms": [
            {"name": "reception", "width": 8000, "length": 5000, "position": [0, 0]},
            {"name": "hallway", "width": 8000, "length": 2000, "position": [0, 5000]}
        ],
        "extrude_height": 3000,
        "wall_thickness": 200
    }

    try:
        # Validate schema
        _validate_instruction_schema(instructions)
        print("✅ Schema validation passed")

        # Convert to model
        model = _instructions_to_model(instructions, "L-shaped office", {})

        print(f"✅ Model generated")
        print(f"   Rooms: {len(model['contours'])}")

        # Verify positions
        reception = model['contours'][0]
        hallway = model['contours'][1]

        assert reception[0] == [0.0, 0.0], "Reception at origin"
        assert reception[2] == [8000.0, 5000.0], "Reception size correct"

        assert hallway[0] == [0.0, 5000.0], "Hallway below reception"
        assert hallway[2] == [8000.0, 7000.0], "Hallway size correct"

        print("✅ L-shaped layout positioned correctly")
        print(f"   Reception: [0,0] to [8000,5000]")
        print(f"   Hallway: [0,5000] to [8000,7000]")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_polygon_pentagon():
    """Test 2.3: Custom polygon room (pentagon)"""
    print("\n" + "="*60)
    print("Test 2.3: Custom Polygon (Pentagon)")
    print("="*60)

    from app.pipelines.prompt import _instructions_to_model, _validate_instruction_schema

    # Pentagon-shaped conference room
    instructions = {
        "rooms": [
            {
                "name": "conference",
                "vertices": [
                    [0, 0],
                    [5000, 0],
                    [6000, 3000],
                    [2500, 5000],
                    [-1000, 3000]
                ]
            }
        ],
        "extrude_height": 3000
    }

    try:
        # Validate schema
        _validate_instruction_schema(instructions)
        print("✅ Schema validation passed")

        # Convert to model
        model = _instructions_to_model(instructions, "Pentagon conference room", {})

        print(f"✅ Model generated")
        print(f"   Contours: {len(model['contours'])}")

        # Verify polygon
        polygon = model['contours'][0]
        assert len(polygon) == 5, "Pentagon should have 5 vertices"
        assert polygon[0] == [0.0, 0.0], "First vertex correct"
        assert polygon[4] == [-1000.0, 3000.0], "Last vertex correct"

        print("✅ Custom pentagon polygon works correctly")
        print(f"   Vertices: {len(polygon)}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mixed_layout():
    """Test 2.3: Mixed layout (rectangular + custom polygon)"""
    print("\n" + "="*60)
    print("Test 2.3: Mixed Layout (Rectangular + Custom Polygon)")
    print("="*60)

    from app.pipelines.prompt import _instructions_to_model, _validate_instruction_schema

    # Mix of rectangular rooms and custom polygon
    instructions = {
        "rooms": [
            {"name": "office1", "width": 5000, "length": 4000, "position": [0, 0]},
            {"name": "office2", "width": 5000, "length": 4000, "position": [5000, 0]},
            {
                "name": "lobby",
                "vertices": [[0, 4000], [10000, 4000], [10000, 7000], [5000, 8000], [0, 7000]]
            }
        ],
        "extrude_height": 3000
    }

    try:
        # Validate schema
        _validate_instruction_schema(instructions)
        print("✅ Schema validation passed")

        # Convert to model
        model = _instructions_to_model(instructions, "Mixed layout", {})

        print(f"✅ Model generated")
        print(f"   Rooms: {len(model['contours'])}")

        # Verify
        assert len(model['contours']) == 3, "Should have 3 rooms"
        assert len(model['contours'][0]) == 4, "Office1 is rectangle (4 vertices)"
        assert len(model['contours'][1]) == 4, "Office2 is rectangle (4 vertices)"
        assert len(model['contours'][2]) == 5, "Lobby is custom polygon (5 vertices)"

        print("✅ Mixed layout works correctly")
        print(f"   Office1: {len(model['contours'][0])} vertices (rectangle)")
        print(f"   Office2: {len(model['contours'][1])} vertices (rectangle)")
        print(f"   Lobby: {len(model['contours'][2])} vertices (custom polygon)")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_validation():
    """Test 2.3: LLM response validation"""
    print("\n" + "="*60)
    print("Test 2.3: LLM Response Validation")
    print("="*60)

    from app.services.llm import LLMService

    # Create service instance (disabled, just for validation testing)
    llm = LLMService(provider="none", api_key=None)

    test_cases = [
        # Valid response
        (
            {
                "rooms": [
                    {"name": "main", "width": 5000, "length": 4000}
                ],
                "extrude_height": 3000
            },
            True,
            "Valid simple room"
        ),
        # Valid positioned room
        (
            {
                "rooms": [
                    {"name": "office", "width": 6000, "length": 5000, "position": [0, 0]}
                ]
            },
            True,
            "Valid positioned room"
        ),
        # Valid custom polygon
        (
            {
                "rooms": [
                    {"name": "lobby", "vertices": [[0,0], [5000,0], [5000,3000], [0,3000]]}
                ]
            },
            True,
            "Valid custom polygon"
        ),
        # Invalid: missing rooms
        (
            {"extrude_height": 3000},
            False,
            "Missing rooms key"
        ),
        # Invalid: empty rooms
        (
            {"rooms": []},
            False,
            "Empty rooms array"
        ),
        # Invalid: room without dimensions or vertices
        (
            {"rooms": [{"name": "invalid"}]},
            False,
            "Room without dimensions or vertices"
        ),
        # Invalid: negative width
        (
            {"rooms": [{"name": "bad", "width": -1000, "length": 3000}]},
            False,
            "Negative width"
        ),
        # Invalid: vertices with < 3 points
        (
            {"rooms": [{"name": "bad", "vertices": [[0,0], [100,100]]}]},
            False,
            "Vertices with < 3 points"
        ),
        # Invalid: position not [x,y]
        (
            {"rooms": [{"name": "bad", "width": 5000, "length": 3000, "position": [0]}]},
            False,
            "Invalid position format"
        ),
    ]

    passed = 0
    failed = 0

    for response, should_pass, description in test_cases:
        try:
            llm._validate_llm_response(response)
            if should_pass:
                print(f"✅ {description}: PASS (valid)")
                passed += 1
            else:
                print(f"❌ {description}: FAIL (should have rejected)")
                failed += 1
        except ValueError as e:
            if not should_pass:
                print(f"✅ {description}: PASS (correctly rejected)")
                passed += 1
            else:
                print(f"❌ {description}: FAIL (should have accepted) - {e}")
                failed += 1

    print(f"\n✅ Validation tests: {passed}/{len(test_cases)} passed")

    if failed == 0:
        print("✅ All validation tests passed")
        return True
    else:
        print(f"⚠️  {failed} validation tests failed")
        return False


def test_cluster_layout():
    """Test 2.3: Cluster layout (3 bedrooms side by side)"""
    print("\n" + "="*60)
    print("Test 2.3: Cluster Layout (3 Bedrooms)")
    print("="*60)

    from app.pipelines.prompt import _instructions_to_model, _validate_instruction_schema

    # Three 4x3m bedrooms side by side
    instructions = {
        "rooms": [
            {"name": "bedroom1", "width": 4000, "length": 3000, "position": [0, 0]},
            {"name": "bedroom2", "width": 4000, "length": 3000, "position": [4000, 0]},
            {"name": "bedroom3", "width": 4000, "length": 3000, "position": [8000, 0]}
        ],
        "extrude_height": 3000
    }

    try:
        # Validate schema
        _validate_instruction_schema(instructions)
        print("✅ Schema validation passed")

        # Convert to model
        model = _instructions_to_model(instructions, "Three bedrooms", {})

        print(f"✅ Model generated")
        print(f"   Rooms: {len(model['contours'])}")

        # Verify positions
        bed1 = model['contours'][0]
        bed2 = model['contours'][1]
        bed3 = model['contours'][2]

        assert bed1[0] == [0.0, 0.0], "Bedroom1 at origin"
        assert bed2[0] == [4000.0, 0.0], "Bedroom2 next to bedroom1"
        assert bed3[0] == [8000.0, 0.0], "Bedroom3 next to bedroom2"

        # Verify they're touching (shared walls)
        assert bed1[1][0] == bed2[0][0], "Bedroom1 and 2 share wall"
        assert bed2[1][0] == bed3[0][0], "Bedroom2 and 3 share wall"

        print("✅ Cluster layout positioned correctly")
        print(f"   Bedroom1: x=0, Bedroom2: x=4000, Bedroom3: x=8000")
        print(f"   Rooms share walls (touching)")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 2.3 tests"""
    print("\n" + "#"*60)
    print("# Phase 2.3 Prompt Pipeline Improvements Test Suite")
    print("#"*60)

    results = {
        "simple_rectangular": test_simple_rectangular_room(),
        "positioned_l_shaped": test_positioned_l_shaped_layout(),
        "custom_polygon": test_custom_polygon_pentagon(),
        "mixed_layout": test_mixed_layout(),
        "llm_validation": test_llm_validation(),
        "cluster_layout": test_cluster_layout(),
    }

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25s}: {status}")

    print("\n" + "="*60)
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("="*60)
        print("\nPhase 2.3 implementations verified!")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
