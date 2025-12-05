/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_ENABLE_JOB_LOGS?: string;
  readonly VITE_ENABLE_LOCAL_JOBS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

const rawApiBase = import.meta.env.VITE_API_BASE_URL ?? '';
const rawLogging = import.meta.env.VITE_ENABLE_JOB_LOGS ?? 'true';
const rawLocalFallback = import.meta.env.VITE_ENABLE_LOCAL_JOBS ?? 'true';

export const env = {
  API_BASE_URL: rawApiBase.trim(),
  ENABLE_JOB_LOGS: rawLogging !== 'false',
  ENABLE_LOCAL_JOBS: rawLocalFallback !== 'false',
};
