import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

// Create a custom event for language switch overlay
export const triggerLanguageSwitch = () => {
  window.dispatchEvent(new CustomEvent('cadlift-lang-switch'));
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { i18n } = useTranslation();
  const [showOverlay, setShowOverlay] = useState(false);
  const [overlayOpacity, setOverlayOpacity] = useState(0);

  // Listen for language switch trigger from Header
  useEffect(() => {
    const handleLangSwitch = () => {
      // Step 1: Show overlay and start fading in
      setShowOverlay(true);
      setOverlayOpacity(0);

      // Step 2: Fade overlay to full opacity
      requestAnimationFrame(() => {
        setOverlayOpacity(1);
      });

      // Step 3: Change language when overlay is fully opaque (150ms)
      setTimeout(() => {
        // Get the pending language from localStorage (set by Header dropdown)
        const pendingLang = window.localStorage.getItem('cadlift_pending_lang');
        if (pendingLang && pendingLang !== i18n.language) {
          i18n.changeLanguage(pendingLang);
          window.localStorage.setItem('cadlift_language', pendingLang);
          window.localStorage.removeItem('cadlift_pending_lang');
        } else {
          // Fallback: cycle if no pending lang (shouldn't happen with dropdown)
          const langOrder = ['en', 'tr', 'de'];
          const currentIdx = langOrder.indexOf(i18n.language);
          const newLang = langOrder[(currentIdx + 1) % langOrder.length];
          i18n.changeLanguage(newLang);
          window.localStorage.setItem('cadlift_language', newLang);
        }

        // Step 4: Start fading out after a tiny delay for React to re-render
        setTimeout(() => {
          setOverlayOpacity(0);

          // Step 5: Hide overlay completely after fade out
          setTimeout(() => {
            setShowOverlay(false);
          }, 150);
        }, 50);
      }, 150);
    };

    window.addEventListener('cadlift-lang-switch', handleLangSwitch);
    return () => window.removeEventListener('cadlift-lang-switch', handleLangSwitch);
  }, [i18n]);

  return (
    <div className="flex flex-col min-h-screen font-sans relative selection:bg-primary-500 selection:text-white">

      {/* Language Switch Overlay */}
      {showOverlay && (
        <div
          className="fixed inset-0 z-[9999] bg-slate-50 dark:bg-slate-950 pointer-events-none transition-opacity duration-150 ease-in-out"
          style={{ opacity: overlayOpacity }}
        />
      )}

      {/* Dynamic Background Elements */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-800 [mask-image:linear-gradient(to_bottom,white,transparent)] opacity-100 dark:opacity-10" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-400/20 dark:bg-primary-600/3 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-70 dark:opacity-20 animate-blob" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-blue-400/20 dark:bg-blue-600/3 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-70 dark:opacity-20 animate-blob animation-delay-2000" />
        <div className="absolute -bottom-32 left-1/3 w-96 h-96 bg-indigo-400/20 dark:bg-indigo-600/3 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-70 dark:opacity-20 animate-blob animation-delay-4000" />
      </div>

      <div className="relative z-10 flex flex-col flex-grow">
        <Header />
        <main className="flex-grow container mx-auto px-4 py-8 sm:px-6 lg:px-8 flex flex-col">
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default Layout;