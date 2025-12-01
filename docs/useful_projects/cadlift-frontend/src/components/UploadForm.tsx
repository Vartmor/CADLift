
import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Upload, FileCheck, FileX, Settings2, Layers, MoveVertical, Ruler, 
  ArrowRight, FileDigit, Image as ImageIcon, Sparkles, Box, FileType2, Loader2
} from 'lucide-react';
import { UploadFormData, ConversionMode, Unit, JobType, Preset } from '../types';

interface UploadFormProps {
  onSubmit: (data: UploadFormData) => void;
  defaultUnit?: Unit;
  defaultHeight?: number;
  defaultMode?: ConversionMode;
  isLoading?: boolean;
  preset?: Preset | null;
}

const UploadForm: React.FC<UploadFormProps> = ({ 
  onSubmit, 
  defaultUnit = Unit.MM, 
  defaultHeight = 3000, 
  defaultMode = ConversionMode.FLOOR_PLAN,
  isLoading = false,
  preset 
}) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<JobType>('cad');
  
  // Common State
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // CAD Specific
  const [cadMode, setCadMode] = useState<ConversionMode>(defaultMode);
  const [unit, setUnit] = useState<Unit>(defaultUnit);
  const [height, setHeight] = useState<number>(defaultHeight);

  // Image/Prompt Specific
  const [targetFormat, setTargetFormat] = useState<'2d' | '3d'>('3d');
  const [prompt, setPrompt] = useState<string>('');
  const [useTripoSG, setUseTripoSG] = useState<boolean>(false);
  const [useGeminiTripoSG, setUseGeminiTripoSG] = useState<boolean>(true);

  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize Defaults
  useEffect(() => {
    if (!preset) {
      setUnit(defaultUnit);
      setHeight(defaultHeight);
      setCadMode(defaultMode);
    }
  }, [defaultUnit, defaultHeight, defaultMode, preset]);

  // Apply Preset
  useEffect(() => {
    if (preset) {
      setActiveTab(preset.type);
      if (preset.config.unit) setUnit(preset.config.unit);
      if (preset.config.extrudeHeight) setHeight(preset.config.extrudeHeight);
      if (preset.config.mode) setCadMode(preset.config.mode);
      if (preset.config.prompt) setPrompt(preset.config.prompt);
      if (preset.config.targetFormat) setTargetFormat(preset.config.targetFormat);
      
      // Scroll to top to show changes
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [preset]);

  // Clear file when switching tabs manually
  useEffect(() => {
    setFile(null);
    setError(null);
    // Don't clear prompt if it came from a preset matching the current tab, 
    // but if user switches tabs manually, we usually want a fresh start.
    // For simplicity, we clear prompt only if switching AWAY from prompt tab.
    if (activeTab !== 'prompt') setPrompt('');
  }, [activeTab]);

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
    if (activeTab === 'cad') {
      if (!selectedFile.name.toLowerCase().endsWith('.dxf')) {
        setError("Invalid file format. Only .dxf is supported.");
        return;
      }
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError("File too large (Max 50MB).");
        return;
      }
    } else if (activeTab === 'image') {
      const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
      if (!validTypes.includes(selectedFile.type)) {
        setError("Invalid file format. Use JPG or PNG.");
        return;
      }
      if (selectedFile.size > 20 * 1024 * 1024) {
        setError("File too large (Max 20MB).");
        return;
      }
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
    if (isLoading) return;
    
    let finalMode: ConversionMode = ConversionMode.FLOOR_PLAN;
    if (activeTab === 'cad') finalMode = cadMode;
    if (activeTab === 'image') finalMode = targetFormat === '3d' ? ConversionMode.IMAGE_TO_3D : ConversionMode.IMAGE_TO_2D;
    if (activeTab === 'prompt') finalMode = targetFormat === '3d' ? ConversionMode.PROMPT_TO_3D : ConversionMode.PROMPT_TO_2D;

    const formData: UploadFormData = {
      type: activeTab,
      mode: finalMode,
      file: file,
      unit: unit,
      extrudeHeight: height,
      prompt: prompt,
      use_gemini_triposg: activeTab === 'prompt' ? useGeminiTripoSG : undefined,
      use_triposg: activeTab === 'image' ? useTripoSG : undefined,
      targetFormat: targetFormat
    };

    if (activeTab === 'prompt' && !prompt.trim()) return;
    if (activeTab !== 'prompt' && !file) return;

    onSubmit(formData);
  };

  const tabs = [
    { id: 'cad' as JobType, label: t('dashboard.tab_cad'), icon: FileDigit, desc: t('dashboard.desc_cad') },
    { id: 'image' as JobType, label: t('dashboard.tab_image'), icon: ImageIcon, desc: t('dashboard.desc_image') },
    { id: 'prompt' as JobType, label: t('dashboard.tab_prompt'), icon: Sparkles, desc: t('dashboard.desc_prompt') },
  ];

  return (
    <div className="w-full bg-white dark:bg-slate-900/50 backdrop-blur-sm rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-black/40 border border-slate-200 dark:border-slate-800 overflow-hidden animate-fade-in-up flex flex-col">
      
      {/* Tabs / Mode Selection Header */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
         {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => !isLoading && setActiveTab(tab.id)}
              disabled={isLoading}
              className={`flex-1 py-4 px-2 md:px-6 relative transition-all duration-300 flex flex-col md:flex-row items-center justify-center gap-2 md:gap-3 group
                ${activeTab === tab.id 
                  ? 'text-primary-600 dark:text-primary-400 bg-white dark:bg-slate-900/80 shadow-sm z-10' 
                  : 'text-slate-500 dark:text-slate-500 hover:bg-slate-100/50 dark:hover:bg-slate-800/30'
                }
                ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {activeTab === tab.id && (
                <div className="absolute top-0 left-0 w-full h-0.5 bg-primary-500" />
              )}
              <div className={`p-2 rounded-lg transition-colors ${activeTab === tab.id ? 'bg-primary-50 dark:bg-primary-900/20' : 'bg-transparent group-hover:bg-slate-200 dark:group-hover:bg-slate-800'}`}>
                 <tab.icon size={20} />
              </div>
              <div className="text-center md:text-left">
                <div className="text-sm font-bold">{tab.label}</div>
                <div className="text-[10px] opacity-70 font-medium hidden md:block">{tab.desc}</div>
              </div>
            </button>
         ))}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col md:flex-row min-h-[350px]">
        
        {/* Left Side: Input Area (File or Prompt) */}
        <div className="w-full md:w-5/12 p-6 bg-slate-50 dark:bg-slate-900/80 border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-800 flex flex-col">
           <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
             {activeTab === 'prompt' ? <Sparkles className="w-5 h-5 text-primary-500" /> : <Upload className="w-5 h-5 text-primary-500" />}
             {activeTab === 'prompt' ? t('dashboard.prompt_label') : t('common.upload_title')}
           </h3>
           
           {activeTab === 'prompt' ? (
             <div className="flex-grow flex flex-col">
                <div className="relative flex-grow">
                   <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      disabled={isLoading}
                      placeholder={t('dashboard.prompt_placeholder')}
                      className="w-full h-full min-h-[200px] p-4 rounded-2xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 resize-none transition-all text-slate-900 dark:text-white placeholder:text-slate-400 disabled:opacity-50 disabled:cursor-not-allowed"
                      required
                   />
                   <div className="absolute bottom-4 right-4 text-xs text-slate-400 font-mono bg-white dark:bg-slate-900 px-2 py-1 rounded border border-slate-200 dark:border-slate-800">
                     AI Enabled
                   </div>
                </div>
             </div>
           ) : (
             <div
              className={`flex-grow relative group flex flex-col items-center justify-center w-full rounded-2xl border-2 border-dashed transition-all duration-300 ease-out cursor-pointer overflow-hidden min-h-[200px]
                ${dragActive 
                  ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/20' 
                  : 'border-slate-300 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 bg-white dark:bg-slate-900'
                }
                ${error ? 'border-red-500 bg-red-50 dark:bg-red-900/10' : ''}
                ${isLoading ? 'opacity-50 pointer-events-none' : ''}
              `}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => !isLoading && inputRef.current?.click()}
            >
              <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-800 opacity-50 pointer-events-none" />

              <input
                ref={inputRef}
                type="file"
                className="hidden"
                disabled={isLoading}
                accept={activeTab === 'cad' ? ".dxf" : "image/png, image/jpeg, image/webp"}
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
                    {!isLoading && (
                      <button 
                        type="button"
                        onClick={(e) => { e.stopPropagation(); setFile(null); }}
                        className="mt-4 px-3 py-1 text-xs font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
                      >
                        Remove File
                      </button>
                    )}
                  </div>
                ) : (
                  <>
                    <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-3 group-hover:shadow-md transition-all group-hover:bg-white dark:group-hover:bg-slate-700">
                       {error ? <FileX className="w-6 h-6 text-red-500" /> : <Upload className="w-6 h-6 text-slate-400 dark:text-slate-500 group-hover:text-primary-500 transition-colors" />}
                    </div>
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                      {error ? <span className="text-red-500">{error}</span> : t('common.upload_drag')}
                    </p>
                    <p className="text-[10px] text-slate-500 dark:text-slate-500 mt-2 max-w-[200px]">
                      {activeTab === 'cad' ? t('common.upload_hint_dxf') : t('common.upload_hint_img')}
                    </p>
                  </>
                )}
              </div>
            </div>
           )}
        </div>

        {/* Right Side: Config (Dynamic based on Tab) */}
        <div className="w-full md:w-7/12 p-8 flex flex-col justify-between bg-white/50 dark:bg-slate-900/50">
           <div className={isLoading ? "opacity-50 pointer-events-none" : ""}>
             <div className="flex items-center gap-2 mb-6">
               <Settings2 className="w-5 h-5 text-primary-500" />
               <h3 className="text-lg font-bold text-slate-900 dark:text-white">Configuration</h3>
             </div>

             <div className="space-y-6">
                
                {/* CAD Configuration */}
                {activeTab === 'cad' && (
                  <>
                    <div className="group">
                      <label className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                        <Layers className="w-3 h-3 mr-1.5" />
                        {t('common.mode_label')}
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        <label className={`cursor-pointer relative rounded-xl border p-3 flex flex-col items-center text-center transition-all duration-200
                          ${cadMode === ConversionMode.FLOOR_PLAN 
                            ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 ring-1 ring-primary-500 text-primary-700 dark:text-primary-300' 
                            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400'
                          }`}>
                          <input type="radio" className="hidden" name="mode" checked={cadMode === ConversionMode.FLOOR_PLAN} onChange={() => setCadMode(ConversionMode.FLOOR_PLAN)} />
                          <span className="text-sm font-semibold">{t('common.mode_floor')}</span>
                        </label>
                        <label className={`cursor-pointer relative rounded-xl border p-3 flex flex-col items-center text-center transition-all duration-200
                          ${cadMode === ConversionMode.MECHANICAL 
                            ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 ring-1 ring-primary-500 text-primary-700 dark:text-primary-300' 
                            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400'
                          }`}>
                          <input type="radio" className="hidden" name="mode" checked={cadMode === ConversionMode.MECHANICAL} onChange={() => setCadMode(ConversionMode.MECHANICAL)} />
                          <span className="text-sm font-semibold">{t('common.mode_mech')}</span>
                        </label>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <label className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                          <Ruler className="w-3 h-3 mr-1.5" />
                          {t('common.unit_label')}
                        </label>
                        <select
                          value={unit}
                          onChange={(e) => setUnit(e.target.value as Unit)}
                          className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 text-slate-900 dark:text-white font-medium transition-all appearance-none text-sm"
                        >
                          <option value={Unit.MM}>mm</option>
                          <option value={Unit.CM}>cm</option>
                          <option value={Unit.M}>meters</option>
                        </select>
                      </div>

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
                            className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 text-slate-900 dark:text-white font-medium transition-all text-sm"
                          />
                          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400 uppercase">{unit}</span>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Image & Prompt Configuration */}
                {(activeTab === 'image' || activeTab === 'prompt') && (
                  <div className="group">
                    <label className="flex items-center text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                      <Box className="w-3 h-3 mr-1.5" />
                      {t('dashboard.target_label')}
                    </label>
                    <div className="grid grid-cols-1 gap-3">
                      <label className={`cursor-pointer relative rounded-xl border p-3 flex items-center gap-3 transition-all duration-200
                        ${targetFormat === '2d' 
                          ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 ring-1 ring-primary-500 text-primary-700 dark:text-primary-300' 
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400'
                        }`}>
                        <input type="radio" className="hidden" name="target" checked={targetFormat === '2d'} onChange={() => setTargetFormat('2d')} />
                        <div className={`p-2 rounded-lg ${targetFormat === '2d' ? 'bg-primary-100 dark:bg-primary-800/30' : 'bg-slate-100 dark:bg-slate-800'}`}>
                          <FileType2 size={20} />
                        </div>
                        <div className="flex-grow">
                          <span className="block text-sm font-bold">{t('dashboard.target_2d')}</span>
                          <span className="text-xs opacity-70">Best for laser cutting & CNC</span>
                        </div>
                        {targetFormat === '2d' && <div className="w-3 h-3 bg-primary-500 rounded-full" />}
                      </label>

                      <label className={`cursor-pointer relative rounded-xl border p-3 flex items-center gap-3 transition-all duration-200
                        ${targetFormat === '3d' 
                          ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500 ring-1 ring-primary-500 text-primary-700 dark:text-primary-300' 
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-600 dark:text-slate-400'
                        }`}>
                        <input type="radio" className="hidden" name="target" checked={targetFormat === '3d'} onChange={() => setTargetFormat('3d')} />
                        <div className={`p-2 rounded-lg ${targetFormat === '3d' ? 'bg-primary-100 dark:bg-primary-800/30' : 'bg-slate-100 dark:bg-slate-800'}`}>
                          <Box size={20} />
                        </div>
                        <div className="flex-grow">
                           <span className="block text-sm font-bold">{t('dashboard.target_3d')}</span>
                           <span className="text-xs opacity-70">Best for visualization & printing</span>
                        </div>
                        {targetFormat === '3d' && <div className="w-3 h-3 bg-primary-500 rounded-full" />}
                      </label>
                    </div>

                    {/* AI toggles */}
                    {activeTab === 'prompt' && (
                      <label className="mt-4 flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 transition-colors cursor-pointer">
                        <input
                          type="checkbox"
                          className="mt-1 h-4 w-4"
                          checked={useGeminiTripoSG}
                          onChange={(e) => setUseGeminiTripoSG(e.target.checked)}
                        />
                        <div>
                          <div className="text-sm font-bold text-slate-800 dark:text-slate-100">Use AI mesh (Gemini → TripoSG)</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">Best for organic/artistic prompts. Disable to force parametric CAD.</div>
                        </div>
                      </label>
                    )}
                    {activeTab === 'image' && (
                      <label className="mt-4 flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 transition-colors cursor-pointer">
                        <input
                          type="checkbox"
                          className="mt-1 h-4 w-4"
                          checked={useTripoSG}
                          onChange={(e) => setUseTripoSG(e.target.checked)}
                        />
                        <div>
                          <div className="text-sm font-bold text-slate-800 dark:text-slate-100">Use AI mesh (TripoSG)</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">Try AI reconstruction from the image; fallback uses contour/OpenSCAD.</div>
                        </div>
                      </label>
                    )}
                  </div>
                )}
             </div>
           </div>

           <div className="mt-6 pt-6 border-t border-slate-200/60 dark:border-slate-700/60">
             <button
              type="submit"
              disabled={isLoading || (activeTab === 'prompt' ? !prompt.trim() : !file)}
              className={`w-full group relative flex items-center justify-center py-3.5 px-6 rounded-xl font-bold text-lg shadow-xl transition-all duration-300
                ${(isLoading || (activeTab === 'prompt' ? !prompt.trim() : !file))
                  ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed' 
                  : 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:scale-[1.02] hover:shadow-2xl shadow-primary-500/20'
                }
              `}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="animate-spin" size={20} />
                  <span>Processing...</span>
                </div>
              ) : (
                <>
                  <span className="mr-2">{t('common.convert')}</span>
                  {(activeTab === 'prompt' ? prompt.trim() : file) && <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}
                </>
              )}
            </button>
           </div>
        </div>
      </form>
    </div>
  );
};

export default UploadForm;
