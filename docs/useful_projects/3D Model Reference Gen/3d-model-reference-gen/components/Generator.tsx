import React, { useState, useCallback } from 'react';
import { generateReferenceImage } from '../services/geminiService';
import { GeneratedImage, GenerationStatus } from '../types';
import { SparklesIcon, DownloadIcon, LoadingSpinner } from './Icons';

interface GeneratorProps {
  onAuthError: () => void;
}

export const Generator: React.FC<GeneratorProps> = ({ onAuthError }) => {
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState<GenerationStatus>(GenerationStatus.IDLE);
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = useCallback(async () => {
    if (!prompt.trim()) return;

    setStatus(GenerationStatus.LOADING);
    setErrorMsg(null);
    setCurrentImage(null);

    try {
      const imageUrl = await generateReferenceImage(prompt);
      
      setCurrentImage({
        url: imageUrl,
        prompt: prompt,
        timestamp: Date.now()
      });
      setStatus(GenerationStatus.SUCCESS);
    } catch (err: any) {
      console.error(err);
      
      // Handle authentication errors
      const errorMessage = err.message || JSON.stringify(err);
      if (
        errorMessage.includes("Requested entity was not found") || 
        errorMessage.includes("403") || 
        errorMessage.includes("PERMISSION_DENIED")
      ) {
        onAuthError();
        return;
      }

      setErrorMsg("Failed to generate image. The model might be busy or the prompt was blocked.");
      setStatus(GenerationStatus.ERROR);
    }
  }, [prompt, onAuthError]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-8">
      {/* Input Section */}
      <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 p-6 rounded-2xl shadow-xl">
        <label className="block text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">
          Object Description
        </label>
        <div className="flex gap-4 flex-col sm:flex-row">
          <input
            type="text"
            className="flex-1 bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            placeholder="e.g. A futuristic cyber-punk motorcycle helmet"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={status === GenerationStatus.LOADING}
          />
          <button
            onClick={handleGenerate}
            disabled={status === GenerationStatus.LOADING || !prompt.trim()}
            className={`
              flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold text-white transition-all
              ${status === GenerationStatus.LOADING || !prompt.trim() 
                ? 'bg-slate-700 cursor-not-allowed text-slate-400' 
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-lg shadow-blue-500/20 active:scale-95'}
            `}
          >
            {status === GenerationStatus.LOADING ? (
              <>
                <LoadingSpinner className="w-5 h-5" />
                <span>Designing...</span>
              </>
            ) : (
              <>
                <SparklesIcon className="w-5 h-5" />
                <span>Generate Reference</span>
              </>
            )}
          </button>
        </div>
        <p className="mt-3 text-xs text-slate-500">
          *The AI will optimize your prompt to create a perfect reference for 3D modeling.
        </p>
      </div>

      {/* Result Section */}
      <div className="min-h-[400px] flex items-center justify-center">
        {status === GenerationStatus.ERROR && (
          <div className="text-center p-8 bg-red-900/20 border border-red-800 rounded-xl max-w-lg">
            <p className="text-red-400 font-medium mb-2">Generation Failed</p>
            <p className="text-red-300 text-sm">{errorMsg}</p>
          </div>
        )}

        {status === GenerationStatus.IDLE && (
          <div className="text-center text-slate-500">
             <div className="w-24 h-24 mx-auto border-2 border-dashed border-slate-700 rounded-2xl flex items-center justify-center mb-4">
                <span className="text-4xl opacity-20">?</span>
             </div>
             <p className="text-lg">Waiting for input...</p>
             <p className="text-sm opacity-60">Describe an object to get a 3D-ready reference.</p>
          </div>
        )}

        {status === GenerationStatus.LOADING && (
          <div className="flex flex-col items-center justify-center gap-4">
             <div className="relative">
                <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 rounded-full animate-pulse"></div>
                <LoadingSpinner className="w-16 h-16 text-blue-500 relative z-10" />
             </div>
             <p className="text-blue-400 animate-pulse font-medium tracking-wide">Synthesizing Geometry...</p>
          </div>
        )}

        {status === GenerationStatus.SUCCESS && currentImage && (
          <div className="w-full animate-fade-in-up">
            <div className="bg-slate-800 rounded-2xl overflow-hidden shadow-2xl border border-slate-700">
              <div className="relative group">
                <img 
                  src={currentImage.url} 
                  alt={currentImage.prompt} 
                  className="w-full h-auto object-contain max-h-[600px] bg-slate-900" 
                />
                <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <a 
                      href={currentImage.url} 
                      download={`reference-${Date.now()}.png`}
                      className="flex items-center gap-2 bg-white text-slate-900 px-4 py-2 rounded-lg font-bold shadow-lg hover:bg-slate-200"
                    >
                      <DownloadIcon className="w-5 h-5" />
                      Download
                    </a>
                </div>
              </div>
              <div className="p-6 border-t border-slate-700">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">Generated Reference</h3>
                    <p className="text-slate-400 text-sm italic">"{currentImage.prompt}"</p>
                  </div>
                  <div className="bg-slate-700/50 px-3 py-1 rounded text-xs text-slate-300 border border-slate-600">
                    Nano Banana Pro
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};