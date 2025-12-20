import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { Moon, Sun, Box, Languages, ChevronRight, User, ChevronDown, Check, Github } from 'lucide-react';
import { triggerLanguageSwitch } from './Layout';

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
];

const Header: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const langMenuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (langMenuRef.current && !langMenuRef.current.contains(e.target as Node)) {
        setLangMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectLanguage = (langCode: string) => {
    if (langCode !== i18n.language) {
      // Store the selected language, then trigger the animation
      window.localStorage.setItem('cadlift_pending_lang', langCode);
      triggerLanguageSwitch();
    }
    setLangMenuOpen(false);
  };


  const isAuthPage = location.pathname === '/signin' || location.pathname === '/signup';

  const getUserInitials = () => {
    if (!user?.display_name) return 'U';
    return user.display_name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const currentLang = languages.find(l => l.code === i18n.language) || languages[0];

  return (
    <header className="sticky top-4 z-50 mx-4 sm:mx-6 lg:mx-8 mb-6">
      <div className="max-w-7xl mx-auto bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-2xl shadow-lg shadow-slate-200/50 dark:shadow-black/20 border border-slate-200/60 dark:border-slate-700/60 px-4 sm:px-6 h-16 flex items-center justify-between transition-all duration-300">

        {/* Left section - Logo + GitHub */}
        <div className="flex items-center gap-4">
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

          {/* GitHub Link */}
          <a
            href="https://github.com/Vartmor/CADLift"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:scale-105 transition-all text-sm font-bold shadow-md hover:shadow-lg"
          >
            <Github size={16} />
            <span>{t('navigation.viewOnGithub')}</span>
          </a>
        </div>

        {/* Center Navigation - Absolute positioned for true centering */}
        {!isAuthPage && (
          <nav className="hidden md:flex items-center gap-3 absolute left-1/2 -translate-x-1/2">
            {location.pathname !== '/dashboard' && (
              <button
                onClick={() => navigate('/dashboard')}
                className="group relative px-5 py-2 bg-gradient-to-r from-primary-600 to-blue-600 text-white rounded-xl font-bold text-sm shadow-lg shadow-primary-500/30 hover:shadow-primary-500/50 hover:scale-105 transition-all duration-300 flex items-center gap-2 overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                <span className="relative z-10">{t('navigation.dashboard_btn')}</span>
                <ChevronRight size={16} className="relative z-10 group-hover:translate-x-1 transition-transform" />
              </button>
            )}

            {/* About button - only on Home page */}
            {location.pathname === '/' && (
              <button
                onClick={() => navigate('/about')}
                className="px-5 py-2 rounded-xl text-sm font-semibold text-slate-600 dark:text-slate-300 bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200/50 dark:border-slate-700/50 hover:bg-slate-200/80 dark:hover:bg-slate-700/80 hover:text-slate-900 dark:hover:text-white transition-all"
              >
                {t('navigation.about')}
              </button>
            )}
          </nav>
        )}

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Language Dropdown */}
          <div ref={langMenuRef} className="relative hidden sm:block">
            <button
              onClick={() => setLangMenuOpen(!langMenuOpen)}
              className="group flex items-center gap-2 px-3 py-2 rounded-xl text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors outline-none"
              aria-label="Select Language"
            >
              <Languages size={18} className="group-hover:text-primary-500 transition-colors" />
              <span className="text-xs font-bold uppercase tracking-wider">{currentLang.code}</span>
              <ChevronDown size={14} className={`transition-transform ${langMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {langMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 py-2 z-50 animate-fade-in">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => selectLanguage(lang.code)}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${i18n.language === lang.code ? 'bg-primary-50 dark:bg-primary-900/20' : ''
                      }`}
                  >
                    <span className="text-lg">{lang.flag}</span>
                    <span className={`flex-1 font-medium ${i18n.language === lang.code ? 'text-primary-600 dark:text-primary-400' : 'text-slate-700 dark:text-slate-300'}`}>
                      {lang.name}
                    </span>
                    {i18n.language === lang.code && (
                      <Check size={16} className="text-primary-500" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

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

          {/* User Button (when authenticated) / Sign In (when not) */}
          {/* Avatar Only Logic */}
          <button
            onClick={() => isAuthenticated ? navigate('/profile') : navigate('/signin')}
            className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:shadow-md hover:scale-105 transition-all overflow-hidden"
            title={isAuthenticated ? 'Profile' : 'Sign In'}
          >
            {isAuthenticated ? (
              <div className="w-full h-full bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold">
                {getUserInitials()}
              </div>
            ) : (
              <User size={20} className="text-slate-500 dark:text-slate-400" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;

