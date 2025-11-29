import React from 'react';
import { useTranslation } from 'react-i18next';

const Footer: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 transition-colors duration-300">
      <div className="container mx-auto px-4 text-center text-sm text-slate-500 dark:text-slate-400">
        {t('common.footer_text')}
      </div>
    </footer>
  );
};

export default Footer;