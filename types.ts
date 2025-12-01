export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  QUEUED = 'queued',
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

export type JobIntent = 'cad' | 'image' | 'prompt';

export interface Job {
  job_id: string;
  status: JobStatus;
  download_url?: string;
  dxf_download_url?: string;
  glb_download_url?: string;
  step_download_url?: string;
  error_code?: string;
  progress: number; // 0-100 for UI visualization
}

export interface UploadFormData {
  file: File | null;
  mode: ConversionMode;
  unit: Unit;
  extrudeHeight: number;
  intent?: JobIntent;
  inputLabel?: string;
  outputLabel?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}
