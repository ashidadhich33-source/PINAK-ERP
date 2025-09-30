"""
WhatsApp Integration Tests
Comprehensive test suite for WhatsApp functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.whatsapp.whatsapp_models import (
    WhatsAppTemplate, WhatsAppMessage, WhatsAppCustomer, WhatsAppCampaign,
    WhatsAppTemplateStatus, WhatsAppMessageStatus, WhatsAppCampaignStatus
)
from app.services.whatsapp.whatsapp_service import WhatsAppService
from app.services.whatsapp.whatsapp_template_service import WhatsAppTemplateService
from app.services.whatsapp.whatsapp_integration_service import WhatsAppIntegrationService
from app.services.whatsapp.whatsapp_campaign_service import WhatsAppCampaignService


class TestWhatsAppService:
    """Test WhatsApp core service"""
    
    def test_send_template_message_success(self):
        """Test successful template message sending"""
        with patch('requests.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {
                "messages": [{"id": "wamid.test123"}]
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            service = WhatsAppService()
            result = service.send_template_message(
                to="+919876543210",
                template_name="test_template",
                language_code="en"
            )
            
            assert result["success"] is True
            assert result["message_id"] == "wamid.test123"
            assert result["status"] == "sent"
    
    def test_send_template_message_failure(self):
        """Test template message sending failure"""
        with patch('requests.post') as mock_post:
            # Mock failed response
            mock_post.side_effect = Exception("API Error")
            
            service = WhatsAppService()
            result = service.send_template_message(
                to="+919876543210",
                template_name="test_template",
                language_code="en"
            )
            
            assert result["success"] is False
            assert "error" in result
    
    def test_send_text_message_success(self):
        """Test successful text message sending"""
        with patch('requests.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {
                "messages": [{"id": "wamid.test123"}]
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            service = WhatsAppService()
            result = service.send_text_message(
                to="+919876543210",
                text="Hello World"
            )
            
            assert result["success"] is True
            assert result["message_id"] == "wamid.test123"
    
    def test_verify_webhook_success(self):
        """Test successful webhook verification"""
        service = WhatsAppService()
        result = service.verify_webhook(
            mode="subscribe",
            token="erp_webhook_token",
            challenge="test_challenge"
        )
        
        assert result == "test_challenge"
    
    def test_verify_webhook_failure(self):
        """Test failed webhook verification"""
        service = WhatsAppService()
        result = service.verify_webhook(
            mode="subscribe",
            token="wrong_token",
            challenge="test_challenge"
        )
        
        assert result is None


class TestWhatsAppTemplateService:
    """Test WhatsApp template service"""
    
    def test_create_template_success(self, db_session):
        """Test successful template creation"""
        service = WhatsAppTemplateService()
        
        result = service.create_template(
            db=db_session,
            name="test_template",
            category="TRANSACTIONAL",
            language="en",
            body_text="Hello {{customer_name}}!",
            created_by="test_user"
        )
        
        assert result["success"] is True
        assert "template_id" in result
        
        # Verify template was created in database
        template = db_session.query(WhatsAppTemplate).filter(
            WhatsAppTemplate.name == "test_template"
        ).first()
        assert template is not None
        assert template.status == WhatsAppTemplateStatus.DRAFT
    
    def test_create_template_duplicate_name(self, db_session):
        """Test template creation with duplicate name"""
        service = WhatsAppTemplateService()
        
        # Create first template
        service.create_template(
            db=db_session,
            name="duplicate_template",
            category="TRANSACTIONAL",
            language="en",
            body_text="First template",
            created_by="test_user"
        )
        
        # Try to create duplicate
        result = service.create_template(
            db=db_session,
            name="duplicate_template",
            category="TRANSACTIONAL",
            language="en",
            body_text="Second template",
            created_by="test_user"
        )
        
        assert result["success"] is False
        assert "already exists" in result["error"]
    
    def test_submit_template_for_approval(self, db_session):
        """Test template submission for approval"""
        service = WhatsAppTemplateService()
        
        # Create template first
        create_result = service.create_template(
            db=db_session,
            name="submit_template",
            category="TRANSACTIONAL",
            language="en",
            body_text="Test template",
            created_by="test_user"
        )
        
        template_id = create_result["template_id"]
        
        # Submit for approval
        result = service.submit_template_for_approval(
            db=db_session,
            template_id=template_id,
            submitted_by="test_user"
        )
        
        assert result["success"] is True
        assert "submitted for approval" in result["message"]
        
        # Verify template status updated
        template = db_session.query(WhatsAppTemplate).filter(
            WhatsAppTemplate.id == template_id
        ).first()
        assert template.status == WhatsAppTemplateStatus.PENDING_APPROVAL
    
    def test_get_templates_with_filters(self, db_session):
        """Test getting templates with filters"""
        service = WhatsAppTemplateService()
        
        # Create test templates
        service.create_template(
            db=db_session,
            name="transactional_template",
            category="TRANSACTIONAL",
            language="en",
            body_text="Transactional message",
            created_by="test_user"
        )
        
        service.create_template(
            db=db_session,
            name="marketing_template",
            category="MARKETING",
            language="en",
            body_text="Marketing message",
            created_by="test_user"
        )
        
        # Get only transactional templates
        templates = service.get_templates(
            db=db_session,
            category="TRANSACTIONAL"
        )
        
        assert len(templates) == 1
        assert templates[0].name == "transactional_template"


class TestWhatsAppIntegrationService:
    """Test WhatsApp integration service"""
    
    def test_send_pos_receipt_success(self, db_session):
        """Test successful POS receipt sending"""
        # Create test customer with WhatsApp preferences
        whatsapp_customer = WhatsAppCustomer(
            customer_id=1,
            phone_number="+919876543210",
            transactional_opt_in=True
        )
        db_session.add(whatsapp_customer)
        db_session.commit()
        
        # Mock WhatsApp service
        with patch('app.services.whatsapp.whatsapp_integration_service.WhatsAppService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_template_message.return_value = {
                "success": True,
                "message_id": "wamid.test123"
            }
            mock_service.return_value = mock_instance
            
            service = WhatsAppIntegrationService()
            result = service.send_pos_receipt(
                db=db_session,
                customer_id=1,
                transaction_id=123,
                receipt_data={
                    "store_name": "Test Store",
                    "transaction_id": "TXN123",
                    "total_amount": 100.0,
                    "items_count": 2,
                    "customer_name": "Test Customer",
                    "date": "2024-01-01 10:00",
                    "payment_method": "Cash"
                }
            )
            
            assert result["success"] is True
            assert "message_id" in result
    
    def test_send_pos_receipt_customer_not_opted_in(self, db_session):
        """Test POS receipt sending when customer not opted in"""
        # Create test customer without opt-in
        whatsapp_customer = WhatsAppCustomer(
            customer_id=1,
            phone_number="+919876543210",
            transactional_opt_in=False
        )
        db_session.add(whatsapp_customer)
        db_session.commit()
        
        service = WhatsAppIntegrationService()
        result = service.send_pos_receipt(
            db=db_session,
            customer_id=1,
            transaction_id=123,
            receipt_data={}
        )
        
        assert result["success"] is False
        assert "not opted in" in result["error"]
    
    def test_send_loyalty_points_update(self, db_session):
        """Test loyalty points update sending"""
        # Create test customer
        whatsapp_customer = WhatsAppCustomer(
            customer_id=1,
            phone_number="+919876543210",
            transactional_opt_in=True
        )
        db_session.add(whatsapp_customer)
        db_session.commit()
        
        # Mock WhatsApp service
        with patch('app.services.whatsapp.whatsapp_integration_service.WhatsAppService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_template_message.return_value = {
                "success": True,
                "message_id": "wamid.test123"
            }
            mock_service.return_value = mock_instance
            
            service = WhatsAppIntegrationService()
            result = service.send_loyalty_points_update(
                db=db_session,
                customer_id=1,
                points_earned=10,
                points_redeemed=0,
                current_balance=50,
                transaction_id=123
            )
            
            assert result["success"] is True
    
    def test_handle_customer_opt_in(self, db_session):
        """Test customer opt-in handling"""
        service = WhatsAppIntegrationService()
        
        result = service.handle_customer_opt_in(
            db=db_session,
            phone_number="+919876543210",
            opt_type="transactional",
            customer_id=1
        )
        
        assert result["success"] is True
        assert "opted in" in result["message"]
        
        # Verify customer record created
        whatsapp_customer = db_session.query(WhatsAppCustomer).filter(
            WhatsAppCustomer.phone_number == "+919876543210"
        ).first()
        assert whatsapp_customer is not None
        assert whatsapp_customer.transactional_opt_in is True
    
    def test_handle_customer_opt_out(self, db_session):
        """Test customer opt-out handling"""
        # Create test customer first
        whatsapp_customer = WhatsAppCustomer(
            customer_id=1,
            phone_number="+919876543210",
            transactional_opt_in=True
        )
        db_session.add(whatsapp_customer)
        db_session.commit()
        
        service = WhatsAppIntegrationService()
        
        result = service.handle_customer_opt_out(
            db=db_session,
            phone_number="+919876543210",
            opt_type="transactional"
        )
        
        assert result["success"] is True
        assert "opted out" in result["message"]
        
        # Verify customer opt-out status
        db_session.refresh(whatsapp_customer)
        assert whatsapp_customer.transactional_opt_in is False


class TestWhatsAppCampaignService:
    """Test WhatsApp campaign service"""
    
    def test_create_campaign_success(self, db_session):
        """Test successful campaign creation"""
        # Create test template first
        template = WhatsAppTemplate(
            name="test_template",
            category="MARKETING",
            language="en",
            body_text="Test message",
            status=WhatsAppTemplateStatus.APPROVED
        )
        db_session.add(template)
        db_session.commit()
        
        service = WhatsAppCampaignService()
        
        result = service.create_campaign(
            db=db_session,
            name="Test Campaign",
            description="Test campaign description",
            template_id=template.id,
            target_audience={"customer_segments": ["premium"]},
            created_by="test_user"
        )
        
        assert result["success"] is True
        assert "campaign_id" in result
        
        # Verify campaign was created
        campaign = db_session.query(WhatsAppCampaign).filter(
            WhatsAppCampaign.name == "Test Campaign"
        ).first()
        assert campaign is not None
        assert campaign.status == WhatsAppCampaignStatus.DRAFT
    
    def test_create_campaign_invalid_template(self, db_session):
        """Test campaign creation with invalid template"""
        service = WhatsAppCampaignService()
        
        result = service.create_campaign(
            db=db_session,
            name="Test Campaign",
            description="Test campaign description",
            template_id=999,  # Non-existent template
            target_audience={"customer_segments": ["premium"]},
            created_by="test_user"
        )
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_start_campaign_success(self, db_session):
        """Test successful campaign start"""
        # Create test campaign
        campaign = WhatsAppCampaign(
            name="Test Campaign",
            description="Test campaign",
            template_id=1,
            target_audience={"customer_segments": ["premium"]},
            status=WhatsAppCampaignStatus.DRAFT,
            created_by="test_user"
        )
        db_session.add(campaign)
        db_session.commit()
        
        # Mock target customers
        with patch.object(WhatsAppCampaignService, '_get_target_customers') as mock_get_customers:
            mock_customer = Mock()
            mock_customer.phone_number = "+919876543210"
            mock_get_customers.return_value = [mock_customer]
            
            # Mock WhatsApp service
            with patch('app.services.whatsapp.whatsapp_campaign_service.WhatsAppService') as mock_service:
                mock_instance = Mock()
                mock_instance.send_template_message.return_value = {
                    "success": True,
                    "message_id": "wamid.test123"
                }
                mock_service.return_value = mock_instance
                
                service = WhatsAppCampaignService()
                result = service.start_campaign(
                    db=db_session,
                    campaign_id=campaign.id
                )
                
                assert result["success"] is True
                assert "started" in result["message"]
    
    def test_get_campaign_statistics(self, db_session):
        """Test getting campaign statistics"""
        # Create test campaign
        campaign = WhatsAppCampaign(
            name="Test Campaign",
            description="Test campaign",
            template_id=1,
            target_audience={"customer_segments": ["premium"]},
            status=WhatsAppCampaignStatus.COMPLETED,
            total_recipients=100,
            messages_sent=95,
            messages_delivered=90,
            messages_read=80,
            messages_failed=5,
            created_by="test_user"
        )
        db_session.add(campaign)
        db_session.commit()
        
        service = WhatsAppCampaignService()
        
        result = service.get_campaign_statistics(
            db=db_session,
            campaign_id=campaign.id
        )
        
        assert result["success"] is True
        statistics = result["statistics"]
        assert statistics["total_recipients"] == 100
        assert statistics["messages_sent"] == 95
        assert statistics["delivery_rate"] == 94.74  # 90/95 * 100
        assert statistics["read_rate"] == 88.89  # 80/90 * 100


class TestWhatsAppTemplateManager:
    """Test WhatsApp template manager"""
    
    def test_get_default_templates(self):
        """Test getting default templates"""
        from app.services.whatsapp.whatsapp_template_management import WhatsAppTemplateManager
        
        templates = WhatsAppTemplateManager.get_default_templates()
        
        assert len(templates) > 0
        
        # Check for specific templates
        template_names = [t["name"] for t in templates]
        assert "pos_receipt" in template_names
        assert "loyalty_points_earned" in template_names
        assert "marketing_promotion" in template_names
    
    def test_get_template_by_use_case(self):
        """Test getting template by use case"""
        from app.services.whatsapp.whatsapp_template_management import WhatsAppTemplateManager
        
        template = WhatsAppTemplateManager.get_template_by_use_case("pos_receipt")
        
        assert template is not None
        assert template["name"] == "pos_receipt"
        assert template["category"] == "TRANSACTIONAL"
    
    def test_validate_template_variables(self):
        """Test template variable validation"""
        from app.services.whatsapp.whatsapp_template_management import WhatsAppTemplateManager
        
        template = {
            "name": "test_template",
            "variables": ["customer_name", "total_amount", "date"]
        }
        
        provided_variables = {
            "customer_name": "John Doe",
            "total_amount": "100.00"
            # Missing "date" variable
        }
        
        validated = WhatsAppTemplateManager.validate_template_variables(
            template, provided_variables
        )
        
        assert validated["customer_name"] == "John Doe"
        assert validated["total_amount"] == "100.00"
        assert "date" in validated  # Should have default value


# Fixtures for testing
@pytest.fixture
def db_session():
    """Create test database session"""
    from app.database import get_db
    # This would be set up with test database
    # Implementation depends on your test setup
    pass


if __name__ == "__main__":
    pytest.main([__file__])