# backend/app/models/l10n_in/indian_geography.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from .base import BaseModel

class Country(BaseModel):
    """Country model for international support"""
    __tablename__ = "country"
    
    # Basic Information
    country_code = Column(String(3), nullable=False, unique=True, index=True)  # ISO 3166-1 alpha-3
    country_name = Column(String(100), nullable=False)
    country_name_local = Column(String(100), nullable=True)  # Local language name
    currency_code = Column(String(3), nullable=True)  # ISO 4217 currency code
    currency_symbol = Column(String(5), nullable=True)
    phone_code = Column(String(5), nullable=True)  # International dialing code
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Country(code='{self.country_code}', name='{self.country_name}')>"

class IndianState(BaseModel):
    """Indian States and Union Territories"""
    __tablename__ = "indian_state"
    
    # Basic Information
    state_code = Column(String(2), nullable=False, unique=True, index=True)  # 2-digit state code
    state_name = Column(String(100), nullable=False)
    state_name_local = Column(String(100), nullable=True)  # Local language name
    state_type = Column(String(20), default='state')  # state, union_territory
    
    # GST Information
    gst_state_code = Column(String(2), nullable=True)  # GST state code
    gst_state_name = Column(String(100), nullable=True)
    
    # Geographic Information
    region = Column(String(50), nullable=True)  # North, South, East, West, Central, Northeast
    capital = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Country Reference
    country_id = Column(Integer, ForeignKey('country.id'), nullable=False)
    country = relationship("Country", back_populates="states")
    
    def __repr__(self):
        return f"<IndianState(code='{self.state_code}', name='{self.state_name}', type='{self.state_type}')>"

class IndianCity(BaseModel):
    """Indian Cities and Towns"""
    __tablename__ = "indian_city"
    
    # Basic Information
    city_name = Column(String(100), nullable=False)
    city_name_local = Column(String(100), nullable=True)  # Local language name
    city_type = Column(String(20), default='city')  # city, town, village, metro
    
    # Geographic Information
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    pincode = Column(String(10), nullable=True)  # Primary pincode
    area_code = Column(String(5), nullable=True)  # STD code
    
    # Status
    is_active = Column(Boolean, default=True)
    is_major_city = Column(Boolean, default=False)
    
    # State Reference
    state_id = Column(Integer, ForeignKey('indian_state.id'), nullable=False)
    state = relationship("IndianState", back_populates="cities")
    
    def __repr__(self):
        return f"<IndianCity(name='{self.city_name}', state='{self.state.state_name if self.state else None}')>"

class IndianPincode(BaseModel):
    """Indian Pincode Database"""
    __tablename__ = "indian_pincode"
    
    # Pincode Information
    pincode = Column(String(6), nullable=False, index=True)
    area_name = Column(String(200), nullable=False)
    area_type = Column(String(50), nullable=True)  # Post Office, Area, Locality
    
    # Geographic Information
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # City Reference
    city_id = Column(Integer, ForeignKey('indian_city.id'), nullable=True)
    city = relationship("IndianCity", back_populates="pincodes")
    
    # State Reference
    state_id = Column(Integer, ForeignKey('indian_state.id'), nullable=False)
    state = relationship("IndianState", back_populates="pincodes")
    
    def __repr__(self):
        return f"<IndianPincode(pincode='{self.pincode}', area='{self.area_name}')>"

class IndianDistrict(BaseModel):
    """Indian Districts"""
    __tablename__ = "indian_district"
    
    # Basic Information
    district_name = Column(String(100), nullable=False)
    district_name_local = Column(String(100), nullable=True)
    
    # Geographic Information
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # State Reference
    state_id = Column(Integer, ForeignKey('indian_state.id'), nullable=False)
    state = relationship("IndianState", back_populates="districts")
    
    def __repr__(self):
        return f"<IndianDistrict(name='{self.district_name}', state='{self.state.state_name if self.state else None}')>"

class IndianTaluka(BaseModel):
    """Indian Talukas/Tehsils"""
    __tablename__ = "indian_taluka"
    
    # Basic Information
    taluka_name = Column(String(100), nullable=False)
    taluka_name_local = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # District Reference
    district_id = Column(Integer, ForeignKey('indian_district.id'), nullable=False)
    district = relationship("IndianDistrict", back_populates="talukas")
    
    def __repr__(self):
        return f"<IndianTaluka(name='{self.taluka_name}', district='{self.district.district_name if self.district else None}')>"

class IndianVillage(BaseModel):
    """Indian Villages"""
    __tablename__ = "indian_village"
    
    # Basic Information
    village_name = Column(String(100), nullable=False)
    village_name_local = Column(String(100), nullable=True)
    
    # Geographic Information
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Taluka Reference
    taluka_id = Column(Integer, ForeignKey('indian_taluka.id'), nullable=False)
    taluka = relationship("IndianTaluka", back_populates="villages")
    
    def __repr__(self):
        return f"<IndianVillage(name='{self.village_name}', taluka='{self.taluka.taluka_name if self.taluka else None}')>"

# Add relationships
Country.states = relationship("IndianState", back_populates="country", cascade="all, delete-orphan")
IndianState.cities = relationship("IndianCity", back_populates="state", cascade="all, delete-orphan")
IndianState.districts = relationship("IndianDistrict", back_populates="state", cascade="all, delete-orphan")
IndianState.pincodes = relationship("IndianPincode", back_populates="state", cascade="all, delete-orphan")
IndianCity.pincodes = relationship("IndianPincode", back_populates="city", cascade="all, delete-orphan")
IndianDistrict.talukas = relationship("IndianTaluka", back_populates="district", cascade="all, delete-orphan")
IndianTaluka.villages = relationship("IndianVillage", back_populates="taluka", cascade="all, delete-orphan")