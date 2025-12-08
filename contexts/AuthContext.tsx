/**
 * Auth Context - provides authentication state and methods to the app
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService, User, LoginCredentials, RegisterData } from '../services/auth';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    signIn: (credentials: LoginCredentials) => Promise<void>;
    signUp: (data: RegisterData) => Promise<void>;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Initialize auth state from storage
    useEffect(() => {
        const storedUser = authService.getUser();
        if (storedUser && authService.isAuthenticated()) {
            setUser(storedUser);
        }
        setIsLoading(false);
    }, []);

    const signIn = useCallback(async (credentials: LoginCredentials) => {
        const result = await authService.login(credentials);
        setUser(result.user);
    }, []);

    const signUp = useCallback(async (data: RegisterData) => {
        const result = await authService.register(data);
        setUser(result.user);
    }, []);

    const signOut = useCallback(async () => {
        await authService.logout();
        setUser(null);
    }, []);

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                isLoading,
                signIn,
                signUp,
                signOut,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthContext;
