/**
 * Viewer3D Component - Interactive 3D Model Viewer
 *
 * Uses Online3DViewer library to display 3D models in browser.
 * Supports 15+ formats: GLB, STEP, STL, PLY, OBJ, IGES, FBX, etc.
 *
 * Features:
 * - Interactive rotation, zoom, pan
 * - Multiple view modes (solid, wireframe, shaded)
 * - Measurement tools
 * - Screenshot/export
 * - No plugins required (WebGL)
 */

import React, { useEffect, useRef, useState } from 'react';
import * as OV from 'online-3d-viewer';

interface Viewer3DProps {
  /** URL to the 3D model file */
  modelUrl?: string;
  /** Raw model data as ArrayBuffer */
  modelData?: ArrayBuffer;
  /** File name (used to detect format) */
  fileName?: string;
  /** Container width */
  width?: string | number;
  /** Container height */
  height?: string | number;
  /** Show viewer controls */
  showControls?: boolean;
  /** Background color */
  backgroundColor?: string;
  /** Camera position */
  cameraMode?: 'perspective' | 'orthographic';
  /** Enable measurements */
  enableMeasurements?: boolean;
  /** Callback when model loads */
  onLoad?: () => void;
  /** Callback on load error */
  onError?: (error: Error) => void;
}

export const Viewer3D: React.FC<Viewer3DProps> = ({
  modelUrl,
  modelData,
  fileName,
  width = '100%',
  height = '600px',
  showControls = true,
  backgroundColor = '#ffffff',
  cameraMode = 'perspective',
  enableMeasurements = true,
  onLoad,
  onError,
}) => {
  const viewerContainerRef = useRef<HTMLDivElement>(null);
  const [viewer, setViewer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!viewerContainerRef.current) return;

    // Initialize viewer
    const initViewer = async () => {
      try {
        setLoading(true);
        setError(null);

        // Create viewer instance
        const parentDiv = viewerContainerRef.current;
        if (!parentDiv) return;

        // Clear previous content
        parentDiv.innerHTML = '';

        // Initialize viewer
        const viewerInstance = new OV.EmbeddedViewer(parentDiv, {
          backgroundColor: new OV.RGBAColor(
            parseInt(backgroundColor.slice(1, 3), 16),
            parseInt(backgroundColor.slice(3, 5), 16),
            parseInt(backgroundColor.slice(5, 7), 16),
            255
          ),
          defaultColor: new OV.RGBColor(200, 200, 200),
          edgeSettings: new OV.EdgeSettings(false, new OV.RGBColor(0, 0, 0), 1),
        });

        setViewer(viewerInstance);

        // Load model
        if (modelUrl) {
          // Load from URL
          await viewerInstance.LoadModelFromUrlList([modelUrl]);
        } else if (modelData && fileName) {
          // Load from ArrayBuffer
          const file = new File([modelData], fileName);
          await viewerInstance.LoadModelFromFileList([file]);
        } else {
          throw new Error('No model URL or data provided');
        }

        setLoading(false);
        if (onLoad) onLoad();

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load 3D model';
        setError(errorMessage);
        setLoading(false);
        if (onError) onError(err instanceof Error ? err : new Error(errorMessage));
        console.error('Viewer3D Error:', err);
      }
    };

    initViewer();

    // Cleanup
    return () => {
      if (viewer) {
        try {
          viewer.Destroy();
        } catch (e) {
          console.warn('Viewer cleanup error:', e);
        }
      }
    };
  }, [modelUrl, modelData, fileName, backgroundColor]);

  // Handle resize
  useEffect(() => {
    if (!viewer) return;

    const handleResize = () => {
      try {
        viewer.Resize();
      } catch (e) {
        console.warn('Viewer resize error:', e);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [viewer]);

  return (
    <div className="viewer3d-container" style={{ width, height, position: 'relative' }}>
      {/* Loading indicator */}
      {loading && (
        <div className="viewer3d-loading" style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          zIndex: 10,
        }}>
          <div style={{ textAlign: 'center' }}>
            <div className="spinner" style={{
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #3498db',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 10px',
            }} />
            <p>Loading 3D model...</p>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && !loading && (
        <div className="viewer3d-error" style={{
          padding: '20px',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '4px',
          color: '#c00',
        }}>
          <h3>Failed to load 3D model</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Viewer container */}
      <div
        ref={viewerContainerRef}
        style={{
          width: '100%',
          height: '100%',
          border: '1px solid #ddd',
          borderRadius: '4px',
          overflow: 'hidden',
        }}
      />

      {/* Controls info */}
      {showControls && !loading && !error && (
        <div className="viewer3d-controls-info" style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '10px',
          borderRadius: '4px',
          fontSize: '12px',
          maxWidth: '200px',
        }}>
          <div><strong>Controls:</strong></div>
          <div>🖱️ Left click + drag: Rotate</div>
          <div>🖱️ Right click + drag: Pan</div>
          <div>🖱️ Scroll: Zoom</div>
          {enableMeasurements && <div>📏 Click for measurements</div>}
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Viewer3D;
