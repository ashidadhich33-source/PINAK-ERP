# backend/app/api/endpoints/settings.py
"""
System Settings and Configuration API Endpoints
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.rbac import require_role
from app.models.core.user import User
# from app.services.settings_service import (
#     system_settings,
#     company_settings,
#     print_templates
# )

router = APIRouter()

# Request/Response Models
class SettingUpdate(BaseModel):
    section: str
    key: str
    value: Any

class SectionUpdate(BaseModel):
    section: str
    settings: Dict[str, Any]

class CompanySettings(BaseModel):
    name: str
    address: str = None
    city: str = None
    state: str = None
    pincode: str = None
    phone: str = None
    email: str = None
    gstin: str = None
    pan: str = None
    bank_name: str = None
    bank_account: str = None
    bank_ifsc: str = None
    website: str = None
    terms_conditions: str = None
    return_policy: str = None

class TemplateUpdate(BaseModel):
    template_type: str
    content: str

class SystemInfo(BaseModel):
    version: str = "1.0.0"
    database_type: str
    timezone: str
    currency: str
    gst_enabled: bool
    loyalty_enabled: bool
    whatsapp_enabled: bool
    email_enabled: bool
    backup_enabled: bool

# System Settings Endpoints
@router.get("/settings", response_model=Dict[str, Dict[str, str]])
async def get_all_settings(
    current_user: User = Depends(require_role(["admin"]))
):
    """Get all system settings"""
    return system_settings.get_all_settings()

@router.get("/settings/{section}")
async def get_section_settings(
    section: str,
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """Get settings for a specific section"""
    settings = system_settings.get_section(section)
    if not settings:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
    return settings

@router.post("/settings/update")
async def update_setting(
    update: SettingUpdate,
    current_user: User = Depends(require_role(["admin"]))
):
    """Update a single setting"""
    success = system_settings.update_setting(update.section, update.key, update.value)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update setting")
    
    return {"message": "Setting updated successfully"}

@router.post("/settings/update-section")
async def update_section(
    update: SectionUpdate,
    current_user: User = Depends(require_role(["admin"]))
):
    """Update all settings in a section"""
    success = system_settings.update_section(update.section, update.settings)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update section")
    
    return {"message": "Section updated successfully"}

@router.post("/settings/reset/{section}")
async def reset_section(
    section: str,
    current_user: User = Depends(require_role(["admin"]))
):
    """Reset a section to default values"""
    success = system_settings.reset_section(section)
    if not success:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
    
    return {"message": f"Section '{section}' reset to defaults"}

@router.get("/settings/validate")
async def validate_settings(
    current_user: User = Depends(require_role(["admin"]))
):
    """Validate all settings and return any errors"""
    errors = system_settings.validate_settings()
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

@router.post("/settings/export")
async def export_settings(
    current_user: User = Depends(require_role(["admin"]))
):
    """Export all settings to JSON file"""
    filepath = system_settings.export_settings()
    
    return FileResponse(
        path=filepath,
        filename=f"settings_{datetime.now().strftime('%Y%m%d')}.json",
        media_type="application/json"
    )

@router.post("/settings/import")
async def import_settings(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin"]))
):
    """Import settings from JSON file"""
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        success = system_settings.import_settings(temp_path)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to import settings")
        
        return {"message": "Settings imported successfully"}
    finally:
        # Clean up temp file
        import os
        os.remove(temp_path)

# Company Settings Endpoints
@router.get("/company")
async def get_company_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company settings"""
    return company_settings.get_company_settings(db)

@router.post("/company")
async def update_company_settings(
    settings: CompanySettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Update company settings"""
    success = company_settings.update_company_settings(db, settings.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update company settings")
    
    return {"message": "Company settings updated successfully"}

@router.post("/company/logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Upload company logo"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")
    
    # Save logo
    logo_path = f"uploads/logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(logo_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Update company settings
    success = company_settings.update_company_settings(db, {"logo_path": logo_path})
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update logo")
    
    return {"message": "Logo uploaded successfully", "path": logo_path}

# Print Template Endpoints
@router.get("/templates")
async def list_templates(
    current_user: User = Depends(get_current_user)
):
    """List all available print templates"""
    return print_templates.list_templates()

@router.get("/templates/{template_type}")
async def get_template(
    template_type: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific print template"""
    template = print_templates.get_template(template_type)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_type}' not found")
    
    return {"template_type": template_type, "content": template}

