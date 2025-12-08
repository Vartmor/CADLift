# Vendor Dependencies

Third-party libraries bundled with CADLift for AI/CAD functionality.

| Package | License | Purpose |
|---------|---------|---------|
| [TripoSR](https://github.com/VAST-AI-Research/TripoSR) | MIT | Image-to-3D AI reconstruction |
| [TripoSG](https://github.com/VAST-AI-Research/TripoSG) | Apache 2.0 | Alternative image-to-3D AI |
| [SolidPython](https://github.com/jeff-dh/SolidPython) | LGPL | Parametric CAD via OpenSCAD |
| [co2tools](https://github.com/Mambix/co2tools) | MIT | DXF to STL extrusion |
| [Shap-E](https://github.com/openai/shap-e) | MIT | Text-to-3D (currently disabled) |

## Installation

These packages are imported directly from their respective directories. Some require additional setup:

```bash
# Shap-E (if re-enabling)
cd vendor/shap-e && pip install -e .

# TripoSR dependencies
pip install omegaconf einops transformers huggingface-hub rembg
```

## Usage

Services automatically load these vendors from the `vendor/` directory. No manual path configuration needed.
