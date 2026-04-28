/**
 * Progress Component
 */
import React from 'react';

interface ProgressProps {
  value: number;
  className?: string;
  max?: number;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  className = '',
  max = 100
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={`relative h-4 w-full overflow-hidden rounded-full bg-gray-100 ${className}`}>
      <div
        className="h-full w-full flex-1 bg-blue-600 transition-all duration-300"
        style={{ transform: `translateX(-${100 - percentage}%)` }}
      />
    </div>
  );
};