@router.post("/templates")
async def update_template(
    update: TemplateUpdate,
    current_user: User = Depends(require_role(["admin"]))
):
    """Update a print template"""
    success = print_templates.save_template(update.template_type, update.content)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save template")
    
    return {"message": f"Template '{update.template_type}' updated successfully"}

@router.post("/templates/{template_type}/reset")
async def reset_template(
    template_type: str,
    current_user: User = Depends(require_role(["admin"]))
):
    """Reset a template to default"""
    success = print_templates.reset_template(template_type)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset template")
    
    return {"message": f"Template '{template_type}' reset to default"}

# System Information Endpoint
@router.get("/system-info", response_model=SystemInfo)
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """Get system information and status"""
    return SystemInfo(
        version="1.0.0",
        database_type=system_settings.get_setting("database", "type", "sqlite"),
        timezone=system_settings.get_setting("system", "timezone", "Asia/Kolkata"),
        currency=system_settings.get_setting("system", "currency", "INR"),
        gst_enabled=system_settings.get_setting("gst", "enable", "true") == "true",
        loyalty_enabled=system_settings.get_setting("loyalty", "enable", "true") == "true",
        whatsapp_enabled=system_settings.get_setting("whatsapp", "enable", "false") == "true",
        email_enabled=system_settings.get_setting("email", "enable", "false") == "true",
        backup_enabled=system_settings.get_setting("backup", "auto_backup", "true") == "true"
    )

# Quick Settings for common operations
@router.post("/quick-settings/toggle-gst")
async def toggle_gst(
    enable: bool,
    current_user: User = Depends(require_role(["admin"]))
):
    """Enable or disable GST"""
    system_settings.update_setting("gst", "enable", str(enable).lower())
    return {"message": f"GST {'enabled' if enable else 'disabled'}"}

@router.post("/quick-settings/toggle-loyalty")
async def toggle_loyalty(
    enable: bool,
    current_user: User = Depends(require_role(["admin"]))
):
    """Enable or disable loyalty system"""
    system_settings.update_setting("loyalty", "enable", str(enable).lower())
    return {"message": f"Loyalty system {'enabled' if enable else 'disabled'}"}

@router.post("/quick-settings/toggle-whatsapp")
async def toggle_whatsapp(
    enable: bool,
    current_user: User = Depends(require_role(["admin"]))
):
    """Enable or disable WhatsApp integration"""
    system_settings.update_setting("whatsapp", "enable", str(enable).lower())
    return {"message": f"WhatsApp {'enabled' if enable else 'disabled'}"}

@router.post("/quick-settings/update-financial-year")
async def update_financial_year(
    start_date: str,  # Format: MM-DD
    end_date: str,     # Format: MM-DD
    current_user: User = Depends(require_role(["admin"]))
):
    """Update financial year dates"""
    system_settings.update_setting("business", "financial_year_start", start_date)
    system_settings.update_setting("business", "financial_year_end", end_date)
    return {"message": "Financial year updated"}

@router.post("/quick-settings/update-tax-rates")
async def update_tax_rates(
    gst_5_rate: float,
    gst_12_rate: float,
    gst_5_max_price: float,
    current_user: User = Depends(require_role(["admin"]))
):
    """Update GST tax rates and thresholds"""
    system_settings.update_setting("gst", "gst_5_rate", str(gst_5_rate))
    system_settings.update_setting("gst", "gst_12_rate", str(gst_12_rate))
    system_settings.update_setting("gst", "gst_5_max_price", str(gst_5_max_price))
    return {"message": "Tax rates updated"}