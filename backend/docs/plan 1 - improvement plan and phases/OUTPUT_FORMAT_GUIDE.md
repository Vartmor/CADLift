# CADLift Output Format Guide 📦

Complete guide to understanding and using CADLift's output formats in different software.

---

## Table of Contents

1. [Format Overview](#format-overview)
2. [STEP Format](#step-format-cad-editing)
3. [DXF Format](#dxf-format-2d3d-cad)
4. [OBJ Format](#obj-format-3d-modeling)
5. [STL Format](#stl-format-3d-printing)
6. [PLY Format](#ply-format-point-clouds)
7. [glTF/GLB Format](#gltfglb-format-web-3d--game-engines)
8. [Software-Specific Instructions](#software-specific-instructions)

---

## Format Overview

CADLift generates **7 output formats** optimized for different use cases:

| Format | Best For | Editable | File Size | Compatibility |
|--------|----------|----------|-----------|---------------|
| **STEP** | CAD editing, parametric modeling | ✅ Yes | Medium | AutoCAD, FreeCAD, SolidWorks |
| **DXF** | CAD software, 2D/3D drawing | ✅ Yes | Small-Medium | Universal CAD support |
| **OBJ** | 3D modeling, rendering, Blender | ⚠️ Limited | Very Small | Universal 3D software |
| **STL** | 3D printing, rapid prototyping | ❌ No | Small | Printers, slicers (Cura, PrusaSlicer) |
| **PLY** | Research, point cloud processing | ⚠️ Limited | Small | MeshLab, CloudCompare |
| **glTF** | Web 3D, AR/VR (JSON + bin) | ⚠️ Limited | Small | Three.js, Babylon.js, browsers |
| **GLB** | Game engines, web 3D (binary) | ⚠️ Limited | Very Small | Unity, Unreal, Blender, Sketchfab |

**Legend:**
- ✅ **Editable:** Parametric geometry, can modify in CAD
- ⚠️ **Limited:** Mesh only, can edit vertices but not parametric
- ❌ **Not editable:** Optimized mesh, view-only or print

---

## STEP Format (CAD Editing)

**File extension:** `.step`, `.stp`
**MIME type:** `application/step`
**Standard:** ISO 10303-21

### What is STEP?

STEP (Standard for the Exchange of Product Data) is the industry standard for CAD data exchange. It preserves **parametric solid geometry**, making it fully editable in CAD software.

### Advantages
✅ Parametric solid geometry (not just mesh)
✅ Universal CAD compatibility
✅ Preserves dimensions and tolerances
✅ Suitable for manufacturing
✅ Can be modified, filleted, chamfered in CAD

### Disadvantages
❌ Larger file size than mesh formats
❌ Not suitable for game engines or web 3D
❌ Slower to load than mesh formats

### Use Cases
- Architectural design and modeling
- Mechanical engineering
- Manufacturing and CNC
- Further CAD editing required
- Creating technical drawings

### How to Open

#### AutoCAD (2018+)
1. File → Import
2. Select file type: **STEP (*.stp, *.step)**
3. Browse and select your `.step` file
4. Click **Open**
5. Geometry appears as 3D solid

**Tips:**
- Use `3DORBIT` to rotate view
- Use `UNION` to combine separate solids
- Export as DWG to save native format

#### FreeCAD (0.20+)
1. File → Open
2. Select your `.step` file
3. Click **Open**
4. Geometry loads in Part workbench

**Tips:**
- Switch to Part Design workbench for editing
- Use Boolean operations: Union, Cut, Intersection
- Export as STL for 3D printing

#### SolidWorks
1. File → Open
2. Set file type filter: **STEP Files (*.stp; *.step)**
3. Select your file
4. Import options dialog appears
5. Click **OK** to import

#### Fusion 360
1. File → Open
2. From My Computer → Upload file
3. Select `.step` file
4. Opens in new design

---

## DXF Format (2D/3D CAD)

**File extension:** `.dxf`
**MIME type:** `application/dxf`
**Standard:** AutoCAD Drawing Exchange Format

### What is DXF?

DXF (Drawing Exchange Format) is AutoCAD's universal file format for 2D and 3D drawings. CADLift outputs **3D DXF with layers** for walls, footprint, and top.

### Layers in CADLift DXF
- **Footprint:** 2D floor plan outline
- **Walls:** 3D vertical wall geometry
- **Top:** 3D ceiling/roof geometry

### How to Open

#### AutoCAD
1. File → Open or `OPEN` command
2. Select `.dxf` file
3. Drawing loads with all layers

**View 3D:**
```
Command: 3DORBIT
or
View → 3D Views → SE Isometric
```

**Managing Layers:**
```
Command: LAYER
Turn layers ON/OFF, Freeze/Thaw
```

#### FreeCAD (Draft Workbench)
1. File → Open
2. Select `.dxf` file
3. Import options appear
4. Click **OK**

**View Layers:**
- Tree view on left shows all layers
- Toggle visibility by clicking eye icon

#### QCAD
1. File → Open
2. Select `.dxf` file
3. Layers appear in layer list
4. Use layer toolbar to toggle visibility

---

## OBJ Format (3D Modeling)

**File extension:** `.obj`
**MIME type:** `model/obj`
**Standard:** Wavefront OBJ (text-based)

### What is OBJ?

OBJ is a simple, universal 3D mesh format. It's **text-based** and human-readable. Supported by virtually all 3D software.

### File Size
**Very small** - typically 1-5 KB for simple rooms
- Example: 5m×4m room = ~1 KB

### How to Open

#### Blender (3.0+)
1. File → Import → Wavefront (.obj)
2. Select your `.obj` file
3. Click **Import OBJ**
4. Mesh appears in viewport

**Tips:**
- Press `Numpad 7` for top view
- Press `Z` for shading options
- Use Edit Mode (`Tab`) to modify mesh

#### Autodesk Maya
1. File → Import
2. Set file type: **OBJexport**
3. Select `.obj` file
4. Click **Import**

#### SketchUp
1. File → Import
2. Change file type to **All Supported File Types**
3. Select `.obj` file
4. Click **Import**

#### Mesh-based CAD (Rhino, MOI3D)
1. File → Import
2. Select **Wavefront OBJ**
3. Opens as mesh object

---

## STL Format (3D Printing)

**File extension:** `.stl`
**MIME type:** `model/stl`
**Standard:** STereoLithography (binary)

### What is STL?

STL is the standard format for 3D printing. CADLift outputs **binary STL** (more compact than ASCII).

### Validation
CADLift ensures all meshes are:
- ✅ **Watertight** (no holes)
- ✅ **Manifold** (valid for printing)
- ✅ **Properly oriented** (outward-facing normals)

### How to Open

#### Cura (Ultimaker Cura)
1. File → Open File(s)
2. Select `.stl` file
3. Model appears on build plate
4. Adjust scale, orientation
5. Slice for your printer

#### PrusaSlicer
1. Add button or File → Import → Import STL
2. Select file
3. Model loads on print bed
4. Configure print settings
5. Slice and export G-code

#### Simplify3D
1. File → Import Models
2. Select `.stl` file
3. Position on build plate
4. Generate supports if needed
5. Prepare to print

#### MeshLab (View/Repair)
1. File → Import Mesh
2. Select `.stl` file
3. Use Filters → Cleaning and Repairing for mesh fixes

---

## PLY Format (Point Clouds)

**File extension:** `.ply`
**MIME type:** `application/ply`
**Standard:** Polygon File Format

### What is PLY?

PLY stores polygon meshes with optional properties (color, normals, texture coordinates).

### How to Open

#### MeshLab
1. File → Import Mesh
2. Select `.ply` file
3. Mesh loads with all properties

#### CloudCompare
1. File → Open
2. Select `.ply` file
3. Point cloud/mesh appears

#### Blender
1. File → Import → Stanford (.ply)
2. Select file
3. Import as mesh

---

## glTF/GLB Format (Web 3D & Game Engines)

**File extensions:** `.gltf` (JSON + .bin), `.glb` (binary)
**MIME types:** `model/gltf+json`, `model/gltf-binary`
**Standard:** GL Transmission Format 2.0

### What is glTF/GLB?

- **glTF:** JSON file + separate `.bin` binary (geometry data)
- **GLB:** Single binary file (recommended for game engines)

### Advantages
✅ Compact binary format
✅ Fast loading
✅ PBR materials support (future feature)
✅ Animation support (future feature)
✅ Optimized for real-time rendering

### How to Open

#### Unity (2020+)
1. Drag `.glb` file into Assets folder
2. Unity imports automatically
3. Model appears in Project panel
4. Drag into scene

**Tips:**
- GLB imports as GameObject with MeshRenderer
- Materials may need adjustment
- Use ProBuilder for further editing

#### Unreal Engine (4.27+, 5.0+)
1. Content Browser → Import
2. Select `.glb` file
3. Import options appear
4. Click **Import All**

**Tips:**
- Adjust scale if needed (UE uses cm, CADLift uses mm)
- Materials import as basic
- Use Datasmith for better import

#### Blender (3.0+)
1. File → Import → glTF 2.0 (.glb/.gltf)
2. Select file
3. Click **Import glTF 2.0**

#### Three.js (Web 3D)
```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load('model.glb', (gltf) => {
  scene.add(gltf.scene);
});
```

#### Babylon.js (Web 3D)
```javascript
BABYLON.SceneLoader.ImportMesh("", "./", "model.glb", scene, (meshes) => {
  // Meshes loaded
});
```

#### Sketchfab (Online Viewer)
1. Go to sketchfab.com
2. Upload → 3D Models
3. Select `.glb` file
4. Model appears in online viewer
5. Share publicly or keep private

---

## Software-Specific Instructions

### Opening in AutoCAD

**For STEP files:**
```
Command: IMPORT
File type: STEP (*.stp, *.step)
Select file → OK
```

**For DXF files:**
```
Command: OPEN
or
File → Open → Select .dxf file
```

**Viewing 3D:**
```
Command: 3DORBIT
or
View Cube: Click corners for different views
```

---

### Opening in FreeCAD

**For STEP:**
- File → Open → Select .step
- Loads in Part workbench
- Editable as solid

**For DXF:**
- File → Open → Select .dxf
- Loads in Draft workbench
- Switch to Part to extrude if needed

**For OBJ/STL:**
- File → Open → Select file
- Loads as Mesh object
- Use Mesh Design workbench for editing

---

### Opening in Blender

**Import workflow:**
1. File → Import → Select format
2. Navigate to file
3. Click Import button

**Format options:**
- `.obj` → Wavefront (.obj)
- `.stl` → STL (.stl)
- `.ply` → Stanford (.ply)
- `.glb` → glTF 2.0 (.glb/.gltf)

**After import:**
- Object appears at origin
- Select object (left-click)
- Press `G` to move, `R` to rotate, `S` to scale
- Tab for Edit Mode

---

### Opening in Unity

**Supported:** `.glb`, `.obj`

**Method 1: Drag and drop**
1. Open Unity project
2. Drag file into Assets panel
3. Unity imports automatically

**Method 2: Import Assets**
1. Assets → Import New Asset
2. Select file
3. Click Import

**Viewing:**
- Double-click in Project panel
- Or drag into Scene/Hierarchy

---

### Opening in Unreal Engine

**Supported:** `.glb`, `.obj`

1. Content Browser → Import button
2. Select file(s)
3. Import options dialog:
   - Convert Scene: Yes
   - Import Mesh: Yes
   - Import Materials: Yes (if available)
4. Click **Import All**

**Tips:**
- Meshes appear in Content Browser
- Drag into level to place
- Adjust scale in Details panel if needed (UE uses cm, CADLift mm)

---

## Format Comparison

### For CAD Editing
**Best:** STEP > DXF
- Full solid geometry
- Parametric and editable
- Industry standard

### For 3D Modeling/Rendering
**Best:** OBJ > GLB
- Universal support
- Lightweight
- Easy to import

### For 3D Printing
**Best:** STL
- Industry standard
- All slicers support
- Watertight guaranteed

### For Game Engines
**Best:** GLB > OBJ
- Optimized for real-time
- Single file format
- Fast loading

### For Web 3D
**Best:** GLB
- Compact binary
- Native browser support
- Three.js/Babylon.js optimized

---

## File Size Comparison

**Example: 5m × 4m simple room**

| Format | File Size | Compression Ratio |
|--------|-----------|-------------------|
| STEP | ~29 KB | 1.0x (baseline) |
| DXF | ~15 KB | 1.9x smaller |
| OBJ | ~1 KB | 29x smaller |
| STL | ~1.7 KB | 17x smaller |
| PLY | ~1.2 KB | 24x smaller |
| GLB | ~1.3 KB | 22x smaller |

**Mesh formats are 17-29x smaller than STEP!**

---

## Tips for Best Results

### General Tips
✅ Use STEP for CAD work requiring further editing
✅ Use OBJ/GLB for visualization and rendering
✅ Use STL for 3D printing
✅ Use GLB for game engines (Unity, Unreal)

### Scale Issues
CADLift outputs in **millimeters (mm)**:
- 1 unit = 1mm
- 1000 units = 1 meter
- 5000 units = 5 meters

**If model appears too small/large:**
- **Blender:** Scale by 0.001 (mm → m)
- **Unity:** Scale by 0.001 or import as cm
- **Unreal:** Scale by 0.1 (mm → cm)

### Material Issues
CADLift currently outputs **geometry only** (no materials).

**To add materials:**
- **Blender:** Material Properties → New Material
- **Unity:** Create material → assign to MeshRenderer
- **Unreal:** Create Material → assign to Static Mesh

---

## Common Questions

**Q: Which format should I use?**
A: Depends on your use case:
- CAD editing → STEP
- 3D printing → STL
- Game engines → GLB
- General 3D work → OBJ

**Q: Why is my model too small/large?**
A: CADLift uses millimeters. Scale accordingly in your software.

**Q: Can I convert between formats?**
A: Yes! Download same job in multiple formats:
```bash
curl "http://server/api/v1/files/{id}?format=step" -o model.step
curl "http://server/api/v1/files/{id}?format=obj" -o model.obj
curl "http://server/api/v1/files/{id}?format=glb" -o model.glb
```

**Q: Which format preserves the most detail?**
A: STEP preserves parametric solid geometry. Mesh formats (OBJ, STL, GLB) are tessellated approximations.

---

## Next Steps

- 📖 [Quick Start Guide](QUICK_START_GUIDE.md) - Get started in 5 minutes
- 🔌 [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- 🛠️ [Troubleshooting](TROUBLESHOOTING_GUIDE.md) - Fix common issues

---

*Last updated: 2025-11-24*
*CADLift Output Format Guide v1.0*
