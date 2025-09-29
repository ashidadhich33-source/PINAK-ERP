# backend/app/services/report_studio_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import uuid
import pandas as pd
import io
import base64

from ..models.core import (
    ReportCategory, ReportTemplate, ReportInstance, ReportView, ReportSchedule,
    ReportScheduleLog, ReportBuilder, ReportDashboard, ReportWidget, ReportExport,
    ReportAnalytics, ReportPermission, ReportCache
)

logger = logging.getLogger(__name__)

class ReportStudioService:
    """Service class for report studio management"""
    
    def __init__(self):
        pass
    
    # Report Category Management
    def create_report_category(
        self, 
        db: Session, 
        company_id: int,
        category_name: str,
        category_code: str,
        description: str = None,
        parent_category_id: int = None,
        display_order: int = 0,
        icon: str = None,
        color: str = None,
        notes: str = None,
        user_id: int = None
    ) -> ReportCategory:
        """Create report category"""
        
        # Check if category code already exists
        existing_category = db.query(ReportCategory).filter(
            ReportCategory.company_id == company_id,
            ReportCategory.category_code == category_code
        ).first()
        
        if existing_category:
            raise ValueError(f"Report category code {category_code} already exists")
        
        # Validate parent category if provided
        if parent_category_id:
            parent_category = db.query(ReportCategory).filter(
                ReportCategory.id == parent_category_id,
                ReportCategory.company_id == company_id
            ).first()
            
            if not parent_category:
                raise ValueError("Parent category not found")
        
        # Create report category
        category = ReportCategory(
            company_id=company_id,
            category_name=category_name,
            category_code=category_code,
            description=description,
            parent_category_id=parent_category_id,
            display_order=display_order,
            icon=icon,
            color=color,
            notes=notes,
            created_by=user_id
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        logger.info(f"Report category created: {category_name}")
        
        return category
    
    def get_report_categories(
        self, 
        db: Session, 
        company_id: int,
        parent_category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[ReportCategory]:
        """Get report categories"""
        
        query = db.query(ReportCategory).filter(ReportCategory.company_id == company_id)
        
        if parent_category_id is not None:
            query = query.filter(ReportCategory.parent_category_id == parent_category_id)
        
        if is_active is not None:
            query = query.filter(ReportCategory.is_active == is_active)
        
        categories = query.order_by(ReportCategory.display_order, ReportCategory.category_name).all()
        
        return categories
    
    # Report Template Management
    def create_report_template(
        self, 
        db: Session, 
        company_id: int,
        template_name: str,
        template_code: str,
        category_id: int,
        report_type: str,
        data_source: str,
        query_sql: str = None,
        template_config: Dict = None,
        parameters: Dict = None,
        filters: Dict = None,
        columns: Dict = None,
        chart_config: Dict = None,
        layout_config: Dict = None,
        is_public: bool = False,
        is_system: bool = False,
        version: str = '1.0',
        notes: str = None,
        user_id: int = None
    ) -> ReportTemplate:
        """Create report template"""
        
        # Check if template code already exists
        existing_template = db.query(ReportTemplate).filter(
            ReportTemplate.company_id == company_id,
            ReportTemplate.template_code == template_code
        ).first()
        
        if existing_template:
            raise ValueError(f"Report template code {template_code} already exists")
        
        # Validate category
        category = db.query(ReportCategory).filter(
            ReportCategory.id == category_id,
            ReportCategory.company_id == company_id
        ).first()
        
        if not category:
            raise ValueError("Report category not found")
        
        # Create report template
        template = ReportTemplate(
            company_id=company_id,
            template_name=template_name,
            template_code=template_code,
            category_id=category_id,
            report_type=report_type,
            data_source=data_source,
            query_sql=query_sql,
            template_config=template_config or {},
            parameters=parameters,
            filters=filters,
            columns=columns,
            chart_config=chart_config,
            layout_config=layout_config,
            is_public=is_public,
            is_system=is_system,
            version=version,
            notes=notes,
            created_by=user_id
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Report template created: {template_name}")
        
        return template
    
    def get_report_templates(
        self, 
        db: Session, 
        company_id: int,
        category_id: Optional[int] = None,
        report_type: Optional[str] = None,
        is_public: Optional[bool] = None,
        is_system: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> List[ReportTemplate]:
        """Get report templates"""
        
        query = db.query(ReportTemplate).filter(ReportTemplate.company_id == company_id)
        
        if category_id:
            query = query.filter(ReportTemplate.category_id == category_id)
        
        if report_type:
            query = query.filter(ReportTemplate.report_type == report_type)
        
        if is_public is not None:
            query = query.filter(ReportTemplate.is_public == is_public)
        
        if is_system is not None:
            query = query.filter(ReportTemplate.is_system == is_system)
        
        if is_active is not None:
            query = query.filter(ReportTemplate.is_active == is_active)
        
        templates = query.order_by(ReportTemplate.template_name).all()
        
        return templates
    
    # Report Instance Management
    def create_report_instance(
        self, 
        db: Session, 
        company_id: int,
        template_id: int,
        instance_name: str,
        instance_code: str = None,
        parameters: Dict = None,
        filters: Dict = None,
        notes: str = None,
        user_id: int = None
    ) -> ReportInstance:
        """Create report instance"""
        
        # Generate instance code if not provided
        if not instance_code:
            instance_code = f"INST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        # Validate template
        template = db.query(ReportTemplate).filter(
            ReportTemplate.id == template_id,
            ReportTemplate.company_id == company_id
        ).first()
        
        if not template:
            raise ValueError("Report template not found")
        
        # Create report instance
        instance = ReportInstance(
            company_id=company_id,
            template_id=template_id,
            instance_name=instance_name,
            instance_code=instance_code,
            parameters=parameters,
            filters=filters,
            notes=notes,
            created_by=user_id
        )
        
        db.add(instance)
        db.commit()
        db.refresh(instance)
        
        logger.info(f"Report instance created: {instance_name}")
        
        return instance
    
    def generate_report_instance(
        self, 
        db: Session, 
        company_id: int,
        instance_id: int,
        user_id: int = None
    ) -> ReportInstance:
        """Generate report instance data"""
        
        instance = db.query(ReportInstance).filter(
            ReportInstance.id == instance_id,
            ReportInstance.company_id == company_id
        ).first()
        
        if not instance:
            raise ValueError("Report instance not found")
        
        template = instance.template
        
        try:
            start_time = datetime.utcnow()
            
            # Execute query based on template configuration
            if template.query_sql:
                # Execute SQL query
                data = self._execute_sql_query(db, template.query_sql, instance.parameters, instance.filters)
            else:
                # Use data source
                data = self._get_data_from_source(db, template.data_source, instance.parameters, instance.filters)
            
            # Process data based on template configuration
            processed_data = self._process_report_data(data, template.template_config)
            
            # Update instance
            instance.data = processed_data
            instance.status = 'generated'
            instance.generated_date = datetime.utcnow()
            instance.execution_time = (datetime.utcnow() - start_time).total_seconds()
            instance.row_count = len(processed_data) if isinstance(processed_data, list) else 0
            instance.updated_by = user_id
            instance.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Report instance generated: {instance.instance_name}")
            
            return instance
            
        except Exception as e:
            # Update instance with error
            instance.status = 'failed'
            instance.error_message = str(e)
            instance.updated_by = user_id
            instance.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.error(f"Report generation failed: {str(e)}")
            raise ValueError(f"Report generation failed: {str(e)}")
    
    def _execute_sql_query(
        self, 
        db: Session, 
        query_sql: str, 
        parameters: Dict = None, 
        filters: Dict = None
    ) -> List[Dict]:
        """Execute SQL query"""
        
        # Apply parameters to query
        if parameters:
            for key, value in parameters.items():
                query_sql = query_sql.replace(f"{{{key}}}", str(value))
        
        # Apply filters to query
        if filters:
            where_conditions = []
            for key, value in filters.items():
                if value is not None:
                    where_conditions.append(f"{key} = '{value}'")
            
            if where_conditions:
                if "WHERE" in query_sql.upper():
                    query_sql += " AND " + " AND ".join(where_conditions)
                else:
                    query_sql += " WHERE " + " AND ".join(where_conditions)
        
        # Execute query
        result = db.execute(query_sql)
        columns = result.keys()
        rows = result.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return data
    
    def _get_data_from_source(
        self, 
        db: Session, 
        data_source: str, 
        parameters: Dict = None, 
        filters: Dict = None
    ) -> List[Dict]:
        """Get data from data source"""
        
        # This is a simplified implementation
        # In a real system, you would have a data source registry
        # and execute the appropriate query based on the data source
        
        if data_source == 'sales':
            # Example: Get sales data
            query = "SELECT * FROM sale_bill WHERE company_id = :company_id"
            result = db.execute(query, {"company_id": parameters.get('company_id') if parameters else None})
        elif data_source == 'purchases':
            # Example: Get purchase data
            query = "SELECT * FROM purchase_bill WHERE company_id = :company_id"
            result = db.execute(query, {"company_id": parameters.get('company_id') if parameters else None})
        else:
            # Default: Return empty data
            return []
        
        columns = result.keys()
        rows = result.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return data
    
    def _process_report_data(
        self, 
        data: List[Dict], 
        template_config: Dict
    ) -> List[Dict]:
        """Process report data based on template configuration"""
        
        if not data:
            return []
        
        # Apply sorting
        if template_config.get('sorting'):
            sort_field = template_config['sorting'].get('field')
            sort_direction = template_config['sorting'].get('direction', 'asc')
            
            if sort_field:
                data.sort(key=lambda x: x.get(sort_field, ''), reverse=(sort_direction == 'desc'))
        
        # Apply grouping
        if template_config.get('grouping'):
            group_field = template_config['grouping'].get('field')
            if group_field:
                # Group data by field
                grouped_data = {}
                for item in data:
                    key = item.get(group_field, '')
                    if key not in grouped_data:
                        grouped_data[key] = []
                    grouped_data[key].append(item)
                
                # Convert back to list
                data = []
                for key, group in grouped_data.items():
                    data.extend(group)
        
        # Apply aggregation
        if template_config.get('aggregation'):
            agg_config = template_config['aggregation']
            agg_field = agg_config.get('field')
            agg_function = agg_config.get('function', 'sum')
            
            if agg_field and agg_function:
                if agg_function == 'sum':
                    total = sum(item.get(agg_field, 0) for item in data if isinstance(item.get(agg_field), (int, float)))
                    data.append({agg_field: total, 'aggregation_type': 'sum'})
                elif agg_function == 'count':
                    count = len(data)
                    data.append({agg_field: count, 'aggregation_type': 'count'})
                elif agg_function == 'average':
                    values = [item.get(agg_field, 0) for item in data if isinstance(item.get(agg_field), (int, float))]
                    average = sum(values) / len(values) if values else 0
                    data.append({agg_field: average, 'aggregation_type': 'average'})
        
        return data
    
    # Report View Management
    def create_report_view(
        self, 
        db: Session, 
        company_id: int,
        instance_id: int,
        view_name: str,
        view_type: str,
        view_config: Dict,
        chart_type: str = None,
        chart_config: Dict = None,
        filters: Dict = None,
        sorting: Dict = None,
        grouping: Dict = None,
        aggregation: Dict = None,
        display_order: int = 0,
        is_default: bool = False,
        notes: str = None,
        user_id: int = None
    ) -> ReportView:
        """Create report view"""
        
        # Validate instance
        instance = db.query(ReportInstance).filter(
            ReportInstance.id == instance_id,
            ReportInstance.company_id == company_id
        ).first()
        
        if not instance:
            raise ValueError("Report instance not found")
        
        # Create report view
        view = ReportView(
            company_id=company_id,
            instance_id=instance_id,
            view_name=view_name,
            view_type=view_type,
            view_config=view_config,
            chart_type=chart_type,
            chart_config=chart_config,
            filters=filters,
            sorting=sorting,
            grouping=grouping,
            aggregation=aggregation,
            display_order=display_order,
            is_default=is_default,
            notes=notes,
            created_by=user_id
        )
        
        db.add(view)
        db.commit()
        db.refresh(view)
        
        logger.info(f"Report view created: {view_name}")
        
        return view
    
    # Report Schedule Management
    def create_report_schedule(
        self, 
        db: Session, 
        company_id: int,
        template_id: int,
        schedule_name: str,
        schedule_type: str,
        cron_expression: str = None,
        schedule_time: str = None,
        schedule_date: date = None,
        parameters: Dict = None,
        email_recipients: List[str] = None,
        email_subject: str = None,
        email_body: str = None,
        file_format: str = 'pdf',
        notes: str = None,
        user_id: int = None
    ) -> ReportSchedule:
        """Create report schedule"""
        
        # Validate template
        template = db.query(ReportTemplate).filter(
            ReportTemplate.id == template_id,
            ReportTemplate.company_id == company_id
        ).first()
        
        if not template:
            raise ValueError("Report template not found")
        
        # Create report schedule
        schedule = ReportSchedule(
            company_id=company_id,
            template_id=template_id,
            schedule_name=schedule_name,
            schedule_type=schedule_type,
            cron_expression=cron_expression,
            schedule_time=schedule_time,
            schedule_date=schedule_date,
            parameters=parameters,
            email_recipients=email_recipients,
            email_subject=email_subject,
            email_body=email_body,
            file_format=file_format,
            notes=notes,
            created_by=user_id
        )
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        logger.info(f"Report schedule created: {schedule_name}")
        
        return schedule
    
    def execute_report_schedule(
        self, 
        db: Session, 
        company_id: int,
        schedule_id: int,
        user_id: int = None
    ) -> ReportScheduleLog:
        """Execute report schedule"""
        
        schedule = db.query(ReportSchedule).filter(
            ReportSchedule.id == schedule_id,
            ReportSchedule.company_id == company_id
        ).first()
        
        if not schedule:
            raise ValueError("Report schedule not found")
        
        # Create schedule log
        log = ReportScheduleLog(
            company_id=company_id,
            schedule_id=schedule_id,
            created_by=user_id
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        try:
            start_time = datetime.utcnow()
            
            # Create report instance
            instance = self.create_report_instance(
                db=db,
                company_id=company_id,
                template_id=schedule.template_id,
                instance_name=f"Scheduled: {schedule.schedule_name}",
                parameters=schedule.parameters,
                user_id=user_id
            )
            
            # Generate report
            self.generate_report_instance(db, company_id, instance.id, user_id)
            
            # Update schedule
            schedule.last_run = datetime.utcnow()
            schedule.run_count += 1
            schedule.success_count += 1
            
            # Update log
            log.status = 'success'
            log.execution_time = (datetime.utcnow() - start_time).total_seconds()
            log.file_path = instance.file_path
            log.file_size = instance.file_size
            
            # Send email if configured
            if schedule.email_recipients:
                # This would integrate with email service
                log.email_sent = True
                log.email_recipients = schedule.email_recipients
            
            db.commit()
            
            logger.info(f"Report schedule executed: {schedule.schedule_name}")
            
            return log
            
        except Exception as e:
            # Update schedule and log with error
            schedule.failure_count += 1
            log.status = 'failed'
            log.error_message = str(e)
            
            db.commit()
            
            logger.error(f"Report schedule execution failed: {str(e)}")
            raise ValueError(f"Report schedule execution failed: {str(e)}")
    
    # Report Export Management
    def export_report_instance(
        self, 
        db: Session, 
        company_id: int,
        instance_id: int,
        export_format: str,
        export_config: Dict = None,
        user_id: int = None
    ) -> ReportExport:
        """Export report instance"""
        
        instance = db.query(ReportInstance).filter(
            ReportInstance.id == instance_id,
            ReportInstance.company_id == company_id
        ).first()
        
        if not instance:
            raise ValueError("Report instance not found")
        
        if instance.status != 'generated':
            raise ValueError("Report instance must be generated before export")
        
        try:
            # Create export record
            export = ReportExport(
                company_id=company_id,
                instance_id=instance_id,
                export_name=f"{instance.instance_name} - {export_format.upper()}",
                export_format=export_format,
                export_config=export_config,
                created_by=user_id
            )
            
            db.add(export)
            db.commit()
            db.refresh(export)
            
            # Generate export file
            file_path = self._generate_export_file(instance, export_format, export_config)
            
            # Update export record
            export.file_path = file_path
            export.file_size = self._get_file_size(file_path)
            export.status = 'completed'
            export.export_date = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Report exported: {export.export_name}")
            
            return export
            
        except Exception as e:
            # Update export with error
            export.status = 'failed'
            export.error_message = str(e)
            db.commit()
            
            logger.error(f"Report export failed: {str(e)}")
            raise ValueError(f"Report export failed: {str(e)}")
    
    def _generate_export_file(
        self, 
        instance: ReportInstance, 
        export_format: str, 
        export_config: Dict = None
    ) -> str:
        """Generate export file"""
        
        # This is a simplified implementation
        # In a real system, you would use appropriate libraries for each format
        
        if export_format == 'csv':
            return self._export_to_csv(instance, export_config)
        elif export_format == 'excel':
            return self._export_to_excel(instance, export_config)
        elif export_format == 'json':
            return self._export_to_json(instance, export_config)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _export_to_csv(
        self, 
        instance: ReportInstance, 
        export_config: Dict = None
    ) -> str:
        """Export to CSV format"""
        
        if not instance.data:
            raise ValueError("No data to export")
        
        # Convert data to DataFrame
        df = pd.DataFrame(instance.data)
        
        # Generate file path
        file_path = f"/tmp/report_{instance.instance_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        
        # Export to CSV
        df.to_csv(file_path, index=False)
        
        return file_path
    
    def _export_to_excel(
        self, 
        instance: ReportInstance, 
        export_config: Dict = None
    ) -> str:
        """Export to Excel format"""
        
        if not instance.data:
            raise ValueError("No data to export")
        
        # Convert data to DataFrame
        df = pd.DataFrame(instance.data)
        
        # Generate file path
        file_path = f"/tmp/report_{instance.instance_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        
        # Export to Excel
        df.to_excel(file_path, index=False)
        
        return file_path
    
    def _export_to_json(
        self, 
        instance: ReportInstance, 
        export_config: Dict = None
    ) -> str:
        """Export to JSON format"""
        
        if not instance.data:
            raise ValueError("No data to export")
        
        # Generate file path
        file_path = f"/tmp/report_{instance.instance_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        
        # Export to JSON
        with open(file_path, 'w') as f:
            json.dump(instance.data, f, indent=2, default=str)
        
        return file_path
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        
        import os
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0
    
    # Report Analytics
    def get_report_analytics(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        template_id: Optional[int] = None
    ) -> Dict:
        """Get report analytics"""
        
        # Get report instances
        query = db.query(ReportInstance).filter(ReportInstance.company_id == company_id)
        
        if from_date:
            query = query.filter(ReportInstance.generated_date >= from_date)
        
        if to_date:
            query = query.filter(ReportInstance.generated_date <= to_date)
        
        if template_id:
            query = query.filter(ReportInstance.template_id == template_id)
        
        instances = query.all()
        
        # Calculate analytics
        total_instances = len(instances)
        successful_instances = len([i for i in instances if i.status == 'generated'])
        failed_instances = len([i for i in instances if i.status == 'failed'])
        
        if total_instances > 0:
            success_rate = (successful_instances / total_instances) * 100
        else:
            success_rate = 0
        
        # Get average execution time
        execution_times = [i.execution_time for i in instances if i.execution_time]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Get total row count
        total_rows = sum(i.row_count for i in instances if i.row_count)
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "summary": {
                "total_instances": total_instances,
                "successful_instances": successful_instances,
                "failed_instances": failed_instances,
                "success_rate": success_rate,
                "average_execution_time": avg_execution_time,
                "total_rows": total_rows
            },
            "instances": [
                {
                    "id": instance.id,
                    "name": instance.instance_name,
                    "status": instance.status,
                    "generated_date": instance.generated_date,
                    "execution_time": instance.execution_time,
                    "row_count": instance.row_count
                }
                for instance in instances
            ]
        }

# Global service instance
report_studio_service = ReportStudioService()