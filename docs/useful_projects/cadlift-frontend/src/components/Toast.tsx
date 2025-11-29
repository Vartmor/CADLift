
import React, { useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastProps {
  id: string;
  message: string;
  type: ToastType;
  onDismiss: (id: string) => void;
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({ id, message, type, onDismiss, duration = 5000 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onDismiss]);

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-green-500" />,
    error: <AlertCircle className="w-5 h-5 text-red-500" />,
    info: <Info className="w-5 h-5 text-blue-500" />
  };

  const styles = {
    success: "border-l-4 border-green-500 bg-white dark:bg-slate-900",
    error: "border-l-4 border-red-500 bg-white dark:bg-slate-900",
    info: "border-l-4 border-blue-500 bg-white dark:bg-slate-900"
  };

  return (
    <div className={`
      relative flex items-start w-full max-w-sm p-4 rounded-lg shadow-xl shadow-slate-200/50 dark:shadow-black/50
      mb-3 transform transition-all duration-300 ease-out animate-fade-in-up
      border border-slate-100 dark:border-slate-800
      ${styles[type]}
    `}>
      <div className="flex-shrink-0 mr-3 pt-0.5">
        {icons[type]}
      </div>
      <div className="flex-1 mr-2">
        <p className="text-sm font-medium text-slate-900 dark:text-slate-100 leading-5">
          {message}
        </p>
      </div>
      <button 
        onClick={() => onDismiss(id)}
        className="flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
      >
        <X size={16} />
      </button>
    </div>
  );
};

export default Toast;
