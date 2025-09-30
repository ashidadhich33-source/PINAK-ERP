# PINAK-ERP Frontend

A modern React-based frontend for the PINAK-ERP system, built with Vite, Tailwind CSS, and React Router.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── common/         # Common UI components
│   └── layout/         # Layout components
├── contexts/           # React Context providers
├── pages/              # Page components
├── services/           # API services
├── utils/              # Utility functions
└── styles/             # Global styles
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier

## 🎨 Styling

This project uses Tailwind CSS for styling. Key design tokens:

- **Primary**: Blue (#3b82f6)
- **Secondary**: Gray (#64748b)
- **Success**: Green (#22c55e)
- **Warning**: Yellow (#f59e0b)
- **Danger**: Red (#ef4444)

## 🔧 Configuration

Environment variables are configured in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_APP_NAME=PINAK-ERP
```

## 📱 Features

- ✅ Responsive design
- ✅ Dark/light theme support
- ✅ Authentication & authorization
- ✅ Role-based access control
- ✅ Real-time notifications
- ✅ Form validation
- ✅ Error handling
- ✅ Loading states

## 🚀 Deployment

1. **Build the project:**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to your hosting provider.

## 🤝 Contributing

1. Follow the existing code style
2. Use meaningful commit messages
3. Test your changes thoroughly
4. Update documentation as needed

## 📄 License

This project is part of the PINAK-ERP system.