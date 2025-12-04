import React from 'react';
import { useTranslation } from 'react-i18next';

const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-10 transition-colors duration-300">
      <div className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
        <div className="space-y-2">
          <p className="text-lg font-bold text-slate-900 dark:text-white">CADLift</p>
          <p className="text-slate-500 dark:text-slate-400">{t('common.footer_text')}</p>
          <p className="text-slate-500 dark:text-slate-400">
            {t('common.footer_made')} <span className="font-semibold text-primary-600">Vartmor</span>
          </p>
        </div>
        <div className="space-y-2">
          <p className="font-semibold text-slate-900 dark:text-white">{t('common.footer_docs')}</p>
          <ul className="space-y-1 text-slate-500 dark:text-slate-400">
            <li><a className="hover:text-primary-500" href="http://localhost:8000/docs" target="_blank" rel="noreferrer">API Docs</a></li>
            <li><a className="hover:text-primary-500" href="/resources">Resources</a></li>
          </ul>
        </div>
        <div className="space-y-2">
          <p className="font-semibold text-slate-900 dark:text-white">{t('common.footer_support')}</p>
          <ul className="space-y-1 text-slate-500 dark:text-slate-400">
            <li><a className="hover:text-primary-500" href="/resources#faq">FAQ</a></li>
            <li><a className="hover:text-primary-500" href="/resources#community">Community</a></li>
          </ul>
        </div>
        <div className="space-y-2">
          <p className="font-semibold text-slate-900 dark:text-white">{t('common.footer_github')}</p>
          <ul className="space-y-1 text-slate-500 dark:text-slate-400">
            <li><a className="hover:text-primary-500" href="https://github.com/vartmor" target="_blank" rel="noreferrer">GitHub</a></li>
          </ul>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
