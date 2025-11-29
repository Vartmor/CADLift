import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, FileCheck, FileX, Settings2, Layers, MoveVertical, Ruler, ArrowRight } from 'lucide-react';
import { UploadFormData, ConversionMode, Unit } from '../types';

interface UploadFormProps {
  onSubmit: (data: UploadFormData) => void;
  presetMode?: ConversionMode | null;
  presetModeSignal?: number;
}

const UploadForm: React.FC<UploadFormProps> = ({ onSubmit, presetMode = null, presetModeSignal = 0 }) => {
  const { t } = useTranslation();
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Form States
  const [mode, setMode] = useState<ConversionMode>(ConversionMode.FLOOR_PLAN);
  const [unit, setUnit] = useState<Unit>(Unit.MM);
  const [height, setHeight] = useState<number>(3000); // Default 3000mm

  const inputRef = useRef<HTMLInputElement>(null);
  const presetRef = useRef<ConversionMode | null>(null);
  const presetSignalRef = useRef<number>(presetModeSignal);

  useEffect(() => {
    if (!presetMode) {
      presetRef.current = null;
      presetSignalRef.current = presetModeSignal;
      return;
    }
    if (presetModeSignal !== presetSignalRef.current || presetMode !== presetRef.current) {
      presetRef.current = presetMode;
      presetSignalRef.current = presetModeSignal;
      setMode(presetMode);
    }
  }, [presetMode, presetModeSignal]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    if (!selectedFile.name.toLowerCase().endsWith('.dxf')) {
      setError("Invalid file format. Only .dxf is supported.");
      return;
    }
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError("File too large (Max 50MB).");
      return;
    }
    setFile(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      onSubmit({
        file,
        mode,
        unit,
        extrudeHeight: height,
        intent: 'cad',
        inputLabel: file.name,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto bg-white dark:bg-slate-900/50 backdrop-blur-sm rounded-3xl shadow-2xl shadow-slate-200/50 dark:shadow-black/40 border border-white/20 dark:border-slate-800 overflow-hidden">
      <div className="flex flex-col md:flex-row h-full min-h-[400px]">
        
        {/* Left Side: Upload Zone */}
        <div className="w-full md:w-5/12 p-6 bg-slate-50 dark:bg-slate-900/80 border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-800 flex flex-col">
           <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
             <Upload className="w-5 h-5 text-primary-500" />
             {t('common.upload_title')}
           </h3>
           
           <div
            className={`flex-grow relative group flex flex-col items-center justify-center w-full rounded-2xl border-2 border-dashed transition-all duration-300 ease-out cursor-pointer overflow-hidden
              ${dragActive 
                ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/20' 
                : 'border-slate-300 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 bg-white dark:bg-slate-900'
              }
              ${error ? 'border-red-500 bg-red-50 dark:bg-red-900/10' : ''}
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
          >
            {/* Blueprint Grid Background for effect */}
            <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-800 opacity-50 pointer-events-none" />

            <input
              ref={inputRef}
              type="file"
              className="hidden"
              accept=".dxf"
              onChange={handleChange}
            />
            
            <div className="relative z-10 p-6 flex flex-col items-center text-center transition-transform duration-300 group-hover:scale-105">
              {file ? (
                <div className="animate-fade-in">
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                    <FileCheck className="w-8 h-8 text-green-600 dark:text-green-400" />
                  </div>
                  <p className="text-base font-bold text-slate-900 dark:text-white break-all line-clamp-2">{file.name}</p>
                  <p className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  <button 
                    type="button"
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="mt-4 px-3 py-1 text-xs font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
                  >
                    Remove File
                  </button>
                </div>
              ) : (
                <>
                  <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-md transition-all group-hover:bg-white dark:group-hover:bg-slate-700">
                     {error ? <FileX className="w-8 h-8 text-red-500" /> : <Upload className="w-8 h-8 text-slate-400 dark:text-slate-500 group-hover:text-primary-500 transition-colors" />}
                  </div>
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                    {error ? <span className="text-red-500">{error}</span> : t('common.upload_drag')}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-500 mt-2 max-w-[200px]">
                    {t('common.upload_hint')}
                  </p>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Right Side: Config */}
        <div className="w-full md:w-7/12 p-8 flex flex-col justify-between bg-white/50 dark:bg-slate-900/50">
           <div>
             <div className="flex items-center gap-2 mb-6">
               <Settings2 className="w-5 h-5 text-primary-500" />
               <h3 className="text-lg font-bold text-slate-900 dark:text-white">Configuration</h3>
             </div>

             <div className="space-y-6">
                {/* Mode Selection */}
                <div className="group">
                  <label className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                    <Layers className="w-3 h-3 mr-1.5" />
                    {t('common.mode_label')}
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <label className={`cursor-pointer relative rounded-xl border p-3 flex flex-col items-center text-center transition-all duration-200
                      ${mode === ConversionMode.FLOOR_PLAN 
                        ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 ring-1 ring-primary-500 text-primary-700 dark:text-primary-300' 
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400'
                      }`}>
                      <input type="radio" className="hidden" name="mode" checked={mode === ConversionMode.FLOOR_PLAN} onChange={() => setMode(ConversionMode.FLOOR_PLAN)} />
                      <span className="text-sm font-semibold">{t('common.mode_floor')}</span>
                    </label>
                    <label className={`cursor-pointer relative rounded-xl border p-3 flex flex-col items-center text-center transition-all duration-200
                      ${mode === ConversionMode.MECHANICAL 
                        ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 ring-1 ring-primary-500 text-primary-700 dark:text-primary-300' 
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400'
                      }`}>
                      <input type="radio" className="hidden" name="mode" checked={mode === ConversionMode.MECHANICAL} onChange={() => setMode(ConversionMode.MECHANICAL)} />
                      <span className="text-sm font-semibold">{t('common.mode_mech')}</span>
                    </label>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  {/* Unit */}
                  <div>
                    <label className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                      <Ruler className="w-3 h-3 mr-1.5" />
                      {t('common.unit_label')}
                    </label>
                    <select
                      value={unit}
                      onChange={(e) => setUnit(e.target.value as Unit)}
                      className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 text-slate-900 dark:text-white font-medium transition-all appearance-none"
                    >
                      <option value={Unit.MM}>mm</option>
                      <option value={Unit.CM}>cm</option>
                      <option value={Unit.M}>meters</option>
                    </select>
                  </div>

                  {/* Height */}
                  <div>
                    <label className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                      <MoveVertical className="w-3 h-3 mr-1.5" />
                      {t('common.height_label')}
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        value={height}
                        onChange={(e) => setHeight(Number(e.target.value))}
                        min={0}
                        className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 text-slate-900 dark:text-white font-medium transition-all"
                      />
                      <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400 uppercase">{unit}</span>
                    </div>
                  </div>
                </div>
             </div>
           </div>

           <div className="mt-8 pt-6 border-t border-slate-200/60 dark:border-slate-700/60">
             <button
              type="submit"
              disabled={!file}
              className={`w-full group relative flex items-center justify-center py-4 px-6 rounded-xl font-bold text-lg shadow-xl transition-all duration-300
                ${!file 
                  ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed' 
                  : 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:scale-[1.02] hover:shadow-2xl shadow-primary-500/20'
                }
              `}
            >
              <span className="mr-2">{t('common.convert')}</span>
              {file && <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}
            </button>
           </div>
        </div>
      </div>
    </form>
  );
};

export default UploadForm;
