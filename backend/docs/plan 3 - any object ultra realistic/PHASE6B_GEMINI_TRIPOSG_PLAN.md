# Phase 6B — Gemini → TripoSG Hybrid Path

**Goal**: For organic/artistic prompts, generate an image with Gemini (Nano Banana / Pro), then convert it to 3D with TripoSG. Keep engineering/mechanical/architectural prompts on the existing parametric pipeline.

## Steps
1) Routing
   - Add `use_gemini_triposg` flag (default ON).
   - Route organic/freeform prompts to the Gemini→TripoSG path; keep engineering prompts parametric.

2) Gemini image service
   - Config keys (from `backend/.env`): `GEMINI_API_KEY`, `gemini_image_model` (default `gemini-2.5-flash-image`), `gemini_image_aspect_ratio` (`1:1`), `gemini_image_resolution` (`1K|2K|4K` depending on model support).
   - Function: `generate_image(prompt, aspect_ratio, resolution) -> bytes`.
   - ResponseModalities = Image only; prefer neutral background, orthographic view, clear geometry.

3) TripoSG wrapper
   - Input: image bytes.
   - Output: GLB/OBJ bytes (limit faces if needed).
   - Prefer GPU; CPU fallback with warning. Handle first-time weight download gracefully.

4) Pipeline integration
   - Prompt jobs: if flagged + routed organic, run Gemini→TripoSG, then mesh processing + conversions (GLB/OBJ/STEP/DXF). On failure, fall back to parametric and set `fallback_used=True`.
   - Image jobs: optional `use_triposg` flag to run TripoSG directly on uploaded images; otherwise keep contour/OpenSCAD flow.

5) Frontend
   - Toggles: “AI mesh (Gemini→TripoSG)” vs “Parametric CAD” for prompt jobs; “AI mesh (TripoSG)” for image jobs.
   - Show provider/quality metadata when AI path is used.

6) Tests/Docs
   - Unit tests mocking Gemini + TripoSG.
   - Doc: env var placement, latency expectations, GPU recommendation.

## Env (when ready)
Add to `backend/.env`:
```
GEMINI_API_KEY=
```
Other optional configs (already defaulted in settings): `gemini_image_model`, `gemini_image_aspect_ratio`, `gemini_image_resolution`, `enable_gemini_triposg`.
