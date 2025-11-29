import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../contexts/ThemeContext';
import { Moon, Sun, Box, Languages, ChevronRight } from 'lucide-react';

const Header: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'tr' : 'en';
    i18n.changeLanguage(newLang);
  };

  const isActive = (path: string) => location.pathname === path;
  
  // Check if we are in auth pages to hide navigation elements
  const isAuthPage = location.pathname === '/signin' || location.pathname === '/signup';
  const isDashboard = location.pathname === '/dashboard';

  return (
    <header className="sticky top-4 z-50 mx-4 sm:mx-6 lg:mx-8 mb-6">
      <div className="max-w-7xl mx-auto bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-2xl shadow-lg shadow-slate-200/50 dark:shadow-black/20 border border-slate-200/60 dark:border-slate-700/60 px-4 sm:px-6 h-16 flex items-center justify-between transition-all duration-300">
        
        {/* Logo */}
        <div 
          onClick={() => navigate('/')} 
          className="flex items-center space-x-3 group cursor-pointer"
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/')}
        >
          <div className="relative">
            <div className="absolute inset-0 bg-primary-500 blur-md opacity-40 group-hover:opacity-60 transition-opacity rounded-lg"></div>
            <div className="relative w-10 h-10 bg-gradient-to-br from-primary-600 to-blue-700 dark:from-primary-500 dark:to-blue-600 rounded-xl flex items-center justify-center text-white shadow-sm ring-1 ring-white/20">
              <Box size={22} strokeWidth={2.5} className="transform group-hover:rotate-12 transition-transform duration-500 ease-out" />
            </div>
          </div>
          <span className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-slate-700 to-slate-900 dark:from-white dark:via-slate-200 dark:to-slate-400">
            {t('common.title')}
          </span>
        </div>

        {/* Navigation Desktop */}
        {!isAuthPage && (
          <nav className="hidden md:flex items-center bg-slate-100/50 dark:bg-slate-800/50 px-2 py-1.5 rounded-full border border-slate-200/50 dark:border-slate-700/50">
            <button 
              onClick={() => navigate('/')}
              className={`px-5 py-1.5 rounded-full text-sm font-medium transition-all duration-300 outline-none focus-visible:ring-2 focus-visible:ring-primary-500 ${
                isActive('/') 
                  ? 'bg-white dark:bg-slate-700 text-primary-600 dark:text-primary-400 shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/50 dark:hover:bg-slate-700/50'
              }`}
            >
              {t('common.home')}
            </button>
            <button 
              onClick={() => navigate('/about')}
              className={`px-5 py-1.5 rounded-full text-sm font-medium transition-all duration-300 outline-none focus-visible:ring-2 focus-visible:ring-primary-500 ${
                isActive('/about') 
                  ? 'bg-white dark:bg-slate-700 text-primary-600 dark:text-primary-400 shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/50 dark:hover:bg-slate-700/50'
              }`}
            >
              {t('common.about')}
            </button>
          </nav>
        )}

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Language Toggle */}
          <button
            onClick={toggleLanguage}
            className="hidden sm:flex group relative p-2 rounded-xl text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors outline-none"
            aria-label="Toggle Language"
          >
            <div className="flex items-center space-x-1">
              <Languages size={18} className="group-hover:text-primary-500 transition-colors" />
              <span className="text-xs font-bold uppercase tracking-wider">{i18n.language}</span>
            </div>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors outline-none overflow-hidden relative"
            aria-label="Toggle Theme"
          >
             <div className="relative z-10 group-hover:text-yellow-500 dark:group-hover:text-yellow-400 transition-colors">
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
             </div>
          </button>

          <div className="h-6 w-px bg-slate-200 dark:bg-slate-700 mx-1 hidden sm:block"></div>

          {/* Sign In / User Button */}
          {isDashboard ? (
             <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-primary-500 to-blue-500 flex items-center justify-center text-white text-xs font-bold">
                  U
                </div>
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 hidden sm:inline">User</span>
             </div>
          ) : (
            <button 
              onClick={() => navigate('/signin')}
              className={`flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2 rounded-xl text-sm font-bold hover:scale-105 transition-transform shadow-lg hover:shadow-xl cursor-pointer ${isAuthPage ? 'hidden' : ''}`}
            >
              <span className="hidden sm:inline">Sign In</span>
              <ChevronRight size={14} className="opacity-60" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;