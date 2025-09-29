# backend/app/api/endpoints/testing/integration_testing.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.testing.integration_testing_service import IntegrationTestingService

router = APIRouter()

# Initialize service
integration_testing_service = IntegrationTestingService()

# Pydantic schemas for Integration Testing
class IntegrationTestResponse(BaseModel):
    success: bool
    test_results: dict
    overall_results: dict
    message: str

class TestResultResponse(BaseModel):
    status: str
    tests: List[dict]
    total_tests: int
    passed_tests: int
    failed_tests: int

class OverallTestResults(BaseModel):
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    average_response_time: float
    overall_status: str

# Integration Testing Endpoints
@router.post("/run-comprehensive-tests", response_model=IntegrationTestResponse)
async def run_comprehensive_integration_tests(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.run")),
    db: Session = Depends(get_db)
):
    """Run comprehensive integration tests for all modules"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Run comprehensive integration tests
        result = integration_testing_service.run_comprehensive_integration_tests(db, company_id)
        
        return IntegrationTestResponse(
            success=result['success'],
            test_results=result['test_results'],
            overall_results=result['overall_results'],
            message=result['message']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run comprehensive integration tests: {str(e)}"
        )

@router.get("/test-core-integrations", response_model=TestResultResponse)
async def test_core_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.core")),
    db: Session = Depends(get_db)
):
    """Test core module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test core integrations
        result = integration_testing_service.test_core_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test core integrations: {str(e)}"
        )

@router.get("/test-sales-purchase-integrations", response_model=TestResultResponse)
async def test_sales_purchase_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.sales_purchase")),
    db: Session = Depends(get_db)
):
    """Test sales and purchase integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test sales and purchase integrations
        result = integration_testing_service.test_sales_purchase_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test sales purchase integrations: {str(e)}"
        )

@router.get("/test-pos-integrations", response_model=TestResultResponse)
async def test_pos_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.pos")),
    db: Session = Depends(get_db)
):
    """Test POS integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test POS integrations
        result = integration_testing_service.test_pos_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test POS integrations: {str(e)}"
        )

@router.get("/test-customer-loyalty-integrations", response_model=TestResultResponse)
async def test_customer_loyalty_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.customer_loyalty")),
    db: Session = Depends(get_db)
):
    """Test customer and loyalty integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test customer and loyalty integrations
        result = integration_testing_service.test_customer_loyalty_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test customer loyalty integrations: {str(e)}"
        )

@router.get("/test-discount-integrations", response_model=TestResultResponse)
async def test_discount_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.discount")),
    db: Session = Depends(get_db)
):
    """Test discount integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test discount integrations
        result = integration_testing_service.test_discount_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test discount integrations: {str(e)}"
        )

@router.get("/test-compliance-integrations", response_model=TestResultResponse)
async def test_compliance_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.compliance")),
    db: Session = Depends(get_db)
):
    """Test compliance integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test compliance integrations
        result = integration_testing_service.test_compliance_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test compliance integrations: {str(e)}"
        )

@router.get("/test-banking-integrations", response_model=TestResultResponse)
async def test_banking_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.banking")),
    db: Session = Depends(get_db)
):
    """Test banking integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test banking integrations
        result = integration_testing_service.test_banking_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test banking integrations: {str(e)}"
        )

@router.get("/test-reports-integrations", response_model=TestResultResponse)
async def test_reports_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.reports")),
    db: Session = Depends(get_db)
):
    """Test reports integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Test reports integrations
        result = integration_testing_service.test_reports_integrations(db, company_id)
        
        return TestResultResponse(
            status=result['status'],
            tests=result['tests'],
            total_tests=result['total_tests'],
            passed_tests=result['passed_tests'],
            failed_tests=result['failed_tests']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test reports integrations: {str(e)}"
        )

@router.get("/test-status")
async def get_test_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("testing.status")),
    db: Session = Depends(get_db)
):
    """Get integration test status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get test status
        return {
            "integration_testing": {
                "core_integrations": "ready",
                "sales_purchase_integrations": "ready",
                "pos_integrations": "ready",
                "customer_loyalty_integrations": "ready",
                "discount_integrations": "ready",
                "compliance_integrations": "ready",
                "banking_integrations": "ready",
                "reports_integrations": "ready"
            },
            "test_capabilities": [
                "Comprehensive integration testing",
                "Module-specific testing",
                "Performance testing",
                "Error handling testing",
                "Real-time testing",
                "API testing"
            ],
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get test status: {str(e)}"
        )