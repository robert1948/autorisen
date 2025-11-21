// Service Worker registration helper
export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    // Only register in production and if not disabled
    const isProduction = import.meta.env.PROD;
    const isDisabled = import.meta.env.VITE_DISABLE_SW === 'true';
    
    if (isProduction && !isDisabled) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('SW registered:', registration);
          
          // Listen for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // New content available, prompt user to refresh
                  if (confirm('New version available! Refresh to update?')) {
                    newWorker.postMessage({ type: 'SKIP_WAITING' });
                    window.location.reload();
                  }
                }
              });
            }
          });
        })
        .catch((error) => {
          console.warn('SW registration failed:', error);
        });
    } else {
      console.log('Service Worker disabled:', { isProduction, isDisabled });
    }
  }
}