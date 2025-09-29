#!/usr/bin/env python3
"""
Simple ERP Server for Frontend Demo
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Create FastAPI app
app = FastAPI(
    title="ERP System API",
    description="Enterprise Resource Planning System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "ERP System is running",
        "version": "1.0.0"
    }

# API endpoints for demo
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    return {
        "total_sales": 125450,
        "total_orders": 1234,
        "active_customers": 2456,
        "inventory_items": 5678,
        "total_revenue": 2500000,
        "pending_orders": 23,
        "low_stock_items": 15
    }

@app.get("/api/companies")
async def get_companies():
    return [
        {
            "id": "demo",
            "name": "Demo Company",
            "location": "Mumbai, Maharashtra",
            "phone": "+91 9876543210",
            "email": "demo@company.com",
            "employees": 25,
            "branches": 3,
            "revenue": 2500000,
            "customers": 150,
            "status": "active"
        },
        {
            "id": "test",
            "name": "Test Company",
            "location": "Delhi, NCR",
            "phone": "+91 9876543211",
            "email": "test@company.com",
            "employees": 15,
            "branches": 2,
            "revenue": 1200000,
            "customers": 75,
            "status": "active"
        }
    ]

@app.get("/api/inventory/items")
async def get_inventory_items():
    return [
        {
            "id": "LAP-001",
            "name": "Laptop Computer",
            "description": "High-performance laptop",
            "category": "Electronics",
            "price": 50000,
            "stock": 15,
            "min_stock": 10,
            "status": "active"
        },
        {
            "id": "MOU-001",
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "category": "Electronics",
            "price": 500,
            "stock": 5,
            "min_stock": 10,
            "status": "low_stock"
        }
    ]

@app.get("/api/sales/invoices")
async def get_sales_invoices():
    return [
        {
            "id": "INV-001",
            "customer": "John Doe",
            "date": "2024-01-15",
            "amount": 2500,
            "status": "paid"
        },
        {
            "id": "INV-002",
            "customer": "Jane Smith",
            "date": "2024-01-14",
            "amount": 5000,
            "status": "pending"
        }
    ]

@app.get("/api/purchase/orders")
async def get_purchase_orders():
    return [
        {
            "id": "PO-001",
            "supplier": "ABC Electronics",
            "date": "2024-01-15",
            "amount": 25000,
            "status": "pending"
        },
        {
            "id": "PO-002",
            "supplier": "XYZ Suppliers",
            "date": "2024-01-14",
            "amount": 15000,
            "status": "approved"
        }
    ]

@app.get("/api/accounting/accounts")
async def get_accounts():
    return [
        {
            "code": "1001",
            "name": "Cash",
            "type": "Asset",
            "balance": 45000,
            "status": "active"
        },
        {
            "code": "1002",
            "name": "Bank Account",
            "type": "Asset",
            "balance": 250000,
            "status": "active"
        }
    ]

@app.get("/api/reports/summary")
async def get_reports_summary():
    return {
        "total_reports": 45,
        "scheduled_reports": 12,
        "exports_today": 8,
        "data_points": 1234
    }

# Serve static files
app.mount("/static", StaticFiles(directory="frontend-mockups"), name="static")

# Serve main index page
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

# Serve frontend pages
@app.get("/{path:path}")
async def serve_frontend(path: str):
    # Check if it's a frontend page
    if path.endswith('.html') or path in ['dashboard', 'companies', 'gst', 'inventory', 'purchase', 'sales', 'accounting', 'reports', 'loyalty', 'system']:
        if path.endswith('.html'):
            file_path = f"frontend-mockups/{path}"
        else:
            # Map paths to HTML files
            path_map = {
                'dashboard': '03-dashboard.html',
                'companies': '04-companies.html',
                'gst': '05-gst-management.html',
                'inventory': '06-inventory.html',
                'purchase': '07-purchase.html',
                'sales': '08-sales.html',
                'accounting': '09-accounting.html',
                'reports': '10-reports.html',
                'loyalty': '11-loyalty.html',
                'system': '12-system.html'
            }
            file_path = f"frontend-mockups/{path_map.get(path, '03-dashboard.html')}"
        
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    # Default to index.html
    return FileResponse("index.html")

if __name__ == "__main__":
    print("Starting ERP System Server...")
    print("Frontend available at: http://127.0.0.1:8000")
    print("API documentation at: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        "simple_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )