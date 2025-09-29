# backend/app/services/performance_monitoring_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import time
import psutil
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitoringService:
    """Service class for performance monitoring"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitor_performance)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitor_performance(self):
        """Monitor system performance"""
        
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Store metrics
                timestamp = datetime.utcnow()
                for metric_name, metric_value in metrics.items():
                    self.metrics[metric_name].append({
                        "timestamp": timestamp,
                        "value": metric_value
                    })
                
                # Keep only last 1000 entries per metric
                for metric_name in self.metrics:
                    if len(self.metrics[metric_name]) > 1000:
                        self.metrics[metric_name] = self.metrics[metric_name][-1000:]
                
                # Sleep for 60 seconds
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {str(e)}")
                time.sleep(60)
    
    def _collect_system_metrics(self) -> Dict:
        """Collect system metrics"""
        
        metrics = {}
        
        try:
            # CPU metrics
            metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
            metrics["cpu_count"] = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics["memory_percent"] = memory.percent
            metrics["memory_available"] = memory.available
            metrics["memory_total"] = memory.total
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics["disk_percent"] = disk.percent
            metrics["disk_free"] = disk.free
            metrics["disk_total"] = disk.total
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics["network_bytes_sent"] = network.bytes_sent
            metrics["network_bytes_recv"] = network.bytes_recv
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
        
        return metrics
    
    def get_performance_metrics(
        self, 
        db: Session, 
        company_id: int,
        metric_type: Optional[str] = None,
        hours: int = 24
    ) -> Dict:
        """Get performance metrics"""
        
        try:
            # Get system metrics
            system_metrics = self._get_system_metrics(metric_type, hours)
            
            # Get database metrics
            db_metrics = self._get_database_metrics(db, company_id)
            
            # Get application metrics
            app_metrics = self._get_application_metrics(db, company_id)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "company_id": company_id,
                "system_metrics": system_metrics,
                "database_metrics": db_metrics,
                "application_metrics": app_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            return {"error": str(e)}
    
    def _get_system_metrics(self, metric_type: Optional[str], hours: int) -> Dict:
        """Get system metrics"""
        
        if metric_type:
            if metric_type in self.metrics:
                # Filter by time range
                cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
                filtered_metrics = [
                    m for m in self.metrics[metric_type]
                    if m["timestamp"].timestamp() > cutoff_time
                ]
                return {metric_type: filtered_metrics}
            else:
                return {metric_type: []}
        else:
            # Return all metrics
            cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
            all_metrics = {}
            
            for metric_name, metric_data in self.metrics.items():
                filtered_data = [
                    m for m in metric_data
                    if m["timestamp"].timestamp() > cutoff_time
                ]
                all_metrics[metric_name] = filtered_data
            
            return all_metrics
    
    def _get_database_metrics(self, db: Session, company_id: int) -> Dict:
        """Get database metrics"""
        
        try:
            # Test database performance
            start_time = time.time()
            
            # Perform various database operations
            db.query(Company).filter(Company.id == company_id).first()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "response_time": response_time,
                "connection_count": 1,
                "query_count": 1
            }
            
        except Exception as e:
            logger.error(f"Failed to get database metrics: {str(e)}")
            return {"error": str(e)}
    
    def _get_application_metrics(self, db: Session, company_id: int) -> Dict:
        """Get application metrics"""
        
        try:
            # Get data counts
            user_count = db.query(User).filter(User.company_id == company_id).count()
            customer_count = db.query(Customer).filter(Customer.company_id == company_id).count()
            item_count = db.query(Item).filter(Item.company_id == company_id).count()
            
            return {
                "user_count": user_count,
                "customer_count": customer_count,
                "item_count": item_count,
                "active_sessions": 1
            }
            
        except Exception as e:
            logger.error(f"Failed to get application metrics: {str(e)}")
            return {"error": str(e)}
    
    def get_performance_alerts(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get performance alerts"""
        
        alerts = []
        
        try:
            # Check CPU usage
            if "cpu_percent" in self.metrics:
                recent_cpu = self.metrics["cpu_percent"][-1]["value"] if self.metrics["cpu_percent"] else 0
                if recent_cpu > 80:
                    alerts.append({
                        "type": "warning",
                        "message": f"High CPU usage: {recent_cpu}%",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Check memory usage
            if "memory_percent" in self.metrics:
                recent_memory = self.metrics["memory_percent"][-1]["value"] if self.metrics["memory_percent"] else 0
                if recent_memory > 90:
                    alerts.append({
                        "type": "critical",
                        "message": f"High memory usage: {recent_memory}%",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Check disk usage
            if "disk_percent" in self.metrics:
                recent_disk = self.metrics["disk_percent"][-1]["value"] if self.metrics["disk_percent"] else 0
                if recent_disk > 85:
                    alerts.append({
                        "type": "warning",
                        "message": f"High disk usage: {recent_disk}%",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Failed to get performance alerts: {str(e)}")
            alerts.append({
                "type": "error",
                "message": f"Failed to get performance alerts: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def get_performance_recommendations(
        self, 
        db: Session, 
        company_id: int
    ) -> List[str]:
        """Get performance recommendations"""
        
        recommendations = []
        
        try:
            # Analyze metrics and provide recommendations
            if "cpu_percent" in self.metrics and self.metrics["cpu_percent"]:
                avg_cpu = sum(m["value"] for m in self.metrics["cpu_percent"][-10:]) / min(10, len(self.metrics["cpu_percent"]))
                if avg_cpu > 70:
                    recommendations.append("Consider upgrading CPU or optimizing application performance")
            
            if "memory_percent" in self.metrics and self.metrics["memory_percent"]:
                avg_memory = sum(m["value"] for m in self.metrics["memory_percent"][-10:]) / min(10, len(self.metrics["memory_percent"]))
                if avg_memory > 80:
                    recommendations.append("Consider increasing memory or optimizing memory usage")
            
            if "disk_percent" in self.metrics and self.metrics["disk_percent"]:
                avg_disk = sum(m["value"] for m in self.metrics["disk_percent"][-10:]) / min(10, len(self.metrics["disk_percent"]))
                if avg_disk > 80:
                    recommendations.append("Consider increasing disk space or cleaning up old data")
            
            # General recommendations
            recommendations.append("Monitor system performance regularly")
            recommendations.append("Implement automated scaling if needed")
            recommendations.append("Consider implementing caching strategies")
            
        except Exception as e:
            logger.error(f"Failed to get performance recommendations: {str(e)}")
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations

# Global service instance
performance_monitoring_service = PerformanceMonitoringService()