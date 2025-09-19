import React from 'react';

const PageShell = ({ title, subtitle, actions, children, className = '' }) => {
  return (
    <div className={`space-y-6 ${className}`}>
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">{title}</h1>
          {subtitle && <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{subtitle}</p>}
        </div>
        {actions && (
          <div className="flex items-center space-x-2">{actions}</div>
        )}
      </header>

      <section className="space-y-6">
        {children}
      </section>
    </div>
  );
};

export default PageShell;
