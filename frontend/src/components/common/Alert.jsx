import React from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import clsx from 'clsx';

const Alert = ({
  type = 'info',
  title,
  children,
  onClose,
  className = '',
}) => {
  const typeConfig = {
    success: {
      icon: CheckCircle,
      classes: 'alert-success',
      iconClasses: 'text-success-600',
    },
    warning: {
      icon: AlertTriangle,
      classes: 'alert-warning',
      iconClasses: 'text-warning-600',
    },
    danger: {
      icon: AlertCircle,
      classes: 'alert-danger',
      iconClasses: 'text-danger-600',
    },
    info: {
      icon: Info,
      classes: 'alert-info',
      iconClasses: 'text-primary-600',
    },
  };

  const config = typeConfig[type];
  const Icon = config.icon;

  return (
    <div className={clsx('alert', config.classes, className)}>
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={clsx('h-5 w-5', config.iconClasses)} />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className="text-sm font-medium">{title}</h3>
          )}
          <div className={clsx('text-sm', title && 'mt-1')}>
            {children}
          </div>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <button
              type="button"
              className="inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2"
              onClick={onClose}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alert;