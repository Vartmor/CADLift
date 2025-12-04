import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowRight, Box, Layers, Ruler, Sparkles, MousePointer2, FileDigit, Cpu } from 'lucide-react';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const howItWorksRef = useRef<HTMLDivElement>(null);
  const { t } = useTranslation();

  const scrollToHowItWorks = () => {
    howItWorksRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="w-full flex flex-col min-h-[calc(100vh-140px)] relative overflow-hidden">
      
      {/* Background Blueprint Decor */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {/* Large circles */}
        <div className="absolute -top-[20%] -right-[10%] w-[60vw] h-[60vw] border border-slate-200/40 dark:border-slate-700/20 rounded-full opacity-50" />
        <div className="absolute top-[10%] -right-[5%] w-[40vw] h-[40vw] border border-slate-200/40 dark:border-slate-700/20 rounded-full border-dashed opacity-30 animate-spin-slow" />
        
        {/* Technical Lines */}
        <div className="absolute top-1/3 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary-200/30 dark:via-primary-700/30 to-transparent" />
        <div className="absolute left-1/3 top-0 h-full w-px bg-gradient-to-b from-transparent via-slate-200/30 dark:via-slate-700/30 to-transparent" />
        
        {/* Floating Measurements */}
        <div className="absolute top-32 left-[15%] flex items-center gap-2 opacity-40 animate-pulse">
          <div className="h-px w-12 bg-primary-500"></div>
          <span className="text-[10px] font-mono text-primary-500">2450mm</span>
          <div className="h-px w-12 bg-primary-500"></div>
        </div>
        <div className="absolute bottom-40 right-[20%] flex flex-col items-center gap-2 opacity-40 animate-pulse animation-delay-2000">
          <div className="w-px h-12 bg-blue-500"></div>
          <span className="text-[10px] font-mono text-blue-500 rotate-90">1200mm</span>
          <div className="w-px h-12 bg-blue-500"></div>
        </div>
      </div>

      {/* Hero Content */}
      <div className="flex-grow flex flex-col items-center justify-center relative z-10 px-4 py-20">
        
        <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          
          {/* Left: Text */}
          <div className="text-left space-y-10 animate-fade-in-up order-2 lg:order-1">
            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 backdrop-blur-md shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs font-bold tracking-widest uppercase text-slate-600 dark:text-slate-300">{t('home.hero.badge')}</span>
            </div>
            
            <h1 className="text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter text-slate-900 dark:text-white leading-[0.9]">
              {t('home.hero.title_build')} <br/>
              <span className="relative inline-block">
                <span className="relative z-10 bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-blue-600 dark:from-primary-400 dark:to-blue-400">
                  {t('home.hero.title_accent')}
                </span>
                <div className="absolute -bottom-2 left-0 w-full h-4 bg-primary-200/50 dark:bg-primary-900/50 -skew-x-12 -z-0"></div>
              </span> <br/>
              {t('home.hero.title_suffix')}
            </h1>
            
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-lg leading-relaxed border-l-4 border-primary-500 pl-6">
              {t('home.hero.subtitle')}
            </p>
            
            <div className="flex flex-wrap items-center gap-4">
              <button 
                onClick={() => navigate('/dashboard')}
                className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-200 bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 dark:ring-offset-slate-900 hover:shadow-2xl hover:scale-105 cursor-pointer"
              >
                {t('home.hero.primaryCta')}
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <div className="absolute inset-0 -z-10 rounded-xl blur-lg bg-primary-500/30 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              </button>
              
              <button 
                onClick={scrollToHowItWorks}
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-slate-700 dark:text-slate-200 transition-all duration-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 hover:shadow-lg cursor-pointer"
              >
                {t('home.hero.secondaryCta')}
              </button>
            </div>
            
            <div className="pt-8 flex items-center space-x-8 text-slate-400 dark:text-slate-500 grayscale opacity-70">
               <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider"><Layers size={16} /> {t('home.hero.tag1')}</span>
               <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider"><Box size={16} /> {t('home.hero.tag2')}</span>
            </div>
          </div>

          {/* Right: Visual */}
          <div className="relative h-[500px] w-full flex items-center justify-center order-1 lg:order-2 perspective-1000 group">
             {/* Floating Abstract Card */}
             <div className="relative w-80 h-96 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-2xl transform rotate-y-12 rotate-x-6 transition-transform duration-700 group-hover:rotate-y-6 group-hover:rotate-x-3 z-20 flex flex-col overflow-hidden">
                
                {/* Header of Card */}
                <div className="h-12 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex items-center px-4 space-x-2">
                   <div className="w-3 h-3 rounded-full bg-red-400"></div>
                   <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                   <div className="w-3 h-3 rounded-full bg-green-400"></div>
                </div>

                {/* Body of Card */}
                <div className="flex-1 p-6 relative bg-grid-slate-100 dark:bg-grid-slate-800/50">
                   <div className="absolute top-10 left-8 w-32 h-32 border-2 border-primary-500 rounded-lg flex items-center justify-center bg-primary-500/10 backdrop-blur-sm">
                      <Box size={40} className="text-primary-600 dark:text-primary-400 animate-pulse" />
                   </div>
                   {/* Measurements */}
                   <div className="absolute top-6 left-8 w-32 flex justify-between text-[10px] font-mono text-slate-400">
                      <span>|</span><span>3.5m</span><span>|</span>
                   </div>
                   <div className="absolute top-10 left-4 h-32 flex flex-col justify-between text-[10px] font-mono text-slate-400">
                      <span>-</span><span className="-rotate-90">3.5m</span><span>-</span>
                   </div>

                   <div className="absolute bottom-6 right-6 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2 rounded-lg text-xs font-bold shadow-lg flex items-center gap-2 animate-bounce">
                     <Sparkles size={12} />
                     Generated
                   </div>
                </div>
             </div>

             {/* Background Decor Card */}
             <div className="absolute top-10 right-10 w-80 h-96 bg-primary-500/10 rounded-3xl border border-primary-500/20 backdrop-blur-sm transform -rotate-6 scale-90 z-10"></div>
             
             {/* Floating Icons */}
             <div className="absolute -top-10 right-20 p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-xl animate-[blob_6s_infinite] z-30 border border-slate-100 dark:border-slate-700">
                <Ruler size={24} className="text-purple-500" />
             </div>
             <div className="absolute bottom-20 -left-10 p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-xl animate-[blob_8s_infinite] z-30 border border-slate-100 dark:border-slate-700">
                <MousePointer2 size={24} className="text-blue-500" />
             </div>
          </div>

        </div>
      </div>

      {/* How It Works Section */}
      <div ref={howItWorksRef} className="w-full relative z-10 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-6xl mx-auto py-24 px-4">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white mb-6">
                    From 2D to 3D in <span className="text-primary-500">Three Steps</span>
                </h2>
                <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                    Our intelligent geometry engine handles the complexity so you don't have to.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
                {/* Connecting Line */}
                <div className="hidden md:block absolute top-12 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-700 to-transparent z-0"></div>
                
                {/* Step 1 */}
                <div className="relative z-10 flex flex-col items-center text-center group">
                    <div className="w-24 h-24 bg-white dark:bg-slate-800 rounded-3xl border-4 border-slate-100 dark:border-slate-700 flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 group-hover:border-primary-500 transition-all duration-300">
                        <FileDigit size={40} className="text-slate-400 group-hover:text-primary-500 transition-colors" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">1. Upload DXF</h3>
                    <p className="text-slate-500 dark:text-slate-400 leading-relaxed">
                        Drag & drop your standard CAD files. We support all major DXF versions.
                    </p>
                </div>

                {/* Step 2 */}
                <div className="relative z-10 flex flex-col items-center text-center group">
                     <div className="w-24 h-24 bg-white dark:bg-slate-800 rounded-3xl border-4 border-slate-100 dark:border-slate-700 flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 group-hover:border-blue-500 transition-all duration-300">
                        <Cpu size={40} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">2. Process</h3>
                    <p className="text-slate-500 dark:text-slate-400 leading-relaxed">
                        Our engine detects closed loops, walls, and extrusion paths automatically.
                    </p>
                </div>

                {/* Step 3 */}
                <div className="relative z-10 flex flex-col items-center text-center group">
                     <div className="w-24 h-24 bg-white dark:bg-slate-800 rounded-3xl border-4 border-slate-100 dark:border-slate-700 flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 group-hover:border-purple-500 transition-all duration-300">
                        <Box size={40} className="text-slate-400 group-hover:text-purple-500 transition-colors" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">3. Export 3D</h3>
                    <p className="text-slate-500 dark:text-slate-400 leading-relaxed">
                        Download production-ready FBX or OBJ files compatible with Blender & AutoCAD.
                    </p>
                </div>
            </div>
        </div>
      </div>

      {/* Footer Ribbon */}
      <div className="h-2 bg-gradient-to-r from-primary-500 via-purple-500 to-blue-500 w-full"></div>
    </div>
  );
};

export default Home;
