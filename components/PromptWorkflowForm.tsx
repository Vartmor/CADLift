import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Sparkles, Cog, Ruler, Keyboard, ArrowRight } from 'lucide-react';
import { ConversionMode, Unit, UploadFormData } from '../types';

interface PromptWorkflowFormProps {
  onCreate: (data: UploadFormData) => Promise<void>;
  onSuccess?: () => void;
}

type GenerationMode = 'creative_3d' | 'precision_3d' | 'precision_2d';

interface ModeConfig {
  id: GenerationMode;
  icon: React.ReactNode;
  title: string;
  tagline: string;
  description: string;
  placeholder: string;
  examples: string[];
  outputLabel: string;
  conversionMode: ConversionMode;
  is3D: boolean;
  // Color classes
  iconBg: string;
  iconBgSelected: string;
  borderSelected: string;
  bgSelected: string;
  descBg: string;
  descBorder: string;
  descText: string;
  buttonBg: string;
  pillBg: string;
  pillHover: string;
}

const MODE_CONFIGS: ModeConfig[] = [
  {
    id: 'creative_3d',
    icon: <Sparkles className="w-5 h-5" />,
    title: 'Creative 3D',
    tagline: 'Imagine it',
    description: 'AI generates organic 3D models from your description. Best for artistic objects, furniture, products.',
    placeholder: 'A modern ergonomic office chair with mesh back...',
    examples: [
      'A sleek smartphone',
      'Modern table lamp',
      'Ergonomic mouse',
      'Decorative vase'
    ],
    outputLabel: 'creative_model.glb',
    conversionMode: ConversionMode.PROMPT_TO_3D,
    is3D: true,
    // Purple theme
    iconBg: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    iconBgSelected: 'bg-purple-500 text-white',
    borderSelected: 'border-purple-500',
    bgSelected: 'bg-purple-50 dark:bg-purple-900/20',
    descBg: 'bg-purple-50 dark:bg-purple-900/20',
    descBorder: 'border-purple-100 dark:border-purple-800/50',
    descText: 'text-purple-700 dark:text-purple-300',
    buttonBg: 'bg-purple-600 hover:bg-purple-700 dark:bg-purple-500 dark:hover:bg-purple-600',
    pillBg: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-700',
    pillHover: 'hover:bg-purple-200 dark:hover:bg-purple-800/50',
  },
  {
    id: 'precision_3d',
    icon: <Cog className="w-5 h-5" />,
    title: 'Precision 3D',
    tagline: 'Engineer it',
    description: 'Exact parametric CAD parts with precise dimensions. Best for mechanical parts, boxes, cylinders.',
    placeholder: 'A box 100x50x30mm with a 6mm hole in the center...',
    examples: [
      'A box 100x50x30mm',
      'Cylinder r=20, h=50mm',
      'Sphere radius 25mm',
      'Box with M6 hole'
    ],
    outputLabel: 'precision_part.step',
    conversionMode: ConversionMode.PROMPT_TO_3D,
    is3D: true,
    // Blue theme
    iconBg: 'bg-sky-100 dark:bg-sky-900/30 text-sky-600 dark:text-sky-400',
    iconBgSelected: 'bg-sky-500 text-white',
    borderSelected: 'border-sky-500',
    bgSelected: 'bg-sky-50 dark:bg-sky-900/20',
    descBg: 'bg-sky-50 dark:bg-sky-900/20',
    descBorder: 'border-sky-100 dark:border-sky-800/50',
    descText: 'text-sky-700 dark:text-sky-300',
    buttonBg: 'bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600',
    pillBg: 'bg-sky-100 dark:bg-sky-900/30 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-700',
    pillHover: 'hover:bg-sky-200 dark:hover:bg-sky-800/50',
  },
  {
    id: 'precision_2d',
    icon: <Ruler className="w-5 h-5" />,
    title: 'Precision 2D',
    tagline: 'Draft it',
    description: 'Technical drawings & floor plans with accurate dimensions. DXF output for CAD software.',
    placeholder: 'A 5x4m living room with a door on the south wall...',
    examples: [
      'A 5x4m living room',
      '3x3m bedroom with door',
      'Office 8x6m',
      '4x3m bathroom'
    ],
    outputLabel: 'floor_plan.dxf',
    conversionMode: ConversionMode.PROMPT_TO_2D,
    is3D: false,
    // Emerald/Teal theme
    iconBg: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400',
    iconBgSelected: 'bg-emerald-500 text-white',
    borderSelected: 'border-emerald-500',
    bgSelected: 'bg-emerald-50 dark:bg-emerald-900/20',
    descBg: 'bg-emerald-50 dark:bg-emerald-900/20',
    descBorder: 'border-emerald-100 dark:border-emerald-800/50',
    descText: 'text-emerald-700 dark:text-emerald-300',
    buttonBg: 'bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600',
    pillBg: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-700',
    pillHover: 'hover:bg-emerald-200 dark:hover:bg-emerald-800/50',
  },
];

