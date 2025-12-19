import React from 'react';
import { Lock, Github, ExternalLink } from 'lucide-react';

interface LockedFeatureOverlayProps {
    title?: string;
    message?: string;
    githubUrl?: string;
}

/**
 * Overlay component for locked features in demo mode.
 * Shows a lock icon and directs users to download from GitHub.
 */
const LockedFeatureOverlay: React.FC<LockedFeatureOverlayProps> = ({
    title = 'Desktop App Required',
    message = 'This feature requires GPU and is only available in the desktop version.',
    githubUrl = 'https://github.com/Vartmor/CADLift',
}) => {
    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center backdrop-blur-sm bg-slate-900/80 rounded-xl">
            <div className="text-center p-8 max-w-md">
                {/* Lock Icon */}
                <div className="mx-auto w-16 h-16 mb-4 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center border border-amber-500/30">
                    <Lock className="w-8 h-8 text-amber-400" />
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-white mb-2">{title}</h3>

                {/* Message */}
                <p className="text-slate-400 mb-6">{message}</p>

                {/* GitHub Button */}
                <a
                    href={githubUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white font-medium rounded-lg transition-all duration-200 border border-slate-600 hover:border-slate-500"
                >
                    <Github className="w-5 h-5" />
                    Download from GitHub
                    <ExternalLink className="w-4 h-4" />
                </a>

                {/* Info */}
                <p className="text-xs text-slate-500 mt-4">
                    Clone the repo and run locally for full features
                </p>
            </div>
        </div>
    );
};

export default LockedFeatureOverlay;

// Helper to check if demo mode is enabled
export const isDemoMode = (): boolean => {
    return import.meta.env.VITE_DEMO_MODE === 'true';
};
