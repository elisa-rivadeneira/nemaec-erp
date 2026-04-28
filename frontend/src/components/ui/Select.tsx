/**
 * 🔽 SELECT COMPONENT - NEMAEC ERP
 * Componente de select reutilizable
 */

import React, { forwardRef } from 'react';
import { clsx } from 'clsx';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  children: React.ReactNode;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(({
  label,
  error,
  size = 'md',
  fullWidth = false,
  className,
  children,
  ...props
}, ref) => {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  return (
    <div className={clsx('flex flex-col', fullWidth && 'w-full')}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <select
        ref={ref}
        className={clsx(
          'border border-gray-300 rounded-lg focus:ring-2 focus:ring-nemaec-500 focus:border-nemaec-500 disabled:bg-gray-100 disabled:text-gray-500 bg-white',
          sizeClasses[size],
          error && 'border-red-300 focus:ring-red-500 focus:border-red-500',
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {children}
      </select>
      {error && (
        <span className="mt-1 text-sm text-red-600">{error}</span>
      )}
    </div>
  );
});

Select.displayName = 'Select';

export default Select;