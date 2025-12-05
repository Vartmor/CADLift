/**
 * Utility functions for the CADLift frontend application
 */

/**
 * Safe localStorage helper with error handling
 */
export const safeStorage = {
    get: <T>(key: string, defaultValue: T): T => {
        if (typeof window === 'undefined') return defaultValue;
        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn(`Failed to read ${key} from localStorage:`, error);
            return defaultValue;
        }
    },

    set: <T>(key: string, value: T): boolean => {
        if (typeof window === 'undefined') return false;
        try {
            window.localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.warn(`Failed to write ${key} to localStorage:`, error);
            return false;
        }
    },

    remove: (key: string): boolean => {
        if (typeof window === 'undefined') return false;
        try {
            window.localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn(`Failed to remove ${key} from localStorage:`, error);
            return false;
        }
    },

    getString: (key: string): string | null => {
        if (typeof window === 'undefined') return null;
        try {
            return window.localStorage.getItem(key);
        } catch (error) {
            console.warn(`Failed to read ${key} from localStorage:`, error);
            return null;
        }
    },

    setString: (key: string, value: string): boolean => {
        if (typeof window === 'undefined') return false;
        try {
            window.localStorage.setItem(key, value);
            return true;
        } catch (error) {
            console.warn(`Failed to write ${key} to localStorage:`, error);
            return false;
        }
    },
};

/**
 * Format a timestamp to a human-readable string
 */
export const formatTimestamp = (
    timestamp: number,
    options?: Intl.DateTimeFormatOptions
): string => {
    const date = new Date(timestamp);
    return date.toLocaleString(undefined, {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        ...options,
    });
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (timestamp: number): string => {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'Just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;

    return formatTimestamp(timestamp);
};

/**
 * Format file size to human-readable string
 */
export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Truncate string with ellipsis
 */
export const truncate = (str: string, maxLength: number): string => {
    if (str.length <= maxLength) return str;
    return `${str.slice(0, maxLength)}…`;
};

/**
 * Generate a unique ID
 */
export const generateId = (prefix = 'id'): string => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return `${prefix}_${crypto.randomUUID()}`;
    }
    return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
};

/**
 * Debounce function execution
 */
export const debounce = <T extends (...args: unknown[]) => unknown>(
    func: T,
    wait: number
): ((...args: Parameters<T>) => void) => {
    let timeout: ReturnType<typeof setTimeout> | null = null;

    return (...args: Parameters<T>) => {
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};

/**
 * Throttle function execution
 */
export const throttle = <T extends (...args: unknown[]) => unknown>(
    func: T,
    limit: number
): ((...args: Parameters<T>) => void) => {
    let inThrottle = false;

    return (...args: Parameters<T>) => {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
};

/**
 * Class name utility (similar to clsx/classnames)
 */
export const cn = (...classes: (string | boolean | undefined | null)[]): string => {
    return classes.filter(Boolean).join(' ');
};

/**
 * Sleep utility for async operations
 */
export const sleep = (ms: number): Promise<void> => {
    return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Check if code is running on client side
 */
export const isClient = (): boolean => typeof window !== 'undefined';

/**
 * Check if code is running on server side
 */
export const isServer = (): boolean => typeof window === 'undefined';

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
    if (!isClient()) return false;

    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.warn('Failed to copy to clipboard:', error);
        // Fallback for older browsers
        try {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-9999px';
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        } catch {
            return false;
        }
    }
};
