# POS System Frontend

A modern React-based Point of Sale (POS) system frontend built with Vite, React, and Tailwind CSS.

## Features

- **Dashboard**: Overview of sales, inventory, and key metrics
- **Sales Management**: Process sales with cart functionality
- **Inventory Management**: Track products and stock levels
- **Customer Management**: Manage customer database
- **Reports & Analytics**: View sales reports and business insights
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

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

4. Open your browser and visit `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable React components
│   │   └── Layout.jsx      # Main layout component
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx   # Dashboard page
│   │   ├── Sales.jsx       # Sales management page
│   │   ├── Inventory.jsx   # Inventory management page
│   │   ├── Customers.jsx   # Customer management page
│   │   └── Reports.jsx     # Reports and analytics page
│   ├── services/           # API services
│   │   └── api.js          # Axios configuration
│   ├── App.jsx             # Main App component
│   ├── main.jsx            # React entry point
│   └── index.css           # Global styles with Tailwind
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
└── tailwind.config.js      # Tailwind CSS configuration
```

## API Integration

The frontend is configured to communicate with a Python backend API. The API endpoints are proxied through Vite's development server:

- Base URL: `/api` (proxied to `http://localhost:8000`)
- Authentication: JWT tokens stored in localStorage
- Error handling: Global error interceptor

## Key Components

### Layout Component
- Responsive sidebar navigation
- Mobile-friendly hamburger menu
- User profile section

### Dashboard
- Sales statistics cards
- Recent activity feed
- Low stock alerts

### Sales Page
- Product search and filtering
- Shopping cart functionality
- Checkout process with payment methods

### Inventory Management
- Product listing with search
- Stock level tracking
- Add/edit/delete products

### Customer Management
- Customer database
- Search and filter customers
- Customer purchase history

### Reports
- Daily sales charts
- Top products analysis
- Category-wise sales
- Monthly revenue trends

## Customization

### Styling
The project uses Tailwind CSS for styling. You can customize:
- Colors: Modify `tailwind.config.js`
- Layout: Update component styles
- Responsive breakpoints: Configure in Tailwind config

### API Endpoints
Update the API service in `src/services/api.js` to match your backend endpoints.

### Routing
Add new routes in `src/App.jsx` and create corresponding page components.

## Development

### Adding New Pages
1. Create a new component in `src/pages/`
2. Add the route in `src/App.jsx`
3. Update the navigation in `src/components/Layout.jsx`

### API Integration
1. Add API calls to `src/services/api.js`
2. Use the API service in your components
3. Handle loading states and errors

## Production Build

To build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Contributing

1. Follow the existing code structure
2. Use functional components with hooks
3. Follow Tailwind CSS best practices
4. Add proper error handling
5. Test on different screen sizes

## License

This project is part of a POS system and is intended for business use.