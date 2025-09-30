"""
Schema Validation and Consistency Checker
"""
from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel, ValidationError
import inspect
from datetime import datetime, date
from decimal import Decimal


class SchemaValidator:
    """Comprehensive schema validation and consistency checker"""
    
    def __init__(self):
        self.validation_results = {
            "total_schemas": 0,
            "valid_schemas": 0,
            "invalid_schemas": 0,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
    
    def validate_all_schemas(self) -> Dict[str, Any]:
        """Validate all schemas in the system"""
        try:
            # Import all schema modules
            from . import (
                user_schema, customer_schema, sales_schema, purchase_schema,
                inventory_schema, pos_schema, loyalty_schema, accounting_schema,
                core_schema, l10n_in_schema, whatsapp_schema
            )
            
            schema_modules = [
                user_schema, customer_schema, sales_schema, purchase_schema,
                inventory_schema, pos_schema, loyalty_schema, accounting_schema,
                core_schema, l10n_in_schema, whatsapp_schema
            ]
            
            for module in schema_modules:
                self._validate_module_schemas(module)
            
            self.validation_results["total_schemas"] = len(self._get_all_schemas())
            self.validation_results["valid_schemas"] = self.validation_results["total_schemas"] - len(self.validation_results["errors"])
            self.validation_results["invalid_schemas"] = len(self.validation_results["errors"])
            
            return self.validation_results
            
        except Exception as e:
            self.validation_results["errors"].append(f"Schema validation failed: {str(e)}")
            return self.validation_results
    
    def _validate_module_schemas(self, module):
        """Validate schemas in a specific module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseModel) and 
                obj != BaseModel):
                self._validate_schema(obj)
    
    def _validate_schema(self, schema_class: Type[BaseModel]):
        """Validate a specific schema class"""
        schema_name = schema_class.__name__
        
        try:
            # Check for required fields consistency
            self._check_required_fields_consistency(schema_class)
            
            # Check for field type consistency
            self._check_field_type_consistency(schema_class)
            
            # Check for validation rules
            self._check_validation_rules(schema_class)
            
            # Check for naming conventions
            self._check_naming_conventions(schema_class)
            
            # Check for documentation
            self._check_documentation(schema_class)
            
        except Exception as e:
            self.validation_results["errors"].append(f"Error validating {schema_name}: {str(e)}")
    
    def _check_required_fields_consistency(self, schema_class: Type[BaseModel]):
        """Check for consistency in required fields"""
        schema_name = schema_class.__name__
        
        # Check if Create schemas have required fields
        if schema_name.endswith("Create"):
            fields = schema_class.__fields__
            required_fields = [name for name, field in fields.items() if field.is_required()]
            
            if not required_fields:
                self.validation_results["warnings"].append(
                    f"{schema_name} has no required fields - consider if this is intentional"
                )
        
        # Check if Update schemas have optional fields
        if schema_name.endswith("Update"):
            fields = schema_class.__fields__
            required_fields = [name for name, field in fields.items() if field.is_required()]
            
            if required_fields:
                self.validation_results["warnings"].append(
                    f"{schema_name} has required fields - Update schemas should typically have all optional fields"
                )
    
    def _check_field_type_consistency(self, schema_class: Type[BaseModel]):
        """Check for field type consistency"""
        schema_name = schema_class.__name__
        
        for field_name, field_info in schema_class.__fields__.items():
            # Check for proper use of Optional
            if field_info.type_origin is Union and None in field_info.type_args:
                if not field_name.startswith("optional_") and not field_name.endswith("_optional"):
                    self.validation_results["suggestions"].append(
                        f"{schema_name}.{field_name} uses Optional but field name doesn't indicate it's optional"
                    )
            
            # Check for proper use of List
            if hasattr(field_info.type_, '__origin__') and field_info.type_.__origin__ is list:
                if not field_name.endswith("s") and not field_name.endswith("_list"):
                    self.validation_results["suggestions"].append(
                        f"{schema_name}.{field_name} is a list but field name doesn't indicate plurality"
                    )
    
    def _check_validation_rules(self, schema_class: Type[BaseModel]):
        """Check for validation rules consistency"""
        schema_name = schema_class.__name__
        
        for field_name, field_info in schema_class.__fields__.items():
            # Check for proper validation on common field types
            if field_name in ["email", "phone", "mobile"]:
                if not hasattr(field_info, 'regex') and not hasattr(field_info, 'validator'):
                    self.validation_results["warnings"].append(
                        f"{schema_name}.{field_name} should have validation rules"
                    )
            
            # Check for proper validation on amount fields
            if "amount" in field_name.lower() or "price" in field_name.lower():
                if field_info.type_ is not Decimal:
                    self.validation_results["suggestions"].append(
                        f"{schema_name}.{field_name} should use Decimal type for monetary values"
                    )
            
            # Check for proper validation on date fields
            if "date" in field_name.lower():
                if field_info.type_ not in [date, datetime, Optional[date], Optional[datetime]]:
                    self.validation_results["suggestions"].append(
                        f"{schema_name}.{field_name} should use date or datetime type"
                    )
    
    def _check_naming_conventions(self, schema_class: Type[BaseModel]):
        """Check for naming convention consistency"""
        schema_name = schema_class.__name__
        
        # Check schema naming conventions
        if not schema_name.endswith(("Create", "Update", "Response", "Request")):
            if not schema_name.endswith(("Base", "Enum")):
                self.validation_results["suggestions"].append(
                    f"{schema_name} doesn't follow naming convention (should end with Create/Update/Response/Request)"
                )
        
        # Check field naming conventions
        for field_name in schema_class.__fields__.keys():
            if not field_name.islower() and "_" not in field_name:
                self.validation_results["suggestions"].append(
                    f"{schema_name}.{field_name} should use snake_case naming"
                )
    
    def _check_documentation(self, schema_class: Type[BaseModel]):
        """Check for documentation completeness"""
        schema_name = schema_class.__name__
        
        if not schema_class.__doc__:
            self.validation_results["suggestions"].append(
                f"{schema_name} should have a docstring"
            )
        
        # Check for field documentation
        for field_name, field_info in schema_class.__fields__.items():
            if not field_info.field_info.description:
                self.validation_results["suggestions"].append(
                    f"{schema_name}.{field_name} should have a description"
                )
    
    def _get_all_schemas(self) -> List[Type[BaseModel]]:
        """Get all schema classes"""
        schemas = []
        try:
            from . import (
                user_schema, customer_schema, sales_schema, purchase_schema,
                inventory_schema, pos_schema, loyalty_schema, accounting_schema,
                core_schema, l10n_in_schema, whatsapp_schema
            )
            
            modules = [
                user_schema, customer_schema, sales_schema, purchase_schema,
                inventory_schema, pos_schema, loyalty_schema, accounting_schema,
                core_schema, l10n_in_schema, whatsapp_schema
            ]
            
            for module in modules:
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseModel) and 
                        obj != BaseModel):
                        schemas.append(obj)
            
        except Exception as e:
            self.validation_results["errors"].append(f"Error getting schemas: {str(e)}")
        
        return schemas
    
    def validate_schema_relationships(self) -> Dict[str, Any]:
        """Validate relationships between schemas"""
        relationship_results = {
            "missing_relationships": [],
            "inconsistent_relationships": [],
            "orphaned_schemas": []
        }
        
        try:
            # Check for Create/Update/Response schema pairs
            schemas = self._get_all_schemas()
            schema_names = [schema.__name__ for schema in schemas]
            
            for schema in schemas:
                schema_name = schema.__name__
                base_name = schema_name.replace("Create", "").replace("Update", "").replace("Response", "")
                
                # Check for missing pairs
                if schema_name.endswith("Create"):
                    if f"{base_name}Update" not in schema_names:
                        relationship_results["missing_relationships"].append(
                            f"Missing Update schema for {base_name}"
                        )
                    if f"{base_name}Response" not in schema_names:
                        relationship_results["missing_relationships"].append(
                            f"Missing Response schema for {base_name}"
                        )
                
                # Check for orphaned schemas
                if not any(schema_name.endswith(suffix) for suffix in ["Create", "Update", "Response", "Request", "Base", "Enum"]):
                    relationship_results["orphaned_schemas"].append(schema_name)
            
        except Exception as e:
            relationship_results["error"] = str(e)
        
        return relationship_results
    
    def generate_schema_report(self) -> str:
        """Generate a comprehensive schema validation report"""
        validation_results = self.validate_all_schemas()
        relationship_results = self.validate_schema_relationships()
        
        report = f"""
# Schema Validation Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Schemas: {validation_results['total_schemas']}
- Valid Schemas: {validation_results['valid_schemas']}
- Invalid Schemas: {validation_results['invalid_schemas']}
- Warnings: {len(validation_results['warnings'])}
- Errors: {len(validation_results['errors'])}

## Errors
"""
        
        for error in validation_results['errors']:
            report += f"- {error}\n"
        
        report += "\n## Warnings\n"
        for warning in validation_results['warnings']:
            report += f"- {warning}\n"
        
        report += "\n## Suggestions\n"
        for suggestion in validation_results['suggestions']:
            report += f"- {suggestion}\n"
        
        report += "\n## Schema Relationships\n"
        report += f"- Missing Relationships: {len(relationship_results.get('missing_relationships', []))}\n"
        report += f"- Inconsistent Relationships: {len(relationship_results.get('inconsistent_relationships', []))}\n"
        report += f"- Orphaned Schemas: {len(relationship_results.get('orphaned_schemas', []))}\n"
        
        if relationship_results.get('missing_relationships'):
            report += "\n### Missing Relationships\n"
            for missing in relationship_results['missing_relationships']:
                report += f"- {missing}\n"
        
        if relationship_results.get('orphaned_schemas'):
            report += "\n### Orphaned Schemas\n"
            for orphaned in relationship_results['orphaned_schemas']:
                report += f"- {orphaned}\n"
        
        return report


def validate_schemas() -> Dict[str, Any]:
    """Main function to validate all schemas"""
    validator = SchemaValidator()
    return validator.validate_all_schemas()


def generate_schema_report() -> str:
    """Generate a comprehensive schema report"""
    validator = SchemaValidator()
    return validator.generate_schema_report()


if __name__ == "__main__":
    # Run schema validation
    results = validate_schemas()
    print(f"Validation completed: {results['valid_schemas']}/{results['total_schemas']} schemas valid")
    
    # Generate report
    report = generate_schema_report()
    print("\n" + "="*50)
    print(report)