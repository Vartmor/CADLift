import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import {
  User,
  Mail,
  Calendar,
  LogOut,
  Shield,
  Palette,
  Globe,
  ChevronRight,
  Sparkles,
  Box,
  History,
  Key,
  Moon,
  Sun,
  Check,
  X,
  Save,
  Eye,
  EyeOff,
  AlertTriangle,
} from 'lucide-react';

// Modal component
const Modal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 max-w-md w-full max-h-[90vh] overflow-y-auto animate-fade-in-up">
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">{title}</h3>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X size={20} className="text-slate-500" />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

const Profile: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { theme, setTheme } = useTheme();

  // Modal states
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [showSessionsModal, setShowSessionsModal] = useState(false);
  const [showLoginHistory, setShowLoginHistory] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Form states
  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState(false);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const memberSince = new Date().toLocaleDateString(i18n.language === 'tr' ? 'tr-TR' : 'en-US', {
    month: 'long',
    year: 'numeric',
  });

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
  ];

  const currentLanguage = languages.find(l => l.code === i18n.language) || languages[0];

  const themeOptions = [
    { value: 'light' as const, label: t('profile.theme.light'), icon: Sun },
    { value: 'dark' as const, label: t('profile.theme.dark'), icon: Moon },
  ];

  const handleSaveProfile = async () => {
    setSaving(true);
    setErrorMessage('');
    try {
      // TODO: Implement API call to update profile
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setSuccessMessage(t('profile.modals.editProfile.success'));
      setTimeout(() => {
        setShowEditProfile(false);
        setSuccessMessage('');
      }, 1500);
    } catch {
      setErrorMessage(t('profile.modals.editProfile.error'));
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      setErrorMessage(t('profile.modals.changePassword.mismatch'));
      return;
    }
    setSaving(true);
    setErrorMessage('');
    try {
      // TODO: Implement API call to change password
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setSuccessMessage(t('profile.modals.changePassword.success'));
      setTimeout(() => {
        setShowChangePassword(false);
        setSuccessMessage('');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      }, 1500);
    } catch {
      setErrorMessage(t('profile.modals.changePassword.error'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">

      {/* Profile Header Card */}
      <div className="relative rounded-[2rem] overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-slate-900 dark:bg-slate-950" />
        <div className="absolute -top-20 -left-20 w-80 h-80 bg-cyan-500/20 rounded-full blur-[100px]" />
        <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-purple-500/20 rounded-full blur-[100px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-60 h-60 bg-violet-500/10 rounded-full blur-[80px]" />

        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
        </div>

        <div className="relative z-10 p-8 md:p-12">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 rounded-3xl blur opacity-40 group-hover:opacity-60 transition-opacity" />
              <div className="relative w-28 h-28 rounded-3xl bg-slate-800/80 backdrop-blur-xl flex items-center justify-center text-white text-4xl font-black ring-1 ring-white/10">
                {user ? getInitials(user.display_name) : 'U'}
              </div>
              <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-xl bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/50 ring-2 ring-slate-900">
                <Check size={16} className="text-white" />
              </div>
            </div>

            <div className="flex-1 text-white">
              <h1 className="text-3xl md:text-4xl font-black tracking-tight">
                {user?.display_name || 'User'}
              </h1>
              <div className="flex flex-wrap items-center gap-4 mt-3 text-slate-300">
                <div className="flex items-center gap-2">
                  <Mail size={16} className="text-cyan-400" />
                  <span className="text-sm font-medium">{user?.email || 'No email'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar size={16} className="text-purple-400" />
                  <span className="text-sm font-medium">{t('profile.memberSince')} {memberSince}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-4 mt-6">
                <div className="px-4 py-2 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
                  <span className="text-2xl font-bold text-cyan-400">0</span>
                  <span className="text-sm ml-2 text-slate-400">{i18n.language === 'tr' ? 'Proje' : 'Projects'}</span>
                </div>
                <div className="px-4 py-2 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
                  <span className="text-2xl font-bold text-purple-400">{t('profile.openSource')}</span>
                </div>
              </div>
            </div>

            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-red-500/10 hover:bg-red-500/20 backdrop-blur-sm text-red-400 font-semibold transition-all hover:scale-105 border border-red-500/20"
            >
              <LogOut size={18} />
              {t('auth.signOut')}
            </button>
          </div>
        </div>
      </div>

      {/* Settings Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* Account Settings */}
        <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 dark:bg-cyan-500/20 flex items-center justify-center text-cyan-600 dark:text-cyan-400 ring-1 ring-cyan-500/20">
                <User size={24} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{t('profile.settings.account')}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{i18n.language === 'tr' ? 'Profilinizi yönetin' : 'Manage your profile'}</p>
              </div>
            </div>
            <div className="space-y-3">
              <button
                onClick={() => {
                  setDisplayName(user?.display_name || '');
                  setShowEditProfile(true);
                }}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <User size={18} className="text-slate-500 dark:text-slate-400" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('profile.actions.editProfile')}</span>
                </div>
                <ChevronRight size={18} className="text-slate-400" />
              </button>
              <button
                onClick={() => {
                  setCurrentPassword('');
                  setNewPassword('');
                  setConfirmPassword('');
                  setShowChangePassword(true);
                }}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <Key size={18} className="text-slate-500 dark:text-slate-400" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('profile.actions.changePassword')}</span>
                </div>
                <ChevronRight size={18} className="text-slate-400" />
              </button>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-purple-500/10 dark:bg-purple-500/20 flex items-center justify-center text-purple-600 dark:text-purple-400 ring-1 ring-purple-500/20">
                <Palette size={24} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{i18n.language === 'tr' ? 'Tercihler' : 'Preferences'}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{i18n.language === 'tr' ? 'Deneyiminizi özelleştirin' : 'Customize your experience'}</p>
              </div>
            </div>
            <div className="space-y-4">
              {/* Theme Toggle */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400">
                  <Palette size={16} />
                  {t('profile.settings.appearance')}
                </label>
                <div className="flex gap-2">
                  {themeOptions.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setTheme(opt.value)}
                      className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-xl font-medium text-sm transition-all ${theme === opt.value
                        ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-lg'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
                        }`}
                    >
                      <opt.icon size={16} />
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Language Selector */}
              <div className="space-y-2 relative">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400">
                  <Globe size={16} />
                  {t('profile.settings.language')}
                </label>
                <button
                  onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                  className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <span className="text-lg">{currentLanguage.flag}</span>
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{currentLanguage.name}</span>
                  </span>
                  <ChevronRight size={18} className={`text-slate-400 transition-transform ${showLanguageMenu ? 'rotate-90' : ''}`} />
                </button>

                {showLanguageMenu && (
                  <div className="absolute z-20 top-full left-0 right-0 mt-2 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xl">
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          i18n.changeLanguage(lang.code);
                          setShowLanguageMenu(false);
                        }}
                        className={`w-full flex items-center justify-between px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ${i18n.language === lang.code ? 'bg-slate-50 dark:bg-slate-700/50' : ''
                          }`}
                      >
                        <span className="flex items-center gap-3">
                          <span className="text-lg">{lang.flag}</span>
                          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{lang.name}</span>
                        </span>
                        {i18n.language === lang.code && (
                          <Check size={16} className="text-emerald-500" />
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Security */}
        <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
          <div className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 dark:bg-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20">
                <Shield size={24} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{t('profile.settings.security')}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{i18n.language === 'tr' ? 'Hesabınızı güvende tutun' : 'Keep your account safe'}</p>
              </div>
            </div>
            <div className="space-y-3">
              <button
                onClick={() => alert(t('profile.modals.twoFactorMessage'))}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
              >
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('profile.actions.twoFactor')}</span>
                <span className="text-sm font-semibold text-slate-500">{i18n.language === 'tr' ? 'Kapalı' : 'Off'}</span>
              </button>
              <button
                onClick={() => setShowSessionsModal(true)}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
              >
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('profile.actions.activeSessions')}</span>
                <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">1 {i18n.language === 'tr' ? 'cihaz' : 'device'}</span>
              </button>
              <button
                onClick={() => setShowLoginHistory(true)}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
              >
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('profile.actions.loginHistory')}</span>
                <span className="text-sm font-semibold text-cyan-600 dark:text-cyan-400">{i18n.language === 'tr' ? 'Görüntüle' : 'View'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Activity - Full width */}
        <div className="md:col-span-2 lg:col-span-3 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-amber-500/10 dark:bg-amber-500/20 flex items-center justify-center text-amber-600 dark:text-amber-400 ring-1 ring-amber-500/20">
                  <History size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">{i18n.language === 'tr' ? 'Son Aktiviteler' : 'Recent Activity'}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{i18n.language === 'tr' ? 'Son dönüşümleriniz' : 'Your latest conversions'}</p>
                </div>
              </div>
              <button
                onClick={() => navigate('/dashboard#activity')}
                className="flex items-center gap-2 text-cyan-600 dark:text-cyan-400 font-semibold text-sm hover:underline"
              >
                {i18n.language === 'tr' ? 'Tümünü Gör' : 'View All'}
                <ChevronRight size={16} />
              </button>
            </div>

            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-20 h-20 rounded-3xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4 ring-1 ring-slate-200 dark:ring-slate-700">
                <Box size={36} className="text-slate-400" />
              </div>
              <p className="text-lg font-semibold text-slate-700 dark:text-slate-300">{i18n.language === 'tr' ? 'Henüz dönüşüm yok' : 'No conversions yet'}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-md">
                {i18n.language === 'tr'
                  ? 'Panelden CAD dosyaları, görüntüler veya promptlar ile 3D modeller oluşturmaya başlayın.'
                  : 'Start creating 3D models from CAD files, images, or prompts in the dashboard.'}
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="mt-6 px-6 py-3 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center gap-2"
              >
                <Sparkles size={18} />
                {i18n.language === 'tr' ? 'İlk Modelinizi Oluşturun' : 'Create Your First Model'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="rounded-3xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 p-6">
        <h3 className="text-lg font-bold text-red-700 dark:text-red-400 mb-2">{t('profile.settings.dangerZone')}</h3>
        <p className="text-sm text-red-600/80 dark:text-red-400/80 mb-4">
          {i18n.language === 'tr' ? 'Geri alınamayan kalıcı işlemler.' : 'Permanent actions that cannot be undone.'}
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="px-4 py-2 rounded-xl border-2 border-red-300 dark:border-red-800 text-red-600 dark:text-red-400 font-semibold text-sm hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
          >
            {t('profile.actions.deleteData')}
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="px-4 py-2 rounded-xl border-2 border-red-300 dark:border-red-800 text-red-600 dark:text-red-400 font-semibold text-sm hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
          >
            {t('profile.actions.deleteAccount')}
          </button>
        </div>
      </div>

      {/* Edit Profile Modal */}
      <Modal isOpen={showEditProfile} onClose={() => setShowEditProfile(false)} title={t('profile.modals.editProfile.title')}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">{t('profile.modals.editProfile.displayName')}</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
              placeholder={i18n.language === 'tr' ? 'Adınız' : 'Your name'}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Email</label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-slate-500 cursor-not-allowed"
            />
            <p className="text-xs text-slate-500 mt-1">{i18n.language === 'tr' ? 'E-posta değiştirilemez' : 'Email cannot be changed'}</p>
          </div>

          {successMessage && (
            <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-sm font-medium flex items-center gap-2">
              <Check size={16} /> {successMessage}
            </div>
          )}
          {errorMessage && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm font-medium">
              {errorMessage}
            </div>
          )}

          <button
            onClick={handleSaveProfile}
            disabled={saving}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold hover:scale-[1.02] transition-transform disabled:opacity-50"
          >
            {saving ? t('profile.modals.editProfile.saving') : <><Save size={18} /> {t('profile.modals.editProfile.save')}</>}
          </button>
        </div>
      </Modal>

      {/* Change Password Modal */}
      <Modal isOpen={showChangePassword} onClose={() => setShowChangePassword(false)} title={t('profile.modals.changePassword.title')}>
        <div className="space-y-4">
          <div className="relative">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">{t('profile.modals.changePassword.current')}</label>
            <input
              type={showPasswords ? 'text' : 'password'}
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-4 py-3 pr-12 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-cyan-500"
              placeholder="••••••••"
            />
          </div>
          <div className="relative">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">{t('profile.modals.changePassword.new')}</label>
            <input
              type={showPasswords ? 'text' : 'password'}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-4 py-3 pr-12 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-cyan-500"
              placeholder="••••••••"
            />
            <p className="text-xs text-slate-500 mt-1">{t('profile.modals.changePassword.hint')}</p>
          </div>
          <div className="relative">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">{t('profile.modals.changePassword.confirm')}</label>
            <input
              type={showPasswords ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-3 pr-12 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-cyan-500"
              placeholder="••••••••"
            />
          </div>

          <button
            type="button"
            onClick={() => setShowPasswords(!showPasswords)}
            className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          >
            {showPasswords ? <EyeOff size={16} /> : <Eye size={16} />}
            {showPasswords
              ? (i18n.language === 'tr' ? 'Şifreleri gizle' : 'Hide passwords')
              : (i18n.language === 'tr' ? 'Şifreleri göster' : 'Show passwords')}
          </button>

          {successMessage && (
            <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-sm font-medium flex items-center gap-2">
              <Check size={16} /> {successMessage}
            </div>
          )}
          {errorMessage && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm font-medium">
              {errorMessage}
            </div>
          )}

          <button
            onClick={handleChangePassword}
            disabled={saving || !currentPassword || !newPassword || !confirmPassword}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold hover:scale-[1.02] transition-transform disabled:opacity-50"
          >
            {saving ? t('profile.modals.changePassword.saving') : <><Key size={18} /> {t('profile.modals.changePassword.save')}</>}
          </button>
        </div>
      </Modal>

      {/* Active Sessions Modal */}
      <Modal isOpen={showSessionsModal} onClose={() => setShowSessionsModal(false)} title={t('profile.modals.sessions.title')}>
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-slate-900 dark:text-white">{t('profile.modals.sessions.current')}</p>
                <p className="text-sm text-slate-500">Windows • Chrome • {i18n.language === 'tr' ? 'Şimdi' : 'Just now'}</p>
              </div>
              <span className="px-2 py-1 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold">{i18n.language === 'tr' ? 'Aktif' : 'Active'}</span>
            </div>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 text-center">
            {i18n.language === 'tr' ? 'Bu tek aktif oturumunuz.' : 'This is your only active session.'}
          </p>
        </div>
      </Modal>

      {/* Login History Modal */}
      <Modal isOpen={showLoginHistory} onClose={() => setShowLoginHistory(false)} title={t('profile.modals.loginHistory.title')}>
        <div className="space-y-3">
          {[
            { date: i18n.language === 'tr' ? 'Bugün, 18:10' : 'Today, 6:10 PM', device: 'Windows • Chrome', location: i18n.language === 'tr' ? 'Mevcut oturum' : 'Current session' },
            { date: i18n.language === 'tr' ? 'Bugün, 14:30' : 'Today, 2:30 PM', device: 'Windows • Chrome', location: i18n.language === 'tr' ? 'Çıkış yapıldı' : 'Signed out' },
          ].map((item, i) => (
            <div key={i} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <p className="font-medium text-slate-900 dark:text-white text-sm">{item.date}</p>
              <p className="text-xs text-slate-500">{item.device}</p>
              <p className="text-xs text-slate-400">{item.location}</p>
            </div>
          ))}
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={showDeleteConfirm} onClose={() => setShowDeleteConfirm(false)} title={t('profile.modals.deleteConfirm.title')}>
        <div className="space-y-4 text-center">
          <div className="w-16 h-16 mx-auto rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <AlertTriangle size={32} className="text-red-500" />
          </div>
          <p className="text-slate-700 dark:text-slate-300">
            {t('profile.modals.deleteConfirm.warning')}
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="flex-1 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              {t('profile.modals.deleteConfirm.cancel')}
            </button>
            <button
              onClick={() => alert(i18n.language === 'tr' ? 'Özellik henüz uygulanmadı' : 'Feature not implemented yet')}
              className="flex-1 px-4 py-3 rounded-xl bg-red-500 text-white font-semibold hover:bg-red-600 transition-colors"
            >
              {t('profile.modals.deleteConfirm.confirm')}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Profile;