const PromptWorkflowForm: React.FC<PromptWorkflowFormProps> = ({ onCreate, onSuccess }) => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [selectedMode, setSelectedMode] = useState<GenerationMode>('creative_3d');
  const [detail] = useState(100);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentConfig = MODE_CONFIGS.find(m => m.id === selectedMode)!;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError(t('dashboard.promptForm.errors.required'));
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const extrudeHeight = currentConfig.is3D ? 3000 : 100;
      await onCreate({
        file: null,
        mode: currentConfig.conversionMode,
        unit: Unit.MM,
        extrudeHeight,
        intent: 'prompt',
        inputLabel: `"${prompt.trim().slice(0, 40)}${prompt.length > 40 ? '…' : ''}"`,
        outputLabel: currentConfig.outputLabel,
        notes: `${t('dashboard.promptForm.detailLabel')}: ${detail}`,
        metadata: {
          prompt,
          detail,
          precision_mode: selectedMode !== 'creative_3d',
          generation_mode: selectedMode,
        },
      });
      if (onSuccess) onSuccess();
      setPrompt('');
    } catch (err: any) {
      console.error(err);
      setError(err.message || t('common.status_failed'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {/* Mode Selection */}
      <div>
        <label className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 mb-3 block">
          Generation Mode
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {MODE_CONFIGS.map((config) => {
            const isSelected = selectedMode === config.id;
            return (
              <button
                key={config.id}
                type="button"
                onClick={() => setSelectedMode(config.id)}
                className={`p-4 rounded-2xl border-2 text-left transition-all ${isSelected
                    ? `${config.borderSelected} shadow-lg ${config.bgSelected}`
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className={`p-1.5 rounded-lg transition-colors ${isSelected ? config.iconBgSelected : config.iconBg
                    }`}>
                    {config.icon}
                  </div>
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">
                    {config.title}
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 italic">
                  "{config.tagline}"
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Mode Description - Color-coded */}
      <div className={`p-4 rounded-2xl border transition-colors ${currentConfig.descBg} ${currentConfig.descBorder}`}>
        <p className={`text-sm ${currentConfig.descText}`}>
          {currentConfig.description}
        </p>
      </div>

      {/* Prompt Input */}
      <div>
        <label className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-2 mb-2">
          <Keyboard size={14} />
          {t('dashboard.promptForm.promptLabel')}
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          className={`w-full rounded-2xl border-2 bg-white dark:bg-slate-900 p-4 text-sm text-slate-700 dark:text-slate-200 focus:outline-none transition-colors border-slate-200 dark:border-slate-700 focus:${currentConfig.borderSelected}`}
          placeholder={currentConfig.placeholder}
        />
        {error && <p className="mt-2 text-sm text-red-500 font-semibold">{error}</p>}
      </div>

      {/* Example Prompts - Color-coded pills */}
      <div>
        <label className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 mb-2 block">
          Quick Examples
        </label>
        <div className="flex flex-wrap gap-2">
          {currentConfig.examples.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => setPrompt(example)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${currentConfig.pillBg} ${currentConfig.pillHover}`}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Submit Button - Color-coded */}
      <button
        type="submit"
        disabled={isSubmitting || !prompt.trim()}
        className={`w-full inline-flex items-center justify-center gap-2 px-6 py-4 rounded-2xl text-white font-bold shadow-xl hover:scale-[1.01] transition disabled:opacity-50 ${currentConfig.buttonBg}`}
      >
        {currentConfig.icon}
        {isSubmitting
          ? t('dashboard.promptForm.submitLoading')
          : `Generate ${currentConfig.title}`}
        {!isSubmitting && <ArrowRight size={18} />}
      </button>
    </form>
  );
};

export default PromptWorkflowForm;
