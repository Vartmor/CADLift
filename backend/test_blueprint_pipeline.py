import sys
from unittest.mock import MagicMock

# Mock ezdxf and cadquery before importing app
mock_ezdxf = MagicMock()
sys.modules["ezdxf"] = mock_ezdxf
sys.modules["ezdxf.render"] = MagicMock()
sys.modules["ezdxf.units"] = MagicMock()

sys.modules["cadquery"] = MagicMock()
sys.modules["cadquery.exporters"] = MagicMock()
sys.modules["trimesh"] = MagicMock()
sys.modules["cv2"] = MagicMock()
sys.modules["numpy"] = MagicMock()

import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path
from app.models import Job
# app.pipelines.image imports geometry which (now mocked) imports ezdxf
from app.pipelines.image import run
import json

@pytest.mark.asyncio
async def test_smart_blueprint_processing_success():
    """Test that image pipeline prioritizes Vision AI and generates parametric model."""
    
    # Mock data
    mock_job = MagicMock(spec=Job)
    mock_job.id = "test_job_123"
    mock_job.params = {"use_vision": True, "prompt": "bracket"}
    mock_job.input_file_id = "file_123"
    mock_job.user_id = "user_1"
    mock_job.mode = "image_to_2d"
    
    mock_session = AsyncMock()
    mock_session.get.return_value = MagicMock(storage_key="test_image.jpg")
    
    # Mock services
    # Patch where they are defined or imported
    with patch("app.pipelines.image.storage_service") as mock_storage, \
         patch("app.pipelines.image.build_artifacts") as mock_build, \
         patch("app.pipelines.image.get_triposg_service") as mock_triposg, \
         patch("app.pipelines.image.vision_service") as mock_vision, \
         patch("app.services.llm.llm_service") as mock_llm: # Patch at source
         
        mock_path = MagicMock()
        mock_path.read_bytes.return_value = b"fake_image_bytes"
        mock_storage.resolve_path.return_value = mock_path
        mock_storage.save_bytes = AsyncMock(return_value=("key", 100)) # Apply AsyncMock here
        
        # Mock LLM response (Vision success)
        mock_llm.enabled = True
        mock_llm.generate_from_image = AsyncMock(return_value={ # Apply AsyncMock here
            "shapes": [
                {"type": "box", "width": 100, "length": 50, "height": 20}
            ],
            "units": "mm"
        })
        
        # Mock build_artifacts to return Bytes
        mock_build.return_value = (b"DXF", b"STEP")
        
        # Run pipeline
        await run(mock_job, mock_session)
        
        # Verify LLM was called with image
        mock_llm.generate_from_image.assert_called_once()
        
        # Verify fallback (vision_service) was NOT called
        mock_vision.vectorize.assert_not_called()
        
        # Verify artifact generation was called with parametric data
        # Check first arg of build_artifacts (contours)
        # box 100x50 -> should be a rectangle
        assert mock_build.call_count == 1
        call_args = mock_build.call_args
        contours = call_args[0][0]
        assert len(contours) == 1
        assert len(contours[0]) == 4 # Rectangle has 4 points
        
        # Verify job status
        assert mock_job.status == "completed"
        # Check if ai_metadata was updated
        assert mock_job.params["ai_metadata"]["vision_pipeline"] is True

@pytest.mark.asyncio
async def test_smart_blueprint_processing_fallback():
    """Test that image pipeline falls back to pixel tracing if Vision AI fails."""
    
    # Mock data
    mock_job = MagicMock(spec=Job)
    mock_job.id = "test_job_123"
    mock_job.params = {"use_vision": True}
    mock_job.input_file_id = "file_123"
    
    mock_session = AsyncMock()
    mock_session.get.return_value = MagicMock(storage_key="test_image.jpg")
    
    with patch("app.pipelines.image.storage_service") as mock_storage, \
         patch("app.services.llm.llm_service") as mock_llm, \
         patch("app.pipelines.image.build_artifacts") as mock_build, \
         patch("app.pipelines.image._generate_model") as mock_generate_model:
         
        # Setup mocks
        mock_path = MagicMock()
        mock_path.read_bytes.return_value = b"fake_image_bytes"
        mock_storage.resolve_path.return_value = mock_path
        mock_storage.save_bytes = AsyncMock(return_value=("key", 100)) # Apply AsyncMock here
        
        
        # Case 1: LLM disabled
        mock_llm.enabled = False
        mock_generate_model.side_effect = None # Clear any previous
        # Make it awaitable
        f = asyncio.Future()
        f.set_result({"shapes": []})
        mock_generate_model.return_value = f
        
        await run(mock_job, mock_session)
        mock_generate_model.assert_called()
        
        # Case 2: LLM fails
        mock_llm.enabled = True
        mock_llm.generate_from_image = AsyncMock(side_effect=Exception("Vision API Error")) # Apply AsyncMock here
        
        # Reset generate model mock future for next call
        f2 = asyncio.Future()
        f2.set_result({"shapes": []})
        mock_generate_model.return_value = f2
        mock_generate_model.reset_mock()
        
        await run(mock_job, mock_session)

if __name__ == "__main__":
    import asyncio
    print("Running manual tests...")
    asyncio.run(test_smart_blueprint_processing_success())
    print("Success test passed!")
    asyncio.run(test_smart_blueprint_processing_fallback())
    print("Fallback test passed!")
    print("All manual tests passed.")
