
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Job, JobStatus as StatusEnum } from '../types';
import { CheckCircle2, Download, AlertCircle, RefreshCw, Cpu, Box, Eye } from 'lucide-react';

interface JobStatusProps {
  jobId: string;
  initialJob?: Job;
  onReset: () => void;
}

const JobStatusComponent: React.FC<JobStatusProps> = ({ jobId, initialJob, onReset }) => {
  const { t } = useTranslation();
  // Use initialJob if provided, otherwise create placeholder
  const [job, setJob] = useState<Job>(initialJob || {
    job_id: jobId,
    type: 'cad',
    name: 'Processing Job',
    status: StatusEnum.PENDING,
    progress: 0,
    conversion_mode: undefined as any,
    date: new Date().toISOString()
  });
  
  const [log, setLog] = useState<string>("status_pending");

  useEffect(() => {
    // If props update (e.g. polling updates the object passed in), update state
    if (initialJob) {
      setJob(initialJob);
      
      if (initialJob.status === StatusEnum.COMPLETED) setLog("status_completed");
      else if (initialJob.status === StatusEnum.FAILED) setLog("status_failed");
      else if (initialJob.status === StatusEnum.CANCELLED) setLog("status_cancelled");
      else if (initialJob.status === StatusEnum.PROCESSING) setLog("status_processing");
      else setLog("status_pending");
      
      return;
    }
  }, [initialJob]);

  useEffect(() => {
    // Simulation Logic: Only run if we don't have a real initialJob passed in
    // AND the job isn't already in a terminal state
    if (initialJob) return;
    
    if (job.status === StatusEnum.COMPLETED || job.status === StatusEnum.FAILED || job.status === StatusEnum.CANCELLED) return;

    let timer: ReturnType<typeof setTimeout>;
    
    const steps = [
      { status: StatusEnum.PROCESSING, progress: 10, log: 'processing_step_1', time: 1000 },
      { status: StatusEnum.PROCESSING, progress: 45, log: 'processing_step_2', time: 2500 },
      { status: StatusEnum.PROCESSING, progress: 80, log: 'processing_step_3', time: 4500 },
      { status: StatusEnum.COMPLETED, progress: 100, log: 'status_completed', time: 6000 },
    ];

    let currentStepIndex = 0;

    const processNextStep = () => {
      if (currentStepIndex < steps.length) {
        const step = steps[currentStepIndex];
        
        timer = setTimeout(() => {
          setJob(prev => ({
            ...prev,
            status: step.status,
            progress: step.progress,
            download_url: step.status === StatusEnum.COMPLETED ? "#download-link-mock" : undefined
          }));
          setLog(step.log);
          currentStepIndex++;
          processNextStep();
        }, step.time - (steps[currentStepIndex - 1]?.time || 0));
      }
    };

    processNextStep();

    return () => clearTimeout(timer);
  }, [jobId, initialJob]);

  const isProcessing = job.status === StatusEnum.PROCESSING || job.status === StatusEnum.PENDING;
  const isCompleted = job.status === StatusEnum.COMPLETED;

  return (
    <div className="max-w-3xl mx-auto animate-fade-in-up">
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
              ${job.status === StatusEnum.FAILED || job.status === StatusEnum.CANCELLED ? 'bg-red-50 dark:bg-red-900/20 text-red-500' : ''}
            `}>
               {isProcessing && <Cpu size={24} className="animate-pulse" />}
               {isCompleted && <CheckCircle2 size={28} />}
               {(job.status === StatusEnum.FAILED || job.status === StatusEnum.CANCELLED) && <AlertCircle size={28} />}
            </div>
            <div>
              <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {isCompleted ? t('common.status_completed') : job.status === StatusEnum.CANCELLED ? t('common.status_cancelled') : job.status === StatusEnum.FAILED ? t('common.status_failed') : t('common.status_processing')}
              </h2>
              <p className="text-xs font-mono text-slate-400 dark:text-slate-500 uppercase tracking-wider mt-1">
                ID: <span className="select-all">{jobId.slice(0, 8)}</span>
              </p>
            </div>
          </div>
          
          {/* Detail Toggle (Optional) */}
          {initialJob && (
             <button onClick={onReset} className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
                <Eye size={20} />
             </button>
          )}
        </div>

        {/* Body */}
        <div className="p-8 relative z-10">
          
          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex justify-between items-end mb-3">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
                {isProcessing && <span className="block w-2 h-2 bg-primary-500 rounded-full animate-ping" />}
                {t(`common.${log}`) || log}
              </span>
              <span className="text-3xl font-black text-slate-200 dark:text-slate-700">{job.progress}%</span>
            </div>
            <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-700 ease-out relative
                  ${isCompleted ? 'bg-green-500' : 'bg-primary-500'}
                  ${job.status === StatusEnum.FAILED || job.status === StatusEnum.CANCELLED ? 'bg-red-500' : ''}
                `}
                style={{ width: `${job.progress}%` }}
              >
                {isProcessing && <div className="absolute inset-0 bg-white/30 w-full h-full animate-[shimmer_1s_infinite] -skew-x-12" />}
              </div>
            </div>
          </div>

          {/* Preview Area */}
          <div className="aspect-[21/9] bg-slate-50 dark:bg-black/40 rounded-2xl border border-slate-200 dark:border-slate-800 flex items-center justify-center relative overflow-hidden group shadow-inner">
             <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-800 opacity-20" />
             
             {isCompleted ? (
               <div className="text-center z-10 animate-fade-in">
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
                 <p className="text-xs font-mono uppercase tracking-widest opacity-70">
                    {job.status === StatusEnum.FAILED ? t('common.status_failed') : 
                     job.status === StatusEnum.CANCELLED ? t('common.status_cancelled') : 
                     "Rendering"}
                 </p>
               </div>
             )}
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            {isCompleted && (
              <button className="flex-1 flex items-center justify-center space-x-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-6 py-4 rounded-xl font-bold shadow-xl hover:scale-[1.02] transition-all">
                <Download size={20} />
                <span>{t('common.download_btn')}</span>
              </button>
            )}
            
            {(isCompleted || job.status === StatusEnum.FAILED || job.status === StatusEnum.CANCELLED) && (
              <button 
                onClick={onReset}
                className="flex items-center justify-center space-x-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 px-6 py-4 rounded-xl font-bold transition-colors"
              >
                <RefreshCw size={18} />
                <span>{t('common.start_new')}</span>
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};

export default JobStatusComponent;
