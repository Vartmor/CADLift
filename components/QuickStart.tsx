import React from 'react';
import { useTranslation } from 'react-i18next';
import { Rocket, PenTool, Image as ImageIcon, MessageCircle } from 'lucide-react';

interface QuickStartProps {
  onCad: () => void;
  onImage: () => void;
  onPrompt: () => void;
  isOpen: boolean;
  toggle: () => void;
}

const QuickStart: React.FC<QuickStartProps> = ({ onCad, onImage, onPrompt, isOpen, toggle }) => {
  const { t } = useTranslation();

  return (
    <div className="fixed bottom-6 right-6 z-[100]">
      {isOpen && (
        <div className="mb-3 w-64 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-xl p-4 space-y-3 animate-fade-in">
          <div>
            <p className="text-sm font-bold text-slate-900 dark:text-white">{t('dashboard.quickStart.title')}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{t('dashboard.quickStart.description')}</p>
          </div>
          <button
            type="button"
            onClick={onCad}
            className="w-full inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-sm font-semibold text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition"
          >
            <PenTool size={16} />
            {t('dashboard.quickStart.actions.uploadCad')}
          </button>
          <button
            type="button"
            onClick={onImage}
            className="w-full inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-sm font-semibold text-blue-700 dark:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition"
          >
            <ImageIcon size={16} />
            {t('dashboard.quickStart.actions.uploadImage')}
          </button>
          <button
            type="button"
            onClick={onPrompt}
            className="w-full inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-purple-50 dark:bg-purple-900/30 text-sm font-semibold text-purple-700 dark:text-purple-200 hover:bg-purple-100 dark:hover:bg-purple-900/50 transition"
          >
            <MessageCircle size={16} />
            {t('dashboard.quickStart.actions.startPrompt')}
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={toggle}
        className="w-14 h-14 rounded-full bg-gradient-to-r from-primary-500 to-purple-500 text-white shadow-2xl flex items-center justify-center hover:scale-105 transition-transform"
      >
        <Rocket size={20} />
      </button>
    </div>
  );
};

export default QuickStart;
