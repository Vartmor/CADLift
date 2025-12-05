import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import UploadForm from '../components/UploadForm';
import JobStatusComponent from '../components/JobStatus';
import { UploadFormData, ConversionMode, JobStatus as JobState } from '../types';
import { jobService, JobRecord } from '../services/jobService';
import { useJobHistory } from '../hooks/useJobHistory';
import QuickStart from '../components/QuickStart';
import ImageWorkflowForm from '../components/ImageWorkflowForm';
import PromptWorkflowForm from '../components/PromptWorkflowForm';
import OnboardingTips from '../components/OnboardingTips';
import {
  ArrowRight,
  Layers3,
  Image as ImageIcon,
  MessageSquare,
  Download,
  Eye,
  RefreshCw,
  BookOpen,
  PlayCircle,
  HelpCircle,
  LifeBuoy,
  Terminal,
  Sparkles,
  CircleDot,
  ClipboardList,
  FileText,
} from 'lucide-react';

type WorkflowTab = 'dxf' | 'image' | 'prompt';

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [presetMode, setPresetMode] = useState<ConversionMode | null>(null);
  const [presetModeSignal, setPresetModeSignal] = useState(0);
  const uploadSectionRef = useRef<HTMLDivElement>(null);
  const jobStatusRef = useRef<HTMLDivElement>(null);
  const { jobs: jobHistory } = useJobHistory();
  const [activeTab, setActiveTab] = useState<WorkflowTab>('prompt');
  const [submitProgress, setSubmitProgress] = useState<number | null>(null);
  const [quickStartOpen, setQuickStartOpen] = useState(false);
  const [showTips, setShowTips] = useState(() => {
    if (typeof window === 'undefined') return true;
    return window.localStorage.getItem('cadlift_tips_dismissed') !== 'true';
  });

  const handleLaunchWorkspace = (mode?: ConversionMode) => {
    if (mode) {
      setPresetMode(mode);
      setPresetModeSignal((prev) => prev + 1);
    }
    if (uploadSectionRef.current) {
      uploadSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handler = (event: KeyboardEvent) => {
      const key = event.key.toLowerCase();
      if (event.ctrlKey && key === 'u') {
        event.preventDefault();
        handleLaunchWorkspace();
      }
      if (event.ctrlKey && key === 'l') {
        event.preventDefault();
        handleLaunchWorkspace(ConversionMode.MECHANICAL);
      }
      if (event.ctrlKey && key === 'i') {
        event.preventDefault();
        setActiveTab('image');
        handleLaunchWorkspace();
      }
      if (event.ctrlKey && key === 'p') {
        event.preventDefault();
        setActiveTab('prompt');
        handleLaunchWorkspace();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const dismissTips = () => {
    setShowTips(false);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('cadlift_tips_dismissed', 'true');
    }
  };

  const heroStats = useMemo(() => {
    const completedJobs = jobHistory.filter((job) => job.status === JobState.COMPLETED);
    const avgSeconds = completedJobs.length
      ? Math.max(
        1,
        Math.round(
          completedJobs.reduce((acc, job) => acc + ((job.completedAt ?? job.updatedAt) - job.createdAt), 0) /
          completedJobs.length /
          1000
        )
      )
      : 12;
    const detectionRate = jobHistory.length
      ? Math.min(99, Math.round((completedJobs.length / jobHistory.length) * 100))
      : 0;

    return [
      { label: t('dashboard.hero.statUploads'), value: jobHistory.length.toString() },
      { label: t('dashboard.hero.statTime'), value: `${avgSeconds}s` },
      { label: t('dashboard.hero.statAccuracy'), value: `${detectionRate}%` },
    ];
  }, [jobHistory, t]);

  const conversionCards = useMemo(() => ([
    {
      id: 'cad',
      title: t('dashboard.modes.cad.title'),
      description: t('dashboard.modes.cad.description'),
      tag: t('dashboard.modes.cad.badge'),
      icon: <Layers3 className="w-8 h-8" />,
      gradient: 'from-primary-500 to-blue-500',
      cta: t('dashboard.modes.cad.cta'),
      action: () => handleLaunchWorkspace(ConversionMode.FLOOR_PLAN),
      comingSoon: false,
      extra: (
        <div className="flex flex-wrap gap-2">
          {['DXF', 'DWG'].map((format) => (
            <span key={format} className="px-3 py-1 rounded-full text-xs font-semibold bg-white/20 text-white/90 border border-white/30">
              {format}
            </span>
          ))}
        </div>
      ),
    },
    {
      id: 'image',
      title: t('dashboard.modes.image.title'),
      description: t('dashboard.modes.image.description'),
      tag: t('dashboard.modes.betaLabel'),
      icon: <ImageIcon className="w-8 h-8" />,
      gradient: 'from-purple-500 to-pink-500',
      cta: t('dashboard.modes.image.cta'),
      action: () => { setActiveTab('image'); handleLaunchWorkspace(); },
      comingSoon: false,
      extra: (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase tracking-widest text-white/70">{t('dashboard.modes.image.optionsLabel')}</p>
          <div className="flex flex-wrap gap-2">
            {[t('dashboard.modes.image.option2d'), t('dashboard.modes.image.option3d')].map((option) => (
              <span key={option} className="px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white/90 border border-white/20">
                {option}
              </span>
            ))}
          </div>
        </div>
      ),
    },
    {
      id: 'prompt',
      title: t('dashboard.modes.prompt.title'),
      description: t('dashboard.modes.prompt.description'),
      tag: t('dashboard.modes.betaLabel'),
      icon: <MessageSquare className="w-8 h-8" />,
      gradient: 'from-amber-500 to-orange-500',
      cta: t('dashboard.modes.prompt.cta'),
      action: () => { setActiveTab('prompt'); handleLaunchWorkspace(); },
      comingSoon: false,
      extra: (
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-widest text-white/70">{t('dashboard.modes.prompt.examplesLabel')}</p>
          {[t('dashboard.modes.prompt.exampleOne'), t('dashboard.modes.prompt.exampleTwo')].map((example) => (
            <div key={example} className="flex items-center gap-2 text-white/80 text-sm bg-white/10 rounded-xl px-3 py-2">
              <CircleDot className="w-3 h-3" />
              <span>{example}</span>
            </div>
          ))}
        </div>
      ),
    }
  ]), [t]);

  const recentJobs = useMemo<JobRecord[]>(() => jobHistory.slice(0, 4), [jobHistory]);

  const quickLinks = useMemo(() => ([
    {
      id: 'docs',
      title: t('dashboard.quickLinks.documentation.title'),
      description: t('dashboard.quickLinks.documentation.description'),
      icon: <BookOpen className="w-5 h-5 text-primary-500" />,
      href: 'http://localhost:8000/docs',
    },
    {
      id: 'tutorials',
      title: t('dashboard.quickLinks.tutorials.title'),
      description: t('dashboard.quickLinks.tutorials.description'),
      icon: <PlayCircle className="w-5 h-5 text-purple-500" />,
      href: '/resources#videos',
    },
    {
      id: 'faq',
      title: t('dashboard.quickLinks.faq.title'),
      description: t('dashboard.quickLinks.faq.description'),
      icon: <HelpCircle className="w-5 h-5 text-amber-500" />,
      href: '/resources#faq',
    },
    {
      id: 'support',
      title: t('dashboard.quickLinks.support.title'),
      description: t('dashboard.quickLinks.support.description'),
      icon: <LifeBuoy className="w-5 h-5 text-blue-500" />,
      href: '/resources#community',
    },
  ]), [t]);

  const statusStyles: Record<JobState, { bg: string; dot: string; text: string }> = {
    [JobState.COMPLETED]: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      dot: 'bg-green-500',
      text: 'text-green-600 dark:text-green-400'
    },
    [JobState.PROCESSING]: {
      bg: 'bg-amber-50 dark:bg-amber-900/20',
      dot: 'bg-amber-500',
      text: 'text-amber-600 dark:text-amber-400'
    },
    [JobState.PENDING]: {
      bg: 'bg-slate-100 dark:bg-slate-800/60',
      dot: 'bg-slate-400',
      text: 'text-slate-600 dark:text-slate-300'
    },
    [JobState.FAILED]: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      dot: 'bg-red-500',
      text: 'text-red-600 dark:text-red-400'
    },
    [JobState.QUEUED]: {
      bg: 'bg-slate-50 dark:bg-slate-800/40',
      dot: 'bg-slate-400',
      text: 'text-slate-600 dark:text-slate-300'
    },
  };

  const statusLabels: Record<JobState, string> = {
    [JobState.COMPLETED]: t('common.status_completed'),
    [JobState.PROCESSING]: t('common.status_processing'),
    [JobState.PENDING]: t('common.status_pending'),
    [JobState.FAILED]: t('common.status_failed'),
    [JobState.QUEUED]: t('common.status_queued'),
  };

  const jobIntentLabel = (job: JobRecord) => {
    if (job.intent === 'image') return t('dashboard.modes.image.title');
    if (job.intent === 'prompt') return t('dashboard.modes.prompt.title');
    return t('dashboard.modes.cad.title');
  };

  const jobInputPreview = (job: JobRecord) => {
    const prompt = job.metadata && typeof job.metadata.prompt === 'string' ? job.metadata.prompt : null;
    if (prompt) {
      return `"${prompt.slice(0, 24)}${prompt.length > 24 ? '…' : ''}"`;
    }
    return job.inputName;
  };

  const jobModeLabel = (job: JobRecord) => {
    switch (job.mode) {
      case ConversionMode.FLOOR_PLAN:
        return t('common.mode_floor');
      case ConversionMode.MECHANICAL:
        return t('common.mode_mech');
      case ConversionMode.IMAGE_TO_2D:
        return t('dashboard.imageForm.option2d.title');
      case ConversionMode.IMAGE_TO_3D:
        return t('dashboard.imageForm.option3d.title');
      case ConversionMode.PROMPT_TO_2D:
        return t('dashboard.promptForm.option2d.title');
      case ConversionMode.PROMPT_TO_3D:
        return t('dashboard.promptForm.option3d.title');
      default:
        return '';
    }
  };

  const handleJobSubmit = async (formData: UploadFormData) => {
    const job = await jobService.createJob(formData);
    setCurrentJobId(job.job_id);
    setPresetMode(null);
    setQuickStartOpen(false);
    setSubmitProgress(0);
    if (jobStatusRef.current) {
      jobStatusRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const resetJob = () => {
    setCurrentJobId(null);
  };

  const renderActions = (job: JobRecord) => {
    if (job.status === JobState.COMPLETED) {
      const glbUrl = job.glb_download_url;
      const dxfUrl = job.dxf_download_url || job.download_url;
      const stepUrl = job.step_download_url;

      return (
        <div className="flex items-center gap-2 flex-wrap">
          {/* View 3D button */}
          {glbUrl && (
            <button
              onClick={() => {
                setCurrentJobId(job.job_id);
                if (jobStatusRef.current) {
                  jobStatusRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              }}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors"
              title="View in 3D"
            >
              <Eye size={14} />
              3D
            </button>
          )}
          {/* Download buttons */}
          {glbUrl && (
            <a
              href={glbUrl}
              download
              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors"
              title="Download GLB"
            >
              <Download size={14} />
              GLB
            </a>
          )}
          {dxfUrl && (
            <a
              href={dxfUrl}
              download
              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
              title="Download DXF"
            >
              <Download size={14} />
              DXF
            </a>
          )}
          {stepUrl && (
            <a
              href={stepUrl}
              download
              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/50 transition-colors"
              title="Download STEP"
            >
              <Download size={14} />
              STEP
            </a>
          )}
        </div>
      );
    }
    if (job.status === JobState.FAILED) {
      return (
        <button
          type="button"
          className="flex items-center gap-1 text-sm font-semibold text-red-500 hover:text-red-400 transition-colors"
        >
          <RefreshCw size={16} />
          {t('dashboard.recent.action.retry')}
        </button>
      );
    }
    // Processing/Pending - show progress
    const progress = (job as JobRecord & { progress?: number }).progress ?? 0;
    return (
      <div className="flex items-center gap-2">
        <div className="w-20 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-slate-500">{progress}%</span>
      </div>
    );
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleString(undefined, {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="w-full max-w-7xl mx-auto space-y-10 animate-fade-in">
      <section className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70 backdrop-blur p-6 sm:p-8 shadow-xl">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-xs font-semibold uppercase tracking-[0.3em] text-slate-600 dark:text-slate-300">
              <ClipboardList size={14} />
              <span>{t('dashboard.workspace.title')}</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-black leading-tight text-slate-900 dark:text-white">
              {t('dashboard.hero.title')}
            </h1>
            <p className="text-base md:text-lg text-slate-600 dark:text-slate-300 max-w-3xl">
              {t('dashboard.hero.subtitle')}
            </p>
          </div>
          <div className="flex flex-wrap gap-3 justify-start md:justify-end">
            {heroStats.map((stat) => (
              <div key={stat.label} className="min-w-[140px] rounded-2xl bg-white/90 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 shadow-sm p-4">
                <p className="text-3xl font-black text-slate-900 dark:text-white">{stat.value}</p>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start" ref={uploadSectionRef}>
        <div className="lg:col-span-2 space-y-4">
          {/* Section Header */}
          <div className="flex flex-col gap-1">
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-primary-500">{t('dashboard.workspace.title')}</p>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white">Choose Your Workflow</h2>
          </div>

          <div className="rounded-3xl border border-slate-200/50 dark:border-slate-700/50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl shadow-2xl shadow-slate-200/30 dark:shadow-black/30 overflow-hidden">
            {/* Creative Tab Navigation */}
            <div className="p-2 bg-slate-100 dark:bg-slate-800">
              <div className="flex gap-2">
                <button
                  onClick={() => { setActiveTab('dxf'); setCurrentJobId(null); }}
                  className={`flex-1 flex items-center justify-center gap-3 px-4 py-4 rounded-2xl text-sm font-bold transition-all duration-300 ${activeTab === 'dxf'
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30 scale-[1.02]'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-white/80 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
                    }`}
                >
                  <div className={`p-2 rounded-xl ${activeTab === 'dxf' ? 'bg-white/20' : 'bg-slate-200 dark:bg-slate-600'}`}>
                    <FileText size={18} />
                  </div>
                  <span className="hidden sm:inline">DXF to 3D</span>
                  <span className="sm:hidden">DXF</span>
                </button>
                <button
                  onClick={() => { setActiveTab('image'); setCurrentJobId(null); }}
                  className={`flex-1 flex items-center justify-center gap-3 px-4 py-4 rounded-2xl text-sm font-bold transition-all duration-300 ${activeTab === 'image'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30 scale-[1.02]'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-white/80 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
                    }`}
                >
                  <div className={`p-2 rounded-xl ${activeTab === 'image' ? 'bg-white/20' : 'bg-slate-200 dark:bg-slate-600'}`}>
                    <ImageIcon size={18} />
                  </div>
                  <span className="hidden sm:inline">Image to 3D</span>
                  <span className="sm:hidden">Image</span>
                </button>
                <button
                  onClick={() => { setActiveTab('prompt'); setCurrentJobId(null); }}
                  className={`flex-1 flex items-center justify-center gap-3 px-4 py-4 rounded-2xl text-sm font-bold transition-all duration-300 ${activeTab === 'prompt'
                    ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/30 scale-[1.02]'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-white/80 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
                    }`}
                >
                  <div className={`p-2 rounded-xl ${activeTab === 'prompt' ? 'bg-white/20' : 'bg-slate-200 dark:bg-slate-600'}`}>
                    <Sparkles size={18} />
                  </div>
                  <span className="hidden sm:inline">Prompt to 3D</span>
                  <span className="sm:hidden">AI</span>
                </button>
              </div>
            </div>

            {/* Solid accent line under active tab */}
            <div className={`h-1 transition-all duration-500 ${activeTab === 'dxf' ? 'bg-purple-600' :
              activeTab === 'image' ? 'bg-blue-600' :
                'bg-orange-500'
              }`} />

            {/* Content Area */}
            <div className="p-6 min-h-[520px]">
              {currentJobId ? (
                <div className="w-full" ref={jobStatusRef}>
                  <JobStatusComponent jobId={currentJobId} onReset={resetJob} />
                </div>
              ) : (
                <div className="w-full animate-fade-in-up">
                  {activeTab === 'dxf' && (
                    <UploadForm onSubmit={handleJobSubmit} presetMode={presetMode} presetModeSignal={presetModeSignal} />
                  )}
                  {activeTab === 'image' && (
                    <ImageWorkflowForm onCreate={handleJobSubmit} />
                  )}
                  {activeTab === 'prompt' && (
                    <PromptWorkflowForm onCreate={handleJobSubmit} />
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="lg:col-span-1 space-y-4">
          {showTips && <OnboardingTips onDismiss={dismissTips} />}



          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/85 dark:bg-slate-900/70 backdrop-blur p-5 shadow-md space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold uppercase tracking-[0.3em] text-primary-500">{t('dashboard.modes.title')}</p>
            </div>
            <div className="space-y-3">
              {conversionCards.map((card) => (
                <div key={card.id} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-gradient-to-br from-white/90 via-white to-white/90 dark:from-slate-900/80 dark:via-slate-900/70 dark:to-slate-900/80 p-4 shadow-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-white ${card.id === 'cad' ? 'bg-primary-500' : card.id === 'image' ? 'bg-purple-500' : 'bg-amber-500'}`}>
                        {card.icon}
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">{card.tag}</p>
                        <h4 className="text-base font-bold text-slate-900 dark:text-white">{card.title}</h4>
                        <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-3">{card.description}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={card.comingSoon ? undefined : card.action}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:-translate-y-0.5 transition-transform disabled:opacity-60"
                      disabled={card.comingSoon}
                    >
                      {card.comingSoon ? t('dashboard.modes.comingSoon') : card.cta}
                      {!card.comingSoon && <ArrowRight size={14} />}
                    </button>
                  </div>
                  {card.extra && <div className="mt-3">{card.extra}</div>}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="activity" className="space-y-6">
        <div className="flex flex-col gap-2">
          <p className="text-xs font-bold uppercase tracking-[0.4em] text-primary-500">{t('dashboard.recent.title')}</p>
          <h2 className="text-3xl font-black text-slate-900 dark:text-white">{t('dashboard.recent.subtitle')}</h2>
        </div>
        <div className="overflow-hidden rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70 backdrop-blur">
          <div className="hidden md:grid grid-cols-12 px-6 py-4 text-xs font-semibold uppercase tracking-widest text-slate-400 border-b border-slate-200 dark:border-slate-800">
            <div className="col-span-3">{t('dashboard.recent.table.type')}</div>
            <div className="col-span-2">{t('dashboard.recent.table.input')}</div>
            <div className="col-span-2">{t('dashboard.recent.table.output')}</div>
            <div className="col-span-2">{t('dashboard.recent.table.status')}</div>
            <div className="col-span-2">{t('dashboard.recent.table.created')}</div>
            <div className="col-span-1 text-right">{t('dashboard.recent.table.actions')}</div>
          </div>

          {recentJobs.length === 0 ? (
            <div className="p-6 text-center text-slate-500">{t('dashboard.recent.empty')}</div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {recentJobs.map((job) => (
                <div key={job.job_id} className="grid grid-cols-1 md:grid-cols-12 gap-4 px-6 py-4 items-center">
                  <div className="md:col-span-3">
                    <p className="font-semibold text-slate-900 dark:text-white">{jobIntentLabel(job)}</p>
                    <p className="text-xs text-slate-500">{jobModeLabel(job)}</p>
                    <p className="text-xs text-slate-400">{job.job_id}</p>
                  </div>
                  <div className="md:col-span-2 text-sm font-mono text-slate-600 dark:text-slate-300">{jobInputPreview(job)}</div>
                  <div className="md:col-span-2 text-sm font-mono text-slate-600 dark:text-slate-300">{job.outputName ?? '--'}</div>
                  <div className="md:col-span-2">
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${statusStyles[job.status].bg} ${statusStyles[job.status].text}`}>
                      <span className={`w-2 h-2 rounded-full ${statusStyles[job.status].dot} animate-pulse`} />
                      {statusLabels[job.status]}
                    </div>
                  </div>
                  <div className="md:col-span-2 text-sm text-slate-500">{formatTimestamp(job.createdAt)}</div>
                  <div className="md:col-span-1 md:text-right">{renderActions(job)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      <section id="resources" className="space-y-6">
        <div className="flex flex-col gap-2">
          <p className="text-xs font-bold uppercase tracking-[0.4em] text-primary-500">{t('dashboard.quickLinks.title')}</p>
          <h2 className="text-3xl font-black text-slate-900 dark:text-white">{t('dashboard.quickLinks.subtitle')}</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickLinks.map((link) => (
            <a
              key={link.id}
              href={link.href}
              target={link.href?.startsWith('http') ? '_blank' : undefined}
              rel="noreferrer"
              className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur flex items-start gap-4 hover:-translate-y-1 transition-transform shadow-sm"
            >
              <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                {link.icon}
              </div>
              <div>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{link.title}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">{link.description}</p>
              </div>
            </a>
          ))}
        </div>
      </section>

      <QuickStart
        onCad={() => { setActiveTab('dxf'); handleLaunchWorkspace(); }}
        onImage={() => {
          setActiveTab('image');
          handleLaunchWorkspace();
          setQuickStartOpen(false);
        }}
        onPrompt={() => {
          setActiveTab('prompt');
          handleLaunchWorkspace();
          setQuickStartOpen(false);
        }}
        isOpen={quickStartOpen}
        toggle={() => setQuickStartOpen((prev) => !prev)}
      />


    </div>
  );
};

export default Dashboard;
