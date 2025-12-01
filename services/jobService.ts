import { ConversionMode, JobStatus, Unit, UploadFormData, JobIntent } from '../types';
import { env } from '../config/env';
import { logger } from './logger';

export interface JobRecord {
  job_id: string;
  status: JobStatus;
  progress: number;
  download_url?: string;
  dxf_download_url?: string;
  step_download_url?: string;
  glb_download_url?: string;
  error_code?: string;
  logKey: string;
  createdAt: number;
  completedAt?: number;
  updatedAt: number;
  inputName: string;
  outputName?: string;
  mode: ConversionMode;
  unit: Unit;
  extrudeHeight: number;
  intent: JobIntent;
  notes?: string;
  metadata?: Record<string, unknown>;
}

interface StoredJob extends JobRecord {
  failedAt?: number;
}

const JOB_STORAGE_KEY = 'cadlift.jobs.v1';
const FALLBACK_STORE: StoredJob[] = [];

const API_BASE_URL = env.API_BASE_URL;

const TIMELINE = [
  { status: JobStatus.QUEUED, duration: 1500, progress: 5, logKey: 'status_pending' },
  { status: JobStatus.PROCESSING, duration: 2200, progress: 35, logKey: 'processing_step_1' },
  { status: JobStatus.PROCESSING, duration: 2500, progress: 70, logKey: 'processing_step_2' },
  { status: JobStatus.PROCESSING, duration: 2800, progress: 90, logKey: 'processing_step_3' },
];

const FINAL_STAGE = { status: JobStatus.COMPLETED, progress: 100, logKey: 'status_completed' };

const hasBrowserStorage = () => typeof window !== 'undefined' && !!window.localStorage;

const loadStore = (): StoredJob[] => {
  if (!hasBrowserStorage()) {
    return [...FALLBACK_STORE];
  }
  try {
    const raw = window.localStorage.getItem(JOB_STORAGE_KEY);
    if (!raw) return [];
    const parsed: StoredJob[] = JSON.parse(raw);
    return parsed;
  } catch {
    return [];
  }
};

const saveStore = (jobs: StoredJob[]) => {
  if (!hasBrowserStorage()) {
    FALLBACK_STORE.splice(0, FALLBACK_STORE.length, ...jobs);
    return;
  }
  try {
    window.localStorage.setItem(JOB_STORAGE_KEY, JSON.stringify(jobs));
  } catch {
    // ignore write errors
  }
};

const listeners = new Set<(jobId?: string) => void>();
const notify = (jobId?: string) => listeners.forEach((cb) => cb(jobId));

const deriveJobState = (job: StoredJob, now: number) => {
  if (job.status === JobStatus.COMPLETED || job.status === JobStatus.FAILED) {
    return job;
  }

  const elapsed = now - job.createdAt;
  let accumulated = 0;
  for (const stage of TIMELINE) {
    accumulated += stage.duration;
    if (elapsed < accumulated) {
      job.status = stage.status;
      job.progress = stage.progress;
      job.logKey = stage.logKey;
      job.updatedAt = now;
      return job;
    }
  }

  job.status = FINAL_STAGE.status;
  job.progress = FINAL_STAGE.progress;
  job.logKey = FINAL_STAGE.logKey;
  job.download_url = job.download_url || `https://download.cadlift/jobs/${job.job_id}/${job.outputName ?? 'output.step'}`;
  job.completedAt = job.completedAt ?? now;
  job.updatedAt = now;
  return job;
};

const generateJobId = () => `job_${typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2, 10)}`;

const defaultOutputByMode = (mode: ConversionMode) => {
  switch (mode) {
    case ConversionMode.IMAGE_TO_2D:
      return 'vector_plan.dxf';
    case ConversionMode.IMAGE_TO_3D:
      return 'image_model.fbx';
    case ConversionMode.PROMPT_TO_2D:
      return 'prompt_sketch.dxf';
    case ConversionMode.PROMPT_TO_3D:
      return 'prompt_mesh.step';
    default:
      return 'model.step';
  }
};

