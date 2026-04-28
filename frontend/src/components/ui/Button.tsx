/**
 * 🔘 BUTTON COMPONENT
 * Componente de botón reutilizable con estilos NEMAEC.
 * Sigue el design system militar/policial.
 */
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ButtonVariant, Size } from '@/types';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: Size;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  children,
  className,
  disabled,
  ...props
}) => {
  const baseClasses = [
    // Base styles
    'inline-flex items-center justify-center',
    'font-medium rounded-lg',
    'transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'hover:transform hover:-translate-y-0.5',
    'active:transform active:translate-y-0',
  ];

  const variantClasses = {
    primary: [
      'bg-nemaec-green-700 text-white border border-nemaec-green-500',
      'hover:bg-nemaec-green-600 hover:border-nemaec-green-400',
      'focus:ring-nemaec-green-500',
      'shadow-nemaec hover:shadow-nemaec-lg',
    ],
    secondary: [
      'bg-nemaec-gray-800 text-nemaec-gray-100 border border-nemaec-gray-600',
      'hover:bg-nemaec-gray-700 hover:border-nemaec-gray-500',
      'focus:ring-nemaec-gray-500',
    ],
    danger: [
      'bg-nemaec-red-800 text-white border border-nemaec-red-600',
      'hover:bg-nemaec-red-700 hover:border-nemaec-red-500',
      'focus:ring-nemaec-red-500',
      'shadow-critical',
    ],
    success: [
      'bg-success text-white border border-nemaec-green-400',
      'hover:bg-nemaec-green-500',
      'focus:ring-success',
    ],
    warning: [
      'bg-warning text-nemaec-gray-900 border border-nemaec-yellow-400',
      'hover:bg-nemaec-yellow-400',
      'focus:ring-warning',
    ],
    ghost: [
      'bg-transparent text-gray-600 border border-transparent',
      'hover:bg-gray-100 hover:text-gray-800',
      'focus:ring-gray-300',
    ],
    outline: [
      'bg-white text-gray-700 border border-gray-300',
      'hover:bg-gray-50 hover:border-gray-400',
      'focus:ring-gray-300',
    ],
  };

  const sizeClasses = {
    xs: ['px-2 py-1', 'text-xs', 'gap-1'],
    sm: ['px-3 py-1.5', 'text-sm', 'gap-1.5'],
    md: ['px-4 py-2', 'text-sm', 'gap-2'],
    lg: ['px-5 py-2.5', 'text-base', 'gap-2.5'],
    xl: ['px-6 py-3', 'text-lg', 'gap-3'],
  };

  const fullWidthClass = fullWidth ? 'w-full' : '';

  const isDisabled = disabled || loading;

  return (
    <button
      className={twMerge(
        clsx(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          fullWidthClass,
          className
        )
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && (
        <svg
          className="w-4 h-4 animate-spin"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}

      {!loading && leftIcon && (
        <span className="flex-shrink-0">{leftIcon}</span>
      )}

      {children}

      {!loading && rightIcon && (
        <span className="flex-shrink-0">{rightIcon}</span>
      )}
    </button>
  );
};

export default Button;