import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/Layout';

// Lazy load pages for better performance (code splitting)
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const SignIn = lazy(() => import('./pages/SignIn'));
const SignUp = lazy(() => import('./pages/SignUp'));
const Resources = lazy(() => import('./pages/Resources'));
const Profile = lazy(() => import('./pages/Profile'));

// Loading fallback component
const PageLoader: React.FC = () => (
  <div className="min-h-[60vh] flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      <p className="text-sm text-slate-500 dark:text-slate-400 animate-pulse">Loading...</p>
    </div>
  </div>
);

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/signin" element={<SignIn />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/about" element={<About />} />
              {/* Catch-all route for 404 */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
};

// Simple 404 page
const NotFound: React.FC = () => (
  <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
    <h1 className="text-6xl font-black text-slate-200 dark:text-slate-800">404</h1>
    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-4">Page Not Found</h2>
    <p className="text-slate-500 dark:text-slate-400 mt-2 max-w-md">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <a
      href="/"
      className="mt-6 px-6 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 transition-colors"
    >
      Go Home
    </a>
  </div>
);

export default App;
