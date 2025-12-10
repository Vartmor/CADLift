import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { JobStatus as StatusEnum } from '../types';
import { CheckCircle2, Download, AlertCircle, RefreshCw, Cpu, Box, Layers, Eye, MoreVertical, Image as ImageIcon, X, XCircle } from 'lucide-react';
import { useJobPolling } from '../hooks/useJobPolling';
import { Viewer3DModal } from './Viewer3DModal';
import { jobService } from '../services/jobService';

interface JobStatusProps {
  jobId: string;
  onReset: () => void;
}

// Helper function to download file - uses fetch to get proper filename from Content-Disposition
const downloadFile = async (url: string, fallbackFilename: string) => {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Download failed: ${response.status}`);

    // Get filename from Content-Disposition header (now exposed via CORS)
    let filename = fallbackFilename;
    const contentDisposition = response.headers.get('Content-Disposition');
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^";\n]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    // Create blob and download
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  } catch (error) {
    console.error('Download error:', error);
    // Fallback to window.open if fetch fails
    window.open(url, '_blank');
  }
};


const JobStatusComponent: React.FC<JobStatusProps> = ({ jobId, onReset }) => {
  const { t } = useTranslation();
  const job = useJobPolling(jobId);
  const glbUrl = job?.glb_download_url;
  const dxfUrl = job?.dxf_download_url || job?.download_url;
  const stepUrl = job?.step_download_url;
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [showRefImage, setShowRefImage] = useState(false);
  const status = job?.status ?? StatusEnum.PENDING;
  const logKey = job?.logKey ?? 'status_pending';
  const progress = job?.progress ?? 0;
  const isProcessing = status === StatusEnum.PROCESSING || status === StatusEnum.PENDING || status === StatusEnum.QUEUED;
  const isCompleted = status === StatusEnum.COMPLETED;
  const isFailed = status === StatusEnum.FAILED;
  const isCancelled = (job as any)?.error_message === 'Job cancelled by user';
  const pipeline = job?.intent ?? 'cad';
  const [isCancelling, setIsCancelling] = useState(false);
  const statusHeadingKey = isFailed
    ? 'common.status_failed'
    : isCompleted
      ? 'common.status_completed'
      : 'common.status_processing';
  const statusHeading = t(statusHeadingKey);

  // Close 3D viewer and menu when job changes (user started a new job)
  React.useEffect(() => {
    setIsViewerOpen(false);
    setShowMenu(false);
    setShowRefImage(false);
  }, [jobId]);

  // Get reference image URL from job params/metadata
  const jobMeta = (job as any)?.metadata || (job as any)?.params || {};
  const aiMeta = jobMeta?.ai_metadata || {};
  const referenceImageId =
    aiMeta?.reference_image_file_id ||
    jobMeta?.reference_image_file_id ||
    jobMeta?.output_image_file_id;
  const referenceImageUrl = referenceImageId ? `/api/v1/files/${referenceImageId}` : null;

  // Generate filenames - use 'prompt_model' as default for prompt jobs
  const baseName = job?.outputName?.replace(/\.[^.]+$/, '') || 'prompt_model';


  return (
    <div className="max-w-2xl mx-auto mt-8 animate-fade-in-up">
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-3xl shadow-2xl shadow-slate-200/50 dark:shadow-black/50 border border-white/20 dark:border-slate-800 overflow-hidden relative">

        {/* Background decorative glow */}
        {isProcessing && (
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary-500 to-transparent animate-[shimmer_1.5s_infinite] z-20"></div>
        )}

        {/* Header */}
        <div className="p-8 border-b border-slate-100 dark:border-slate-800/60 flex items-center justify-between relative z-10">
          <div className="flex items-center space-x-4">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg transition-all duration-500
              ${isProcessing ? 'bg-slate-50 dark:bg-slate-800 text-primary-500' : ''}
              ${isCompleted ? 'bg-green-50 dark:bg-green-900/20 text-green-500' : ''}
              ${isFailed ? 'bg-red-50 dark:bg-red-900/20 text-red-500' : ''}
            `}>
              {isProcessing && <Cpu size={24} className="animate-pulse" />}
              {isCompleted && <CheckCircle2 size={28} />}
              {isFailed && <AlertCircle size={28} />}
            </div>
            <div>
              <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {statusHeading}
              </h2>
              <p className="text-xs font-mono text-slate-400 dark:text-slate-500 uppercase tracking-wider mt-1">
                ID: <span className="select-all">{jobId.slice(0, 8)}</span>
              </p>
            </div>
          </div>
          {/* More Options Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className={`p-2.5 rounded-xl border transition-all duration-200 ${showMenu
                ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-200 dark:border-primary-800 text-primary-600 dark:text-primary-400'
                : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600'
                }`}
              title="More options"
            >
              <MoreVertical size={18} />
            </button>
            {showMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 py-2 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 z-30">
                {referenceImageUrl && (
                  <button
                    onClick={() => { setShowRefImage(true); setShowMenu(false); }}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  >
                    <ImageIcon size={16} />
                    View Reference Image
                  </button>
                )}
                {!referenceImageUrl && (
                  <p className="px-4 py-2 text-sm text-slate-400 dark:text-slate-500">No options available</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Body */}
        <div className="p-8 relative z-10">

          {/* Progress Indicator - only show when processing */}
          {isProcessing && (
            <div className="mb-8">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-2">
                <span className="inline-flex items-center gap-2 border border-slate-200 dark:border-slate-700 rounded-full px-3 py-1 bg-white/60 dark:bg-slate-800/60">
                  <span className="w-2 h-2 rounded-full bg-primary-500" />
                  {pipeline.toUpperCase()} pipeline
                </span>
                {job?.outputName && (
                  <span className="font-mono truncate max-w-[160px]" title={job.outputName}>
                    {job.outputName}
                  </span>
                )}
              </div>
              <div className="flex justify-between items-end mb-3">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
                  <span className="block w-2 h-2 bg-primary-500 rounded-full animate-ping" />
                  {t(`common.${logKey}`, { defaultValue: t('common.status_processing') })}
                </span>
                <span className="text-3xl font-black text-slate-200 dark:text-slate-700">{progress}%</span>
              </div>
              <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700 ease-out relative bg-primary-500"
                  style={{ width: `${progress}%` }}
                >
                  <div className="absolute inset-0 bg-white/30 w-full h-full animate-[shimmer_1s_infinite] -skew-x-12" />
                </div>
              </div>

              {/* Cancel Button */}
              <button
                onClick={async () => {
                  setIsCancelling(true);
                  try {
                    await jobService.cancelJob(jobId);
                  } catch (e) {
                    console.error('Cancel failed:', e);
                  } finally {
                    setIsCancelling(false);
                  }
                }}
                disabled={isCancelling}
                className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors disabled:opacity-50"
              >
                <XCircle size={18} />
                <span>{isCancelling ? 'Cancelling...' : 'Cancel Job'}</span>
              </button>
            </div>
          )}

          {/* Output File Info - show when completed */}
          {isCompleted && job?.outputName && (
            <div className="mb-6 flex items-center gap-3 text-sm text-slate-600 dark:text-slate-400">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 font-mono">
                <Box size={14} />
                {job.outputName}
              </span>
              <span className="text-slate-400">•</span>
              <span>Download or view in 3D below</span>
            </div>
          )}

          {isFailed && (job?.error_code || job?.error_message) && (
            <div className="mb-6 rounded-2xl border border-red-200 bg-red-50/70 dark:border-red-900/50 dark:bg-red-900/20 px-4 py-3 text-sm text-red-700 dark:text-red-100">
              <p className="font-semibold flex items-center gap-2">
                <AlertCircle size={16} /> {job.error_code || 'Error'}
              </p>
              {job.error_message && <p className="mt-1">{job.error_message}</p>}
            </div>
          )}

          {/* Preview Area */}
          <div className="aspect-[21/9] bg-slate-50 dark:bg-black/40 rounded-2xl border border-slate-200 dark:border-slate-800 flex items-center justify-center relative overflow-hidden group shadow-inner">
            {/* Grid lines inside preview */}
            <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-800 opacity-20" />

            {isCompleted ? (
              <div className="text-center z-10 animate-fade-in">
                {/* Abstract representation of a 3D model */}
                <div className="relative w-24 h-24 mx-auto mb-2">
                  <div className="absolute inset-0 border-4 border-primary-500/30 rounded-lg transform rotate-45"></div>
                  <div className="absolute inset-0 border-4 border-primary-500/30 rounded-lg transform -rotate-12"></div>
                  <Box className="absolute inset-0 m-auto text-primary-500 w-12 h-12 drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]" />
                </div>
                <p className="text-slate-900 dark:text-white font-bold bg-white/50 dark:bg-black/50 px-4 py-1 rounded-full backdrop-blur-sm">3D Model Ready</p>
              </div>
            ) : (
              <div className="text-slate-400 flex flex-col items-center z-10">
                <div className="relative mb-3">
                  <div className="w-12 h-12 border-2 border-slate-300 dark:border-slate-700 rounded-lg animate-spin-slow" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-2 h-2 bg-slate-400 rounded-full" />
                  </div>
                </div>
                <p className="text-xs font-mono uppercase tracking-widest opacity-70">Rendering</p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col gap-4 justify-center">
            {isCompleted && (
              <>
                {/* View in 3D Button */}
                <button
                  onClick={() => setIsViewerOpen(true)}
                  disabled={!glbUrl}
                  className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-primary-500 to-cyan-500 text-white px-6 py-4 rounded-xl font-bold shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Eye size={20} />
                  <span>View in 3D</span>
                </button>

                {/* Download Buttons */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={() => dxfUrl && downloadFile(dxfUrl, `${baseName}.dxf`)}
                    disabled={!dxfUrl}
                    className="flex-1 flex items-center justify-center space-x-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-6 py-4 rounded-xl font-bold shadow-xl hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Download size={20} />
                    <span>{t('common.download_btn')} (DXF)</span>
                  </button>
                  <button
                    onClick={() => stepUrl && downloadFile(stepUrl, `${baseName}.step`)}
                    disabled={!stepUrl}
                    className="flex-1 flex items-center justify-center space-x-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-6 py-4 rounded-xl font-bold shadow-lg hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Layers size={18} />
                    <span>Download STEP</span>
                  </button>
                  <button
                    onClick={() => glbUrl && downloadFile(glbUrl, `${baseName}.glb`)}
                    disabled={!glbUrl}
                    className="flex-1 flex items-center justify-center space-x-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-6 py-4 rounded-xl font-bold shadow-lg hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Download size={18} />
                    <span>Download GLB</span>
                  </button>
                </div>
              </>
            )}

            {(isCompleted || isFailed) && (
              <a
                onClick={(e) => { e.preventDefault(); onReset(); }}
                href="#"
                className="flex items-center justify-center space-x-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 px-6 py-4 rounded-xl font-bold transition-colors"
              >
                <RefreshCw size={18} />
                <span>{t('common.start_new')}</span>
              </a>
            )}
          </div>

        </div>
      </div>

      {/* 3D Viewer Modal */}
      <Viewer3DModal
        isOpen={isViewerOpen}
        onClose={() => setIsViewerOpen(false)}
        modelUrl={glbUrl}
        fileName={(job?.outputName && job.outputName.endsWith('.glb') ? job.outputName : 'model.glb')}
        title="3D Model Viewer"
        downloadUrl={glbUrl}
      />

      {/* Reference Image Modal */}
      {showRefImage && referenceImageUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowRefImage(false)}>
          <div className="relative max-w-2xl w-full mx-4 bg-white dark:bg-slate-900 rounded-3xl shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <ImageIcon size={20} className="text-primary-500" />
                AI Reference Image
              </h3>
              <button
                onClick={() => setShowRefImage(false)}
                className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-500"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-4">
              <img
                src={referenceImageUrl}
                alt="AI-generated reference image"
                className="w-full rounded-xl shadow-lg"
              />
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400 text-center">
                This image was generated by AI and used to create the 3D model
              </p>
            </div>
            <div className="p-4 border-t border-slate-200 dark:border-slate-700 flex justify-end gap-2">
              <button
                onClick={() => downloadFile(referenceImageUrl, 'reference_image.png')}
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-xl font-semibold transition-colors"
              >
                <Download size={16} />
                Download Image
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobStatusComponent;

