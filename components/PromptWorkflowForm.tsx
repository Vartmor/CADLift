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
  const [generationMode, setGenerationMode] = useState<'creative' | 'precision'>('creative');
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
        metadata: {
          prompt,
          detail,
          precision_mode: generationMode === 'precision'
        },
      });
      if (onSuccess) onSuccess();
      setPrompt('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {/* Generation Mode Toggle */}
      <div className="flex gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-2xl">
        <button
          type="button"
          onClick={() => setGenerationMode('creative')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${generationMode === 'creative'
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
            : 'text-slate-600 dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-700'
            }`}
        >
          <span>🎨</span>
          <span>Creative (AI Mesh)</span>
        </button>
        <button
          type="button"
          onClick={() => setGenerationMode('precision')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${generationMode === 'precision'
            ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg'
            : 'text-slate-600 dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-700'
            }`}
        >
          <span>🔧</span>
          <span>Precision (CAD)</span>
        </button>
      </div>

      {/* Mode Description */}
      <div className={`p-3 rounded-xl text-sm ${generationMode === 'creative'
        ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
        : 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
        }`}>
        {generationMode === 'creative'
          ? '✨ AI generates organic 3D shapes from your description. Best for artistic objects, furniture, products.'
          : '📐 Parametric CAD from dimensions. Best for precise mechanical parts, boxes, cylinders, holes.'}
      </div>

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
          placeholder={generationMode === 'precision'
            ? 'e.g., "A box 100x50x30mm with a 6mm hole in the center"'
            : t('dashboard.promptForm.placeholder') ?? ''}
        />
        {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
      </div>

      {/* 2D/3D toggle for both modes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          type="button"
          onClick={() => setMode('2d')}
          className={`p-4 rounded-2xl border text-left transition-all ${mode === '2d'
            ? 'border-primary-500 shadow-lg bg-primary-50 dark:bg-primary-900/20'
            : 'border-slate-200 dark:border-slate-700'
            }`}
        >
          <p className="text-sm font-semibold text-slate-900 dark:text-white">
            {generationMode === 'precision' ? '📐 2D Floor Plan' : t('dashboard.promptForm.option2d.title')}
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {generationMode === 'precision'
              ? 'DXF output with room outlines and dimensions'
              : t('dashboard.promptForm.option2d.desc')}
          </p>
        </button>
        <button
          type="button"
          onClick={() => setMode('3d')}
          className={`p-4 rounded-2xl border text-left transition-all ${mode === '3d'
            ? 'border-primary-500 shadow-lg bg-primary-50 dark:bg-primary-900/20'
            : 'border-slate-200 dark:border-slate-700'
            }`}
        >
          <p className="text-sm font-semibold text-slate-900 dark:text-white">
            {generationMode === 'precision' ? '🔩 3D Mechanical Part' : t('dashboard.promptForm.option3d.title')}
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {generationMode === 'precision'
              ? 'STEP/STL output with exact dimensions'
              : t('dashboard.promptForm.option3d.desc')}
          </p>
        </button>
      </div>

      {/* Precision mode examples - different for 2D vs 3D */}
      {generationMode === 'precision' && (
        <div className="space-y-2">
          <p className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400">
            Example prompts:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(mode === '2d' ? [
              'A 5x4m living room',
              '3x3m bedroom with door on south wall',
              'Office 8x6m with 2 windows',
              '4x3m bathroom'
            ] : [
              'A box 100x50x30mm',
              'Cylinder r=20, h=50mm',
              'Sphere radius 25mm',
              'Box with M6 hole'
            ]).map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setPrompt(example)}
                className="text-left p-2 text-xs bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-slate-600 dark:text-slate-300"
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className={`w-full inline-flex items-center justify-center gap-2 px-6 py-4 rounded-2xl text-white font-bold shadow-xl hover:scale-[1.01] transition disabled:opacity-50 ${generationMode === 'precision'
          ? 'bg-gradient-to-r from-blue-600 to-cyan-600'
          : 'bg-slate-900 dark:bg-white dark:text-slate-900'
          }`}
      >
        {isSubmitting
          ? t('dashboard.promptForm.submitLoading')
          : generationMode === 'precision'
            ? 'Generate Precision CAD'
            : t('dashboard.promptForm.submit')}
      </button>
    </form>
  );
};

export default PromptWorkflowForm;
