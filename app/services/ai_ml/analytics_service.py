# backend/app/services/ai_ml/analytics_service.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from ...models.ai_ml_analytics import (
    MLModel, MLPrediction, SalesForecast, InventoryPrediction,
    CustomerChurnPrediction, ProductRecommendation, AnalyticsType, ModelStatus
)
from ...models.sales import SaleInvoice, SaleInvoiceItem
from ...models.inventory import Item, StockItem
from ...models.customers import Customer
from ...models.purchase import PurchaseInvoice, PurchaseInvoiceItem
from ...database import get_db_session

logger = logging.getLogger(__name__)

class AnalyticsService:
    """AI/ML Analytics Service"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
    
    def prepare_sales_data(self, days_back: int = 365) -> pd.DataFrame:
        """Prepare sales data for ML training"""
        try:
            with get_db_session() as db:
                # Get sales data
                sales_data = db.query(SaleInvoice).filter(
                    SaleInvoice.invoice_date >= date.today() - timedelta(days=days_back)
                ).all()
                
                # Convert to DataFrame
                sales_list = []
                for sale in sales_data:
                    sales_list.append({
                        'date': sale.invoice_date,
                        'total_amount': float(sale.total_amount),
                        'customer_id': sale.customer_id,
                        'payment_status': sale.payment_status,
                        'gst_amount': float(sale.gst_amount) if sale.gst_amount else 0,
                        'discount_amount': float(sale.discount_amount) if sale.discount_amount else 0
                    })
                
                df = pd.DataFrame(sales_list)
                
                # Feature engineering
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                df['day'] = df['date'].dt.day
                df['day_of_week'] = df['date'].dt.dayofweek
                df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
                df['quarter'] = df['date'].dt.quarter
                
                return df
                
        except Exception as e:
            logger.error(f"Failed to prepare sales data: {str(e)}")
            return pd.DataFrame()
    
    def prepare_inventory_data(self, days_back: int = 365) -> pd.DataFrame:
        """Prepare inventory data for ML training"""
        try:
            with get_db_session() as db:
                # Get inventory movements
                stock_data = db.query(StockItem).filter(
                    StockItem.created_at >= datetime.now() - timedelta(days=days_back)
                ).all()
                
                # Convert to DataFrame
                stock_list = []
                for stock in stock_data:
                    stock_list.append({
                        'date': stock.created_at.date(),
                        'product_id': stock.item_id,
                        'quantity': float(stock.quantity),
                        'unit_price': float(stock.unit_price) if stock.unit_price else 0,
                        'total_value': float(stock.quantity * stock.unit_price) if stock.unit_price else 0
                    })
                
                df = pd.DataFrame(stock_list)
                
                # Feature engineering
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                df['day'] = df['date'].dt.day
                df['day_of_week'] = df['date'].dt.dayofweek
                df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
                df['quarter'] = df['date'].dt.quarter
                
                return df
                
        except Exception as e:
            logger.error(f"Failed to prepare inventory data: {str(e)}")
            return pd.DataFrame()
    
    def prepare_customer_data(self, days_back: int = 365) -> pd.DataFrame:
        """Prepare customer data for ML training"""
        try:
            with get_db_session() as db:
                # Get customer data with sales history
                customers = db.query(Customer).all()
                
                customer_list = []
                for customer in customers:
                    # Get customer sales history
                    sales_count = db.query(SaleInvoice).filter(
                        SaleInvoice.customer_id == customer.id
                    ).count()
                    
                    total_sales = db.query(SaleInvoice).filter(
                        SaleInvoice.customer_id == customer.id
                    ).with_entities(SaleInvoice.total_amount).all()
                    
                    total_amount = sum([float(sale[0]) for sale in total_sales]) if total_sales else 0
                    
                    # Get last purchase date
                    last_purchase = db.query(SaleInvoice).filter(
                        SaleInvoice.customer_id == customer.id
                    ).order_by(SaleInvoice.invoice_date.desc()).first()
                    
                    days_since_last_purchase = 0
                    if last_purchase:
                        days_since_last_purchase = (date.today() - last_purchase.invoice_date).days
                    
                    customer_list.append({
                        'customer_id': customer.id,
                        'customer_type': customer.customer_type,
                        'sales_count': sales_count,
                        'total_amount': total_amount,
                        'average_order_value': total_amount / sales_count if sales_count > 0 else 0,
                        'days_since_last_purchase': days_since_last_purchase,
                        'is_active': customer.is_active
                    })
                
                return pd.DataFrame(customer_list)
                
        except Exception as e:
            logger.error(f"Failed to prepare customer data: {str(e)}")
            return pd.DataFrame()
    
    def train_sales_forecast_model(self, model_id: int) -> Dict[str, Any]:
        """Train sales forecasting model"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model:
                    raise ValueError("Model not found")
                
                # Update model status
                model.status = ModelStatus.TRAINING
                model.training_started_at = datetime.utcnow()
                db.commit()
                
                # Prepare data
                df = self.prepare_sales_data(model.training_data_period)
                if df.empty:
                    raise ValueError("No sales data available")
                
                # Feature engineering
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                # Create lag features
                for lag in [1, 7, 30]:
                    df[f'sales_lag_{lag}'] = df['total_amount'].shift(lag)
                
                # Create rolling averages
                for window in [7, 30]:
                    df[f'sales_rolling_{window}'] = df['total_amount'].rolling(window=window).mean()
                
                # Remove rows with NaN values
                df = df.dropna()
                
                # Prepare features and target
                feature_columns = ['year', 'month', 'day', 'day_of_week', 'is_weekend', 'quarter']
                for lag in [1, 7, 30]:
                    feature_columns.append(f'sales_lag_{lag}')
                for window in [7, 30]:
                    feature_columns.append(f'sales_rolling_{window}')
                
                X = df[feature_columns]
                y = df['total_amount']
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=float(model.test_split), random_state=42
                )
                
                # Train model
                model_instance = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1
                )
                model_instance.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model_instance.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Update model
                model.status = ModelStatus.TRAINED
                model.training_completed_at = datetime.utcnow()
                model.training_duration = int((model.training_completed_at - model.training_started_at).total_seconds())
                model.accuracy_score = Decimal(str(r2))
                model.accuracy_level = self._get_accuracy_level(r2)
                model.training_samples = len(X_train)
                model.performance_metrics = {
                    'mse': float(mse),
                    'r2_score': float(r2),
                    'feature_importance': dict(zip(feature_columns, model_instance.feature_importances_))
                }
                
                # Save model
                model_file_path = f"models/sales_forecast_{model_id}.joblib"
                joblib.dump(model_instance, model_file_path)
                model.model_file_path = model_file_path
                
                db.commit()
                
                return {
                    'success': True,
                    'model_id': model_id,
                    'accuracy_score': float(r2),
                    'training_samples': len(X_train),
                    'training_duration': model.training_duration
                }
                
        except Exception as e:
            logger.error(f"Sales forecast model training failed: {str(e)}")
            if 'model' in locals():
                model.status = ModelStatus.FAILED
                db.commit()
            return {'success': False, 'error': str(e)}
    
    def train_inventory_prediction_model(self, model_id: int) -> Dict[str, Any]:
        """Train inventory prediction model"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model:
                    raise ValueError("Model not found")
                
                # Update model status
                model.status = ModelStatus.TRAINING
                model.training_started_at = datetime.utcnow()
                db.commit()
                
                # Prepare data
                df = self.prepare_inventory_data(model.training_data_period)
                if df.empty:
                    raise ValueError("No inventory data available")
                
                # Feature engineering
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values(['product_id', 'date'])
                
                # Create product-specific features
                df['quantity_lag_1'] = df.groupby('product_id')['quantity'].shift(1)
                df['quantity_lag_7'] = df.groupby('product_id')['quantity'].shift(7)
                df['quantity_rolling_7'] = df.groupby('product_id')['quantity'].rolling(7).mean().reset_index(0, drop=True)
                df['quantity_rolling_30'] = df.groupby('product_id')['quantity'].rolling(30).mean().reset_index(0, drop=True)
                
                # Remove rows with NaN values
                df = df.dropna()
                
                # Prepare features and target
                feature_columns = ['year', 'month', 'day', 'day_of_week', 'is_weekend', 'quarter',
                                 'quantity_lag_1', 'quantity_lag_7', 'quantity_rolling_7', 'quantity_rolling_30']
                
                X = df[feature_columns]
                y = df['quantity']
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=float(model.test_split), random_state=42
                )
                
                # Train model
                model_instance = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1
                )
                model_instance.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model_instance.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Update model
                model.status = ModelStatus.TRAINED
                model.training_completed_at = datetime.utcnow()
                model.training_duration = int((model.training_completed_at - model.training_started_at).total_seconds())
                model.accuracy_score = Decimal(str(r2))
                model.accuracy_level = self._get_accuracy_level(r2)
                model.training_samples = len(X_train)
                model.performance_metrics = {
                    'mse': float(mse),
                    'r2_score': float(r2),
                    'feature_importance': dict(zip(feature_columns, model_instance.feature_importances_))
                }
                
                # Save model
                model_file_path = f"models/inventory_prediction_{model_id}.joblib"
                joblib.dump(model_instance, model_file_path)
                model.model_file_path = model_file_path
                
                db.commit()
                
                return {
                    'success': True,
                    'model_id': model_id,
                    'accuracy_score': float(r2),
                    'training_samples': len(X_train),
                    'training_duration': model.training_duration
                }
                
        except Exception as e:
            logger.error(f"Inventory prediction model training failed: {str(e)}")
            if 'model' in locals():
                model.status = ModelStatus.FAILED
                db.commit()
            return {'success': False, 'error': str(e)}
    
    def train_customer_churn_model(self, model_id: int) -> Dict[str, Any]:
        """Train customer churn prediction model"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model:
                    raise ValueError("Model not found")
                
                # Update model status
                model.status = ModelStatus.TRAINING
                model.training_started_at = datetime.utcnow()
                db.commit()
                
                # Prepare data
                df = self.prepare_customer_data(model.training_data_period)
                if df.empty:
                    raise ValueError("No customer data available")
                
                # Create churn label (customers with no purchase in last 90 days)
                df['is_churn'] = (df['days_since_last_purchase'] > 90).astype(int)
                
                # Prepare features and target
                feature_columns = ['sales_count', 'total_amount', 'average_order_value', 'days_since_last_purchase']
                X = df[feature_columns]
                y = df['is_churn']
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=float(model.test_split), random_state=42
                )
                
                # Train model
                model_instance = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    n_jobs=-1
                )
                model_instance.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model_instance.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Update model
                model.status = ModelStatus.TRAINED
                model.training_completed_at = datetime.utcnow()
                model.training_duration = int((model.training_completed_at - model.training_started_at).total_seconds())
                model.accuracy_score = Decimal(str(accuracy))
                model.accuracy_level = self._get_accuracy_level(accuracy)
                model.training_samples = len(X_train)
                model.performance_metrics = {
                    'accuracy': float(accuracy),
                    'classification_report': classification_report(y_test, y_pred, output_dict=True),
                    'feature_importance': dict(zip(feature_columns, model_instance.feature_importances_))
                }
                
                # Save model
                model_file_path = f"models/customer_churn_{model_id}.joblib"
                joblib.dump(model_instance, model_file_path)
                model.model_file_path = model_file_path
                
                db.commit()
                
                return {
                    'success': True,
                    'model_id': model_id,
                    'accuracy_score': float(accuracy),
                    'training_samples': len(X_train),
                    'training_duration': model.training_duration
                }
                
        except Exception as e:
            logger.error(f"Customer churn model training failed: {str(e)}")
            if 'model' in locals():
                model.status = ModelStatus.FAILED
                db.commit()
            return {'success': False, 'error': str(e)}
    
    def predict_sales_forecast(self, model_id: int, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict sales forecast"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model or model.status != ModelStatus.TRAINED:
                    raise ValueError("Model not trained")
                
                # Load model
                model_instance = joblib.load(model.model_file_path)
                
                # Prepare prediction data
                df = self.prepare_sales_data(30)  # Last 30 days
                if df.empty:
                    raise ValueError("No recent sales data available")
                
                # Feature engineering
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                
                # Create lag features
                for lag in [1, 7, 30]:
                    df[f'sales_lag_{lag}'] = df['total_amount'].shift(lag)
                
                # Create rolling averages
                for window in [7, 30]:
                    df[f'sales_rolling_{window}'] = df['total_amount'].rolling(window=window).mean()
                
                # Get latest data for prediction
                latest_data = df.iloc[-1:].copy()
                
                # Prepare features
                feature_columns = ['year', 'month', 'day', 'day_of_week', 'is_weekend', 'quarter']
                for lag in [1, 7, 30]:
                    feature_columns.append(f'sales_lag_{lag}')
                for window in [7, 30]:
                    feature_columns.append(f'sales_rolling_{window}')
                
                X = latest_data[feature_columns]
                
                # Make prediction
                prediction = model_instance.predict(X)[0]
                
                # Create prediction record
                prediction_record = MLPrediction(
                    model_id=model_id,
                    prediction_type=AnalyticsType.SALES_FORECAST,
                    input_data=X.iloc[0].to_dict(),
                    prediction_result={'predicted_sales': float(prediction)},
                    confidence_score=float(model.accuracy_score),
                    prediction_accuracy=model.accuracy_level
                )
                
                db.add(prediction_record)
                db.commit()
                
                return {
                    'success': True,
                    'prediction_id': prediction_record.id,
                    'predicted_sales': float(prediction),
                    'confidence_score': float(model.accuracy_score),
                    'model_accuracy': model.accuracy_level.value
                }
                
        except Exception as e:
            logger.error(f"Sales forecast prediction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_inventory_demand(self, model_id: int, product_id: int) -> Dict[str, Any]:
        """Predict inventory demand for a product"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model or model.status != ModelStatus.TRAINED:
                    raise ValueError("Model not trained")
                
                # Load model
                model_instance = joblib.load(model.model_file_path)
                
                # Prepare prediction data
                df = self.prepare_inventory_data(30)  # Last 30 days
                if df.empty:
                    raise ValueError("No recent inventory data available")
                
                # Filter for specific product
                product_data = df[df['product_id'] == product_id]
                if product_data.empty:
                    raise ValueError("No data for this product")
                
                # Feature engineering
                product_data['date'] = pd.to_datetime(product_data['date'])
                product_data = product_data.sort_values('date')
                
                # Create product-specific features
                product_data['quantity_lag_1'] = product_data['quantity'].shift(1)
                product_data['quantity_lag_7'] = product_data['quantity'].shift(7)
                product_data['quantity_rolling_7'] = product_data['quantity'].rolling(7).mean()
                product_data['quantity_rolling_30'] = product_data['quantity'].rolling(30).mean()
                
                # Get latest data for prediction
                latest_data = product_data.iloc[-1:].copy()
                
                # Prepare features
                feature_columns = ['year', 'month', 'day', 'day_of_week', 'is_weekend', 'quarter',
                                 'quantity_lag_1', 'quantity_lag_7', 'quantity_rolling_7', 'quantity_rolling_30']
                
                X = latest_data[feature_columns]
                
                # Make prediction
                prediction = model_instance.predict(X)[0]
                
                # Create prediction record
                prediction_record = MLPrediction(
                    model_id=model_id,
                    prediction_type=AnalyticsType.INVENTORY_PREDICTION,
                    input_data=X.iloc[0].to_dict(),
                    prediction_result={'predicted_demand': float(prediction)},
                    confidence_score=float(model.accuracy_score),
                    prediction_accuracy=model.accuracy_level,
                    entity_id=product_id,
                    entity_type='product'
                )
                
                db.add(prediction_record)
                db.commit()
                
                return {
                    'success': True,
                    'prediction_id': prediction_record.id,
                    'predicted_demand': float(prediction),
                    'confidence_score': float(model.accuracy_score),
                    'model_accuracy': model.accuracy_level.value
                }
                
        except Exception as e:
            logger.error(f"Inventory demand prediction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_customer_churn(self, model_id: int, customer_id: int) -> Dict[str, Any]:
        """Predict customer churn probability"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model or model.status != ModelStatus.TRAINED:
                    raise ValueError("Model not trained")
                
                # Load model
                model_instance = joblib.load(model.model_file_path)
                
                # Get customer data
                customer_data = self.prepare_customer_data(365)
                customer_row = customer_data[customer_data['customer_id'] == customer_id]
                
                if customer_row.empty:
                    raise ValueError("Customer not found")
                
                # Prepare features
                feature_columns = ['sales_count', 'total_amount', 'average_order_value', 'days_since_last_purchase']
                X = customer_row[feature_columns]
                
                # Make prediction
                churn_probability = model_instance.predict_proba(X)[0][1]  # Probability of churn
                
                # Create prediction record
                prediction_record = MLPrediction(
                    model_id=model_id,
                    prediction_type=AnalyticsType.CUSTOMER_CHURN,
                    input_data=X.iloc[0].to_dict(),
                    prediction_result={'churn_probability': float(churn_probability)},
                    confidence_score=float(model.accuracy_score),
                    prediction_accuracy=model.accuracy_level,
                    entity_id=customer_id,
                    entity_type='customer'
                )
                
                db.add(prediction_record)
                db.commit()
                
                return {
                    'success': True,
                    'prediction_id': prediction_record.id,
                    'churn_probability': float(churn_probability),
                    'confidence_score': float(model.accuracy_score),
                    'model_accuracy': model.accuracy_level.value
                }
                
        except Exception as e:
            logger.error(f"Customer churn prediction failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_accuracy_level(self, accuracy_score: float) -> str:
        """Get accuracy level based on score"""
        if accuracy_score >= 0.9:
            return 'very_high'
        elif accuracy_score >= 0.8:
            return 'high'
        elif accuracy_score >= 0.7:
            return 'medium'
        else:
            return 'low'
    
    def get_model_performance(self, model_id: int) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            with get_db_session() as db:
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if not model:
                    raise ValueError("Model not found")
                
                return {
                    'success': True,
                    'model_id': model_id,
                    'model_name': model.model_name,
                    'model_type': model.model_type.value,
                    'status': model.status.value,
                    'accuracy_score': float(model.accuracy_score) if model.accuracy_score else 0,
                    'accuracy_level': model.accuracy_level.value if model.accuracy_level else 'low',
                    'training_samples': model.training_samples,
                    'training_duration': model.training_duration,
                    'performance_metrics': model.performance_metrics,
                    'feature_importance': model.feature_importance,
                    'created_at': model.created_at,
                    'updated_at': model.updated_at
                }
                
        except Exception as e:
            logger.error(f"Failed to get model performance: {str(e)}")
            return {'success': False, 'error': str(e)}