
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.solidpython_service import get_solidpython_service

def test_advanced_geometry():
    print("Initializing SolidPythonService...")
    service = get_solidpython_service()
    
    if not service.can_render():
        print("Cannot render - check OpenSCAD installation.")
        return

    # Test 1: M6 Threaded Bolt
    print("\n--- Testing M6 Threaded Bolt ---")
    bolt_instructions = {
        "parts": [
            # Hex Head
            {"type": "cylinder", "r": 5, "h": 4, "segments": 6},
            # Threaded Shaft (approximated)
            {"type": "thread", "major_radius": 3, "length": 30, "pitch": 1.0, "position": [0,0,4]}
        ]
    }
    
    try:
        stl = service.render_to_stl(bolt_instructions)
        print(f"✅ Bolt generated: {len(stl)} bytes")
        with open("test_bolt.stl", "wb") as f:
            f.write(stl)
    except Exception as e:
        print(f"❌ Bolt failure: {e}")

    # Test 2: Revolved Bowl
    print("\n--- Testing Revolved Bowl ---")
    bowl_instructions = {
        "parts": [
            {
                "type": "revolve",
                "profile_vertices": [[0,0], [30,0], [40,20], [38,20], [28,2], [0,2]],
                "angle_deg": 360,
                "segments": 50
            }
        ]
    }
    
    try:
        stl = service.render_to_stl(bowl_instructions)
        print(f"✅ Bowl generated: {len(stl)} bytes")
        with open("test_bowl.stl", "wb") as f:
            f.write(stl)
    except Exception as e:
        print(f"❌ Bowl failure: {e}")
        
    # Test 3: Simple Pipe Sweep (Hull method)
    print("\n--- Testing Pipe Sweep ---")
    # A simplified U-shape path
    sweep_instructions = {
        "parts": [
            {
                "type": "sweep",
                "profile_vertices": [[-2,-2], [2,-2], [2,2], [-2,2]], # 4x4 square profile
                "path_vertices": [[0,0,0], [0,0,20], [10,0,30], [20,0,30], [30,0,20], [30,0,0]]
            }
        ]
    }
    
    try:
        stl = service.render_to_stl(sweep_instructions)
        print(f"✅ Sweep generated: {len(stl)} bytes")
        with open("test_sweep.stl", "wb") as f:
            f.write(stl)
    except Exception as e:
        print(f"❌ Sweep failure: {e}")

if __name__ == "__main__":
    test_advanced_geometry()
