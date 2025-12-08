import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Mail, Lock, User, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      fill="#4285F4"
    />
    <path
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      fill="#34A853"
    />
    <path
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      fill="#FBBC05"
    />
    <path
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      fill="#EA4335"
    />
  </svg>
);

const SignUp: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { signUp, isAuthenticated } = useAuth();
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await signUp({ email, password, display_name: displayName });
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.signUp.failed'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center py-12 px-4 w-full min-h-[80vh] relative z-0">
      <div className="w-full max-w-md relative">

        {/* Decorative Elements behind card - Added pointer-events-none */}
        <div className="absolute top-10 -left-20 w-72 h-72 bg-purple-500/10 rounded-full blur-[80px] animate-pulse pointer-events-none"></div>
        <div className="absolute -bottom-10 -right-10 w-60 h-60 bg-primary-500/10 rounded-full blur-[80px] pointer-events-none"></div>

        {/* Card */}
        <div className="relative bg-white/80 dark:bg-slate-900/80 backdrop-blur-2xl border border-white/20 dark:border-slate-700/50 shadow-2xl rounded-3xl overflow-hidden ring-1 ring-slate-900/5 dark:ring-white/10 animate-fade-in z-10">

          <div className="h-1.5 bg-gradient-to-r from-blue-500 via-primary-500 to-purple-500 w-full"></div>

          <div className="p-8 md:p-10">
            <div className="text-center mb-10">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 mb-6 shadow-lg border border-white/50 dark:border-slate-700">
                <Box className="w-7 h-7 text-primary-600 dark:text-primary-400" strokeWidth={2} />
              </div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">{t('auth.signUp.title')}</h2>
              <p className="text-slate-500 dark:text-slate-400 text-sm mt-2 font-medium">{t('auth.signUp.subtitle')}</p>
              {error && (
                <div className="mt-4 p-3 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm font-medium">
                  {error}
                </div>
              )}
            </div>

            <form onSubmit={handleSignUp} className="space-y-5">

              {/* Name Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 ml-1">{t('auth.signUp.nameLabel')}</label>
                <div className="relative group">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary-500 transition-colors duration-300 pointer-events-none">
                    <User size={20} />
                  </div>
                  <input
                    type="text"
                    placeholder={t('auth.signUp.namePlaceholder')}
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="w-full bg-slate-50/50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-700 rounded-xl py-3.5 pl-12 pr-4 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all font-medium shadow-sm"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Email Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 ml-1">{t('auth.signUp.emailLabel')}</label>
                <div className="relative group">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary-500 transition-colors duration-300 pointer-events-none">
                    <Mail size={20} />
                  </div>
                  <input
                    type="email"
                    placeholder={t('auth.signUp.emailPlaceholder')}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-50/50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-700 rounded-xl py-3.5 pl-12 pr-4 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all font-medium shadow-sm"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 ml-1">{t('auth.signUp.passwordLabel')}</label>
                <div className="relative group">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary-500 transition-colors duration-300 pointer-events-none">
                    <Lock size={20} />
                  </div>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-slate-50/50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-700 rounded-xl py-3.5 pl-12 pr-4 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all font-medium shadow-sm"
                    required
                    disabled={isLoading}
                  />
                </div>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 ml-1">{t('auth.signUp.passwordHint')}</p>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full group bg-slate-900 dark:bg-white text-white dark:text-slate-900 py-4 rounded-xl font-bold text-lg shadow-lg shadow-slate-900/20 hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-4 cursor-pointer z-20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <><Loader2 size={20} className="animate-spin" /> {t('auth.signUp.submitting')}</>
                ) : (
                  <><span>{t('auth.signUp.submit')}</span><ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" /></>
                )}
              </button>
            </form>

            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200 dark:border-slate-700"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase tracking-widest">
                <span className="bg-white dark:bg-slate-900 px-4 text-slate-400 font-bold">{t('auth.signUp.or')}</span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 py-3.5 rounded-xl font-bold flex items-center justify-center gap-3 hover:bg-slate-50 dark:hover:bg-slate-750 hover:border-slate-300 dark:hover:border-slate-600 transition-all shadow-sm cursor-pointer z-20"
            >
              <GoogleIcon />
              <span>{t('auth.signUp.googleSignUp')}</span>
            </button>

            <div className="text-center mt-8 pt-2">
              <p className="text-slate-500 dark:text-slate-400 text-sm">
                {t('auth.signUp.hasAccount')}{' '}
                <button onClick={() => navigate('/signin')} className="text-primary-600 dark:text-primary-400 font-bold hover:underline decoration-2 underline-offset-4">
                  {t('auth.signUp.signIn')}
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;