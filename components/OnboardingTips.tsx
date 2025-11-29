import React from 'react';
import { useTranslation } from 'react-i18next';
import { Lightbulb } from 'lucide-react';

interface OnboardingTipsProps {
  onDismiss: () => void;
}

const OnboardingTips: React.FC<OnboardingTipsProps> = ({ onDismiss }) => {
  const { t } = useTranslation();

  return (
    <div className="rounded-3xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 p-5 flex items-start gap-3">
      <div className="shrink-0 p-2 rounded-2xl bg-white/70 dark:bg-black/30">
        <Lightbulb className="text-amber-500" size={20} />
      </div>
      <div className="flex-1 space-y-2 text-sm text-amber-900 dark:text-amber-100">
        <p className="font-bold">{t('dashboard.tips.title')}</p>
        <ul className="space-y-1 list-disc list-inside">
          <li>{t('dashboard.tips.upload')}</li>
          <li>{t('dashboard.tips.prompt')}</li>
        </ul>
        <button
          type="button"
          onClick={onDismiss}
          className="text-xs font-semibold underline underline-offset-4"
        >
          {t('dashboard.tips.dismiss')}
        </button>
      </div>
    </div>
  );
};

export default OnboardingTips;
