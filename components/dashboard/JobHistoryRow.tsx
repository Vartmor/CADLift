import React from 'react';
import { Download, RefreshCw, Eye } from 'lucide-react';
import { JobStatus } from '../../types';
import { JobRecord } from '../../services/jobService';

interface StatusStyle {
    bg: string;
    dot: string;
    text: string;
}

const statusStyles: Record<JobStatus, StatusStyle> = {
    [JobStatus.COMPLETED]: {
        bg: 'bg-green-50 dark:bg-green-900/20',
        dot: 'bg-green-500',
        text: 'text-green-600 dark:text-green-400',
    },
    [JobStatus.PROCESSING]: {
        bg: 'bg-amber-50 dark:bg-amber-900/20',
        dot: 'bg-amber-500',
        text: 'text-amber-600 dark:text-amber-400',
    },
    [JobStatus.PENDING]: {
        bg: 'bg-slate-100 dark:bg-slate-800/60',
        dot: 'bg-slate-400',
        text: 'text-slate-600 dark:text-slate-300',
    },
    [JobStatus.FAILED]: {
        bg: 'bg-red-50 dark:bg-red-900/20',
        dot: 'bg-red-500',
        text: 'text-red-600 dark:text-red-400',
    },
    [JobStatus.QUEUED]: {
        bg: 'bg-slate-50 dark:bg-slate-800/40',
        dot: 'bg-slate-400',
        text: 'text-slate-600 dark:text-slate-300',
    },
};

interface JobHistoryRowProps {
    job: JobRecord;
    intentLabel: string;
    modeLabel: string;
    statusLabel: string;
    inputPreview: string;
    timestamp: string;
    actionLabels: {
        download: string;
        retry: string;
        view: string;
    };
    onRetry?: () => void;
    onView?: () => void;
}

const JobHistoryRow: React.FC<JobHistoryRowProps> = ({
    job,
    intentLabel,
    modeLabel,
    statusLabel,
    inputPreview,
    timestamp,
    actionLabels,
    onRetry,
    onView,
}) => {
    const style = statusStyles[job.status];

    const renderAction = () => {
        if (job.status === JobStatus.COMPLETED && job.download_url) {
            return (
                <a
                    href={job.download_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-sm font-semibold text-slate-900 dark:text-white hover:text-primary-500 transition-colors"
                >
                    <Download size={16} />
                    {actionLabels.download}
                </a>
            );
        }
        if (job.status === JobStatus.FAILED) {
            return (
                <button
                    type="button"
                    onClick={onRetry}
                    className="flex items-center gap-1 text-sm font-semibold text-red-500 hover:text-red-400 transition-colors"
                >
                    <RefreshCw size={16} />
                    {actionLabels.retry}
                </button>
            );
        }
        return (
            <button
                type="button"
                onClick={onView}
                className="flex items-center gap-1 text-sm font-semibold text-slate-500 hover:text-primary-500 transition-colors"
            >
                <Eye size={16} />
                {actionLabels.view}
            </button>
        );
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
            <div className="md:col-span-3">
                <p className="font-semibold text-slate-900 dark:text-white">{intentLabel}</p>
                <p className="text-xs text-slate-500">{modeLabel}</p>
                <p className="text-xs text-slate-400 font-mono">{job.job_id.slice(0, 12)}...</p>
            </div>
            <div className="md:col-span-2 text-sm font-mono text-slate-600 dark:text-slate-300 truncate" title={inputPreview}>
                {inputPreview}
            </div>
            <div className="md:col-span-2 text-sm font-mono text-slate-600 dark:text-slate-300">
                {job.outputName ?? '--'}
            </div>
            <div className="md:col-span-2">
                <div
                    className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${style.bg} ${style.text}`}
                >
                    <span className={`w-2 h-2 rounded-full ${style.dot} animate-pulse`} />
                    {statusLabel}
                </div>
            </div>
            <div className="md:col-span-2 text-sm text-slate-500">{timestamp}</div>
            <div className="md:col-span-1 md:text-right">{renderAction()}</div>
        </div>
    );
};

export default JobHistoryRow;
