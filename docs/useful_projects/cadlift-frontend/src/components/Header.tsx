
import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../contexts/ThemeContext';
import { 
  Moon, Sun, Box, Languages, ChevronRight, Menu, X, 
  LogOut, User, Settings, FileText, LayoutDashboard, FolderOpen 
} from 'lucide-react';

const Header: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'tr' : 'en';
    i18n.changeLanguage(newLang);
  };

  // Check if we are in authenticated view (Dashboard)
  // For MVP, we treat /dashboard as the authenticated state
  const isDashboard = location.pathname === '/dashboard' || location.pathname.startsWith('/dashboard');
  const isAuthPage = location.pathname === '/signin' || location.pathname === '/signup';

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  const navLinks = isDashboard 
    ? [
        { label: 'nav.dashboard', path: '/dashboard', icon: <LayoutDashboard size={18} /> },
        { label: 'nav.projects', path: '#projects', icon: <FolderOpen size={18} /> }, // Placeholder
        { label: 'nav.docs', path: '#docs', icon: <FileText size={18} /> }, // Placeholder
        { label: 'nav.about', path: '/about', icon: <Box size={18} /> },
      ]
    : [
        { label: 'nav.home', path: '/', icon: <Box size={18} /> },
        { label: 'nav.about', path: '/about', icon: <FileText size={18} /> },
      ];

  return (
    <>
      <header className="sticky top-4 z-50 mx-4 sm:mx-6 lg:mx-8 mb-6">
        <div className="max-w-7xl mx-auto bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg rounded-2xl shadow-lg shadow-slate-200/50 dark:shadow-black/20 border border-slate-200/60 dark:border-slate-700/60 px-4 sm:px-6 h-16 flex items-center justify-between transition-all duration-300">
          
          {/* Logo */}
          <div 
            onClick={() => navigate(isDashboard ? '/dashboard' : '/')} 
            className="flex items-center space-x-3 group cursor-pointer select-none"
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && navigate(isDashboard ? '/dashboard' : '/')}
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

          {/* Desktop Navigation */}
          {!isAuthPage && (
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <button 
                  key={link.path}
                  onClick={() => navigate(link.path)}
                  className={`px-4 py-2 rounded-xl text-sm font-bold transition-all duration-200 flex items-center gap-2
                    ${location.pathname === link.path 
                      ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' 
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                >
                  {link.label === 'nav.projects' || link.label === 'nav.docs' ? (
                    // Assuming these are placeholders for now
                    <span className="opacity-60 hover:opacity-100 flex items-center gap-2">{link.label === 'nav.projects' ? t(link.label) : t(link.label)}</span>
                  ) : (
                    <>
                      {/* {link.icon} Optional icon display */}
                      {t(link.label)}
                    </>
                  )}
                </button>
              ))}
            </nav>
          )}

          {/* Controls */}
          <div className="flex items-center gap-2 sm:gap-3">
            
            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              className="hidden sm:flex group relative p-2.5 rounded-xl text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors outline-none"
              title={i18n.language === 'en' ? "Türkçe'ye geç" : "Switch to English"}
            >
              <div className="flex items-center space-x-1.5">
                <Languages size={18} className="group-hover:text-primary-500 transition-colors" />
                <span className="text-xs font-bold uppercase tracking-wider">{i18n.language}</span>
              </div>
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors outline-none overflow-hidden relative"
              title={theme === 'light' ? t('common.theme_dark') : t('common.theme_light')}
            >
              <div className="relative z-10 group-hover:text-amber-500 dark:group-hover:text-yellow-400 transition-colors">
                {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
              </div>
            </button>

            <div className="h-6 w-px bg-slate-200 dark:bg-slate-700 mx-1 hidden sm:block"></div>

            {/* Auth / Profile Section */}
            {isDashboard ? (
              <div className="relative" ref={profileRef}>
                <button 
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center gap-2 pl-2 pr-1 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-750 rounded-full border border-slate-200 dark:border-slate-700 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-500 to-blue-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    JD
                  </div>
                  <ChevronRight size={16} className={`text-slate-400 transition-transform duration-300 ${isProfileOpen ? 'rotate-90' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {isProfileOpen && (
                  <div className="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-slate-900 rounded-2xl shadow-xl shadow-slate-200/50 dark:shadow-black/40 border border-slate-200 dark:border-slate-700 overflow-hidden animate-fade-in-up origin-top-right">
                    <div className="p-4 border-b border-slate-100 dark:border-slate-800">
                      <p className="text-sm font-bold text-slate-900 dark:text-white">John Doe</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 truncate">engineer@cadlift.io</p>
                    </div>
                    <div className="p-1">
                      <button className="w-full text-left flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl transition-colors">
                        <User size={16} />
                        {t('nav.profile')}
                      </button>
                      <button className="w-full text-left flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl transition-colors">
                        <Settings size={16} />
                        {t('nav.settings')}
                      </button>
                      <div className="h-px bg-slate-100 dark:bg-slate-800 my-1"></div>
                      <button 
                        onClick={() => navigate('/signin')}
                        className="w-full text-left flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors"
                      >
                        <LogOut size={16} />
                        {t('nav.signout')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button 
                onClick={() => navigate('/signin')}
                className={`flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-5 py-2.5 rounded-xl text-sm font-bold hover:scale-105 transition-transform shadow-lg hover:shadow-xl cursor-pointer ${isAuthPage ? 'hidden' : ''}`}
              >
                <span className="hidden sm:inline">{t('nav.signin')}</span>
                <ChevronRight size={14} className="opacity-60" />
              </button>
            )}

            {/* Mobile Menu Button */}
            {!isAuthPage && (
              <button 
                onClick={() => setIsMobileMenuOpen(true)}
                className="md:hidden p-2.5 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <Menu size={24} />
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-[60] md:hidden">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-slate-900/20 dark:bg-black/50 backdrop-blur-sm animate-fade-in"
            onClick={() => setIsMobileMenuOpen(false)}
          ></div>
          
          {/* Menu Panel */}
          <div className="absolute right-0 top-0 bottom-0 w-3/4 max-w-sm bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col animate-fade-in p-6">
            <div className="flex items-center justify-between mb-8">
              <span className="text-xl font-black text-slate-900 dark:text-white">{t('common.title')}</span>
              <button 
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <X size={24} className="text-slate-500" />
              </button>
            </div>

            <nav className="flex-grow space-y-2">
              {navLinks.map((link) => (
                 <button 
                  key={link.path}
                  onClick={() => navigate(link.path)}
                  className={`w-full text-left px-4 py-4 rounded-2xl text-lg font-bold transition-all duration-200 flex items-center gap-4
                    ${location.pathname === link.path 
                      ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' 
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                >
                  {link.icon}
                  {t(link.label)}
                </button>
              ))}
            </nav>

            <div className="pt-8 border-t border-slate-100 dark:border-slate-800 space-y-4">
              <button 
                onClick={toggleLanguage}
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-800/50"
              >
                <span className="font-medium text-slate-600 dark:text-slate-300">Language</span>
                <div className="flex items-center gap-2 text-sm font-bold text-primary-600 dark:text-primary-400">
                  <Languages size={18} />
                  <span className="uppercase">{i18n.language}</span>
                </div>
              </button>

               {isDashboard && (
                 <button 
                  onClick={() => navigate('/signin')}
                  className="w-full flex items-center justify-center gap-2 px-4 py-4 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 font-bold"
                >
                  <LogOut size={20} />
                  {t('nav.signout')}
                </button>
               )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Header;
