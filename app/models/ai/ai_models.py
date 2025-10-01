# backend/app/models/ai/ai_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel

class AIAnalytics(BaseModel):
    """AI Analytics model for managing AI analytics"""
    __tablename__ = "ai_analytics"
    
    analytics_name = Column(String(100), nullable=False)
    analytics_type = Column(String(50), nullable=False)  # sales, inventory, customer, etc.
    data_source = Column(String(100), nullable=False)
    metrics = Column(Text, nullable=True)  # JSON metrics
    insights = Column(Text, nullable=True)  # JSON insights
    accuracy = Column(Numeric(5, 2), nullable=True)
    status = Column(String(20), default='active')  # active, inactive, error
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="ai_analytics")
    predictions = relationship("AIPrediction", back_populates="analytics")
    
    def __repr__(self):
        return f"<AIAnalytics(analytics_name='{self.analytics_name}', analytics_type='{self.analytics_type}')>"

class AIPrediction(BaseModel):
    """AI Prediction model for managing AI predictions"""
    __tablename__ = "ai_prediction"
    
    analytics_id = Column(Integer, ForeignKey('ai_analytics.id'), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # sales_forecast, inventory_demand, etc.
    prediction_data = Column(Text, nullable=False)  # JSON prediction data
    confidence_score = Column(Numeric(5, 2), nullable=True)
    prediction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), default='active')  # active, expired, invalid
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    analytics = relationship("AIAnalytics", back_populates="predictions")
    company = relationship("Company", back_populates="ai_predictions")
    
    def __repr__(self):
        return f"<AIPrediction(prediction_type='{self.prediction_type}', confidence_score={self.confidence_score})>"

class AIModel(BaseModel):
    """AI Model model for managing AI models"""
    __tablename__ = "ai_model"
    
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # regression, classification, clustering
    model_version = Column(String(20), nullable=False)
    model_path = Column(String(255), nullable=True)
    model_parameters = Column(Text, nullable=True)  # JSON parameters
    training_data = Column(Text, nullable=True)  # JSON training data info
    performance_metrics = Column(Text, nullable=True)  # JSON performance metrics
    status = Column(String(20), default='draft')  # draft, training, active, deprecated
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="ai_models")
    trainings = relationship("AITraining", back_populates="model")
    
    def __repr__(self):
        return f"<AIModel(model_name='{self.model_name}', model_type='{self.model_type}')>"

class AITraining(BaseModel):
    """AI Training model for managing AI training sessions"""
    __tablename__ = "ai_training"
    
    model_id = Column(Integer, ForeignKey('ai_model.id'), nullable=False)
    training_name = Column(String(100), nullable=False)
    training_data = Column(Text, nullable=False)  # JSON training data
    training_parameters = Column(Text, nullable=True)  # JSON training parameters
    training_status = Column(String(20), default='pending')  # pending, running, completed, failed
    training_start = Column(DateTime, nullable=True)
    training_end = Column(DateTime, nullable=True)
    training_results = Column(Text, nullable=True)  # JSON training results
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    model = relationship("AIModel", back_populates="trainings")
    company = relationship("Company", back_populates="ai_trainings")
    
    def __repr__(self):
        return f"<AITraining(training_name='{self.training_name}', training_status='{self.training_status}')>"

class AIInsight(BaseModel):
    """AI Insight model for managing AI insights"""
    __tablename__ = "ai_insight"
    
    insight_name = Column(String(100), nullable=False)
    insight_type = Column(String(50), nullable=False)  # trend, anomaly, pattern, etc.
    insight_data = Column(Text, nullable=False)  # JSON insight data
    insight_score = Column(Numeric(5, 2), nullable=True)
    insight_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), default='active')  # active, dismissed, archived
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="ai_insights")
    
    def __repr__(self):
        return f"<AIInsight(insight_name='{self.insight_name}', insight_type='{self.insight_type}')>"

class AIRecommendation(BaseModel):
    """AI Recommendation model for managing AI recommendations"""
    __tablename__ = "ai_recommendation"
    
    recommendation_name = Column(String(100), nullable=False)
    recommendation_type = Column(String(50), nullable=False)  # product, pricing, marketing, etc.
    recommendation_data = Column(Text, nullable=False)  # JSON recommendation data
    recommendation_score = Column(Numeric(5, 2), nullable=True)
    recommendation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), default='active')  # active, implemented, dismissed
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="ai_recommendations")
    
    def __repr__(self):
        return f"<AIRecommendation(recommendation_name='{self.recommendation_name}', recommendation_type='{self.recommendation_type}')>"