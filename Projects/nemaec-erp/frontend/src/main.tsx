/**
 * 🚀 MAIN ENTRY POINT - NEMAEC ERP
 * Punto de entrada principal de la aplicación React.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import App from './App';
import './index.css';

// Configuración de React Query para el manejo de estado del servidor
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
      retry: (failureCount, error: any) => {
        // No reintentar errores 4xx
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
    },
    mutations: {
      retry: 1,
    },
  },
});

// Configuración de toast notifications con tema NEMAEC
const toastConfig = {
  duration: 4000,
  position: 'top-right' as const,
  style: {
    background: '#37474F',
    color: '#ECEFF1',
    border: '1px solid #4CAF50',
    borderRadius: '8px',
    fontSize: '14px',
  },
  success: {
    iconTheme: {
      primary: '#4CAF50',
      secondary: '#ECEFF1',
    },
  },
  error: {
    iconTheme: {
      primary: '#C62828',
      secondary: '#ECEFF1',
    },
  },
  loading: {
    iconTheme: {
      primary: '#FFC107',
      secondary: '#ECEFF1',
    },
  },
};

// Error Boundary para capturar errores de React
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('NEMAEC ERP Error Boundary:', error, errorInfo);

    // En producción: enviar error al sistema de monitoring
    if (process.env.NODE_ENV === 'production') {
      // Ejemplo: enviar a Sentry, LogRocket, etc.
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-nemaec-gray-900 to-black flex items-center justify-center text-white">
          <div className="text-center max-w-md mx-auto p-8">
            <div className="w-20 h-20 bg-nemaec-red-800 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">⚠️</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-4">
              Error del Sistema NEMAEC
            </h1>
            <p className="text-nemaec-gray-300 mb-6">
              Ha ocurrido un error inesperado. Por favor, recarga la página o contacta al soporte técnico.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-nemaec-green-700 text-white rounded-lg hover:bg-nemaec-green-600 transition-colors"
              >
                Recargar Página
              </button>
              <button
                onClick={() => this.setState({ hasError: false })}
                className="w-full px-4 py-2 bg-nemaec-gray-700 text-white rounded-lg hover:bg-nemaec-gray-600 transition-colors"
              >
                Reintentar
              </button>
            </div>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-nemaec-gray-400 text-sm">
                  Detalles del Error (Solo Desarrollo)
                </summary>
                <pre className="mt-2 p-4 bg-nemaec-gray-900 rounded-lg text-xs overflow-auto">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Inicializar aplicación
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          <Toaster {...toastConfig} />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

// Performance monitoring en desarrollo
// React Query Devtools se cargan desde el componente App en desarrollo

// Hot Module Replacement para desarrollo
if (process.env.NODE_ENV === 'development' && import.meta.hot) {
  import.meta.hot.accept();
}