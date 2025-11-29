
import { Job, UploadFormData, JobFilters, Preset, ConversionMode, Unit } from '../types';

const API_BASE_URL = '/api/v1';

export class ApiError extends Error {
  constructor(public message: string, public status?: number) {
    super(message);
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An unexpected error occurred' }));
    throw new ApiError(error.message || response.statusText, response.status);
  }
  if (response.status === 204) {
    return {} as T;
  }
  return response.json();
}

// Mock Presets (In-memory storage for demo)
let MOCK_PRESETS: Preset[] = [
  {
    id: 'p1',
    name: 'Standard Wall Height',
    type: 'cad',
    config: { unit: Unit.MM, extrudeHeight: 3000, mode: ConversionMode.FLOOR_PLAN }
  },
  {
    id: 'p2',
    name: 'High Precision Gear',
    type: 'cad',
    config: { unit: Unit.MM, extrudeHeight: 10, mode: ConversionMode.MECHANICAL }
  },
  {
    id: 'p3',
    name: 'Sci-Fi Prop Generator',
    type: 'prompt',
    config: { prompt: "Futuristic container, sci-fi style, metallic texture", targetFormat: '3d', mode: ConversionMode.PROMPT_TO_3D }
  }
];

export const api = {
  /**
   * Creates a new conversion job.
   * Handles Multipart/FormData for files and JSON for text prompts.
   */
  async createJob(data: UploadFormData): Promise<Job> {
    
    // 1. Handle Prompt-based Jobs (JSON)
    if (data.type === 'prompt') {
      const headers = { 'Content-Type': 'application/json' };
      const body = JSON.stringify({
        type: data.type,
        prompt: data.prompt,
        target_format: data.targetFormat,
        mode: data.mode
      });

      const response = await fetch(`${API_BASE_URL}/jobs`, {
        method: 'POST',
        headers,
        body
      });
      // Mock: Attach config back to response for UI
      const job = await handleResponse<Job>(response);
      job.config = { prompt: data.prompt, targetFormat: data.targetFormat, mode: data.mode };
      return job;
    }

    // 2. Handle File-based Jobs (FormData)
    const formData = new FormData();
    formData.append('type', data.type);
    
    if (data.file) {
      formData.append('file', data.file);
    }
    
    formData.append('conversion_mode', data.mode);
    
    if (data.unit) formData.append('unit', data.unit);
    if (data.extrudeHeight) formData.append('extrude_height', data.extrudeHeight.toString());
    if (data.targetFormat) formData.append('target_format', data.targetFormat);

    const response = await fetch(`${API_BASE_URL}/jobs`, {
      method: 'POST',
      body: formData,
    });

    // Mock: Attach config back to response for UI
    const job = await handleResponse<Job>(response);
    job.config = { 
      unit: data.unit, 
      extrudeHeight: data.extrudeHeight, 
      targetFormat: data.targetFormat, 
      mode: data.mode 
    };
    return job;
  },

  /**
   * Fetches the list of jobs.
   * Supports filtering by status, type, date, and search query.
   */
  async getJobs(filters?: JobFilters): Promise<Job[]> {
    const url = new URL(`${API_BASE_URL}/jobs`, window.location.origin);
    
    if (filters) {
      if (filters.status && filters.status !== 'all') url.searchParams.append('status', filters.status);
      if (filters.type && filters.type !== 'all') url.searchParams.append('type', filters.type);
      if (filters.startDate) url.searchParams.append('start_date', filters.startDate);
      if (filters.endDate) url.searchParams.append('end_date', filters.endDate);
      if (filters.search) url.searchParams.append('q', filters.search);
    }
    
    const response = await fetch(url.toString());
    return handleResponse<Job[]>(response);
  },

  /**
   * Fetches a single job status.
   */
  async getJob(id: string): Promise<Job> {
    const response = await fetch(`${API_BASE_URL}/jobs/${id}`);
    return handleResponse<Job>(response);
  },

  /**
   * Cancels a job.
   */
  async cancelJob(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(response);
  },

  /**
   * Retries/Duplicates an existing job.
   */
  async retryJob(id: string): Promise<Job> {
    const response = await fetch(`${API_BASE_URL}/jobs/${id}/retry`, {
      method: 'POST'
    });
    return handleResponse<Job>(response);
  },

  // --- Presets API (Mocked) ---

  async getPresets(): Promise<Preset[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    return [...MOCK_PRESETS];
  },

  async createPreset(preset: Omit<Preset, 'id'>): Promise<Preset> {
    await new Promise(resolve => setTimeout(resolve, 300));
    const newPreset = { ...preset, id: Math.random().toString(36).substr(2, 9) };
    MOCK_PRESETS.push(newPreset);
    return newPreset;
  },

  async deletePreset(id: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 300));
    MOCK_PRESETS = MOCK_PRESETS.filter(p => p.id !== id);
  }
};
