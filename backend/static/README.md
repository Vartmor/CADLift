# CADLift Frontend Demo

This directory contains a simple HTML demo frontend for CADLift (Phase 6.6).

## Features

- **File Upload**: Drag & drop or click to upload DXF/Image files
- **Text Prompt**: Generate 3D models from text descriptions
- **Job Status**: Real-time job status updates
- **Multi-Format Download**: Download generated models in 7 formats (STEP, DXF, OBJ, STL, PLY, glTF, GLB)
- **API Documentation**: Integrated API reference

## Usage

1. Start the CADLift backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. Open the demo in your browser:
   ```
   http://localhost:8000/static/demo.html
   ```

3. Upload a file or enter a prompt, configure parameters, and generate your 3D model!

## Building a Production Frontend

This demo is intentionally simple to demonstrate the API. For a production frontend, consider:

- **Framework**: React, Vue, or Angular for component-based architecture
- **3D Viewer**: Three.js or Babylon.js for GLB/glTF preview
- **State Management**: Redux/Vuex for complex application state
- **Real-time Updates**: WebSockets for live job status updates
- **File Manager**: Organize and browse generated models
- **Advanced Parameters**: UI for all API parameters (materials, multi-story, etc.)

## API Integration Example

```javascript
// Create job
const formData = new FormData();
formData.append('job_type', 'cad');
formData.append('mode', 'cad');
formData.append('upload', file);
formData.append('params', JSON.stringify({
    extrude_height: 3000,
    wall_thickness: 200
}));

const response = await fetch('/api/v1/jobs', {
    method: 'POST',
    body: formData
});

const job = await response.json();

// Poll for status
setInterval(async () => {
    const statusRes = await fetch(`/api/v1/jobs/${job.id}`);
    const status = await statusRes.json();

    if (status.status === 'completed') {
        // Download outputs
        window.location.href = `/api/v1/files/${status.output_file_id}?format=step`;
    }
}, 2000);
```

## Next Steps

- Add Three.js viewer for GLB preview
- Implement user authentication
- Add project/file management
- Create parameter presets
- Add batch processing
- Implement collaborative features
