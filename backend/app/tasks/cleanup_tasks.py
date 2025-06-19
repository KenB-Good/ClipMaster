
"""
Cleanup and maintenance background tasks
"""
import os
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.core.database import database
from app.services.storage_service import StorageService
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

@celery_app.task
def cleanup_temp_files():
    """Clean up temporary files"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def cleanup():
            file_service = FileService()
            result = await file_service.cleanup_temp_files(max_age_hours=24)
            return result
        
        result = loop.run_until_complete(cleanup())
        
        logger.info(f"Temp cleanup completed: {result['count']} files removed")
        return result
        
    except Exception as e:
        logger.error(f"Temp cleanup failed: {e}")
        return {'error': str(e)}

@celery_app.task
def monitor_storage():
    """Monitor storage usage and trigger cleanup if needed"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def monitor():
            await database.connect()
            try:
                storage_service = StorageService(database)
                
                # Record current storage stats
                await storage_service.record_storage_stats()
                
                # Get storage info
                storage_info = await storage_service.get_storage_info()
                
                # Check if cleanup is needed
                if storage_info.usage_percentage > (settings.AUTO_CLEANUP_THRESHOLD * 100):
                    logger.warning(f"Storage usage high: {storage_info.usage_percentage:.1f}%")
                    
                    # Trigger cleanup
                    cleanup_result = await storage_service.cleanup_storage(force=False)
                    
                    return {
                        'storage_info': storage_info.__dict__,
                        'cleanup_triggered': True,
                        'cleanup_result': cleanup_result
                    }
                else:
                    return {
                        'storage_info': storage_info.__dict__,
                        'cleanup_triggered': False
                    }
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(monitor())
        return result
        
    except Exception as e:
        logger.error(f"Storage monitoring failed: {e}")
        return {'error': str(e)}

@celery_app.task
def cleanup_old_videos():
    """Clean up old archived videos"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def cleanup():
            await database.connect()
            try:
                storage_service = StorageService(database)
                result = await storage_service.cleanup_storage(force=False)
                return result
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(cleanup())
        
        logger.info(f"Video cleanup completed: {result['cleaned_files']} files removed")
        return result
        
    except Exception as e:
        logger.error(f"Video cleanup failed: {e}")
        return {'error': str(e)}

@celery_app.task
def optimize_storage():
    """Optimize storage by removing duplicates"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def optimize():
            await database.connect()
            try:
                storage_service = StorageService(database)
                result = await storage_service.optimize_storage()
                return result
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(optimize())
        
        logger.info(f"Storage optimization completed: {result['duplicates_found']} duplicates found")
        return result
        
    except Exception as e:
        logger.error(f"Storage optimization failed: {e}")
        return {'error': str(e)}

@celery_app.task
def cleanup_failed_tasks():
    """Clean up old failed tasks from database"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def cleanup():
            await database.connect()
            try:
                # Remove old failed tasks (older than 7 days)
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                query = """
                DELETE FROM processing_tasks 
                WHERE status = 'FAILED' AND created_at < :cutoff_date
                """
                
                result = await database.execute(query, {"cutoff_date": cutoff_date})
                
                return {
                    'deleted_tasks': result,
                    'cutoff_date': cutoff_date.isoformat()
                }
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(cleanup())
        
        logger.info(f"Task cleanup completed: {result['deleted_tasks']} tasks removed")
        return result
        
    except Exception as e:
        logger.error(f"Task cleanup failed: {e}")
        return {'error': str(e)}

@celery_app.task
def generate_usage_reports():
    """Generate usage reports and statistics"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def generate():
            await database.connect()
            try:
                # Collect various statistics
                stats = {}
                
                # Video statistics
                video_stats_query = """
                SELECT 
                    COUNT(*) as total_videos,
                    COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END) as processed_videos,
                    COUNT(CASE WHEN status = 'PROCESSING' THEN 1 END) as processing_videos,
                    COUNT(CASE WHEN status = 'ERROR' THEN 1 END) as error_videos,
                    AVG(file_size) as avg_file_size,
                    SUM(file_size) as total_file_size
                FROM videos
                WHERE uploaded_at > NOW() - INTERVAL '30 days'
                """
                
                video_stats = await database.fetch_one(video_stats_query)
                stats['videos'] = dict(video_stats) if video_stats else {}
                
                # Task statistics
                task_stats_query = """
                SELECT 
                    type,
                    status,
                    COUNT(*) as count
                FROM processing_tasks
                WHERE created_at > NOW() - INTERVAL '30 days'
                GROUP BY type, status
                """
                
                task_stats = await database.fetch_all(task_stats_query)
                stats['tasks'] = [dict(row) for row in task_stats] if task_stats else []
                
                # Storage statistics
                storage_service = StorageService(database)
                storage_stats = await storage_service.get_storage_stats(days=30)
                stats['storage'] = storage_stats
                
                return {
                    'report_date': datetime.utcnow().isoformat(),
                    'period': '30_days',
                    'statistics': stats
                }
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(generate())
        
        logger.info("Usage report generated successfully")
        return result
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return {'error': str(e)}

@celery_app.task
def health_check_services():
    """Health check for all services"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def check():
            health_status = {
                'timestamp': datetime.utcnow().isoformat(),
                'services': {}
            }
            
            # Database check
            try:
                await database.connect()
                await database.fetch_one("SELECT 1")
                health_status['services']['database'] = {'status': 'healthy'}
                await database.disconnect()
            except Exception as e:
                health_status['services']['database'] = {'status': 'unhealthy', 'error': str(e)}
            
            # Redis check
            try:
                import redis
                r = redis.from_url(settings.REDIS_URL)
                r.ping()
                health_status['services']['redis'] = {'status': 'healthy'}
            except Exception as e:
                health_status['services']['redis'] = {'status': 'unhealthy', 'error': str(e)}
            
            # File system checks
            for name, path in [
                ('upload_dir', settings.UPLOAD_DIR),
                ('clips_dir', settings.CLIPS_DIR),
                ('temp_dir', settings.TEMP_DIR)
            ]:
                try:
                    if os.path.exists(path) and os.access(path, os.W_OK):
                        health_status['services'][name] = {'status': 'healthy'}
                    else:
                        health_status['services'][name] = {'status': 'unhealthy', 'error': 'Directory not accessible'}
                except Exception as e:
                    health_status['services'][name] = {'status': 'unhealthy', 'error': str(e)}
            
            # AI services check
            try:
                import torch
                health_status['services']['ai'] = {
                    'status': 'healthy',
                    'cuda_available': torch.cuda.is_available(),
                    'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
                }
            except Exception as e:
                health_status['services']['ai'] = {'status': 'unhealthy', 'error': str(e)}
            
            return health_status
        
        result = loop.run_until_complete(check())
        
        # Log any unhealthy services
        unhealthy_services = [
            name for name, status in result['services'].items() 
            if status.get('status') != 'healthy'
        ]
        
        if unhealthy_services:
            logger.warning(f"Unhealthy services detected: {unhealthy_services}")
        else:
            logger.info("All services healthy")
        
        return result
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'error': str(e)}
