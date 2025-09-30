# PINAK-ERP Frontend - Comprehensive Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Development Guide](#development-guide)
5. [API Documentation](#api-documentation)
6. [Component Library](#component-library)
7. [Testing Guide](#testing-guide)
8. [Performance Optimization](#performance-optimization)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

---

## 🏗️ System Overview

### **PINAK-ERP Frontend** is a comprehensive, enterprise-grade React application built for business management and operations.

### **Key Features:**
- ✅ **Complete ERP Functionality** - Companies, Customers, Inventory, POS, Sales, Reports
- ✅ **Advanced Features** - AI Analytics, Real-time Updates, Mobile Optimization
- ✅ **Production Ready** - Performance Optimized, Thoroughly Tested, PWA Enabled
- ✅ **Modern Architecture** - React 18, Vite, Tailwind CSS, TypeScript Support
- ✅ **Enterprise Features** - Multi-tenancy, Security, Workflows, Real-time Updates
- ✅ **Mobile First** - Touch-friendly, Offline Support, Cross-platform
- ✅ **API Integration** - Advanced Caching, Third-party Services, Security
- ✅ **Deployment Ready** - Docker, CI/CD, Production Configurations

### **Technology Stack:**
- **Frontend**: React 18, Vite, Tailwind CSS, JavaScript
- **State Management**: React Context, Custom Hooks
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Forms**: React Hook Form
- **Icons**: Lucide React
- **Charts**: Chart.js, React Chart.js 2
- **Real-time**: Socket.io Client
- **Testing**: Jest, React Testing Library, Cypress
- **Build**: Vite, ESLint, Prettier
- **Deployment**: Docker, Nginx, GitHub Actions

---

## 🏛️ Architecture

### **System Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PINAK-ERP Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  Presentation Layer (React Components)                      │
│  ├── Pages (Dashboard, Companies, Customers, etc.)         │
│  ├── Components (UI Components, Forms, Charts)            │
│  └── Layout (Header, Sidebar, Navigation)                 │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer (Services & Contexts)                │
│  ├── Services (API, Auth, Integration, Offline)           │
│  ├── Contexts (App, Auth, POS, Realtime)                   │
│  └── Hooks (Custom React Hooks)                           │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (State Management & Caching)                  │
│  ├── State Management (React Context, Local State)        │
│  ├── Caching (Advanced API Service, Offline Sync)        │
│  └── Storage (LocalStorage, IndexedDB, Service Worker)    │
├─────────────────────────────────────────────────────────────┤
│  Integration Layer (External Services)                    │
│  ├── API Integration (REST, GraphQL, WebSocket)          │
│  ├── Third-party Services (Payment, Shipping, Analytics)  │
│  └── Security (Authentication, Authorization, Threat Detection) │
└─────────────────────────────────────────────────────────────┘
```

### **Module Structure:**

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Common components (Button, Input, etc.)
│   ├── layout/          # Layout components (Header, Sidebar)
│   ├── charts/          # Chart components
│   ├── mobile/          # Mobile-specific components
│   └── ai/              # AI-powered components
├── pages/               # Page components
│   ├── auth/           # Authentication pages
│   ├── companies/      # Company management pages
│   ├── customers/      # Customer management pages
│   ├── inventory/     # Inventory management pages
│   ├── pos/           # Point of Sale pages
│   ├── sales/         # Sales management pages
│   ├── reports/       # Reports and analytics pages
│   └── api/           # API documentation and testing pages
├── services/           # Business logic services
│   ├── apiService.js           # Base API service
│   ├── advancedApiService.js   # Advanced API optimization
│   ├── authService.js          # Authentication service
│   ├── integrationService.js   # Third-party integrations
│   ├── offlineSyncService.js   # Offline synchronization
│   └── performanceOptimizationService.js # Performance optimization
├── contexts/           # React contexts
│   ├── AppContext.js          # Application state
│   ├── AuthContext.js         # Authentication state
│   ├── PosContext.js          # POS state
│   └── RealtimeContext.js     # Real-time updates
├── hooks/              # Custom React hooks
│   ├── usePerformance.js      # Performance hooks
│   └── useMobilePerformance.js # Mobile optimization hooks
└── utils/              # Utility functions
    ├── pwa.js          # PWA utilities
    └── constants.js    # Application constants
```

---

## 🚀 Installation & Setup

### **Prerequisites:**
- Node.js 18+ 
- npm or yarn
- Git

### **Installation:**

```bash
# Clone the repository
git clone https://github.com/your-org/pinak-erp-frontend.git
cd pinak-erp-frontend

# Install dependencies
npm install
# or
yarn install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
# or
yarn dev
```

### **Environment Variables:**

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WEBSOCKET_URL=http://localhost:5000

# Third-party Integrations
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_RAZORPAY_KEY_ID=rzp_test_...
VITE_PAYPAL_CLIENT_ID=...
VITE_SHIPROCKET_TOKEN=...
VITE_TWILIO_ACCOUNT_SID=...
VITE_SENDGRID_API_KEY=...
VITE_GA_TRACKING_ID=...
VITE_MIXPANEL_TOKEN=...
VITE_AWS_ACCESS_KEY_ID=...
VITE_CLOUDINARY_CLOUD_NAME=...

# Application Configuration
VITE_APP_NAME=PINAK-ERP
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development
```

### **Development Commands:**

```bash
# Development
npm run dev              # Start development server
npm run build            # Build for production
npm run preview          # Preview production build

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint issues
npm run format           # Format code with Prettier

# Testing
npm run test             # Run unit tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage
npm run test:e2e         # Run end-to-end tests
npm run test:e2e:open    # Open Cypress test runner

# Production
npm run build:prod       # Build for production
npm run start            # Start production server
npm run docker:build     # Build Docker image
npm run docker:run       # Run Docker container
npm run docker:compose   # Run with Docker Compose
```

---

## 🛠️ Development Guide

### **Component Development:**

```jsx
// Example: Creating a new component
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Button from './common/Button';
import LoadingSpinner from './common/LoadingSpinner';

const MyComponent = ({ title, onAction }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <Button onClick={onAction}>
        Action Button
      </Button>
    </div>
  );
};

export default MyComponent;
```

### **Service Development:**

```javascript
// Example: Creating a new service
import { apiService } from './apiService';

class MyService {
  async getData(params = {}) {
    try {
      const response = await apiService.get('/api/my-endpoint', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
  }
  
  async createData(data) {
    try {
      const response = await apiService.post('/api/my-endpoint', data);
      return response.data;
    } catch (error) {
      console.error('Error creating data:', error);
      throw error;
    }
  }
}

export default new MyService();
```

### **Context Development:**

```jsx
// Example: Creating a new context
import React, { createContext, useContext, useState, useEffect } from 'react';

const MyContext = createContext(null);

export const MyProvider = ({ children }) => {
  const [state, setState] = useState(initialState);
  
  useEffect(() => {
    // Initialize context
  }, []);
  
  const value = {
    state,
    setState,
    // Add other methods
  };
  
  return (
    <MyContext.Provider value={value}>
      {children}
    </MyContext.Provider>
  );
};

export const useMy = () => {
  const context = useContext(MyContext);
  if (!context) {
    throw new Error('useMy must be used within MyProvider');
  }
  return context;
};
```

---

## 📚 API Documentation

### **Base API Service:**

```javascript
import axios from 'axios';

const apiService = axios.create({
  baseURL: process.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiService.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiService.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiService;
```

### **API Endpoints:**

#### **Authentication:**
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

#### **Companies:**
- `GET /api/companies` - List companies
- `POST /api/companies` - Create company
- `GET /api/companies/:id` - Get company
- `PUT /api/companies/:id` - Update company
- `DELETE /api/companies/:id` - Delete company

#### **Customers:**
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/:id` - Get customer
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer

#### **Inventory:**
- `GET /api/inventory/items` - List items
- `POST /api/inventory/items` - Create item
- `GET /api/inventory/items/:id` - Get item
- `PUT /api/inventory/items/:id` - Update item
- `DELETE /api/inventory/items/:id` - Delete item

#### **POS:**
- `POST /api/pos/sales` - Process sale
- `GET /api/pos/sales` - List sales
- `GET /api/pos/sales/:id` - Get sale

#### **Reports:**
- `GET /api/reports/sales` - Sales report
- `GET /api/reports/inventory` - Inventory report
- `GET /api/reports/customers` - Customer report

---

## 🧩 Component Library

### **Common Components:**

#### **Button:**
```jsx
<Button 
  variant="primary" 
  size="md" 
  loading={false}
  onClick={handleClick}
>
  Click Me
</Button>
```

#### **Input:**
```jsx
<Input
  label="Email"
  type="email"
  value={email}
  onChange={setEmail}
  error={errors.email}
  required
/>
```

#### **Alert:**
```jsx
<Alert 
  type="success" 
  title="Success"
  message="Operation completed successfully"
/>
```

#### **LoadingSpinner:**
```jsx
<LoadingSpinner 
  size="lg" 
  text="Loading data..."
/>
```

#### **DataTable:**
```jsx
<DataTable
  data={data}
  columns={columns}
  loading={loading}
  onRowClick={handleRowClick}
  onEdit={handleEdit}
  onDelete={handleDelete}
  searchable
  sortable
  pagination
/>
```

#### **ChartContainer:**
```jsx
<ChartContainer
  type="bar"
  data={chartData}
  title="Sales Overview"
  options={chartOptions}
/>
```

### **Layout Components:**

#### **Layout:**
```jsx
<Layout>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/companies" element={<CompaniesList />} />
    {/* More routes */}
  </Routes>
</Layout>
```

#### **Header:**
```jsx
<Header 
  user={user}
  onLogout={handleLogout}
  onToggleSidebar={handleToggleSidebar}
/>
```

#### **Sidebar:**
```jsx
<Sidebar 
  isOpen={sidebarOpen}
  navigation={navigationItems}
  user={user}
/>
```

---

## 🧪 Testing Guide

### **Unit Testing:**

```javascript
// Example: Testing a component
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '../Button';

describe('Button', () => {
  test('renders with correct text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    fireEvent.click(screen.getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### **Integration Testing:**

```javascript
// Example: Testing API integration
import { render, screen, waitFor } from '@testing-library/react';
import { CompaniesList } from '../pages/companies/CompaniesList';
import * as companiesService from '../services/companiesService';

jest.mock('../services/companiesService');

describe('CompaniesList Integration', () => {
  test('loads and displays companies', async () => {
    const mockCompanies = [
      { id: 1, name: 'Company 1', email: 'company1@example.com' },
      { id: 2, name: 'Company 2', email: 'company2@example.com' }
    ];
    
    companiesService.getCompanies.mockResolvedValue(mockCompanies);
    
    render(<CompaniesList />);
    
    await waitFor(() => {
      expect(screen.getByText('Company 1')).toBeInTheDocument();
      expect(screen.getByText('Company 2')).toBeInTheDocument();
    });
  });
});
```

### **End-to-End Testing:**

```javascript
// Example: Cypress E2E test
describe('Company Management', () => {
  it('should create a new company', () => {
    cy.visit('/companies');
    cy.get('[data-testid="add-company-button"]').click();
    cy.get('[data-testid="company-name-input"]').type('Test Company');
    cy.get('[data-testid="company-email-input"]').type('test@example.com');
    cy.get('[data-testid="save-company-button"]').click();
    cy.get('[data-testid="success-message"]').should('be.visible');
  });
});
```

### **Testing Commands:**

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run end-to-end tests
npm run test:e2e

# Open Cypress test runner
npm run test:e2e:open
```

---

## ⚡ Performance Optimization

### **Code Splitting:**

```javascript
// Lazy load components
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const CompaniesList = lazy(() => import('./pages/companies/CompaniesList'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/companies" element={<CompaniesList />} />
      </Routes>
    </Suspense>
  );
}
```

### **Image Optimization:**

```javascript
// Optimize images
const optimizedImage = {
  src: 'image.jpg',
  srcSet: 'image-320w.jpg 320w, image-640w.jpg 640w, image-1280w.jpg 1280w',
  sizes: '(max-width: 320px) 320px, (max-width: 640px) 640px, 1280px',
  loading: 'lazy'
};
```

### **Caching Strategy:**

```javascript
// Service worker caching
const CACHE_NAME = 'pinak-erp-cache-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});
```

### **Performance Monitoring:**

```javascript
// Monitor Core Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

---

## 🚀 Deployment Guide

### **Docker Deployment:**

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://backend:5000/api
    depends_on:
      - backend

  backend:
    image: pinak-erp-backend:latest
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/pinak_erp
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    environment:
      - POSTGRES_DB=pinak_erp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### **Production Build:**

```bash
# Build for production
npm run build:prod

# Start production server
npm run start

# Docker build
docker build -t pinak-erp-frontend .

# Docker run
docker run -p 3000:80 pinak-erp-frontend
```

### **CI/CD Pipeline:**

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run test
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Deployment steps
```

---

## 🔧 Troubleshooting

### **Common Issues:**

#### **Build Errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
npm run dev
```

#### **API Connection Issues:**
```bash
# Check API URL
echo $VITE_API_BASE_URL

# Test API connectivity
curl -X GET $VITE_API_BASE_URL/health
```

#### **Performance Issues:**
```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer dist

# Check for memory leaks
npm run test:coverage
```

### **Debug Mode:**

```javascript
// Enable debug mode
localStorage.setItem('debug', 'true');

// Check console for debug logs
console.log('Debug mode enabled');
```

---

## 🤝 Contributing

### **Development Workflow:**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Run tests and linting
6. Submit a pull request

### **Code Standards:**

- Use ESLint and Prettier
- Write comprehensive tests
- Follow React best practices
- Document your code
- Use semantic commit messages

### **Pull Request Template:**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support and questions:

- **Documentation**: [https://docs.pinak-erp.com](https://docs.pinak-erp.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/pinak-erp-frontend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/pinak-erp-frontend/discussions)
- **Email**: support@pinak-erp.com

---

## 🎯 Roadmap

### **Upcoming Features:**
- [ ] Advanced AI Analytics
- [ ] Multi-language Support
- [ ] Advanced Reporting
- [ ] Mobile App (React Native)
- [ ] Desktop App (Electron)
- [ ] Advanced Integrations
- [ ] Custom Workflows
- [ ] Advanced Security Features

### **Version History:**
- **v1.0.0** - Initial release with core ERP functionality
- **v1.1.0** - Added AI features and advanced analytics
- **v1.2.0** - Mobile optimization and PWA features
- **v1.3.0** - Advanced API integration and security
- **v2.0.0** - Complete system integration and optimization

---

**PINAK-ERP Frontend** - Built with ❤️ for modern business management.