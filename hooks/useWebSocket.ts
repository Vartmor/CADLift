import { useEffect, useRef, useState, useCallback } from 'react';
import { env } from '../config/env';
import { JobStatus } from '../types';

interface WebSocketMessage {
    type: 'job_update' | 'job_completed' | 'job_failed' | 'ping' | 'pong';
    job_id?: string;
    status?: JobStatus;
    progress?: number;
    error?: string;
    data?: Record<string, unknown>;
}

interface UseWebSocketOptions {
    onMessage?: (message: WebSocketMessage) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    onError?: (error: Event) => void;
    reconnectAttempts?: number;
    reconnectInterval?: number;
    autoConnect?: boolean;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    send: (message: WebSocketMessage) => void;
    connect: () => void;
    disconnect: () => void;
    subscribeToJob: (jobId: string) => void;
    unsubscribeFromJob: (jobId: string) => void;
}

/**
 * Custom hook for WebSocket connection with automatic reconnection
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
    const {
        onMessage,
        onConnect,
        onDisconnect,
        onError,
        reconnectAttempts = 5,
        reconnectInterval = 3000,
        autoConnect = true,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectCountRef = useRef(0);
    const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
    const subscribedJobsRef = useRef<Set<string>>(new Set());

    const getWebSocketUrl = useCallback(() => {
        const baseUrl = env.API_BASE_URL || window.location.origin;
        const wsUrl = baseUrl.replace(/^http/, 'ws');
        return `${wsUrl}/ws/jobs`;
    }, []);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            const wsUrl = getWebSocketUrl();
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                setIsConnected(true);
                reconnectCountRef.current = 0;
                onConnect?.();

                // Re-subscribe to any jobs we were tracking
                subscribedJobsRef.current.forEach((jobId) => {
                    wsRef.current?.send(JSON.stringify({ type: 'subscribe', job_id: jobId }));
                });
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data) as WebSocketMessage;
                    onMessage?.(message);
                } catch (error) {
                    console.warn('Failed to parse WebSocket message:', error);
                }
            };

            wsRef.current.onclose = () => {
                setIsConnected(false);
                onDisconnect?.();

                // Attempt to reconnect
                if (reconnectCountRef.current < reconnectAttempts) {
                    reconnectCountRef.current += 1;
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, reconnectInterval);
                }
            };

            wsRef.current.onerror = (error) => {
                onError?.(error);
            };
        } catch (error) {
            console.warn('Failed to create WebSocket connection:', error);
        }
    }, [getWebSocketUrl, onConnect, onDisconnect, onError, onMessage, reconnectAttempts, reconnectInterval]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectCountRef.current = reconnectAttempts; // Prevent auto-reconnect
        wsRef.current?.close();
        wsRef.current = null;
        setIsConnected(false);
    }, [reconnectAttempts]);

    const send = useCallback((message: WebSocketMessage) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not connected. Message not sent.');
        }
    }, []);

    const subscribeToJob = useCallback((jobId: string) => {
        subscribedJobsRef.current.add(jobId);
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'subscribe', job_id: jobId }));
        }
    }, []);

    const unsubscribeFromJob = useCallback((jobId: string) => {
        subscribedJobsRef.current.delete(jobId);
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'unsubscribe', job_id: jobId }));
        }
    }, []);

    // Auto-connect on mount if enabled
    useEffect(() => {
        if (autoConnect && env.API_BASE_URL) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [autoConnect, connect, disconnect]);

    return {
        isConnected,
        send,
        connect,
        disconnect,
        subscribeToJob,
        unsubscribeFromJob,
    };
}

export default useWebSocket;
