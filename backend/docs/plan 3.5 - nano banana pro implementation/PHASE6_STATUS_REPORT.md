# Phase 6 Status Report (TripoSR Integration)

Date: 2025-11-29

## Summary
- Shap-E is deprecated on Windows (PyTorch/CLIP JIT crash). See backend/docs/plan 3 - any object ultra realistic/SHAP_E_INVESTIGATION.md.
- Docker removed; local-only dev scripts in place (start-dev.ps1 / start-dev.sh).
- Phase 5 (3D viewer + Mayo CAD export) is complete and stable.
- TripoSR integration is code-complete (service + pipeline wiring). Runtime availability depends on installing TripoSR deps and weights.

## What was implemented in Phase 6
- Added TripoSR service (`backend/app/services/triposr.py`) with model load, preprocessing, and OBJ export.
- Updated AI pipeline (`backend/app/pipelines/ai.py`) to route image jobs to TripoSR (expects `params["image_bytes"]`), convert to GLB/OBJ/DXF/STEP, and run mesh processing with quality metrics.
- Added reports: PHASE6_STATUS_REPORT.md and PHASE6_IMPLEMENTATION_REPORT.md.
- Updated the main plan to reflect Shap-E deprecation and TripoSR as the AI path.

## How to enable/run TripoSR
1) From `backend/`, install deps into the venv:
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118  # or CPU wheels
pip install omegaconf einops transformers
pip install -e ../docs/useful_projects/TripoSR  # builds torchmcubes
```
   Ensure CUDA toolkit + VS Build Tools on Windows for GPU builds.
2) Keep `docs/useful_projects/TripoSR` cloned (already present).
3) Start backend; for image jobs, set `source_type="image"` and pass `image_bytes` in params. If TripoSR is unavailable, the pipeline returns a clear error instead of a silent fallback.

## Risks
- torchmcubes build can be heavy on Windows; memory spikes possible. If constrained, use CPU wheels and run without Celery.
- If dependencies are missing, TripoSR is disabled (service_not_available), and jobs will error instead of falling back.

## Next steps
- Add API helper to inject upload bytes into `params["image_bytes"]` for image jobs.
- Add tests: TripoSR available/unavailable + happy path.
- Add a short “Using TripoSR” doc under `backend/docs/plan 3 - any object ultra realistic/`.