const resolveOutputName = (data: UploadFormData) => {
  if (data.outputLabel) return data.outputLabel;
  const file = data.file;
  if (file) {
    const base = file.name.replace(/\.[^/.]+$/, '');
    return data.mode === ConversionMode.FLOOR_PLAN || data.mode === ConversionMode.MECHANICAL
      ? `${base}_3d.step`
      : `${base}_${data.mode === ConversionMode.IMAGE_TO_2D ? 'vector' : 'mesh'}.step`;
  }
  return defaultOutputByMode(data.mode);
};

const resolveInputName = (data: UploadFormData) => {
  if (data.inputLabel) return data.inputLabel;
  if (data.file?.name) return data.file.name;
  return data.intent === 'prompt' ? 'Prompt request' : 'Untitled input';
};

const resolveJobType = (data: UploadFormData): JobIntent => {
  if (data.intent) return data.intent;
  if (data.mode === ConversionMode.IMAGE_TO_2D || data.mode === ConversionMode.IMAGE_TO_3D) return 'image';
  if (data.mode === ConversionMode.PROMPT_TO_2D || data.mode === ConversionMode.PROMPT_TO_3D) return 'prompt';
  return 'cad';
};

const upsertJob = (job: StoredJob) => {
  const jobs = loadStore();
  const idx = jobs.findIndex((item) => item.job_id === job.job_id);
  if (idx > -1) {
    jobs[idx] = job;
  } else {
    jobs.unshift(job);
  }
  saveStore(jobs);
  notify(job.job_id);
};

interface ApiJobEntity {
  id: string;
  job_type: string;
  mode: string;
  status: string;
  params?: Record<string, unknown>;
  error_code?: string;
  error_message?: string;
  input_file_id?: string | null;
  output_file_id?: string | null;
  created_at?: string;
  updated_at?: string;
  completed_at?: string | null;
}

const statusMap: Record<string, JobStatus> = {
  pending: JobStatus.PENDING,
  queued: JobStatus.QUEUED,
  processing: JobStatus.PROCESSING,
  completed: JobStatus.COMPLETED,
  failed: JobStatus.FAILED,
};

const adaptApiJob = (job: ApiJobEntity): JobRecord => {
  const status = statusMap[job.status?.toLowerCase()] ?? JobStatus.PENDING;
  const createdAt = job.created_at ? Date.parse(job.created_at) : Date.now();
  const updatedAt = job.updated_at ? Date.parse(job.updated_at) : createdAt;
  const completedAt = job.completed_at ? Date.parse(job.completed_at) : undefined;
  const download_url = job.output_file_id && API_BASE_URL
    ? `${API_BASE_URL}/api/v1/files/${job.output_file_id}`
    : undefined;
  const step_id = job.params?.step_file_id as string | undefined;
  const step_download_url = step_id && API_BASE_URL
    ? `${API_BASE_URL}/api/v1/files/${step_id}`
    : undefined;
  const dxf_id = job.params?.dxf_file_id as string | undefined;
  const dxf_download_url = dxf_id && API_BASE_URL
    ? `${API_BASE_URL}/api/v1/files/${dxf_id}`
    : undefined;
  const glb_id = job.params?.glb_file_id as string | undefined;
  const glb_download_url = glb_id && API_BASE_URL
    ? `${API_BASE_URL}/api/v1/files/${glb_id}`
    : undefined;

  const rawProgress = (job as Record<string, unknown>).progress;
  const progress = typeof rawProgress === 'number'
    ? rawProgress
    : status === JobStatus.COMPLETED
      ? 100
      : status === JobStatus.PROCESSING
        ? 50
        : 0;

  return {
    job_id: job.id,
    status,
    progress,
    download_url: dxf_download_url || download_url || glb_download_url,
    dxf_download_url,
    step_download_url,
    glb_download_url,
    error_code: job.error_code,
    logKey: 'status_processing',
    createdAt,
    updatedAt,
    completedAt,
    inputName: job.job_type ?? 'Remote job',
    outputName: job.output_file_id ? `${job.job_type}_output.dxf` : undefined,
    mode: (job.mode as ConversionMode) ?? ConversionMode.FLOOR_PLAN,
    unit: Unit.MM,
    extrudeHeight: (job.params?.extrude_height as number) ?? 0,
    intent: (job.job_type as JobIntent) ?? 'cad',
    notes: job.error_message,
    metadata: job.params,
  };
};

