import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models import Job

async def test_routing():
    print("Testing Prompt Routing Logic...")
    
    # Valid model for floor plan
    valid_model = {
        "contours": [[[0,0], [10,0], [10,10], [0,10]]],
        "extrude_height": 3000,
        "wall_thickness": 200,
        "metadata": {"source": "rooms"}
    }

    # Mock dependencies
    with patch("app.pipelines.prompt._run_precision_cad", new_callable=AsyncMock) as mock_precision_cad, \
         patch("app.pipelines.prompt._generate_instructions", new_callable=AsyncMock) as mock_gen_instructions, \
         patch("app.pipelines.prompt._instructions_to_model", return_value=valid_model) as mock_to_model, \
         patch("app.pipelines.prompt.get_routing_service") as mock_routing, \
         patch("app.pipelines.prompt.get_stable_diffusion_service") as mock_sd, \
         patch("app.pipelines.prompt.get_triposr_service") as mock_triposr, \
         patch("app.pipelines.prompt.build_artifacts", return_value=(b"", b"")) as mock_artifacts, \
         patch("app.pipelines.prompt.storage_service") as mock_storage, \
         patch("app.pipelines.prompt.FileModel") as mock_file_model, \
         patch("app.pipelines.prompt.export_gltf_with_materials", return_value=b"") as mock_gltf:

        # Setup mocks
        mock_storage.save_bytes.return_value = ("key", 100)
        mock_gen_instructions.return_value = {"rooms": []}
        mock_file_model.return_value.id = "file_id"
        
        # Test Case 1: Precision 3D
        print("\n1. Testing Precision 3D mode...")
        job_3d = Job(id="job_3d", params={"generation_mode": "precision_3d", "prompt": "test"})
        session = AsyncMock()
        
        from app.pipelines.prompt import run
        await run(job_3d, session)
        
        if mock_precision_cad.called:
            print("✅ Precision 3D correctly called _run_precision_cad")
        else:
            print("❌ Precision 3D FAILED to call _run_precision_cad")
            return False

        # Reset mocks
        mock_precision_cad.reset_mock()
        mock_gen_instructions.reset_mock()

        # Test Case 2: Precision 2D
        print("\n2. Testing Precision 2D mode...")
        job_2d = Job(id="job_2d", params={"generation_mode": "precision_2d", "prompt": "test"})
        
        await run(job_2d, session)
        
        success = True
        if mock_precision_cad.called:
            print("❌ Precision 2D incorrectly called _run_precision_cad")
            success = False
        else:
            print("✅ Precision 2D correctly bypassed _run_precision_cad")
            
        if mock_gen_instructions.called:
            print("✅ Precision 2D correctly called _generate_instructions (Parametric Pipeline)")
        else:
            print("❌ Precision 2D FAILED to call _generate_instructions")
            success = False
            
        return success

if __name__ == "__main__":
    try:
        if asyncio.run(test_routing()):
            print("\nAll routing tests PASSED ✅")
            sys.exit(0)
        else:
            print("\nSome tests FAILED ❌")
            sys.exit(1)
    except Exception as e:
        print(f"\nTest crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
