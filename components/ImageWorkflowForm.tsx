import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { UploadCloud, Sparkles } from 'lucide-react';
import { ConversionMode, Unit, UploadFormData } from '../types';

interface ImageWorkflowFormProps {
  onCreate: (data: UploadFormData) => Promise<void>;
  onSuccess?: () => void;
}

const ImageWorkflowForm: React.FC<ImageWorkflowFormProps> = ({ onCreate, onSuccess }) => {
  const { t } = useTranslation();
  const [image, setImage] = useState<File | null>(null);
  const [conversion, setConversion] = useState<'2d' | '3d' | 'precision'>('2d');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handlePick = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError(t('dashboard.imageForm.errors.unsupported'));
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setError(t('dashboard.imageForm.errors.tooLarge'));
      return;
    }
    setError(null);
    setImage(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handlePick(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image) {
      setError(t('dashboard.imageForm.errors.required'));
      return;
    }
    setIsSubmitting(true);
    const base = image.name.replace(/\.[^/.]+$/, '');

    let outputLabel = `${base}_vector.dxf`;
    let mode = ConversionMode.IMAGE_TO_2D;

    if (conversion === '3d') {
      outputLabel = `${base}_mesh.fbx`;
      mode = ConversionMode.IMAGE_TO_3D;
    } else if (conversion === 'precision') {
      outputLabel = `${base}_precision.step`;
      mode = 'image_to_precision' as ConversionMode; // Temporary cast
    }

    try {
      await onCreate({
        file: image,
        mode,
        unit: Unit.MM,
        extrudeHeight: 0,
        intent: 'image',
        inputLabel: image.name,
        outputLabel,
        notes,
      });
      if (onSuccess) onSuccess();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div
        className={`border-2 border-dashed rounded-3xl p-6 text-center relative overflow-hidden transition-colors ${error ? 'border-red-400 bg-red-50' : 'border-slate-300 bg-slate-50'
          } dark:border-slate-700 dark:bg-slate-900`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => e.target.files && handlePick(e.target.files[0])}
        />
        <div className="flex flex-col items-center gap-3">
          <UploadCloud className="w-10 h-10 text-primary-500" />
          <p className="text-lg font-semibold text-slate-900 dark:text-white">
            {image ? image.name : t('dashboard.imageForm.uploadLabel')}
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md">
            {t('dashboard.imageForm.uploadHint')}
          </p>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="px-5 py-2 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-700"
          >
            {t('dashboard.imageForm.pickButton')}
          </button>
        </div>
        {error && (
          <p className="mt-4 text-sm text-red-500 font-semibold">{error}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          type="button"
          onClick={() => setConversion('2d')}
          className={`p-4 rounded-2xl border text-left transition-all ${conversion === '2d'
            ? 'border-emerald-500 shadow-lg bg-emerald-50 dark:bg-emerald-900/20'
            : 'border-slate-200 dark:border-slate-700'
            }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <div className={`p-1.5 rounded-lg ${conversion === '2d' ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'}`}>
              <span className="text-xs font-bold">2D</span>
            </div>
            <p className="text-sm font-bold text-slate-900 dark:text-white">
              Vectorize Sketch
            </p>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Convert floor plans or sketches into DXF lines.
            <span className="block mt-1 font-medium text-emerald-600 dark:text-emerald-400">Best for: CAD Drafting</span>
          </p>
        </button>

        <button
          type="button"
          onClick={() => setConversion('precision')}
          className={`p-4 rounded-2xl border text-left transition-all ${conversion === 'precision'
            ? 'border-blue-500 shadow-lg bg-blue-50 dark:bg-blue-900/20'
            : 'border-slate-200 dark:border-slate-700'
            }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <div className={`p-1.5 rounded-lg ${conversion === 'precision' ? 'bg-blue-500 text-white' : 'bg-slate-200 text-slate-500'}`}>
              <span className="text-xs font-bold">CAD</span>
            </div>
            <p className="text-sm font-bold text-slate-900 dark:text-white">
              Precision 3D
            </p>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            AI extracts dimensions from blueprints for Parametric CAD.
            <span className="block mt-1 font-medium text-blue-600 dark:text-blue-400">Best for: Engineering</span>
          </p>
        </button>

        <button
          type="button"
          onClick={() => setConversion('3d')}
          className={`p-4 rounded-2xl border text-left transition-all ${conversion === '3d'
            ? 'border-purple-500 shadow-lg bg-purple-50 dark:bg-purple-900/20'
            : 'border-slate-200 dark:border-slate-700'
            }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <div className={`p-1.5 rounded-lg ${conversion === '3d' ? 'bg-purple-500 text-white' : 'bg-slate-200 text-slate-500'}`}>
              <span className="text-xs font-bold">3D</span>
            </div>
            <p className="text-sm font-bold text-slate-900 dark:text-white">
              AI Concept Mesh
            </p>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Generate organic 3D models from photos.
            <span className="block mt-1 font-medium text-purple-600 dark:text-purple-400">Best for: Visualization</span>
          </p>
        </button>
      </div>

      <div>
        <label className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400">
          {t('dashboard.imageForm.notesLabel')}
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder={t('dashboard.imageForm.notesPlaceholder') ?? ''}
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full inline-flex items-center justify-center gap-2 px-6 py-4 rounded-2xl text-white font-bold bg-slate-900 dark:bg-white dark:text-slate-900 shadow-xl hover:scale-[1.01] transition disabled:opacity-50"
      >
        <Sparkles size={18} />
        {isSubmitting
          ? t('dashboard.imageForm.submitLoading')
          : t('dashboard.imageForm.submit')}
      </button>
    </form>
  );
};

export default ImageWorkflowForm;