const apiFetch = async (path: string, options?: RequestInit) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API ${response.status}: ${errorText}`);
  }
  return response;
};

const remoteAdapter = {
  async createJob(data: UploadFormData): Promise<JobRecord> {
    if (!API_BASE_URL) {
      throw new Error('API base URL missing');
    }
    const formData = new FormData();
    const jobType = resolveJobType(data);
    formData.append('job_type', jobType);
    formData.append('mode', data.mode);
    if (data.file) {
      formData.append('upload', data.file, data.file.name);
    }
    const params: Record<string, unknown> = {};
    if (typeof data.extrudeHeight === 'number') params.extrude_height = data.extrudeHeight;
    if (data.metadata?.prompt) params.prompt = data.metadata.prompt;
    if (data.metadata?.detail) params.detail = data.metadata.detail;
    formData.append('params', JSON.stringify(params));
    const response = await apiFetch('/api/v1/jobs', {
      method: 'POST',
      body: formData,
    });
    const payload = (await response.json()) as ApiJobEntity;
    logger.info('Created job via API', payload);
    return adaptApiJob(payload);
  },
  async getJob(jobId: string): Promise<JobRecord | null> {
    if (!API_BASE_URL) return null;
    const response = await apiFetch(`/api/v1/jobs/${jobId}`);
    const payload = (await response.json()) as ApiJobEntity;
    return adaptApiJob(payload);
  },
  async listJobs(): Promise<JobRecord[]> {
    if (!API_BASE_URL) return [];
    const response = await apiFetch('/api/v1/jobs');
    const payload = (await response.json()) as ApiJobEntity[];
    return payload.map(adaptApiJob);
  },
};

const createLocalJob = (data: UploadFormData): JobRecord => {
  const now = Date.now();
  const job: StoredJob = {
    job_id: generateJobId(),
    status: JobStatus.QUEUED,
    progress: 0,
    logKey: 'status_pending',
    download_url: undefined,
    error_code: undefined,
    createdAt: now,
    updatedAt: now,
    inputName: resolveInputName(data),
    outputName: resolveOutputName(data),
    mode: data.mode,
    unit: data.unit ?? Unit.MM,
    extrudeHeight: data.extrudeHeight ?? 0,
    intent: data.intent ?? 'cad',
    notes: data.notes,
    metadata: data.metadata,
  };
  upsertJob(job);
  logger.info('Created local mock job', job);
  return { ...job };
};

const getLocalJob = (jobId: string): JobRecord | null => {
  const jobs = loadStore();
  const target = jobs.find((job) => job.job_id === jobId);
  if (!target) return null;
  const derived = deriveJobState({ ...target }, Date.now());
  if (derived.status !== target.status || derived.progress !== target.progress) {
    upsertJob(derived);
  }
  return { ...derived };
};

const listLocalJobs = (): JobRecord[] => {
  const now = Date.now();
  const jobs = loadStore().map((job) => {
    const derived = deriveJobState({ ...job }, now);
    return { ...derived };
  });
  saveStore(jobs);
  return jobs.sort((a, b) => b.createdAt - a.createdAt);
};

const useRemoteApi = () => Boolean(API_BASE_URL);

const withFallback = async <T>(remoteFn: () => Promise<T>, localFn: () => T | Promise<T>): Promise<T> => {
  if (useRemoteApi()) {
    try {
      return await remoteFn();
    } catch (error) {
      logger.warn('Remote job service failed, falling back to local simulation', error);
      if (!env.ENABLE_LOCAL_JOBS) {
        throw error;
      }
    }
  }
  return localFn();
};

export const jobService = {
  subscribe(listener: (jobId?: string) => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  async createJob(data: UploadFormData): Promise<JobRecord> {
    const job = await withFallback(
      () => remoteAdapter.createJob(data),
      () => createLocalJob(data),
    );
    notify(job.job_id);
    return job;
  },

  async getJob(jobId: string): Promise<JobRecord | null> {
    return withFallback(
      () => remoteAdapter.getJob(jobId),
      () => getLocalJob(jobId),
    );
  },

  async listJobs(): Promise<JobRecord[]> {
    return withFallback(
      () => remoteAdapter.listJobs(),
      () => listLocalJobs(),
    );
  }
};
