import React, { useState, useEffect, useRef } from 'react';
import { TrendingUp, TrendingDown, BarChart3, PieChart, Activity } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

const ChartContainer = ({ 
  type = 'line', 
  data = [], 
  options = {}, 
  loading = false,
  title,
  subtitle,
  className = ''
}) => {
  const chartRef = useRef(null);
  const [chartInstance, setChartInstance] = useState(null);

  // Chart configuration based on type
  const getChartConfig = () => {
    const baseConfig = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          enabled: true,
        },
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: false,
          },
        },
        y: {
          display: true,
          grid: {
            display: true,
            color: '#f3f4f6',
          },
        },
      },
    };

    switch (type) {
      case 'line':
        return {
          ...baseConfig,
          type: 'line',
          data: {
            labels: data.labels || [],
            datasets: data.datasets || [],
          },
          options: {
            ...baseConfig,
            ...options,
            elements: {
              line: {
                tension: 0.4,
              },
            },
          },
        };
      
      case 'bar':
        return {
          ...baseConfig,
          type: 'bar',
          data: {
            labels: data.labels || [],
            datasets: data.datasets || [],
          },
          options: {
            ...baseConfig,
            ...options,
          },
        };
      
      case 'pie':
        return {
          ...baseConfig,
          type: 'pie',
          data: {
            labels: data.labels || [],
            datasets: data.datasets || [],
          },
          options: {
            ...baseConfig,
            ...options,
            plugins: {
              ...baseConfig.plugins,
              legend: {
                position: 'bottom',
              },
            },
          },
        };
      
      case 'doughnut':
        return {
          ...baseConfig,
          type: 'doughnut',
          data: {
            labels: data.labels || [],
            datasets: data.datasets || [],
          },
          options: {
            ...baseConfig,
            ...options,
            plugins: {
              ...baseConfig.plugins,
              legend: {
                position: 'bottom',
              },
            },
          },
        };
      
      default:
        return baseConfig;
    }
  };

  // Initialize chart
  useEffect(() => {
    if (!chartRef.current || loading) return;

    // Dynamic import of Chart.js
    import('chart.js/auto').then(({ Chart }) => {
      if (chartInstance) {
        chartInstance.destroy();
      }

      const config = getChartConfig();
      const newChart = new Chart(chartRef.current, config);
      setChartInstance(newChart);
    });

    return () => {
      if (chartInstance) {
        chartInstance.destroy();
      }
    };
  }, [data, type, loading]);

  // Update chart when data changes
  useEffect(() => {
    if (chartInstance && data) {
      chartInstance.data = data;
      chartInstance.update();
    }
  }, [chartInstance, data]);

  const getChartIcon = () => {
    switch (type) {
      case 'line':
        return TrendingUp;
      case 'bar':
        return BarChart3;
      case 'pie':
      case 'doughnut':
        return PieChart;
      default:
        return Activity;
    }
  };

  const Icon = getChartIcon();

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading chart..." />
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      {(title || subtitle) && (
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <Icon className="w-5 h-5 text-primary-600" />
            {title && (
              <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
      )}
      
      <div className="relative h-64">
        <canvas ref={chartRef} />
      </div>
    </div>
  );
};

export default ChartContainer;