
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api, ApiError } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useTheme } from '../contexts/ThemeContext';
import UploadForm from '../components/UploadForm';
import JobStatusComponent from '../components/JobStatus';
import Skeleton from '../components/Skeleton';
import { UploadFormData, Job, JobStatus, Unit, JobFilters, Preset, ConversionMode, JobConfig } from '../types';
import { 
  LayoutDashboard, 
  Terminal, 
  LogOut, 
  Activity, 
  Clock, 
  Search, 
  Layers, 
  Settings, 
  BookOpen, 
  HelpCircle,
  FileDigit,
  RotateCw,
  Download,
  Play,
  XCircle,
  Eye,
  Image as ImageIcon,
  Sparkles,
  Box,
  Filter,
  X,
  Moon,
  Sun,
  Plus,
  Trash2,
  Globe
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const { success, error: showError, info } = useToast();
  
  // Core Data State
  const [activeJobs, setActiveJobs] = useState<Job[]>([]);
  const [historyJobs, setHistoryJobs] = useState<Job[]>([]);
  const [presets, setPresets] = useState<Preset[]>([]);
  
  // UI State
  const [viewingJob, setViewingJob] = useState<Job | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isLoadingPresets, setIsLoadingPresets] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<Preset | null>(null);

  // Filter State
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");

  // Quick Settings State (Persisted)
  const [defaultUnit, setDefaultUnit] = useState<Unit>(() => 
    (localStorage.getItem('defaultUnit') as Unit) || Unit.MM
  );
  const [defaultHeight, setDefaultHeight] = useState<number>(() => 
    Number(localStorage.getItem('defaultHeight')) || 3000
  );
  const [defaultMode, setDefaultMode] = useState<ConversionMode>(() =>
    (localStorage.getItem('defaultMode') as ConversionMode) || ConversionMode.FLOOR_PLAN
  );

  // New Preset Creation State
  const [isCreatingPreset, setIsCreatingPreset] = useState(false);
  const [newPresetName, setNewPresetName] = useState("");

  const handleLogout = () => navigate('/signin');

  // Persistence Effects
  useEffect(() => { localStorage.setItem('defaultUnit', defaultUnit); }, [defaultUnit]);
  useEffect(() => { localStorage.setItem('defaultHeight', defaultHeight.toString()); }, [defaultHeight]);
  useEffect(() => { localStorage.setItem('defaultMode', defaultMode); }, [defaultMode]);

  // Fetch Data Functions
  const fetchActiveJobs = useCallback(async () => {
    try {
      const jobs = await api.getJobs({ status: 'active' });
      setActiveJobs(jobs);
    } catch (err) {
      console.error("Failed to fetch active jobs", err);
    }
  }, []);

  const fetchHistoryJobs = useCallback(async () => {
    setIsLoadingHistory(true);
    try {
      const filters: JobFilters = {
        status: filterStatus !== 'all' ? filterStatus : undefined,
        type: filterType !== 'all' ? filterType : undefined,
        startDate: dateFrom || undefined,
        endDate: dateTo || undefined,
        search: searchTerm || undefined
      };
      const jobs = await api.getJobs(filters);
      const history = jobs.filter(j => 
        j.status === JobStatus.COMPLETED || 
        j.status === JobStatus.FAILED || 
        j.status === JobStatus.CANCELLED
      );
      setHistoryJobs(history);
    } catch (err) {
      console.error("Failed to fetch history jobs", err);
      showError("Failed to refresh history");
    } finally {
      setIsLoadingHistory(false);
    }
  }, [filterStatus, filterType, dateFrom, dateTo, searchTerm, showError]);

  const fetchPresets = useCallback(async () => {
    setIsLoadingPresets(true);
    try {
      const data = await api.getPresets();
      setPresets(data);
    } catch (err) {
      console.error("Failed to fetch presets", err);
    } finally {
      setIsLoadingPresets(false);
    }
  }, []);

  // Initial Load & Polling
  useEffect(() => {
    fetchActiveJobs();
    fetchHistoryJobs();
    fetchPresets();
    
    const interval = setInterval(() => {
      fetchActiveJobs();
    }, 5000);
    return () => clearInterval(interval);
  }, []); // Run once on mount + interval

  // Debounced History Fetch
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchHistoryJobs();
    }, 500);
    return () => clearTimeout(timer);
  }, [filterStatus, filterType, dateFrom, dateTo, searchTerm, fetchHistoryJobs]);

  // Client-side backup filtering
  const filteredHistory = useMemo(() => {
    return historyJobs.filter(job => {
      if (searchTerm && !job.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      if (filterStatus !== "all") {
        if (filterStatus === "completed" && job.status !== JobStatus.COMPLETED) return false;
        if (filterStatus === "failed" && job.status !== JobStatus.FAILED) return false;
        if (filterStatus === "cancelled" && job.status !== JobStatus.CANCELLED) return false;
      }
      if (filterType !== "all" && job.type !== filterType) return false;
      if (dateFrom && job.date < dateFrom) return false;
      if (dateTo && job.date > dateTo + "T23:59:59") return false;
      return true;
    });
  }, [historyJobs, searchTerm, filterStatus, filterType, dateFrom, dateTo]);

  const clearFilters = () => {
    setSearchTerm("");
    setFilterStatus("all");
    setFilterType("all");
    setDateFrom("");
    setDateTo("");
  };

  // Job Actions
  const handleJobSubmit = async (data: UploadFormData) => {
    setIsSubmitting(true);
    setSelectedPreset(null); // Clear preset selection on submit
    try {
      const newJob = await api.createJob(data);
      setActiveJobs(prev => [newJob, ...prev]);
      success(t('common.status_pending'));
      
      // If creating preset based on this job submission
      if (isCreatingPreset && newPresetName.trim()) {
        const config: JobConfig = {
           unit: data.unit,
           extrudeHeight: data.extrudeHeight,
           prompt: data.prompt,
           targetFormat: data.targetFormat,
           mode: data.mode
        };
        await api.createPreset({
          name: newPresetName,
          type: data.type,
          config
        });
        fetchPresets();
        setNewPresetName("");
        setIsCreatingPreset(false);
        success(t('dashboard.create_preset_success'));
      }
      
      fetchActiveJobs();
    } catch (err) {
      if (err instanceof ApiError) {
        showError(`Submission failed: ${err.message}`);
      } else {
        showError('Failed to create job. Please check your connection.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelJob = async (id: string) => {
    try {
      await api.cancelJob(id);
      success(t('dashboard.cancel_success'));
      setActiveJobs(prev => prev.filter(j => j.job_id !== id));
      fetchHistoryJobs();
    } catch (err) {
      showError(t('dashboard.cancel_error'));
    }
  };

  const handleRerun = async (job: Job) => {
    try {
      success(`Re-running: ${job.name}`);
      const newJob = await api.retryJob(job.job_id);
      setActiveJobs(prev => [newJob, ...prev]);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      showError("Failed to re-run job");
    }
  };

  const handleDownload = (job: Job) => {
    if (job.download_url) {
      window.open(job.download_url, '_blank');
    } else {
      showError("Download link unavailable");
    }
  };

  const handleViewJob = (job: Job) => setViewingJob(job);
  const closeJobView = () => {
    setViewingJob(null);
    fetchActiveJobs();
    fetchHistoryJobs();
  };

  // Preset Actions
  const handleRunPreset = (preset: Preset) => {
    setSelectedPreset(preset);
    info(`Applying preset: ${preset.name}`);
  };

  const handleDeletePreset = async (id: string) => {
    try {
      await api.deletePreset(id);
      setPresets(prev => prev.filter(p => p.id !== id));
      success(t('dashboard.delete_preset_success'));
    } catch (e) {
      showError("Failed to delete preset");
    }
  };

  const handleCreatePresetFromLastJob = async () => {
     // Logic: Get latest history job, create preset
     if (historyJobs.length === 0) {
       showError("No history available to create preset.");
       return;
     }
     const lastJob = historyJobs[0];
     // For MVP we mock extraction or check if config exists
     if (!lastJob.config) {
       // Fallback config if missing
       const mockConfig: JobConfig = { unit: Unit.MM, mode: lastJob.conversion_mode, extrudeHeight: 3000 }; 
       await api.createPreset({
         name: `Preset from ${lastJob.name}`,
         type: lastJob.type,
         config: mockConfig
       });
     } else {
       await api.createPreset({
         name: `Preset from ${lastJob.name}`,
         type: lastJob.type,
         config: lastJob.config
       });
     }
     fetchPresets();
     success(t('dashboard.create_preset_success'));
  };

  // Helper
  const getJobIcon = (type: string) => {
    switch (type) {
      case 'cad': return <FileDigit size={24} />;
      case 'image': return <ImageIcon size={24} />;
      case 'prompt': return <Sparkles size={24} />;
      default: return <Box size={24} />;
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch (e) {
      return dateString;
    }
  };

  // Renderers
  const renderActiveConversions = () => (
    <div className="mb-8 animate-fade-in-up">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        <Activity className="text-green-500 animate-pulse" size={20} />
        {t('dashboard.active_conversions')}
      </h2>
      <div className="grid gap-4">
        {activeJobs.map(job => (
          <div key={job.job_id} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-md flex flex-col sm:flex-row items-center gap-4 transition-all hover:shadow-lg">
            <div className="w-12 h-12 rounded-xl bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center text-primary-600 dark:text-primary-400 shrink-0">
               {getJobIcon(job.type)}
            </div>
            <div className="flex-grow w-full">
               <div className="flex justify-between items-center mb-2">
                 <h3 className="font-bold text-slate-900 dark:text-white truncate max-w-[200px] sm:max-w-md">{job.name}</h3>
                 <div className="flex items-center gap-2">
                   <span className="text-xs font-mono bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-600 dark:text-slate-400 uppercase animate-pulse">
                     {job.status === JobStatus.PENDING ? t('common.status_pending') : t('common.status_processing')}
                   </span>
                 </div>
               </div>
               <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary-500 rounded-full transition-all duration-500 relative" 
                    style={{ width: `${job.progress || 5}%` }}
                  >
                     <div className="absolute inset-0 bg-white/30 animate-[shimmer_1s_infinite]"></div>
                  </div>
               </div>
            </div>
            <div className="flex gap-2 shrink-0 w-full sm:w-auto justify-end">
              <button 
                onClick={() => handleViewJob(job)}
                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors flex items-center gap-2 text-sm font-medium"
              >
                <Eye size={16} />
                <span className="hidden sm:inline">{t('dashboard.view_details')}</span>
              </button>
              <button 
                onClick={() => handleCancelJob(job.job_id)}
                className="p-2 rounded-lg bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 transition-colors"
                title={t('dashboard.cancel_job')}
              >
                <XCircle size={16} />
              </button>
            </div>
          </div>
        ))}
        {activeJobs.length === 0 && (
          <div className="p-6 text-center border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-900/50">
            <Activity className="w-8 h-8 mx-auto text-slate-300 mb-2" />
            <p className="text-slate-500 text-sm">{t('dashboard.empty_active')}</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderHistory = () => (
    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col animate-fade-in-up">
        
        {/* Header & Filters */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Clock size={20} className="text-slate-400" />
              {t('dashboard.recent_activity')}
            </h3>
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors md:hidden ${showFilters ? 'bg-primary-50 text-primary-600' : 'bg-slate-100 text-slate-600'}`}
            >
              <Filter size={16} /> Filters
            </button>
          </div>

          <div className={`flex flex-col xl:flex-row xl:items-center gap-3 transition-all duration-300 ${showFilters ? 'block' : 'hidden md:flex'}`}>
            <div className="relative flex-grow xl:max-w-xs">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder={t('dashboard.search_placeholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              />
            </div>
            
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative min-w-[120px]">
                <select 
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full appearance-none pl-3 pr-8 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-sm text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                >
                  <option value="all">{t('dashboard.filter_all_types')}</option>
                  <option value="cad">CAD</option>
                  <option value="image">Image</option>
                  <option value="prompt">AI Prompt</option>
                </select>
                <Layers size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>

              <div className="relative min-w-[140px]">
                <select 
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full appearance-none pl-3 pr-8 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-sm text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                >
                  <option value="all">{t('dashboard.filter_all_status')}</option>
                  <option value="completed">{t('dashboard.filter_completed')}</option>
                  <option value="failed">{t('dashboard.filter_failed')}</option>
                  <option value="cancelled">{t('dashboard.filter_cancelled')}</option>
                </select>
                <Filter size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>

              <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2">
                <input 
                  type="date" 
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="bg-transparent text-sm text-slate-600 dark:text-slate-300 focus:outline-none"
                />
                <span className="text-slate-300 dark:text-slate-600">-</span>
                <input 
                  type="date" 
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="bg-transparent text-sm text-slate-600 dark:text-slate-300 focus:outline-none"
                />
              </div>

              {(searchTerm || filterStatus !== 'all' || filterType !== 'all' || dateFrom || dateTo) && (
                <button 
                  onClick={clearFilters}
                  className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                >
                  <X size={16} />
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
           <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 dark:bg-slate-950/50 border-b border-slate-100 dark:border-slate-800">
                 <tr>
                   <th className="px-6 py-4 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">{t('dashboard.table_job')}</th>
                   <th className="px-6 py-4 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">{t('dashboard.table_type')}</th>
                   <th className="px-6 py-4 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs hidden sm:table-cell">{t('dashboard.table_output')}</th>
                   <th className="px-6 py-4 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs">{t('dashboard.table_status')}</th>
                   <th className="px-6 py-4 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs hidden md:table-cell">{t('dashboard.table_date')}</th>
                   <th className="px-6 py-4 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-xs text-right">{t('dashboard.table_action')}</th>
                 </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                 {isLoadingHistory ? (
                    // Loading Skeletons
                    Array.from({ length: 3 }).map((_, i) => (
                      <tr key={i}>
                        <td className="px-6 py-4"><div className="flex gap-3"><Skeleton className="w-8 h-8 rounded-lg" /><div className="space-y-1"><Skeleton className="w-24 h-4" /><Skeleton className="w-16 h-3" /></div></div></td>
                        <td className="px-6 py-4"><Skeleton className="w-12 h-6 rounded" /></td>
                        <td className="px-6 py-4 hidden sm:table-cell"><Skeleton className="w-8 h-4" /></td>
                        <td className="px-6 py-4"><Skeleton className="w-20 h-6 rounded-full" /></td>
                        <td className="px-6 py-4 hidden md:table-cell"><Skeleton className="w-24 h-4" /></td>
                        <td className="px-6 py-4"><Skeleton className="w-20 h-6 ml-auto" /></td>
                      </tr>
                    ))
                 ) : filteredHistory.length > 0 ? (
                   filteredHistory.map((job) => (
                   <tr key={job.job_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-500 flex items-center justify-center shrink-0">
                             {getJobIcon(job.type)}
                          </div>
                          <div className="min-w-0">
                            <span className="block font-medium text-slate-900 dark:text-slate-200 truncate max-w-[150px] sm:max-w-[200px]">{job.name}</span>
                            <span className="text-xs text-slate-400 hidden sm:block truncate">{job.conversion_mode}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="capitalize text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-bold">{job.type}</span>
                      </td>
                      <td className="px-6 py-4 hidden sm:table-cell font-mono text-xs text-slate-500">
                        {job.output_format || 'N/A'}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${
                          job.status === JobStatus.COMPLETED ? 'bg-green-50 border-green-100 text-green-600 dark:bg-green-900/20 dark:border-green-900/30 dark:text-green-400' :
                          (job.status === JobStatus.FAILED || job.status === JobStatus.CANCELLED) ? 'bg-red-50 border-red-100 text-red-600 dark:bg-red-900/20 dark:border-red-900/30 dark:text-red-400' :
                          'bg-slate-50 border-slate-200 text-slate-500 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 dark:text-slate-400 hidden md:table-cell text-xs">
                        <div>{formatDate(job.date)}</div>
                      </td>
                      <td className="px-6 py-4 text-right">
                         <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                           {job.status === JobStatus.COMPLETED && (
                             <button 
                               onClick={() => handleDownload(job)}
                               className="p-1.5 rounded text-slate-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors" 
                               title={t('dashboard.action_download')}
                             >
                               <Download size={16} />
                             </button>
                           )}
                           <button 
                             onClick={() => handleRerun(job)}
                             className="p-1.5 rounded text-slate-400 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-colors" 
                             title={t('dashboard.action_retry')}
                           >
                             <RotateCw size={16} />
                           </button>
                           <button 
                             onClick={() => handleViewJob(job)}
                             className="p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors" 
                             title={t('dashboard.view_details')}
                           >
                             <Eye size={16} />
                           </button>
                         </div>
                      </td>
                   </tr>
                 ))) : (
                   <tr>
                     <td colSpan={6} className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center justify-center text-slate-400">
                          <Search size={32} className="mb-2 opacity-50" />
                          <p className="font-medium">{t('dashboard.empty_state')}</p>
                        </div>
                     </td>
                   </tr>
                 )}
              </tbody>
           </table>
        </div>
    </div>
  );

  return (
    <div className="w-full max-w-7xl mx-auto pb-20 animate-fade-in">
      
      {/* Detail Modal */}
      {viewingJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 animate-fade-in">
           <div className="w-full max-w-3xl relative">
              <button 
                onClick={closeJobView} 
                className="absolute -top-12 right-0 text-white/80 hover:text-white flex items-center gap-2 transition-colors"
              >
                Close <XCircle />
              </button>
              <JobStatusComponent 
                jobId={viewingJob.job_id} 
                initialJob={viewingJob}
                onReset={closeJobView}
              />
           </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
            <LayoutDashboard className="text-primary-500" />
            {t('dashboard.workspace')}
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2 text-sm font-mono">
            <Terminal size={14} />
            <span>{t('dashboard.ready')}</span>
          </p>
        </div>
        
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 text-sm font-bold text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-lg transition-colors w-fit"
        >
          <LogOut size={16} />
          <span>{t('dashboard.logout')}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
         
         {/* Left Column (Main Workflow) */}
         <div className="lg:col-span-8 space-y-8">
            
            <div className="bg-slate-50 dark:bg-slate-900/50 rounded-3xl p-1 relative group">
               {selectedPreset && (
                 <div className="absolute top-4 right-4 z-10 bg-primary-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg animate-fade-in flex items-center gap-2">
                   <Sparkles size={12} /> Preset Active: {selectedPreset.name}
                   <button onClick={() => setSelectedPreset(null)} className="hover:bg-white/20 rounded-full p-0.5"><X size={12} /></button>
                 </div>
               )}
               <UploadForm 
                onSubmit={handleJobSubmit} 
                defaultUnit={defaultUnit}
                defaultHeight={defaultHeight}
                defaultMode={defaultMode}
                isLoading={isSubmitting}
                preset={selectedPreset}
              />
              
              {/* Optional Inline Preset Creation */}
              <div className="mt-2 flex justify-end px-4">
                 {!isCreatingPreset ? (
                   <button 
                    onClick={() => setIsCreatingPreset(true)}
                    className="text-xs font-medium text-slate-400 hover:text-primary-500 transition-colors flex items-center gap-1"
                   >
                     <Plus size={14} /> {t('dashboard.save_preset')}
                   </button>
                 ) : (
                   <div className="flex items-center gap-2 bg-white dark:bg-slate-800 p-2 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 animate-fade-in">
                     <input 
                       type="text" 
                       placeholder={t('dashboard.preset_name_placeholder')}
                       value={newPresetName}
                       onChange={(e) => setNewPresetName(e.target.value)}
                       className="text-xs p-1 bg-transparent border-b border-slate-300 dark:border-slate-600 focus:outline-none focus:border-primary-500 w-40"
                       autoFocus
                     />
                     <div className="text-[10px] text-slate-400 italic mr-2">Save on submit</div>
                     <button onClick={() => setIsCreatingPreset(false)} className="text-slate-400 hover:text-red-500"><X size={14} /></button>
                   </div>
                 )}
              </div>
            </div>

            {activeJobs.length > 0 && renderActiveConversions()}
            {renderHistory()}
         </div>

         {/* Right Column (Control Widgets) */}
         <div className="lg:col-span-4 space-y-6">
            
            {/* Quick Settings Widget */}
            <div className="bg-slate-50 dark:bg-slate-950 rounded-3xl border border-slate-200 dark:border-slate-800 p-6">
               <h3 className="font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                 <Settings size={18} className="text-slate-400" />
                 {t('dashboard.settings_title')}
               </h3>
               <div className="space-y-4">
                 {/* UI Settings */}
                 <div className="grid grid-cols-2 gap-3 mb-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                    <button 
                      onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'tr' : 'en')}
                      className="flex flex-col items-center justify-center p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-500 transition-all"
                    >
                       <Globe size={18} className="mb-1 text-slate-500" />
                       <span className="text-xs font-bold">{i18n.language.toUpperCase()}</span>
                    </button>
                    <button 
                      onClick={toggleTheme}
                      className="flex flex-col items-center justify-center p-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-500 transition-all"
                    >
                       {theme === 'light' ? <Moon size={18} className="mb-1 text-slate-500" /> : <Sun size={18} className="mb-1 text-yellow-400" />}
                       <span className="text-xs font-bold capitalize">{theme}</span>
                    </button>
                 </div>

                 {/* Default Logic */}
                 <div>
                   <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">{t('dashboard.default_mode')}</label>
                   <select 
                     value={defaultMode}
                     onChange={(e) => setDefaultMode(e.target.value as ConversionMode)}
                     className="w-full p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm font-medium focus:outline-none focus:border-primary-500"
                   >
                     <option value={ConversionMode.FLOOR_PLAN}>{t('common.mode_floor')}</option>
                     <option value={ConversionMode.MECHANICAL}>{t('common.mode_mech')}</option>
                   </select>
                 </div>
                 <div>
                   <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">{t('dashboard.default_unit')}</label>
                   <select 
                     value={defaultUnit}
                     onChange={(e) => setDefaultUnit(e.target.value as Unit)}
                     className="w-full p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm font-medium focus:outline-none focus:border-primary-500"
                   >
                     <option value={Unit.MM}>Millimeters (mm)</option>
                     <option value={Unit.CM}>Centimeters (cm)</option>
                     <option value={Unit.M}>Meters (m)</option>
                   </select>
                 </div>
                 <div>
                   <label className="text-xs font-bold text-slate-500 uppercase mb-1 block">{t('dashboard.default_height')}</label>
                   <div className="relative">
                     <input 
                       type="number"
                       value={defaultHeight}
                       onChange={(e) => setDefaultHeight(Number(e.target.value))}
                       className="w-full p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm font-medium focus:outline-none focus:border-primary-500"
                     />
                     <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">{defaultUnit}</span>
                   </div>
                 </div>
               </div>
            </div>

            {/* Presets Widget */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
               <div className="flex items-center justify-between mb-4">
                 <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                   <Layers size={18} className="text-slate-400" />
                   {t('dashboard.presets_title')}
                 </h3>
                 <button onClick={handleCreatePresetFromLastJob} className="text-xs font-bold text-primary-600 hover:text-primary-700 dark:text-primary-400" title="Create from History">
                   + Recent
                 </button>
               </div>
               
               <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
                  {isLoadingPresets ? (
                     Array.from({ length: 3 }).map((_, i) => (
                       <div key={i} className="flex gap-3 p-3"><Skeleton className="w-10 h-10 rounded-lg" /><div className="flex-1"><Skeleton className="w-24 h-4 mb-1" /><Skeleton className="w-16 h-3" /></div></div>
                     ))
                  ) : presets.length > 0 ? (
                    presets.map((preset) => (
                      <div key={preset.id} className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 transition-all border border-transparent hover:border-slate-200 dark:hover:border-slate-700 group relative">
                         <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                           preset.type === 'cad' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30' : 
                           preset.type === 'image' ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/30' : 
                           'bg-amber-100 text-amber-600 dark:bg-amber-900/30'
                         }`}>
                           {getJobIcon(preset.type)}
                         </div>
                         <div className="text-left flex-grow min-w-0">
                           <div className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">{preset.name}</div>
                           <div className="text-[10px] text-slate-500 truncate">
                             {preset.config.mode ? t(`common.mode_${preset.config.mode === ConversionMode.FLOOR_PLAN ? 'floor' : 'mech'}`) : preset.type}
                           </div>
                         </div>
                         
                         <div className="flex items-center gap-1">
                           <button 
                              onClick={() => handleRunPreset(preset)}
                              className="p-1.5 rounded-lg bg-white dark:bg-slate-700 text-primary-600 shadow-sm hover:scale-105 transition-transform"
                              title={t('dashboard.run_preset')}
                           >
                             <Play size={14} fill="currentColor" />
                           </button>
                           <button 
                              onClick={() => handleDeletePreset(preset.id)}
                              className="p-1.5 rounded-lg bg-white dark:bg-slate-700 text-slate-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                              title={t('dashboard.delete_preset')}
                           >
                             <Trash2 size={14} />
                           </button>
                         </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-6 text-slate-400 text-xs">
                      {t('dashboard.empty_presets')}
                    </div>
                  )}
               </div>
            </div>

            {/* Quick Links */}
            <div>
               <h3 className="font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                 <BookOpen size={18} className="text-slate-400" />
                 {t('dashboard.quick_links')}
               </h3>
               <div className="grid grid-cols-2 gap-3">
                 <a href="#" className="flex flex-col items-center justify-center p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 hover:shadow-md transition-all text-center group">
                    <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-full text-blue-500 mb-2 group-hover:scale-110 transition-transform"><BookOpen size={18} /></div>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">{t('dashboard.link_docs')}</span>
                 </a>
                 <a href="#" className="flex flex-col items-center justify-center p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 hover:shadow-md transition-all text-center group">
                    <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded-full text-green-500 mb-2 group-hover:scale-110 transition-transform"><HelpCircle size={18} /></div>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">{t('dashboard.link_help')}</span>
                 </a>
               </div>
            </div>

         </div>
      </div>
    </div>
  );
};

export default Dashboard;
