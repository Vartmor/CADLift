/**
 * Viewer3DModal Component - Full-screen 3D Model Viewer Modal
 *
 * Provides a modal dialog for viewing 3D models with controls.
 * Perfect for "View in 3D" buttons on generated models.
 */

import React, { useState } from 'react';
import Viewer3D from './Viewer3D';
import { X, Download, Maximize2, Minimize2, Camera } from 'lucide-react';

interface Viewer3DModalProps {
  /** Is modal open */
  isOpen: boolean;
  /** Close callback */
  onClose: () => void;
  /** Model URL */
  modelUrl?: string;
  /** Model data */
  modelData?: ArrayBuffer;
  /** File name */
  fileName?: string;
  /** Model title */
  title?: string;
  /** Download URL */
  downloadUrl?: string;
}

export const Viewer3DModal: React.FC<Viewer3DModalProps> = ({
  isOpen,
  onClose,
  modelUrl,
  modelData,
  fileName,
  title = '3D Model Viewer',
  downloadUrl,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!isOpen) return null;

  const handleDownload = () => {
    if (downloadUrl) {
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName || 'model.glb';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleScreenshot = () => {
    // TODO: Implement screenshot functionality
    alert('Screenshot feature coming soon!');
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div
      className="viewer3d-modal-overlay"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        className="viewer3d-modal-content"
        style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          width: '100%',
          maxWidth: '1400px',
          height: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="viewer3d-modal-header"
          style={{
            padding: '15px 20px',
            borderBottom: '1px solid #ddd',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#f8f9fa',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
            {title}
            {fileName && <span style={{ color: '#666', fontSize: '14px', marginLeft: '10px' }}>({fileName})</span>}
          </h2>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            {/* Download button */}
            {downloadUrl && (
              <button
                onClick={handleDownload}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                }}
                title="Download model"
              >
                <Download size={16} />
                Download
              </button>
            )}

            {/* Screenshot button */}
            <button
              onClick={handleScreenshot}
              style={{
                padding: '8px 12px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
              }}
              title="Take screenshot"
            >
              <Camera size={16} />
              Screenshot
            </button>

            {/* Fullscreen toggle */}
            <button
              onClick={toggleFullscreen}
              style={{
                padding: '8px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
              title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>

            {/* Close button */}
            <button
              onClick={onClose}
              style={{
                padding: '8px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
              title="Close viewer"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Viewer */}
        <div style={{ flex: 1, padding: '20px', backgroundColor: '#f0f0f0' }}>
          <Viewer3D
            modelUrl={modelUrl}
            modelData={modelData}
            fileName={fileName}
            width="100%"
            height="100%"
            showControls={true}
            backgroundColor="#f0f0f0"
            enableMeasurements={true}
          />
        </div>

        {/* Footer with format info */}
        <div
          className="viewer3d-modal-footer"
          style={{
            padding: '10px 20px',
            borderTop: '1px solid #ddd',
            backgroundColor: '#f8f9fa',
            fontSize: '12px',
            color: '#666',
          }}
        >
          <div style={{ display: 'flex', gap: '20px' }}>
            <div>
              <strong>Supported Formats:</strong> GLB, STEP, STL, PLY, OBJ, IGES, FBX, 3DM, 3DS, and more
            </div>
            <div>
              <strong>Powered by:</strong> Online3DViewer (WebGL)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Viewer3DModal;
