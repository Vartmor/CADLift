export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum ConversionMode {
  FLOOR_PLAN = 'floor_plan',
  MECHANICAL = 'mechanical',
}

export enum Unit {
  MM = 'mm',
  CM = 'cm',
  M = 'm',
}

export interface Job {
  job_id: string;
  status: JobStatus;
  download_url?: string;
  error_code?: string;
  progress: number; // 0-100 for UI visualization
}

export interface UploadFormData {
  file: File | null;
  mode: ConversionMode;
  unit: Unit;
  extrudeHeight: number;
}