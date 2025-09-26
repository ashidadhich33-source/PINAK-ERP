# POS System - Complete Project

This repository contains a complete Point of Sale (POS) system with both backend (Python/FastAPI) and frontend (React/Node.js) components.

## Project Structure

```
/
├── app/                    # Python backend (FastAPI)
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business services
│   └── main.py            # FastAPI application
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   ├── package.json       # Dependencies
│   └── vite.config.js     # Vite configuration
└── README.md              # Backend documentation
```

## Backend Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Database Integration**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **Authentication**: JWT-based user authentication
- **RBAC**: Role-based access control
- **Models**: Sales, Inventory, Customers, Users, Reports
- **API Endpoints**: Complete REST API for all business operations

## Frontend Features

- **React 18**: Modern React with functional components and hooks
- **Vite**: Lightning-fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Responsive Design**: Works seamlessly on desktop and mobile
- **React Router**: Client-side routing for SPA functionality

## Pages and Components

### Dashboard
- Sales statistics and metrics
- Recent activity feed
- Low stock alerts
- Quick overview cards

### Sales Management
- Product search and filtering
- Shopping cart functionality
- Checkout process
- Payment method selection
- Receipt generation

### Inventory Management
- Product catalog
- Stock level tracking
- Add/edit/delete products
- Category management
- Low stock notifications

### Customer Management
- Customer database
- Search and filter
- Purchase history
- Customer analytics

### Reports & Analytics
- Daily sales reports
- Top products analysis
- Category-wise sales
- Monthly revenue trends
- Export functionality

## Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **SQLite/PostgreSQL**: Database
- **JWT**: Authentication
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI library
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **React Router**: Routing
- **Axios**: HTTP client
- **Node.js**: Runtime

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the root directory:
   ```bash
   cd /workspace
   ```

2. Install Python dependencies:
   ```bash
   pip install -r Requirements.txt
   ```

3. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. The API will be available at `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. The frontend will be available at `http://localhost:3000`

### Running Both Services

To run both frontend and backend simultaneously:

1. **Terminal 1** - Backend:
   ```bash
   cd /workspace
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Terminal 2** - Frontend:
   ```bash
   cd /workspace/frontend
   npm run dev
   ```

## API Endpoints

The backend provides RESTful APIs for:

- `/api/sales` - Sales management
- `/api/inventory` - Product and stock management
- `/api/customers` - Customer database
- `/api/reports` - Analytics and reporting
- `/api/users` - User management
- `/api/auth` - Authentication

## Configuration

### Environment Variables (Backend)
Create a `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///./pos_system.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Vite Configuration (Frontend)
The frontend is configured to proxy API requests to the backend:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Proxy: `/api/*` requests are forwarded to the backend

## Development Workflow

### Backend Development
1. Modify models in `app/models/`
2. Update schemas in `app/schemas/`
3. Create/update endpoints in `app/api/`
4. Add business logic in `app/services/`
5. Test with FastAPI's automatic documentation

### Frontend Development
1. Create/modify components in `src/components/`
2. Add pages in `src/pages/`
3. Update API calls in `src/services/`
4. Style with Tailwind CSS classes
5. Test responsive design

## Key Features Implementation

### Sales Processing
- Real-time cart updates
- Inventory validation
- Payment processing
- Receipt generation

### Inventory Tracking
- Stock level monitoring
- Low stock alerts
- Category management
- Supplier tracking

### Customer Management
- Customer profiles
- Purchase history
- Loyalty programs
- Contact management

### Reporting System
- Sales analytics
- Revenue tracking
- Product performance
- Customer insights

## Deployment

### Backend Deployment
```bash
# Production server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files
npm run preview
```

## Security Considerations

- JWT authentication for API access
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- CORS configuration for cross-origin requests
- Environment variable management

## Contributing

1. Follow the existing code structure
2. Use type hints in Python code
3. Follow React best practices
4. Add proper error handling
5. Write meaningful commit messages
6. Test thoroughly before committing

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 (frontend) and 8000 (backend) are available
2. **Database errors**: Check database permissions and connection strings
3. **CORS issues**: Verify CORS configuration in FastAPI
4. **Module imports**: Ensure all dependencies are installed

### Debug Mode
- Backend: Set `DEBUG=True` in environment
- Frontend: Check browser console for errors

## License

This POS system is designed for business use and includes both open-source and proprietary components.

---

**Note**: This is a complete POS system suitable for small to medium businesses. The system includes inventory management, sales processing, customer management, and reporting capabilities.