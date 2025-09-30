"""
WhatsApp Integration Service for POS and Loyalty
Handles integration with POS transactions, loyalty points, and customer communications
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.whatsapp import WhatsAppCustomer, WhatsAppMessage
from app.models.whatsapp.whatsapp_models import WhatsAppMessageStatus
from app.services.whatsapp.whatsapp_service import WhatsAppService
from app.services.whatsapp.whatsapp_template_service import WhatsAppTemplateService

logger = logging.getLogger(__name__)


class WhatsAppIntegrationService:
    """Service for integrating WhatsApp with POS and loyalty systems"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.template_service = WhatsAppTemplateService()
    
    def send_pos_receipt(
        self,
        db: Session,
        customer_id: int,
        transaction_id: int,
        receipt_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send POS receipt via WhatsApp
        
        Args:
            db: Database session
            customer_id: Customer ID
            transaction_id: POS transaction ID
            receipt_data: Receipt data including items, total, etc.
            
        Returns:
            Dict with sending result
        """
        try:
            # Get customer WhatsApp preferences
            whatsapp_customer = self._get_whatsapp_customer(db, customer_id)
            
            if not whatsapp_customer or not whatsapp_customer.transactional_opt_in:
                return {
                    "success": False,
                    "error": "Customer has not opted in for transactional messages"
                }
            
            # Get receipt template
            template = self.template_service.get_template_by_name(db, "pos_receipt")
            if not template or template.status.value != "approved":
                return {
                    "success": False,
                    "error": "Receipt template not available or not approved"
                }
            
            # Prepare template variables
            variables = self._prepare_receipt_variables(receipt_data)
            
            # Send template message
            result = self.whatsapp_service.send_template_message(
                to=whatsapp_customer.phone_number,
                template_name=template.whatsapp_template_name,
                language_code=template.language,
                components=self._build_template_components(variables),
                db=db
            )
            
            if result["success"]:
                # Update template usage
                self.template_service.update_template_usage(db, template.id)
                
                # Log message with context
                self._log_message_with_context(
                    db=db,
                    template_id=template.id,
                    customer_id=customer_id,
                    phone_number=whatsapp_customer.phone_number,
                    context_type="pos_transaction",
                    context_id=transaction_id,
                    content=json.dumps(variables)
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending POS receipt: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_loyalty_points_update(
        self,
        db: Session,
        customer_id: int,
        points_earned: int,
        points_redeemed: int,
        current_balance: int,
        transaction_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send loyalty points update via WhatsApp
        
        Args:
            db: Database session
            customer_id: Customer ID
            points_earned: Points earned in current transaction
            points_redeemed: Points redeemed in current transaction
            current_balance: Current points balance
            transaction_id: Optional transaction ID
            
        Returns:
            Dict with sending result
        """
        try:
            # Get customer WhatsApp preferences
            whatsapp_customer = self._get_whatsapp_customer(db, customer_id)
            
            if not whatsapp_customer or not whatsapp_customer.transactional_opt_in:
                return {
                    "success": False,
                    "error": "Customer has not opted in for transactional messages"
                }
            
            # Determine which template to use
            if points_redeemed > 0:
                template_name = "loyalty_points_redemption"
            else:
                template_name = "loyalty_points_earned"
            
            template = self.template_service.get_template_by_name(db, template_name)
            if not template or template.status.value != "approved":
                return {
                    "success": False,
                    "error": f"{template_name} template not available or not approved"
                }
            
            # Prepare template variables
            variables = {
                "points_earned": points_earned,
                "points_redeemed": points_redeemed,
                "current_balance": current_balance,
                "customer_name": whatsapp_customer.customer.name if whatsapp_customer.customer else "Valued Customer"
            }
            
            # Send template message
            result = self.whatsapp_service.send_template_message(
                to=whatsapp_customer.phone_number,
                template_name=template.whatsapp_template_name,
                language_code=template.language,
                components=self._build_template_components(variables),
                db=db
            )
            
            if result["success"]:
                # Update template usage
                self.template_service.update_template_usage(db, template.id)
                
                # Log message with context
                self._log_message_with_context(
                    db=db,
                    template_id=template.id,
                    customer_id=customer_id,
                    phone_number=whatsapp_customer.phone_number,
                    context_type="loyalty_points",
                    context_id=transaction_id,
                    content=json.dumps(variables)
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending loyalty points update: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_invoice(
        self,
        db: Session,
        customer_id: int,
        invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send invoice via WhatsApp
        
        Args:
            db: Database session
            customer_id: Customer ID
            invoice_data: Invoice data
            
        Returns:
            Dict with sending result
        """
        try:
            # Get customer WhatsApp preferences
            whatsapp_customer = self._get_whatsapp_customer(db, customer_id)
            
            if not whatsapp_customer or not whatsapp_customer.transactional_opt_in:
                return {
                    "success": False,
                    "error": "Customer has not opted in for transactional messages"
                }
            
            # Get invoice template
            template = self.template_service.get_template_by_name(db, "invoice")
            if not template or template.status.value != "approved":
                return {
                    "success": False,
                    "error": "Invoice template not available or not approved"
                }
            
            # Prepare template variables
            variables = self._prepare_invoice_variables(invoice_data)
            
            # Send template message with PDF attachment
            result = self.whatsapp_service.send_media_message(
                to=whatsapp_customer.phone_number,
                media_type="document",
                media_url=invoice_data.get("pdf_url"),
                caption=f"Invoice #{invoice_data.get('invoice_number')}",
                db=db
            )
            
            if result["success"]:
                # Update template usage
                self.template_service.update_template_usage(db, template.id)
                
                # Log message with context
                self._log_message_with_context(
                    db=db,
                    template_id=template.id,
                    customer_id=customer_id,
                    phone_number=whatsapp_customer.phone_number,
                    context_type="invoice",
                    context_id=invoice_data.get("invoice_id"),
                    content=json.dumps(variables)
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending invoice: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_marketing_message(
        self,
        db: Session,
        customer_id: int,
        campaign_id: int,
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send marketing message via WhatsApp
        
        Args:
            db: Database session
            customer_id: Customer ID
            campaign_id: Campaign ID
            message_data: Marketing message data
            
        Returns:
            Dict with sending result
        """
        try:
            # Get customer WhatsApp preferences
            whatsapp_customer = self._get_whatsapp_customer(db, customer_id)
            
            if not whatsapp_customer or not whatsapp_customer.marketing_opt_in:
                return {
                    "success": False,
                    "error": "Customer has not opted in for marketing messages"
                }
            
            # Get marketing template
            template = self.template_service.get_template_by_name(db, "marketing_promotion")
            if not template or template.status.value != "approved":
                return {
                    "success": False,
                    "error": "Marketing template not available or not approved"
                }
            
            # Prepare template variables
            variables = self._prepare_marketing_variables(message_data)
            
            # Send template message
            result = self.whatsapp_service.send_template_message(
                to=whatsapp_customer.phone_number,
                template_name=template.whatsapp_template_name,
                language_code=template.language,
                components=self._build_template_components(variables),
                db=db
            )
            
            if result["success"]:
                # Update template usage
                self.template_service.update_template_usage(db, template.id)
                
                # Log message with context
                self._log_message_with_context(
                    db=db,
                    template_id=template.id,
                    customer_id=customer_id,
                    phone_number=whatsapp_customer.phone_number,
                    context_type="marketing_campaign",
                    context_id=campaign_id,
                    content=json.dumps(variables)
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending marketing message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_customer_opt_in(
        self,
        db: Session,
        phone_number: str,
        opt_type: str,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Handle customer opt-in for WhatsApp messages
        
        Args:
            db: Database session
            phone_number: Customer phone number
            opt_type: Type of opt-in (transactional, marketing, utility)
            customer_id: Optional customer ID
            
        Returns:
            Dict with opt-in result
        """
        try:
            # Get or create WhatsApp customer record
            whatsapp_customer = self._get_or_create_whatsapp_customer(
                db, phone_number, customer_id
            )
            
            # Update opt-in status
            if opt_type == "transactional":
                whatsapp_customer.transactional_opt_in = True
                whatsapp_customer.transactional_opted_in_at = datetime.utcnow()
            elif opt_type == "marketing":
                whatsapp_customer.marketing_opt_in = True
                whatsapp_customer.marketing_opted_in_at = datetime.utcnow()
            elif opt_type == "utility":
                whatsapp_customer.utility_opt_in = True
                whatsapp_customer.utility_opted_in_at = datetime.utcnow()
            
            # Log opt-in action
            self._log_opt_action(
                db, whatsapp_customer.id, opt_type, "opt_in", "pos"
            )
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Successfully opted in for {opt_type} messages"
            }
            
        except Exception as e:
            logger.error(f"Error handling opt-in: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_customer_opt_out(
        self,
        db: Session,
        phone_number: str,
        opt_type: str
    ) -> Dict[str, Any]:
        """
        Handle customer opt-out from WhatsApp messages
        
        Args:
            db: Database session
            phone_number: Customer phone number
            opt_type: Type of opt-out (transactional, marketing, utility)
            
        Returns:
            Dict with opt-out result
        """
        try:
            # Get WhatsApp customer record
            whatsapp_customer = self._get_whatsapp_customer_by_phone(db, phone_number)
            
            if not whatsapp_customer:
                return {
                    "success": False,
                    "error": "Customer not found"
                }
            
            # Update opt-out status
            if opt_type == "transactional":
                whatsapp_customer.transactional_opt_in = False
                whatsapp_customer.transactional_opted_out_at = datetime.utcnow()
            elif opt_type == "marketing":
                whatsapp_customer.marketing_opt_in = False
                whatsapp_customer.marketing_opted_out_at = datetime.utcnow()
            elif opt_type == "utility":
                whatsapp_customer.utility_opt_in = False
                whatsapp_customer.utility_opted_out_at = datetime.utcnow()
            
            # Log opt-out action
            self._log_opt_action(
                db, whatsapp_customer.id, opt_type, "opt_out", "whatsapp"
            )
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Successfully opted out of {opt_type} messages"
            }
            
        except Exception as e:
            logger.error(f"Error handling opt-out: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_whatsapp_customer(self, db: Session, customer_id: int) -> Optional[WhatsAppCustomer]:
        """Get WhatsApp customer by customer ID"""
        return db.query(WhatsAppCustomer).filter(
            WhatsAppCustomer.customer_id == customer_id
        ).first()
    
    def _get_whatsapp_customer_by_phone(self, db: Session, phone_number: str) -> Optional[WhatsAppCustomer]:
        """Get WhatsApp customer by phone number"""
        return db.query(WhatsAppCustomer).filter(
            WhatsAppCustomer.phone_number == phone_number
        ).first()
    
    def _get_or_create_whatsapp_customer(
        self, 
        db: Session, 
        phone_number: str, 
        customer_id: Optional[int] = None
    ) -> WhatsAppCustomer:
        """Get or create WhatsApp customer record"""
        whatsapp_customer = self._get_whatsapp_customer_by_phone(db, phone_number)
        
        if not whatsapp_customer:
            whatsapp_customer = WhatsAppCustomer(
                customer_id=customer_id,
                phone_number=phone_number
            )
            db.add(whatsapp_customer)
            db.commit()
            db.refresh(whatsapp_customer)
        
        return whatsapp_customer
    
    def _prepare_receipt_variables(self, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare variables for receipt template"""
        return {
            "store_name": receipt_data.get("store_name", "Our Store"),
            "transaction_id": receipt_data.get("transaction_id", ""),
            "total_amount": receipt_data.get("total_amount", 0),
            "items_count": receipt_data.get("items_count", 0),
            "customer_name": receipt_data.get("customer_name", "Valued Customer"),
            "date": receipt_data.get("date", datetime.utcnow().strftime("%Y-%m-%d %H:%M")),
            "payment_method": receipt_data.get("payment_method", "Cash")
        }
    
    def _prepare_invoice_variables(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare variables for invoice template"""
        return {
            "invoice_number": invoice_data.get("invoice_number", ""),
            "customer_name": invoice_data.get("customer_name", "Valued Customer"),
            "total_amount": invoice_data.get("total_amount", 0),
            "due_date": invoice_data.get("due_date", ""),
            "company_name": invoice_data.get("company_name", "Our Company")
        }
    
    def _prepare_marketing_variables(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare variables for marketing template"""
        return {
            "customer_name": message_data.get("customer_name", "Valued Customer"),
            "offer_title": message_data.get("offer_title", ""),
            "offer_description": message_data.get("offer_description", ""),
            "discount_percentage": message_data.get("discount_percentage", 0),
            "valid_until": message_data.get("valid_until", ""),
            "store_name": message_data.get("store_name", "Our Store")
        }
    
    def _build_template_components(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build template components for WhatsApp API"""
        components = []
        
        # Add body component with variables
        if variables:
            body_variables = []
            for key, value in variables.items():
                body_variables.append({"type": "text", "text": str(value)})
            
            if body_variables:
                components.append({
                    "type": "body",
                    "parameters": body_variables
                })
        
        return components
    
    def _log_message_with_context(
        self,
        db: Session,
        template_id: int,
        customer_id: int,
        phone_number: str,
        context_type: str,
        context_id: Optional[int],
        content: str
    ):
        """Log message with context information"""
        try:
            message = WhatsAppMessage(
                template_id=template_id,
                customer_id=customer_id,
                phone_number=phone_number,
                message_type="template",
                content=content,
                context_type=context_type,
                context_id=context_id,
                status=WhatsAppMessageStatus.SENT,
                sent_at=datetime.utcnow()
            )
            
            db.add(message)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging message with context: {str(e)}")
            db.rollback()
    
    def _log_opt_action(
        self,
        db: Session,
        whatsapp_customer_id: int,
        opt_type: str,
        action: str,
        method: str
    ):
        """Log opt-in/opt-out action"""
        try:
            from app.models.whatsapp.whatsapp_models import WhatsAppOptIn
            
            opt_record = WhatsAppOptIn(
                whatsapp_customer_id=whatsapp_customer_id,
                opt_type=opt_type,
                action=action,
                method=method
            )
            
            db.add(opt_record)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging opt action: {str(e)}")
            db.rollback()