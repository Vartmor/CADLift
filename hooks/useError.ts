import { useState, useCallback } from 'react';

export interface ErrorState {
    message: string;
    code?: string;
    details?: Record<string, unknown>;
    timestamp: number;
}

interface UseErrorReturn {
    error: ErrorState | null;
    setError: (message: string, code?: string, details?: Record<string, unknown>) => void;
    clearError: () => void;
    hasError: boolean;
}

/**
 * Custom hook for managing error state in a component
 */
export function useError(): UseErrorReturn {
    const [error, setErrorState] = useState<ErrorState | null>(null);

    const setError = useCallback(
        (message: string, code?: string, details?: Record<string, unknown>) => {
            setErrorState({
                message,
                code,
                details,
                timestamp: Date.now(),
            });
        },
        []
    );

    const clearError = useCallback(() => {
        setErrorState(null);
    }, []);

    return {
        error,
        setError,
        clearError,
        hasError: error !== null,
    };
}

/**
 * Parse API errors into a user-friendly message
 */
export function parseApiError(error: unknown): string {
    if (error instanceof Error) {
        // Check for network errors
        if (error.message.includes('fetch')) {
            return 'Unable to connect to the server. Please check your internet connection.';
        }
        if (error.message.includes('timeout')) {
            return 'Request timed out. Please try again.';
        }
        return error.message;
    }

    if (typeof error === 'object' && error !== null) {
        // API error response
        const apiError = error as Record<string, unknown>;
        if (typeof apiError.detail === 'string') {
            return apiError.detail;
        }
        if (typeof apiError.message === 'string') {
            return apiError.message;
        }
    }

    if (typeof error === 'string') {
        return error;
    }

    return 'An unexpected error occurred. Please try again.';
}

export default useError;
