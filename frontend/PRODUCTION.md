# PINAK-ERP Frontend - Production Guide

## 🚀 Production Deployment

### Prerequisites
- Node.js 18+
- Docker (optional)
- Nginx (for production)

### Quick Start

#### 1. Development
```bash
npm install
npm run dev
```

#### 2. Production Build
```bash
npm run build:prod
npm run start
```

#### 3. Docker Deployment
```bash
# Build image
npm run docker:build

# Run container
npm run docker:run

# Or use docker-compose
npm run docker:compose
```

### Environment Variables

#### Development (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG=true
```

#### Production (.env.production)
```env
VITE_API_BASE_URL=https://api.pinak-erp.com
VITE_DEBUG=false
```

### Performance Optimizations

#### Code Splitting
- All routes are lazy-loaded
- Components are split by feature
- Vendor chunks are optimized

#### Caching
- Static assets cached for 1 year
- Service worker for offline support
- API responses cached appropriately

#### Bundle Analysis
```bash
npm run build:analyze
```

### Testing

#### Unit Tests
```bash
npm run test
npm run test:coverage
```

#### E2E Tests
```bash
npm run test:e2e
npm run test:e2e:open
```

### Security

#### Headers
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- X-Content-Type-Options: nosniff
- Content-Security-Policy configured

#### HTTPS
- SSL certificates required for production
- HSTS headers enabled
- Secure cookies only

### Monitoring

#### Error Tracking
- Error boundaries implemented
- Console errors logged
- Production error reporting

#### Performance
- Core Web Vitals monitoring
- Bundle size tracking
- Loading time metrics

### PWA Features

#### Offline Support
- Service worker caching
- Offline indicator
- Background sync

#### Install Prompt
- App installation prompt
- Home screen shortcuts
- Native app experience

### Deployment Options

#### 1. Static Hosting (Netlify, Vercel)
```bash
npm run build
# Deploy dist/ folder
```

#### 2. Docker
```bash
docker build -t pinak-erp-frontend .
docker run -p 3000:80 pinak-erp-frontend
```

#### 3. Nginx
```bash
# Copy nginx.conf to /etc/nginx/
# Copy dist/ to /usr/share/nginx/html/
systemctl restart nginx
```

### CI/CD Pipeline

#### GitHub Actions
- Automated testing
- Build verification
- Deployment automation
- Security scanning

#### Environment Promotion
1. **Development** → Feature testing
2. **Staging** → Integration testing
3. **Production** → Live deployment

### Troubleshooting

#### Common Issues

1. **Build Failures**
   ```bash
   npm run lint:fix
   npm run build
   ```

2. **Test Failures**
   ```bash
   npm run test:watch
   ```

3. **Docker Issues**
   ```bash
   docker system prune
   docker-compose down -v
   ```

#### Performance Issues

1. **Bundle Size**
   - Check bundle analyzer
   - Remove unused dependencies
   - Optimize imports

2. **Loading Speed**
   - Enable gzip compression
   - Use CDN for static assets
   - Implement lazy loading

### Support

#### Documentation
- [API Documentation](./API.md)
- [Component Library](./COMPONENTS.md)
- [Testing Guide](./TESTING.md)

#### Contact
- Technical Support: support@pinak-erp.com
- Documentation: docs.pinak-erp.com
- Issues: GitHub Issues