
export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum ConversionMode {
  FLOOR_PLAN = 'floor_plan',
  MECHANICAL = 'mechanical',
  IMAGE_TO_2D = 'image_to_2d',
  IMAGE_TO_3D = 'image_to_3d',
  PROMPT_TO_2D = 'prompt_to_2d',
  PROMPT_TO_3D = 'prompt_to_3d',
}

export enum Unit {
  MM = 'mm',
  CM = 'cm',
  M = 'm',
}

export type JobType = 'cad' | 'image' | 'prompt';

export interface JobConfig {
  unit?: Unit;
  extrudeHeight?: number;
  prompt?: string;
  targetFormat?: '2d' | '3d';
  mode?: ConversionMode;
}

export interface Job {
  job_id: string;
  type: JobType;
  name: string;
  status: JobStatus;
  conversion_mode: ConversionMode;
  date: string; // Creation date formatted string
  finished_at?: string;
  download_url?: string;
  error_code?: string;
  progress: number; // 0-100
  output_format?: string; // e.g., FBX, OBJ, STEP
  thumbnail?: string;
  config?: JobConfig; // Store parameters to allow re-running or creating presets
}

export interface UploadFormData {
  type: JobType;
  // CAD & Image common
  file?: File | null;
  // Config
  mode: ConversionMode;
  unit?: Unit;
  extrudeHeight?: number;
  // Prompt specific
  prompt?: string;
  // AI toggles
  use_gemini_triposg?: boolean;
  use_triposg?: boolean;
  // Image/Prompt Target
  targetFormat?: '2d' | '3d';
}

export interface JobFilters {
  status?: string;
  type?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
}

export interface Preset {
  id: string;
  name: string;
  type: JobType;
  config: JobConfig;
}
