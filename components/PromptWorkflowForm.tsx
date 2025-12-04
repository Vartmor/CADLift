import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Keyboard, PenLine } from 'lucide-react';
import { ConversionMode, Unit, UploadFormData } from '../types';

interface PromptWorkflowFormProps {
  onCreate: (data: UploadFormData) => Promise<void>;
  onSuccess?: () => void;
}

const PromptWorkflowForm: React.FC<PromptWorkflowFormProps> = ({ onCreate, onSuccess }) => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [mode, setMode] = useState<'2d' | '3d'>('3d');
  const [detail] = useState(100); // always max detail for prompts
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError(t('dashboard.promptForm.errors.required'));
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      // Backend requires extrude_height between 100mm and 100000mm
      const extrudeHeight = mode === '3d' ? 3000 : 100;
      await onCreate({
        file: null,
        mode: mode === '2d' ? ConversionMode.PROMPT_TO_2D : ConversionMode.PROMPT_TO_3D,
        unit: Unit.MM,
        extrudeHeight,
        intent: 'prompt',
        inputLabel: `"${prompt.trim().slice(0, 40)}${prompt.length > 40 ? '…' : ''}"`,
        outputLabel: mode === '2d' ? 'prompt_sketch.dxf' : 'prompt_model.step',
        notes: `${t('dashboard.promptForm.detailLabel')}: ${detail}`,
        metadata: { prompt, detail },
      });
      if (onSuccess) onSuccess();
      setPrompt('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5">
        <label className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-2">
          <Keyboard size={14} />
          {t('dashboard.promptForm.promptLabel')}
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={5}
          className="mt-2 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 p-4 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder={t('dashboard.promptForm.placeholder') ?? ''}
        />
        {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          type="button"
          onClick={() => setMode('2d')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            mode === '2d'
              ? 'border-primary-500 shadow-lg bg-primary-50 dark:bg-primary-900/20'
              : 'border-slate-200 dark:border-slate-700'
          }`}
        >
          <p className="text-sm font-semibold text-slate-900 dark:text-white">
            {t('dashboard.promptForm.option2d.title')}
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {t('dashboard.promptForm.option2d.desc')}
          </p>
        </button>
        <button
          type="button"
          onClick={() => setMode('3d')}
          className={`p-4 rounded-2xl border text-left transition-all ${
            mode === '3d'
              ? 'border-primary-500 shadow-lg bg-primary-50 dark:bg-primary-900/20'
              : 'border-slate-200 dark:border-slate-700'
          }`}
        >
          <p className="text-sm font-semibold text-slate-900 dark:text-white">
            {t('dashboard.promptForm.option3d.title')}
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {t('dashboard.promptForm.option3d.desc')}
          </p>
        </button>
      </div>

      <div>
        <label className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-2">
          <PenLine size={14} />
          {t('dashboard.promptForm.detailLabel')}
        </label>
        <div className="mt-3 text-sm text-slate-600 dark:text-slate-300 flex items-center gap-2">
          <span className="inline-flex items-center gap-2 rounded-full bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 px-3 py-1 font-semibold">
            {t('dashboard.promptForm.detailHigh')}
          </span>
          <span className="text-xs opacity-70">{detail}% (max)</span>
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full inline-flex items-center justify-center gap-2 px-6 py-4 rounded-2xl text-white font-bold bg-slate-900 dark:bg-white dark:text-slate-900 shadow-xl hover:scale-[1.01] transition disabled:opacity-50"
      >
        {isSubmitting ? t('dashboard.promptForm.submitLoading') : t('dashboard.promptForm.submit')}
      </button>
    </form>
  );
};

export default PromptWorkflowForm;
