/**
 * Auth API service - communicates with backend /api/v1/auth endpoints
 */

// Use environment variable for API URL in production, fallback to relative for dev
const API_URL = import.meta.env.VITE_API_URL || '';
const API_BASE = `${API_URL}/api/v1/auth`;

export interface User {
    id: string;
    email: string;
    display_name: string;
    locale?: string;
    theme?: string;
}

export interface AuthTokens {
    access_token: string;
    refresh_token: string;
    user: User;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    display_name: string;
    locale?: string;
    theme?: string;
}

// Token storage
const TOKEN_KEY = 'cadlift_access_token';
const REFRESH_KEY = 'cadlift_refresh_token';
const USER_KEY = 'cadlift_user';

export const authService = {
    /**
     * Login with email and password
     */
    async login(credentials: LoginCredentials): Promise<AuthTokens> {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Login failed' }));
            throw new Error(error.detail || 'Login failed');
        }

        const data: AuthTokens = await response.json();
        this.setTokens(data);
        return data;
    },

    /**
     * Register new user
     */
    async register(data: RegisterData): Promise<AuthTokens> {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
            // FastAPI validation errors come as array in detail
            if (Array.isArray(error.detail)) {
                const messages = error.detail.map((e: { loc?: string[], msg?: string }) =>
                    e.msg || 'Validation error'
                ).join(', ');
                throw new Error(messages);
            }
            throw new Error(error.detail || 'Registration failed');
        }

        const result: AuthTokens = await response.json();
        this.setTokens(result);
        return result;
    },

    /**
     * Logout and revoke refresh token
     */
    async logout(): Promise<void> {
        const refreshToken = localStorage.getItem(REFRESH_KEY);

        if (refreshToken) {
            try {
                await fetch(`${API_BASE}/logout`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken }),
                });
            } catch {
                // Ignore logout errors
            }
        }

        this.clearTokens();
    },

    /**
     * Refresh access token
     */
    async refresh(): Promise<AuthTokens | null> {
        const refreshToken = localStorage.getItem(REFRESH_KEY);
        if (!refreshToken) return null;

        try {
            const response = await fetch(`${API_BASE}/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (!response.ok) {
                this.clearTokens();
                return null;
            }

            const data: AuthTokens = await response.json();
            this.setTokens(data);
            return data;
        } catch {
            this.clearTokens();
            return null;
        }
    },

    /**
     * Get stored access token
     */
    getAccessToken(): string | null {
        return localStorage.getItem(TOKEN_KEY);
    },

    /**
     * Get stored user
     */
    getUser(): User | null {
        const userJson = localStorage.getItem(USER_KEY);
        if (!userJson) return null;
        try {
            return JSON.parse(userJson);
        } catch {
            return null;
        }
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated(): boolean {
        return !!this.getAccessToken() && !!this.getUser();
    },

    /**
     * Store tokens and user
     */
    setTokens(data: AuthTokens): void {
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);
        localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    },

    /**
     * Clear all auth data
     */
    clearTokens(): void {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem(USER_KEY);
    },

    /**
     * Make authenticated request
     */
    async fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
        const token = this.getAccessToken();
        const headers = {
            ...options.headers,
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        };

        let response = await fetch(url, { ...options, headers });

        // If 401, try to refresh and retry
        if (response.status === 401) {
            const refreshed = await this.refresh();
            if (refreshed) {
                const newHeaders = {
                    ...options.headers,
                    Authorization: `Bearer ${refreshed.access_token}`,
                };
                response = await fetch(url, { ...options, headers: newHeaders });
            }
        }

        return response;
    },
};

export default authService;
