# backend/app/models/ai_ml_analytics.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
from .base import BaseModel

class AnalyticsType(PyEnum):
    """Analytics Type"""
    SALES_FORECAST = "sales_forecast"
    INVENTORY_PREDICTION = "inventory_prediction"
    CUSTOMER_CHURN = "customer_churn"
    DEMAND_FORECAST = "demand_forecast"
    PRICE_OPTIMIZATION = "price_optimization"
    FRAUD_DETECTION = "fraud_detection"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    PRODUCT_RECOMMENDATION = "product_recommendation"

class ModelStatus(PyEnum):
    """Model Status"""
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    RETIRED = "retired"

class PredictionAccuracy(PyEnum):
    """Prediction Accuracy Level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class MLModel(BaseModel):
    """Machine Learning Model Management"""
    __tablename__ = "ml_model"
    
    # Model Information
    model_name = Column(String(200), nullable=False)
    model_type = Column(Enum(AnalyticsType), nullable=False)
    model_version = Column(String(20), default='1.0')
    model_description = Column(Text, nullable=True)
    
    # Model Configuration
    algorithm = Column(String(100), nullable=False)  # linear_regression, random_forest, lstm, etc.
    model_parameters = Column(JSON, nullable=True)
    feature_columns = Column(JSON, nullable=True)
    target_column = Column(String(100), nullable=True)
    
    # Training Configuration
    training_data_period = Column(Integer, default=365)  # days
    validation_split = Column(Numeric(5, 4), default=0.2)  # 20%
    test_split = Column(Numeric(5, 4), default=0.1)  # 10%
    
    # Model Status
    status = Column(Enum(ModelStatus), default=ModelStatus.TRAINING)
    accuracy_score = Column(Numeric(5, 4), nullable=True)
    accuracy_level = Column(Enum(PredictionAccuracy), nullable=True)
    
    # Model Files
    model_file_path = Column(String(500), nullable=True)
    scaler_file_path = Column(String(500), nullable=True)
    encoder_file_path = Column(String(500), nullable=True)
    
    # Training Information
    training_started_at = Column(DateTime, nullable=True)
    training_completed_at = Column(DateTime, nullable=True)
    training_duration = Column(Integer, nullable=True)  # seconds
    training_samples = Column(Integer, nullable=True)
    
    # Deployment Information
    deployed_at = Column(DateTime, nullable=True)
    deployed_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    is_active = Column(Boolean, default=False)
    
    # Performance Metrics
    performance_metrics = Column(JSON, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    
    # Relationships
    predictions = relationship("MLPrediction", back_populates="model")
    training_logs = relationship("MLTrainingLog", back_populates="model")
    deployed_by_user = relationship("User", foreign_keys=[deployed_by])
    
    def __repr__(self):
        return f"<MLModel(name='{self.model_name}', type='{self.model_type}', status='{self.status}')>"

class MLPrediction(BaseModel):
    """ML Model Predictions"""
    __tablename__ = "ml_prediction"
    
    # Prediction Information
    model_id = Column(Integer, ForeignKey('ml_model.id'), nullable=False)
    prediction_type = Column(Enum(AnalyticsType), nullable=False)
    
    # Prediction Data
    input_data = Column(JSON, nullable=False)
    prediction_result = Column(JSON, nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=True)
    prediction_accuracy = Column(Enum(PredictionAccuracy), nullable=True)
    
    # Context Information
    prediction_date = Column(DateTime, default=datetime.utcnow)
    prediction_period = Column(String(50), nullable=True)  # daily, weekly, monthly
    entity_id = Column(Integer, nullable=True)  # customer_id, product_id, etc.
    entity_type = Column(String(50), nullable=True)  # customer, product, etc.
    
    # Business Impact
    business_value = Column(Numeric(15, 2), nullable=True)
    action_taken = Column(String(200), nullable=True)
    action_result = Column(String(200), nullable=True)
    
    # Validation
    actual_value = Column(JSON, nullable=True)
    prediction_error = Column(Numeric(10, 6), nullable=True)
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Relationships
    model = relationship("MLModel", back_populates="predictions")
    
    def __repr__(self):
        return f"<MLPrediction(model_id={self.model_id}, type='{self.prediction_type}', confidence={self.confidence_score})>"

class MLTrainingLog(BaseModel):
    """ML Model Training Logs"""
    __tablename__ = "ml_training_log"
    
    # Training Information
    model_id = Column(Integer, ForeignKey('ml_model.id'), nullable=False)
    training_epoch = Column(Integer, nullable=True)
    training_batch = Column(Integer, nullable=True)
    
    # Training Metrics
    loss_value = Column(Numeric(10, 6), nullable=True)
    accuracy_value = Column(Numeric(5, 4), nullable=True)
    validation_loss = Column(Numeric(10, 6), nullable=True)
    validation_accuracy = Column(Numeric(5, 4), nullable=True)
    
    # Training Status
    training_status = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    logged_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model = relationship("MLModel", back_populates="training_logs")
    
    def __repr__(self):
        return f"<MLTrainingLog(model_id={self.model_id}, epoch={self.training_epoch}, accuracy={self.accuracy_value})>"

class SalesForecast(BaseModel):
    """Sales Forecasting Analytics"""
    __tablename__ = "sales_forecast"
    
    # Forecast Information
    forecast_date = Column(Date, nullable=False, index=True)
    forecast_period = Column(String(20), nullable=False)  # daily, weekly, monthly
    forecast_horizon = Column(Integer, nullable=False)  # days ahead
    
    # Forecast Data
    predicted_sales = Column(Numeric(15, 2), nullable=False)
    confidence_interval_lower = Column(Numeric(15, 2), nullable=True)
    confidence_interval_upper = Column(Numeric(15, 2), nullable=True)
    confidence_level = Column(Numeric(5, 4), nullable=True)
    
    # Context Information
    product_id = Column(Integer, ForeignKey('item.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    category_id = Column(Integer, nullable=True)
    region = Column(String(100), nullable=True)
    
    # Model Information
    model_id = Column(Integer, ForeignKey('ml_model.id'), nullable=True)
    prediction_id = Column(Integer, ForeignKey('ml_prediction.id'), nullable=True)
    
    # Validation
    actual_sales = Column(Numeric(15, 2), nullable=True)
    forecast_error = Column(Numeric(10, 6), nullable=True)
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Relationships
    product = relationship("Item")
    customer = relationship("Customer")
    model = relationship("MLModel")
    prediction = relationship("MLPrediction")
    
    def __repr__(self):
        return f"<SalesForecast(date='{self.forecast_date}', sales={self.predicted_sales}, confidence={self.confidence_level})>"

class InventoryPrediction(BaseModel):
    """Inventory Prediction Analytics"""
    __tablename__ = "inventory_prediction"
    
    # Prediction Information
    prediction_date = Column(Date, nullable=False, index=True)
    prediction_horizon = Column(Integer, nullable=False)  # days ahead
    
    # Prediction Data
    predicted_demand = Column(Numeric(12, 2), nullable=False)
    predicted_stockout_risk = Column(Numeric(5, 4), nullable=True)
    recommended_order_quantity = Column(Numeric(12, 2), nullable=True)
    recommended_reorder_point = Column(Numeric(12, 2), nullable=True)
    
    # Context Information
    product_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    warehouse_id = Column(Integer, nullable=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=True)
    
    # Model Information
    model_id = Column(Integer, ForeignKey('ml_model.id'), nullable=True)
    prediction_id = Column(Integer, ForeignKey('ml_prediction.id'), nullable=True)
    
    # Validation
    actual_demand = Column(Numeric(12, 2), nullable=True)
    prediction_error = Column(Numeric(10, 6), nullable=True)
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Relationships
    product = relationship("Item")
    supplier = relationship("Supplier")
    model = relationship("MLModel")
    prediction = relationship("MLPrediction")
    
    def __repr__(self):
        return f"<InventoryPrediction(product_id={self.product_id}, demand={self.predicted_demand}, risk={self.predicted_stockout_risk})>"

class CustomerChurnPrediction(BaseModel):
    """Customer Churn Prediction Analytics"""
    __tablename__ = "customer_churn_prediction"
    
    # Prediction Information
    prediction_date = Column(Date, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    
    # Prediction Data
    churn_probability = Column(Numeric(5, 4), nullable=False)
    churn_risk_level = Column(Enum(PredictionAccuracy), nullable=True)
    predicted_churn_date = Column(Date, nullable=True)
    
    # Risk Factors
    risk_factors = Column(JSON, nullable=True)
    key_indicators = Column(JSON, nullable=True)
    
    # Model Information
    model_id = Column(Integer, ForeignKey('ml_model.id'), nullable=True)
    prediction_id = Column(Integer, ForeignKey('ml_prediction.id'), nullable=True)
    
    # Validation
    actual_churn = Column(Boolean, nullable=True)
    churn_date = Column(Date, nullable=True)
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    model = relationship("MLModel")
    prediction = relationship("MLPrediction")
    
    def __repr__(self):
        return f"<CustomerChurnPrediction(customer_id={self.customer_id}, probability={self.churn_probability}, risk='{self.churn_risk_level}')>"

class ProductRecommendation(BaseModel):
    """Product Recommendation Analytics"""
    __tablename__ = "product_recommendation"
    
    # Recommendation Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    recommendation_date = Column(Date, default=date.today, index=True)
    
    # Recommendation Data
    recommendation_score = Column(Numeric(5, 4), nullable=False)
    recommendation_rank = Column(Integer, nullable=True)
    recommendation_reason = Column(Text, nullable=True)
    
    # Model Information
    model_id = Column(Integer, ForeignKey('ml_model.id'), nullable=True)
    prediction_id = Column(Integer, ForeignKey('ml_prediction.id'), nullable=True)
    
    # Validation
    customer_purchased = Column(Boolean, nullable=True)
    purchase_date = Column(Date, nullable=True)
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    product = relationship("Item")
    model = relationship("MLModel")
    prediction = relationship("MLPrediction")
    
    def __repr__(self):
        return f"<ProductRecommendation(customer_id={self.customer_id}, product_id={self.product_id}, score={self.recommendation_score})>"

class AnalyticsDashboard(BaseModel):
    """Analytics Dashboard Configuration"""
    __tablename__ = "analytics_dashboard"
    
    # Dashboard Information
    dashboard_name = Column(String(200), nullable=False)
    dashboard_type = Column(String(50), nullable=False)  # sales, inventory, customer, financial
    dashboard_description = Column(Text, nullable=True)
    
    # Dashboard Configuration
    dashboard_config = Column(JSON, nullable=False)
    widget_configs = Column(JSON, nullable=True)
    filter_configs = Column(JSON, nullable=True)
    
    # Access Control
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<AnalyticsDashboard(name='{self.dashboard_name}', type='{self.dashboard_type}')>"