"""
Mesh processing and quality enhancement service.

Features:
- Cleanup (deduplicate verts, drop degenerate faces, strip tiny components)
- Repair (normals, holes)
- Decimation (quadric)
- Smoothing (Laplacian)
- Quality metrics and retry helper
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import numpy as np
import trimesh

logger = logging.getLogger("cadlift.services.mesh_processor")


@dataclass
class QualityMetrics:
    """Mesh quality metrics."""

    is_watertight: bool
    is_manifold: bool
    euler_characteristic: int
    genus: int

    face_count: int
    vertex_count: int
    edge_count: int
    bounding_box: tuple[float, float, float]
    volume: float
    surface_area: float

    has_degenerate_faces: bool
    min_edge_length: float
    max_edge_length: float
    avg_edge_length: float
    min_face_angle: float
    max_face_angle: float

    overall_score: float

    needs_repair: bool
    needs_decimation: bool
    needs_smoothing: bool
    needs_remeshing: bool


class MeshProcessor:
    """Mesh processing and quality enhancement."""

    def __init__(self):
        self.min_quality_score = 7.0
        self.target_face_count = 50_000
        self.max_face_count = 200_000

    def _ensure_trimesh(self, mesh) -> trimesh.Trimesh:
        """Ensure input is a Trimesh (if Scene, take first geometry)."""
        if isinstance(mesh, trimesh.Trimesh):
            return mesh
        if isinstance(mesh, trimesh.Scene):
            if len(mesh.geometry) == 0:
                raise ValueError("Scene contains no geometry")
            return next(iter(mesh.geometry.values()))
        raise TypeError(f"Unsupported mesh type: {type(mesh)}")

    async def process_mesh(
        self,
        mesh_bytes: bytes,
        file_type: str = "glb",
        target_faces: Optional[int] = None,
        enable_smoothing: bool = True,
        enable_cleanup: bool = True,
        enable_repair: bool = True,
    ) -> tuple[bytes, QualityMetrics]:
        """Process mesh with cleanup, repair, optimization, smoothing."""
        logger.info(
            "Processing mesh",
            extra={
                "file_type": file_type,
                "target_faces": target_faces,
                "cleanup": enable_cleanup,
                "repair": enable_repair,
                "smoothing": enable_smoothing,
            },
        )

        mesh = trimesh.load(trimesh.util.wrap_as_stream(mesh_bytes), file_type=file_type)
        mesh = self._ensure_trimesh(mesh)

        initial_quality = self._calculate_quality(mesh)
        logger.info(
            "Initial mesh quality",
            extra={
                "faces": initial_quality.face_count,
                "vertices": initial_quality.vertex_count,
                "score": f"{initial_quality.overall_score:.1f}/10",
            },
        )

        if enable_cleanup:
            mesh = self._cleanup_mesh(mesh)

        if enable_repair and initial_quality.needs_repair:
            mesh = self._repair_mesh(mesh)

        if target_faces is None:
            target_faces = self.target_face_count

        if len(mesh.faces) > target_faces:
            mesh = self._decimate_mesh(mesh, target_faces)

        if enable_smoothing:
            mesh = self._smooth_mesh(mesh)

        final_quality = self._calculate_quality(mesh)
        logger.info(
            "Final mesh quality",
            extra={
                "faces": final_quality.face_count,
                "vertices": final_quality.vertex_count,
                "score": f"{final_quality.overall_score:.1f}/10",
                "improvement": f"{final_quality.overall_score - initial_quality.overall_score:.1f}",
            },
        )

        out_stream = BytesIO()
        mesh.export(out_stream, file_type="glb")
        return out_stream.getvalue(), final_quality

    def _cleanup_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Clean up artifacts and disconnected tiny parts."""
        mesh.merge_vertices()

        valid_faces = mesh.area_faces > 1e-10
        if not valid_faces.all():
            mesh.update_faces(valid_faces)

        components = mesh.split(only_watertight=False)
        if len(components) > 1:
            mesh = max(components, key=lambda m: len(m.faces))

        mesh.remove_unreferenced_vertices()
        return mesh

    def _repair_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Repair normals and fill simple holes."""
        mesh.fix_normals()
        try:
            mesh.fill_holes()
        except Exception as exc:  # pragma: no cover - best effort
            logger.warning(f"Hole filling failed: {exc}")

        if not mesh.is_watertight:
            try:
                mesh.process(validate=True)
            except Exception as exc:  # pragma: no cover
                logger.warning(f"Watertight conversion failed: {exc}")
        return mesh

    def _decimate_mesh(self, mesh: trimesh.Trimesh, target_faces: int) -> trimesh.Trimesh:
        """Quadric edge collapse decimation."""
        current_faces = len(mesh.faces)
        if current_faces <= target_faces:
            return mesh

        try:
            decimated = mesh.simplify_quadric_decimation(target_faces)
            return decimated
        except Exception as exc:  # pragma: no cover
            logger.error(f"Decimation failed: {exc}, returning original mesh")
            return mesh

    def _smooth_mesh(
        self,
        mesh: trimesh.Trimesh,
        iterations: int = 2,
        lambda_factor: float = 0.5,
    ) -> trimesh.Trimesh:
        """Laplacian smoothing."""
        try:
            for _ in range(iterations):
                vertex_neighbors = mesh.vertex_neighbors
                smoothed = np.zeros_like(mesh.vertices)
                for i, neighbors in enumerate(vertex_neighbors):
                    if neighbors:
                        neighbor_positions = mesh.vertices[neighbors]
                        avg_position = neighbor_positions.mean(axis=0)
                        smoothed[i] = lambda_factor * avg_position + (1 - lambda_factor) * mesh.vertices[i]
                    else:
                        smoothed[i] = mesh.vertices[i]
                mesh.vertices = smoothed
            return mesh
        except Exception as exc:  # pragma: no cover
            logger.error(f"Smoothing failed: {exc}, returning original mesh")
            return mesh

    def _calculate_quality(self, mesh: trimesh.Trimesh) -> QualityMetrics:
        """Compute quality metrics and score."""
        mesh = self._ensure_trimesh(mesh)
        is_watertight = mesh.is_watertight
        euler = mesh.euler_number
        genus = 1 - (euler // 2) if euler < 2 else 0

        face_count = len(mesh.faces)
        vertex_count = len(mesh.vertices)
        edge_count = len(mesh.edges_unique)
        bbox = tuple(mesh.extents)
        volume = float(mesh.volume) if is_watertight else 0.0
        surface_area = float(mesh.area)

        edge_lengths = np.linalg.norm(
            mesh.vertices[mesh.edges[:, 0]] - mesh.vertices[mesh.edges[:, 1]],
            axis=1,
        )
        min_edge = float(edge_lengths.min()) if len(edge_lengths) else 0.0
        max_edge = float(edge_lengths.max()) if len(edge_lengths) else 0.0
        avg_edge = float(edge_lengths.mean()) if len(edge_lengths) else 0.0

        face_angles = np.degrees(mesh.face_angles)
        min_angle = float(face_angles.min()) if len(face_angles) else 0.0
        max_angle = float(face_angles.max()) if len(face_angles) else 0.0

        has_degenerate = (mesh.area_faces < 1e-10).any()

        score = 10.0
        if not is_watertight:
            score -= 2.0
        if has_degenerate:
            score -= 1.0
        if min_angle < 10:
            score -= 1.0
        if max_angle > 170:
            score -= 1.0
        if face_count > self.max_face_count:
            score -= 1.0
        if face_count < 100:
            score -= 2.0
        score = max(1.0, min(10.0, score))

        needs_repair = not is_watertight or has_degenerate
        needs_decimation = face_count > self.target_face_count * 1.5
        needs_smoothing = min_angle < 15 or max_angle > 165
        needs_remeshing = has_degenerate or (min_edge > 0 and max_edge / min_edge > 100)

        return QualityMetrics(
            is_watertight=is_watertight,
            is_manifold=mesh.is_volume,  # Trimesh uses is_volume for manifold check
            euler_characteristic=euler,
            genus=genus,
            face_count=face_count,
            vertex_count=vertex_count,
            edge_count=edge_count,
            bounding_box=bbox,
            volume=volume,
            surface_area=surface_area,
            has_degenerate_faces=has_degenerate,
            min_edge_length=min_edge,
            max_edge_length=max_edge,
            avg_edge_length=avg_edge,
            min_face_angle=min_angle,
            max_face_angle=max_angle,
            overall_score=score,
            needs_repair=needs_repair,
            needs_decimation=needs_decimation,
            needs_smoothing=needs_smoothing,
            needs_remeshing=needs_remeshing,
        )


_mesh_processor: Optional[MeshProcessor] = None


def get_mesh_processor() -> MeshProcessor:
    """Get mesh processor singleton."""
    global _mesh_processor
    if _mesh_processor is None:
        _mesh_processor = MeshProcessor()
    return _mesh_processor


async def process_mesh(
    mesh_bytes: bytes,
    file_type: str = "glb",
    target_faces: Optional[int] = None,
    min_quality: float = 7.0,
    max_retries: int = 3,
) -> tuple[bytes, QualityMetrics]:
    """Process mesh with retry and quality threshold."""
    processor = get_mesh_processor()
    best_bytes = mesh_bytes
    best_quality: QualityMetrics | None = None

    for attempt in range(max_retries):
        processed_bytes, quality = await processor.process_mesh(
            mesh_bytes=mesh_bytes,
            file_type=file_type,
            target_faces=target_faces,
        )
        best_bytes, best_quality = processed_bytes, quality
        if quality.overall_score >= min_quality:
            logger.info(
                f"Mesh processing successful (attempt {attempt + 1})",
                extra={"quality_score": f"{quality.overall_score:.1f}/10"},
            )
            return processed_bytes, quality

        logger.warning(
            f"Mesh quality below threshold on attempt {attempt + 1}: "
            f"{quality.overall_score:.1f} < {min_quality}"
        )
        if quality.needs_decimation and target_faces:
            target_faces = int(target_faces * 0.8)

    logger.warning(
        f"Mesh processing completed with quality {best_quality.overall_score:.1f}/10 "
        f"(below threshold {min_quality})"
    )
    return best_bytes, best_quality
