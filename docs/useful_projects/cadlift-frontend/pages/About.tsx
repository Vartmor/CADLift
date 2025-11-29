import React from 'react';
import { useTranslation } from 'react-i18next';
import { Layers, Zap, Box, Code2, ArrowRight, Cpu, FileDigit } from 'lucide-react';

const About: React.FC = () => {
  const { t } = useTranslation();

  const features = [
    { 
      icon: <Zap className="w-6 h-6" />, 
      text: t('about.feature_1'),
      color: "bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400"
    },
    { 
      icon: <Layers className="w-6 h-6" />, 
      text: t('about.feature_2'),
      color: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
    },
    { 
      icon: <Box className="w-6 h-6" />, 
      text: t('about.feature_3'),
      color: "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400"
    },
  ];

  const steps = [
    { icon: <FileDigit size={24} />, title: "Upload DXF", desc: "Parse standard 2D CAD interchange format." },
    { icon: <Cpu size={24} />, title: "Process Geometry", desc: "Identify closed loops and extrusion paths." },
    { icon: <Box size={24} />, title: "Generate 3D", desc: "Construct solid meshes and export to FBX/OBJ." },
  ];

  return (
    <div className="max-w-6xl mx-auto py-8 animate-fade-in">
      
      {/* Header Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-24">
        <div className="order-2 lg:order-1 animate-fade-in-up">
          <div className="flex items-center space-x-2 mb-6">
             <div className="w-8 h-1 bg-primary-500 rounded-full"></div>
             <span className="text-primary-600 dark:text-primary-400 font-bold uppercase tracking-widest text-xs md:text-sm">Engineering & Design</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 dark:text-white mb-6 leading-tight tracking-tight">
            Automating the <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-indigo-600 dark:from-primary-400 dark:to-indigo-400">Dimension Shift</span>
          </h1>
          <div className="prose prose-lg dark:prose-invert text-slate-600 dark:text-slate-300 mb-8">
            <p>
              {t('about.description')}
            </p>
          </div>
          
          <div className="flex flex-wrap gap-4">
            {features.map((feat, idx) => (
              <div key={idx} className="flex items-center space-x-2 bg-white dark:bg-slate-800/50 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-700 shadow-sm">
                <div className={`p-1.5 rounded-full ${feat.color}`}>
                  {React.cloneElement(feat.icon as React.ReactElement<any>, { size: 14 })}
                </div>
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{feat.text}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Visual Decoration */}
        <div className="order-1 lg:order-2 relative group perspective-1000">
          <div className="absolute -inset-4 bg-gradient-to-tr from-primary-500 to-purple-600 rounded-[2rem] blur-xl opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative bg-slate-50 dark:bg-slate-900 rounded-[2rem] p-8 aspect-square flex items-center justify-center border border-slate-200 dark:border-slate-700 overflow-hidden shadow-2xl transform transition-transform duration-500 hover:rotate-1 hover:scale-[1.02]">
             {/* Blueprint Background */}
             <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-800 opacity-60" />
             
             {/* Central Element */}
             <div className="relative z-10 flex flex-col items-center">
                <div className="w-32 h-32 bg-slate-900 dark:bg-white rounded-3xl flex items-center justify-center mb-8 shadow-xl relative overflow-hidden">
                   <div className="absolute inset-0 bg-gradient-to-br from-transparent to-black/20 dark:to-black/10"></div>
                   <Code2 size={64} strokeWidth={1.5} className="text-white dark:text-slate-900 relative z-10" />
                </div>
                <div className="flex items-center space-x-3 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-600 shadow-lg">
                   <div className="flex space-x-1">
                     <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                     <div className="w-2 h-2 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
                     <div className="w-2 h-2 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
                   </div>
                   <span className="font-mono text-xs font-bold text-slate-600 dark:text-slate-300">SYSTEM_ONLINE</span>
                </div>
             </div>

             {/* Floating Elements */}
             <div className="absolute top-12 right-12 p-3 bg-white dark:bg-slate-800 rounded-xl shadow-lg animate-[blob_5s_infinite] border border-slate-100 dark:border-slate-700">
               <Box size={20} className="text-primary-500" />
             </div>
             <div className="absolute bottom-16 left-12 p-3 bg-white dark:bg-slate-800 rounded-xl shadow-lg animate-[blob_7s_infinite_reverse] border border-slate-100 dark:border-slate-700">
               <Layers size={20} className="text-purple-500" />
             </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="mb-20">
         <div className="text-center mb-12">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">How CADLift Works</h2>
            <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">A streamlined pipeline designed for speed and accuracy.</p>
         </div>

         <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-slate-300 dark:via-slate-700 to-transparent -translate-y-1/2 z-0"></div>

            {steps.map((step, i) => (
              <div key={i} className="relative z-10 flex flex-col items-center text-center group">
                 <div className="w-16 h-16 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 rounded-2xl flex items-center justify-center mb-4 shadow-lg transition-transform duration-300 group-hover:-translate-y-2 group-hover:border-primary-500 dark:group-hover:border-primary-400">
                    <div className="text-slate-400 dark:text-slate-500 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
                      {step.icon}
                    </div>
                 </div>
                 <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">{step.title}</h3>
                 <p className="text-sm text-slate-500 dark:text-slate-400 px-4">{step.desc}</p>
              </div>
            ))}
         </div>
      </div>

      {/* Footer Disclaimer */}
      <div className="p-8 bg-slate-100 dark:bg-slate-900/50 rounded-3xl text-center border border-slate-200 dark:border-slate-800/50">
        <p className="text-slate-500 dark:text-slate-400 font-medium text-sm">
          {t('about.disclaimer')}
        </p>
      </div>
    </div>
  );
};

export default About;