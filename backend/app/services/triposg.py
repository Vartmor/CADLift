"""
TripoSG image-to-3D wrapper.

Runs the bundled TripoSG reference scripts to convert an image into a 3D mesh.
Designed to be used after Gemini image generation for organic/artistic prompts.
"""
from __future__ import annotations

import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("cadlift.services.triposg")


class TripoSGError(Exception):
    """TripoSG generation error."""


class TripoSGService:
    def __init__(self) -> None:
        self.repo_path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "useful_projects"
            / "TripoSG-main"
        )
        self.enabled = False
        if not self.repo_path.exists():
            logger.warning("TripoSG service disabled: repo not found at %s", self.repo_path)
            return

        # Quick dependency probe: try importing the pipeline to see if diso/cuda is available
        try:
            import importlib
            import sys as _sys
            sys_path_added = False
            if str(self.repo_path) not in _sys.path:
                _sys.path.insert(0, str(self.repo_path))
                sys_path_added = True
            importlib.import_module("triposg")  # noqa: F401
            self.enabled = True
            logger.info("TripoSG service initialized at %s", self.repo_path)
            if sys_path_added:
                _sys.path.remove(str(self.repo_path))
        except Exception as exc:
            logger.warning(
                "TripoSG service disabled: dependencies not available (likely needs CUDA build for 'diso').",
                extra={"error": str(exc)},
            )
            self.enabled = False

    def is_available(self) -> bool:
        return self.enabled

    def generate_mesh(
        self,
        image_bytes: bytes,
        *,
        faces: Optional[int] = None,
        timeout: int = 600,
    ) -> bytes:
        """
        Generate a 3D mesh (GLB) from an image using TripoSG.

        Args:
            image_bytes: Input image data.
            faces: Optional target face count (passed to script).
            timeout: Subprocess timeout in seconds.
        """
        if not self.enabled:
            raise TripoSGError("TripoSG service not available (repo missing).")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_path = tmpdir_path / "input.png"
            output_path = tmpdir_path / "output.glb"

            input_path.write_bytes(image_bytes)

            cmd = [
                sys.executable,
                "-m",
                "scripts.inference_triposg",
                "--image-input",
                str(input_path),
                "--output-path",
                str(output_path),
            ]
            if faces:
                cmd.extend(["--faces", str(faces)])

            logger.info("Running TripoSG inference", extra={"cmd": " ".join(cmd)})
            try:
                subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                )
            except subprocess.CalledProcessError as exc:
                out = exc.stdout.decode(errors="ignore")
                err = exc.stderr.decode(errors="ignore")
                logger.error(
                    "TripoSG failed",
                    extra={
                        "returncode": exc.returncode,
                        "stdout": out,
                        "stderr": err,
                    },
                )
                raise TripoSGError(f"TripoSG inference failed: {err or out or exc}") from exc
            except subprocess.TimeoutExpired as exc:
                logger.error("TripoSG timed out", extra={"timeout": timeout})
                raise TripoSGError(f"TripoSG timed out after {timeout}s") from exc

            if not output_path.exists():
                raise TripoSGError("TripoSG did not produce an output file")

            return output_path.read_bytes()


_triposg_service: Optional[TripoSGService] = None


def get_triposg_service() -> TripoSGService:
    global _triposg_service
    if _triposg_service is None:
        _triposg_service = TripoSGService()
    return _triposg_service
