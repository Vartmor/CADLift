import React from 'react';
import { useTranslation } from 'react-i18next';

const Profile: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-3xl mx-auto w-full bg-white/80 dark:bg-slate-900/70 backdrop-blur rounded-3xl border border-slate-200 dark:border-slate-800 shadow-lg p-8 space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-primary-500 to-blue-500 flex items-center justify-center text-white text-xl font-bold">
          U
        </div>
        <div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">User</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{t('navigation.resources')}</p>
        </div>
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Profile</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          This is your profile page. Link your docs, resources, and support from here as needed.
        </p>
      </div>
    </div>
  );
};

export default Profile;
