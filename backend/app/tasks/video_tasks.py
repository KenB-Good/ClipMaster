
"""
Video processing background tasks
"""
import os
import logging
from typing import Dict, Any
from celery import current_task
from databases import Database

from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.core.database import database
from app.services.video_service import VideoService
from app.services.task_service import TaskService
from app.services.ai_service import AIService
from app.ai.video_processor import VideoProcessor
from app.models.task import TaskStatus, ProcessingTaskUpdate
from app.models.video import VideoUpdate, VideoStatus

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_video_full_pipeline(self, video_id: str, config: Dict[str, Any] = None):
    """Complete video processing pipeline"""
    try:
        # Update task progress
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting video processing'})
        
        # Connect to database
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process():
            await database.connect()
            try:
                video_service = VideoService(database)
                ai_service = AIService()
                
                # Update video status
                await video_service.update_video(
                    video_id, 
                    VideoUpdate(status=VideoStatus.PROCESSING)
                )
                
                # Step 1: Transcription
                self.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Transcribing audio'})
                transcription = await ai_service.transcribe_video(video_id, self.request.id, database)
                
                if transcription:
                    await video_service.update_video(
                        video_id,
                        VideoUpdate(transcription=transcription)
                    )
                
                # Step 2: Highlight Detection
                self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Detecting highlights'})
                highlights = await ai_service.detect_highlights(video_id, self.request.id, database)
                
                # Step 3: Clip Generation
                self.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Generating clips'})
                if highlights:
                    await ai_service.generate_clips(video_id, self.request.id, database)
                
                # Complete processing
                await video_service.update_video(
                    video_id,
                    VideoUpdate(status=VideoStatus.PROCESSED)
                )
                
                self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Processing completed'})
                
                return {
                    'video_id': video_id,
                    'transcription_length': len(transcription) if transcription else 0,
                    'highlights_count': len(highlights) if highlights else 0,
                    'status': 'completed'
                }
                
            except Exception as e:
                logger.error(f"Error in video processing pipeline: {e}")
                await video_service.update_video(
                    video_id,
                    VideoUpdate(status=VideoStatus.ERROR)
                )
                raise
            finally:
                await database.disconnect()
        
        return loop.run_until_complete(process())
        
    except Exception as e:
        logger.error(f"Video processing task failed: {e}")
        self.update_state(state='FAILURE', meta={'progress': 0, 'error': str(e)})
        raise

@celery_app.task(bind=True)
def transcribe_video_task(self, video_id: str, task_id: str, config: Dict[str, Any] = None):
    """Transcribe video audio"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Loading models'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def transcribe():
            await database.connect()
            try:
                ai_service = AIService()
                result = await ai_service.transcribe_video(video_id, task_id, database)
                return result
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(transcribe())
        return {'transcription': result, 'video_id': video_id}
        
    except Exception as e:
        logger.error(f"Transcription task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def detect_highlights_task(self, video_id: str, task_id: str, config: Dict[str, Any] = None):
    """Detect video highlights"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Analyzing video'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def detect():
            await database.connect()
            try:
                ai_service = AIService()
                highlights = await ai_service.detect_highlights(video_id, task_id, database)
                return highlights
            finally:
                await database.disconnect()
        
        highlights = loop.run_until_complete(detect())
        return {'highlights': highlights, 'count': len(highlights)}
        
    except Exception as e:
        logger.error(f"Highlight detection task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def generate_clips_task(self, video_id: str, task_id: str, config: Dict[str, Any] = None):
    """Generate clips from highlights"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Generating clips'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def generate():
            await database.connect()
            try:
                ai_service = AIService()
                await ai_service.generate_clips(video_id, task_id, database)
                
                # Get clip count
                video_service = VideoService(database)
                clips = await video_service.get_video_clips(video_id)
                return len(clips)
            finally:
                await database.disconnect()
        
        clip_count = loop.run_until_complete(generate())
        return {'clips_generated': clip_count, 'video_id': video_id}
        
    except Exception as e:
        logger.error(f"Clip generation task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def add_subtitles_task(self, video_id: str, clip_id: str, config: Dict[str, Any] = None):
    """Add subtitles to a clip"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Adding subtitles'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def add_subtitles():
            await database.connect()
            try:
                # Implementation for adding subtitles
                # This would use the VideoProcessor and transcription data
                processor = VideoProcessor()
                # ... subtitle processing logic
                return True
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(add_subtitles())
        return {'success': result, 'clip_id': clip_id}
        
    except Exception as e:
        logger.error(f"Subtitle task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def optimize_clip_task(self, clip_id: str, platform: str, config: Dict[str, Any] = None):
    """Optimize clip for specific platform"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': f'Optimizing for {platform}'})
        
        # Implementation for platform optimization
        processor = VideoProcessor()
        # ... optimization logic
        
        return {'success': True, 'clip_id': clip_id, 'platform': platform}
        
    except Exception as e:
        logger.error(f"Optimization task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task
def batch_process_videos(video_ids: list, config: Dict[str, Any] = None):
    """Process multiple videos in batch"""
    results = []
    
    for video_id in video_ids:
        try:
            result = process_video_full_pipeline.delay(video_id, config)
            results.append({
                'video_id': video_id,
                'task_id': result.id,
                'status': 'queued'
            })
        except Exception as e:
            results.append({
                'video_id': video_id,
                'status': 'failed',
                'error': str(e)
            })
    
    return results
