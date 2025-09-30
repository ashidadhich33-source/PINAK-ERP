import React, { Suspense } from 'react';
import LoadingSpinner from './LoadingSpinner';

const LazyComponent = ({ children, fallback = null }) => {
  return (
    <Suspense fallback={fallback || <LoadingSpinner size="lg" text="Loading..." />}>
      {children}
    </Suspense>
  );
};

export default LazyComponent;