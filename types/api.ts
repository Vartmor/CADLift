/**
 * CADLift API Types
 * 
 * Type definitions for API requests and responses
 */

// ==================== Base Types ====================

export interface ApiError {
    detail: string;
    code?: string;
    field?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
    has_more: boolean;
}

// ==================== Job Types ====================

export type JobStatusType = 'pending' | 'queued' | 'processing' | 'completed' | 'failed';

export type JobType = 'cad' | 'image' | 'prompt';

export type ConversionModeType =
    | 'floor_plan'
    | 'mechanical'
    | 'image_to_2d'
    | 'image_to_3d'
    | 'prompt_to_2d'
    | 'prompt_to_3d';

export interface JobParams {
    extrude_height?: number;
    wall_thickness?: number;
    unit?: 'mm' | 'cm' | 'm';
    prompt?: string;
    detail?: 'low' | 'medium' | 'high';
    layer_filter?: string[];
    [key: string]: unknown;
}

export interface JobResponse {
    id: string;
    job_type: JobType;
    mode: ConversionModeType;
    status: JobStatusType;
    params?: JobParams;
    error_code?: string;
    error_message?: string;
    input_file_id?: string | null;
    output_file_id?: string | null;
    created_at: string;
    updated_at: string;
    completed_at?: string | null;
    progress?: number;
}

export interface CreateJobRequest {
    job_type: JobType;
    mode: ConversionModeType;
    params?: JobParams;
    file?: File;
}

// ==================== File Types ====================

export interface FileResponse {
    id: string;
    job_id: string;
    role: 'input' | 'output';
    storage_key: string;
    original_name: string;
    mime_type: string;
    size_bytes: number;
    created_at: string;
}

export type ExportFormat = 'dxf' | 'step' | 'obj' | 'stl' | 'ply' | 'gltf' | 'glb';

export interface FileDownloadParams {
    format?: ExportFormat;
}

// ==================== Auth Types ====================

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    name?: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: 'bearer';
    expires_in: number;
}

export interface UserProfile {
    id: string;
    email: string;
    name?: string;
    created_at: string;
    updated_at: string;
}

// ==================== Health Types ====================

export interface HealthResponse {
    status: 'ok' | 'degraded' | 'down';
    service: string;
    environment: string;
    version?: string;
}

// ==================== API Client Types ====================

export interface ApiClientConfig {
    baseUrl: string;
    timeout?: number;
    headers?: Record<string, string>;
}

export interface RequestOptions {
    headers?: Record<string, string>;
    signal?: AbortSignal;
    timeout?: number;
}

// Type guard functions
export function isApiError(error: unknown): error is ApiError {
    return (
        typeof error === 'object' &&
        error !== null &&
        'detail' in error &&
        typeof (error as ApiError).detail === 'string'
    );
}

export function isJobResponse(obj: unknown): obj is JobResponse {
    return (
        typeof obj === 'object' &&
        obj !== null &&
        'id' in obj &&
        'status' in obj &&
        'job_type' in obj
    );
}
