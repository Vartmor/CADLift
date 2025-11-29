import { env } from '../config/env';

type Level = 'info' | 'warn' | 'error';

const log = (level: Level, message: string, payload?: unknown) => {
  if (!env.ENABLE_JOB_LOGS && level === 'info') return;
  const prefix = `[cadlift:${level}]`;
  if (payload !== undefined) {
    // eslint-disable-next-line no-console
    console[level === 'error' ? 'error' : level](prefix, message, payload);
  } else {
    // eslint-disable-next-line no-console
    console[level === 'error' ? 'error' : level](prefix, message);
  }
};

export const logger = {
  info: (message: string, payload?: unknown) => log('info', message, payload),
  warn: (message: string, payload?: unknown) => log('warn', message, payload),
  error: (message: string, payload?: unknown) => log('error', message, payload),
};
