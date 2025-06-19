
"""
Twitch integration background tasks
"""
import logging
from typing import Dict, Any, List
from celery import current_task

from app.tasks.celery_app import celery_app
from app.core.database import database
from app.services.twitch_service import TwitchService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def monitor_twitch_stream_task(self, integration_id: str, duration_minutes: int = 60):
    """Monitor Twitch stream for highlights"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting stream monitoring'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def monitor():
            await database.connect()
            try:
                twitch_service = TwitchService(database)
                integration = await twitch_service.get_integration(integration_id)
                
                if not integration:
                    raise ValueError("Integration not found")
                
                # Start monitoring logic here
                # This would involve connecting to Twitch chat and stream
                result = await _monitor_stream_activity(integration, duration_minutes)
                
                return result
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(monitor())
        return result
        
    except Exception as e:
        logger.error(f"Stream monitoring failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def capture_twitch_clip_task(self, integration_id: str, start_time: float, duration: float = 30):
    """Capture clip from Twitch stream"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Capturing stream clip'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def capture():
            await database.connect()
            try:
                # Implementation for capturing stream clip
                # This would involve Twitch API calls and stream recording
                result = await _capture_stream_segment(integration_id, start_time, duration)
                return result
            finally:
                await database.disconnect()
        
        result = loop.run_until_complete(capture())
        return result
        
    except Exception as e:
        logger.error(f"Clip capture failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def analyze_chat_activity_task(self, integration_id: str, chat_messages: List[Dict[str, Any]]):
    """Analyze chat activity for highlight detection"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Analyzing chat activity'})
        
        # Analyze chat messages for excitement indicators
        highlights = []
        
        # Group messages by time windows
        time_windows = _group_messages_by_time(chat_messages, window_size=30)  # 30-second windows
        
        for window_start, messages in time_windows.items():
            excitement_score = _calculate_excitement_score(messages)
            
            if excitement_score > 0.7:  # Threshold for highlight
                highlights.append({
                    'start_time': window_start,
                    'end_time': window_start + 30,
                    'confidence': excitement_score,
                    'type': 'CHAT_SPIKE',
                    'description': f'Chat excitement detected ({len(messages)} messages)',
                    'metadata': {
                        'message_count': len(messages),
                        'excitement_score': excitement_score,
                        'top_messages': messages[:5]  # Top 5 messages
                    }
                })
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Chat analysis completed'})
        
        return {
            'highlights': highlights,
            'total_messages': len(chat_messages),
            'excitement_windows': len(highlights)
        }
        
    except Exception as e:
        logger.error(f"Chat analysis failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task
def update_stream_status():
    """Periodic task to update stream status for all integrations"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def update_all():
            await database.connect()
            try:
                twitch_service = TwitchService(database)
                integrations = await twitch_service.get_integrations()
                
                updated_count = 0
                for integration in integrations:
                    if integration.is_monitoring:
                        try:
                            # Check stream status
                            stream_info = await twitch_service.get_stream_info(integration.user_id)
                            
                            # Update integration with latest info
                            if stream_info.get('is_live'):
                                await twitch_service.update_integration(
                                    integration.id,
                                    {
                                        'last_stream_title': stream_info.get('stream_title'),
                                        'last_stream_game': stream_info.get('game_name'),
                                        'last_used_at': 'now()'
                                    }
                                )
                                updated_count += 1
                        except Exception as e:
                            logger.error(f"Error updating stream status for {integration.username}: {e}")
                
                return {'updated_integrations': updated_count}
            finally:
                await database.disconnect()
        
        return loop.run_until_complete(update_all())
        
    except Exception as e:
        logger.error(f"Stream status update failed: {e}")
        return {'error': str(e)}

@celery_app.task(bind=True)
def process_twitch_vod_task(self, vod_url: str, integration_id: str):
    """Process a Twitch VOD for highlights"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Downloading VOD'})
        
        # Download VOD
        video_path = await _download_twitch_vod(vod_url)
        
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Processing video'})
        
        # Process with AI pipeline
        from app.tasks.video_tasks import process_video_full_pipeline
        result = process_video_full_pipeline.delay(video_path, {'source': 'twitch_vod'})
        
        processing_result = result.get()
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'VOD processing completed'})
        
        return {
            'vod_url': vod_url,
            'video_path': video_path,
            'processing_result': processing_result
        }
        
    except Exception as e:
        logger.error(f"VOD processing failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

# Helper functions

async def _monitor_stream_activity(integration, duration_minutes: int):
    """Monitor stream activity for the specified duration"""
    # This would implement real-time stream monitoring
    # Including chat monitoring, stream recording, etc.
    
    logger.info(f"Monitoring stream for {integration.username} for {duration_minutes} minutes")
    
    # Placeholder implementation
    return {
        'integration_id': integration.id,
        'duration_monitored': duration_minutes,
        'status': 'monitoring_started'
    }

async def _capture_stream_segment(integration_id: str, start_time: float, duration: float):
    """Capture a segment from the live stream"""
    # This would implement stream capture functionality
    
    logger.info(f"Capturing stream segment: {start_time}s for {duration}s")
    
    # Placeholder implementation
    return {
        'integration_id': integration_id,
        'start_time': start_time,
        'duration': duration,
        'status': 'captured'
    }

def _group_messages_by_time(messages: List[Dict[str, Any]], window_size: int = 30) -> Dict[float, List[Dict[str, Any]]]:
    """Group chat messages by time windows"""
    windows = {}
    
    for message in messages:
        timestamp = message.get('timestamp', 0)
        window_start = (timestamp // window_size) * window_size
        
        if window_start not in windows:
            windows[window_start] = []
        
        windows[window_start].append(message)
    
    return windows

def _calculate_excitement_score(messages: List[Dict[str, Any]]) -> float:
    """Calculate excitement score based on chat messages"""
    if not messages:
        return 0.0
    
    excitement_indicators = [
        'clip', 'poggers', 'pog', 'omg', 'wow', 'insane', 'crazy',
        'unbelievable', 'sick', 'nuts', 'epic', 'legendary', '!!!',
        'wtf', 'no way', 'holy', 'amazing', 'incredible'
    ]
    
    excitement_count = 0
    total_messages = len(messages)
    
    for message in messages:
        text = message.get('text', '').lower()
        
        # Check for excitement indicators
        for indicator in excitement_indicators:
            if indicator in text:
                excitement_count += 1
                break
        
        # Check for caps and exclamation marks
        if text.isupper() and len(text) > 3:
            excitement_count += 1
        
        if text.count('!') >= 3:
            excitement_count += 1
    
    # Calculate score (0-1)
    base_score = excitement_count / total_messages
    
    # Bonus for high message volume
    volume_bonus = min(total_messages / 50, 0.5)  # Up to 0.5 bonus for high volume
    
    return min(base_score + volume_bonus, 1.0)

async def _download_twitch_vod(vod_url: str) -> str:
    """Download Twitch VOD"""
    # This would implement VOD downloading using tools like youtube-dl or twitch-dl
    
    logger.info(f"Downloading VOD: {vod_url}")
    
    # Placeholder implementation
    return f"/tmp/vod_{hash(vod_url)}.mp4"
