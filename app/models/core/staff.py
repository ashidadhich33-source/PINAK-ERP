# backend/app/models/core/staff.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from ..base import BaseModel

class Staff(BaseModel):
    """Staff model for managing staff members"""
    __tablename__ = "staff"
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    hire_date = Column(Date, nullable=False, default=date.today())
    salary = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="staff")
    company = relationship("Company", back_populates="staff")
    roles = relationship("StaffRole", back_populates="staff")
    
    def __repr__(self):
        return f"<Staff(employee_id='{self.employee_id}', department='{self.department}')>"

class StaffRole(BaseModel):
    """Staff Role model for managing staff roles"""
    __tablename__ = "staff_role"
    
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    role_name = Column(String(50), nullable=False)
    permissions = Column(Text, nullable=True)  # JSON permissions
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    staff = relationship("Staff", back_populates="roles")
    company = relationship("Company", back_populates="staff_roles")
    
    def __repr__(self):
        return f"<StaffRole(role_name='{self.role_name}', staff_id={self.staff_id})>"

class StaffPermission(BaseModel):
    """Staff Permission model for managing staff permissions"""
    __tablename__ = "staff_permission"
    
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    permission_name = Column(String(100), nullable=False)
    permission_type = Column(String(50), nullable=False)  # read, write, delete, admin
    resource = Column(String(100), nullable=False)  # sales, inventory, etc.
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    staff = relationship("Staff", back_populates="permissions")
    company = relationship("Company", back_populates="staff_permissions")
    
    def __repr__(self):
        return f"<StaffPermission(permission_name='{self.permission_name}', staff_id={self.staff_id})>"