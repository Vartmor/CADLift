import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Github,
  Twitter,
  Linkedin,
  Mail,
  ExternalLink,
  Sparkles,
  FileText,
  HelpCircle,
  Users,
  Heart
} from 'lucide-react';

const Footer: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { label: 'Dashboard', href: '/dashboard' },
      { label: 'DXF to 3D', href: '/dashboard' },
      { label: 'Image to 3D', href: '/dashboard' },
      { label: 'Prompt to 3D', href: '/dashboard' },
    ],
    resources: [
      { label: 'API Docs', href: 'http://localhost:8000/docs', external: true },
      { label: 'Resources', href: '/resources' },
      { label: 'FAQ', href: '/resources#faq' },
      { label: 'Community', href: '/resources#community' },
    ],
    company: [
      { label: 'About', href: '/about' },
      { label: 'GitHub', href: 'https://github.com/vartmor', external: true },
      { label: 'Contact', href: 'mailto:hello@cadlift.io', external: true },
    ],
  };

  const socialLinks = [
    { icon: Github, href: 'https://github.com/vartmor', label: 'GitHub' },
    { icon: Twitter, href: '#', label: 'Twitter' },
    { icon: Linkedin, href: '#', label: 'LinkedIn' },
  ];

  return (
    <footer className="relative overflow-hidden">
      {/* Top accent line */}
      <div className="h-px bg-slate-200 dark:bg-slate-800" />

      {/* Main footer content */}
      <div className="bg-slate-50 dark:bg-slate-950 pt-16 pb-8">
        <div className="max-w-7xl mx-auto px-6">

          {/* Top section - Brand + Newsletter */}
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-12 pb-12 border-b border-slate-200 dark:border-slate-800">

            {/* Brand section */}
            <div className="max-w-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-slate-900 dark:bg-white flex items-center justify-center">
                  <Box className="w-5 h-5 text-white dark:text-slate-900" />
                </div>
                <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                  CADLift
                </span>
              </div>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
                Transform your 2D designs into stunning 3D models instantly.
                Powered by advanced geometry processing and AI.
              </p>

              {/* Social links */}
              <div className="flex items-center gap-3">
                {socialLinks.map((social) => (
                  <a
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noreferrer"
                    className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-500 hover:text-slate-900 dark:hover:text-white hover:border-slate-300 dark:hover:border-slate-700 transition-all hover:-translate-y-0.5"
                    aria-label={social.label}
                  >
                    <social.icon size={18} />
                  </a>
                ))}
              </div>
            </div>

            {/* Links grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-8 lg:gap-16">
              {/* Product */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4 flex items-center gap-2">
                  <Sparkles size={12} />
                  Product
                </h4>
                <ul className="space-y-3">
                  {footerLinks.product.map((link) => (
                    <li key={link.label}>
                      <button
                        onClick={() => navigate(link.href)}
                        className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
                      >
                        {link.label}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Resources */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4 flex items-center gap-2">
                  <FileText size={12} />
                  Resources
                </h4>
                <ul className="space-y-3">
                  {footerLinks.resources.map((link) => (
                    <li key={link.label}>
                      {link.external ? (
                        <a
                          href={link.href}
                          target="_blank"
                          rel="noreferrer"
                          className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors inline-flex items-center gap-1"
                        >
                          {link.label}
                          <ExternalLink size={10} className="opacity-50" />
                        </a>
                      ) : (
                        <button
                          onClick={() => navigate(link.href)}
                          className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
                        >
                          {link.label}
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Company */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4 flex items-center gap-2">
                  <Users size={12} />
                  Company
                </h4>
                <ul className="space-y-3">
                  {footerLinks.company.map((link) => (
                    <li key={link.label}>
                      {link.external ? (
                        <a
                          href={link.href}
                          target="_blank"
                          rel="noreferrer"
                          className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors inline-flex items-center gap-1"
                        >
                          {link.label}
                          <ExternalLink size={10} className="opacity-50" />
                        </a>
                      ) : (
                        <button
                          onClick={() => navigate(link.href)}
                          className="text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
                        >
                          {link.label}
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Bottom section - Copyright */}
          <div className="pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-500">
              <span>© {currentYear} CADLift.</span>
              <span className="hidden sm:inline">All rights reserved.</span>
            </div>

            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-500">
              <span>Made with</span>
              <Heart size={14} className="text-red-500 fill-red-500" />
              <span>by</span>
              <a
                href="https://github.com/vartmor"
                target="_blank"
                rel="noreferrer"
                className="font-semibold text-slate-700 dark:text-slate-300 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
              >
                Vartmor
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
