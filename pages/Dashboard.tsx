import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import UploadForm from '../components/UploadForm';
import JobStatusComponent from '../components/JobStatus';
import { UploadFormData, ConversionMode, JobStatus as JobState } from '../types';
import { jobService, JobRecord } from '../services/jobService';
import { useJobHistory } from '../hooks/useJobHistory';
import QuickStart from '../components/QuickStart';
import Modal from '../components/Modal';
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
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [presetMode, setPresetMode] = useState<ConversionMode | null>(null);
  const [presetModeSignal, setPresetModeSignal] = useState(0);
  const uploadSectionRef = useRef<HTMLDivElement>(null);
  const jobStatusRef = useRef<HTMLDivElement>(null);
  const { jobs: jobHistory } = useJobHistory();
  const [showImageModal, setShowImageModal] = useState(false);
  const [showPromptModal, setShowPromptModal] = useState(false);
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
        setShowImageModal(true);
      }
      if (event.ctrlKey && key === 'p') {
        event.preventDefault();
        setShowPromptModal(true);
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
      action: () => setShowImageModal(true),
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
      action: () => setShowPromptModal(true),
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
    setShowImageModal(false);
    setShowPromptModal(false);
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
    if (job.status === JobState.COMPLETED && job.download_url) {
      return (
        <a
          href={job.download_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-sm font-semibold text-slate-900 dark:text-white hover:text-primary-500 transition-colors"
        >
          <Download size={16} />
          {t('dashboard.recent.action.download')}
        </a>
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
    return (
      <button
        type="button"
        className="flex items-center gap-1 text-sm font-semibold text-slate-500 hover:text-primary-500 transition-colors"
      >
        <Eye size={16} />
        {t('dashboard.recent.action.view')}
      </button>
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
          <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70 backdrop-blur p-6 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Terminal size={18} />
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.3em] text-primary-500">{t('dashboard.workspace.title')}</p>
                  <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">{t('dashboard.workspace.subtitle')}</h2>
                </div>
              </div>
              <div className="hidden md:flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-full font-mono">
                <Sparkles size={14} />
                <span>{t('dashboard.workspace.statusReady')}</span>
              </div>
            </div>
            <div className="min-h-[520px]">
              {!currentJobId ? (
                <div className="w-full animate-fade-in-up">
                  <UploadForm onSubmit={handleJobSubmit} presetMode={presetMode} presetModeSignal={presetModeSignal} />
                </div>
              ) : (
                <div className="w-full" ref={jobStatusRef}>
                  <JobStatusComponent jobId={currentJobId} onReset={resetJob} />
                </div>
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70 backdrop-blur p-6 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.3em] text-primary-500">{t('dashboard.recent.title')}</p>
                <h3 className="text-xl font-extrabold text-slate-900 dark:text-white">{t('dashboard.recent.subtitle')}</h3>
              </div>
              <button
                type="button"
                onClick={() => handleLaunchWorkspace()}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-sm font-semibold shadow hover:-translate-y-0.5 transition-transform"
              >
                {t('dashboard.hero.primaryCta')}
                <ArrowRight size={16} />
              </button>
            </div>
            {recentJobs.length === 0 ? (
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('dashboard.recent.empty')}</p>
            ) : (
              <div className="space-y-3">
                {recentJobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80"
                  >
                    <div className="min-w-[200px]">
                      <p className="font-semibold text-slate-900 dark:text-white">{jobIntentLabel(job)}</p>
                      <p className="text-xs text-slate-500">{jobModeLabel(job)}</p>
                      <p className="text-[11px] text-slate-400">{job.job_id}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${statusStyles[job.status].bg} ${statusStyles[job.status].text}`}>
                        <span className={`w-2 h-2 rounded-full ${statusStyles[job.status].dot} animate-pulse`} />
                        {statusLabels[job.status]}
                      </div>
                    </div>
                    <div className="text-sm text-slate-500 dark:text-slate-400">{formatTimestamp(job.createdAt)}</div>
                    <div className="flex-shrink-0">
                      {renderActions(job)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-1 space-y-4">
          {showTips && <OnboardingTips onDismiss={dismissTips} />}

          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/85 dark:bg-slate-900/70 backdrop-blur p-5 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.3em] text-primary-500">{t('dashboard.quickStart.title')}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400">{t('dashboard.quickStart.description')}</p>
              </div>
            </div>
            <div className="grid gap-2">
              <button
                type="button"
                onClick={() => handleLaunchWorkspace()}
                className="flex items-center justify-between gap-2 w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white font-semibold hover:-translate-y-0.5 transition-transform"
              >
                <span className="inline-flex items-center gap-2">
                  <Layers3 size={16} />
                  {t('dashboard.quickStart.actions.uploadCad')}
                </span>
                <ArrowRight size={16} />
              </button>
              <button
                type="button"
                onClick={() => setShowImageModal(true)}
                className="flex items-center justify-between gap-2 w-full px-4 py-3 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-200 font-semibold hover:-translate-y-0.5 transition-transform"
              >
                <span className="inline-flex items-center gap-2">
                  <ImageIcon size={16} />
                  {t('dashboard.quickStart.actions.uploadImage')}
                </span>
                <ArrowRight size={16} />
              </button>
              <button
                type="button"
                onClick={() => setShowPromptModal(true)}
                className="flex items-center justify-between gap-2 w-full px-4 py-3 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-200 font-semibold hover:-translate-y-0.5 transition-transform"
              >
                <span className="inline-flex items-center gap-2">
                  <MessageSquare size={16} />
                  {t('dashboard.quickStart.actions.startPrompt')}
                </span>
                <ArrowRight size={16} />
              </button>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-3">
              Shortcuts: Ctrl+U (workspace), Ctrl+L (mechanical), Ctrl+I (image), Ctrl+P (prompt)
            </p>
          </div>

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
        onCad={() => handleLaunchWorkspace()}
        onImage={() => {
          setShowImageModal(true);
          setQuickStartOpen(false);
        }}
        onPrompt={() => {
          setShowPromptModal(true);
          setQuickStartOpen(false);
        }}
        isOpen={quickStartOpen}
        toggle={() => setQuickStartOpen((prev) => !prev)}
      />

      <Modal
        title={t('dashboard.imageForm.title')}
        description={t('dashboard.imageForm.description')}
        isOpen={showImageModal}
        onClose={() => setShowImageModal(false)}
      >
        <ImageWorkflowForm
          onCreate={handleJobSubmit}
          onSuccess={() => setShowImageModal(false)}
        />
      </Modal>

      <Modal
        title={t('dashboard.promptForm.title')}
        description={t('dashboard.promptForm.description')}
        isOpen={showPromptModal}
        onClose={() => setShowPromptModal(false)}
      >
        <PromptWorkflowForm
          onCreate={handleJobSubmit}
          onSuccess={() => setShowPromptModal(false)}
        />
      </Modal>
    </div>
  );
};

export default Dashboard;
