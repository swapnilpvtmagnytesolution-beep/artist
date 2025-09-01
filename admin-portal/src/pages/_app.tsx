import React, { useEffect } from 'react';
import type { AppProps } from 'next/app';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/router';
import '../styles/globals.css';

// Custom toast configuration
const toastOptions = {
  duration: 4000,
  position: 'top-right' as const,
  style: {
    background: 'var(--toast-bg)',
    color: 'var(--toast-color)',
    border: '1px solid var(--toast-border)',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '500',
    padding: '12px 16px',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
  success: {
    iconTheme: {
      primary: '#10B981',
      secondary: '#FFFFFF',
    },
  },
  error: {
    iconTheme: {
      primary: '#EF4444',
      secondary: '#FFFFFF',
    },
  },
  loading: {
    iconTheme: {
      primary: '#3B82F6',
      secondary: '#FFFFFF',
    },
  },
};

function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();

  useEffect(() => {
    // Set CSS custom properties for toast styling based on theme
    const updateToastTheme = () => {
      const isDark = document.documentElement.classList.contains('dark');
      const root = document.documentElement;
      
      if (isDark) {
        root.style.setProperty('--toast-bg', '#374151');
        root.style.setProperty('--toast-color', '#F9FAFB');
        root.style.setProperty('--toast-border', '#4B5563');
      } else {
        root.style.setProperty('--toast-bg', '#FFFFFF');
        root.style.setProperty('--toast-color', '#111827');
        root.style.setProperty('--toast-border', '#E5E7EB');
      }
    };

    // Initial theme setup
    updateToastTheme();

    // Listen for theme changes
    const observer = new MutationObserver(updateToastTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    // Handle route change start
    const handleRouteChangeStart = (url: string) => {
      console.log('Route changing to:', url);
    };

    // Handle route change complete
    const handleRouteChangeComplete = (url: string) => {
      console.log('Route changed to:', url);
      // Scroll to top on route change
      window.scrollTo(0, 0);
    };

    // Handle route change error
    const handleRouteChangeError = (err: any, url: string) => {
      console.error('Route change error:', err, 'URL:', url);
    };

    router.events.on('routeChangeStart', handleRouteChangeStart);
    router.events.on('routeChangeComplete', handleRouteChangeComplete);
    router.events.on('routeChangeError', handleRouteChangeError);

    return () => {
      router.events.off('routeChangeStart', handleRouteChangeStart);
      router.events.off('routeChangeComplete', handleRouteChangeComplete);
      router.events.off('routeChangeError', handleRouteChangeError);
    };
  }, [router]);

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem={true}
      disableTransitionOnChange={false}
    >
      <AnimatePresence
        mode="wait"
        initial={false}
        onExitComplete={() => window.scrollTo(0, 0)}
      >
        <Component {...pageProps} key={router.asPath} />
      </AnimatePresence>
      
      {/* Toast Notifications */}
      <Toaster
        position={toastOptions.position}
        toastOptions={toastOptions}
        containerStyle={{
          top: 20,
          right: 20,
        }}
      />
      
      {/* Global Loading Indicator */}
      <div id="global-loading" className="hidden">
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-gray-900 dark:text-white font-medium">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default MyApp;