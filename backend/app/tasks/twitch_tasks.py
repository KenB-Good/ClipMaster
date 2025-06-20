"""
Twitch-related background tasks for ClipMaster
Handles stream monitoring, VOD processing, and chat analysis
SECURITY: Fixed async function definitions and import issues
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from celery import Celery
from ..core.config import settings
from ..services.twitch_service import TwitchService
from ..services.video_service import VideoService
from ..services.storage_service import StorageService

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery('clipmaster')
celery_app.config_from_object('app.core.celery_config')

@celery_app.task(bind=True)
def monitor_twitch_stream(self, channel_name: str, user_id: int) -> Dict[str, Any]:
    """
    Monitor a Twitch stream for highlight moments
    SECURITY FIX: Proper async function definition
    """
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting stream monitor'})
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_monitor_stream_async(self, channel_name, user_id))
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error monitoring stream {channel_name}: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

async def _monitor_stream_async(task, channel_name: str, user_id: int) -> Dict[str, Any]:
    """Async implementation of stream monitoring"""
    twitch_service = TwitchService()
    
    # Check if stream is live
    stream_info = await twitch_service.get_stream_info(channel_name)
    if not stream_info or not stream_info.get('is_live'):
        return {
            'status': 'completed',
            'message': f'Stream {channel_name} is not live',
            'highlights': []
        }
    
    task.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Stream is live, monitoring chat'})
    
    # Monitor for specified duration (default 1 hour)
    monitor_duration = 3600  # 1 hour in seconds
    start_time = datetime.utcnow()
    highlights = []
    
    try:
        # Start chat monitoring
        chat_monitor = await twitch_service.start_chat_monitor(channel_name)
        
        while (datetime.utcnow() - start_time).seconds < monitor_duration:
            # Check for excitement peaks
            excitement_windows = chat_monitor.get_recent_excitement_windows()
            
            for window in excitement_windows:
                if window['score'] > 8.0:  # High excitement threshold
                    # Create highlight clip
                    clip_data = await twitch_service.create_clip(
                        channel_name,
                        window['start_time'],
                        window['end_time']
                    )
                    
                    if clip_data:
                        highlights.append({
                            'timestamp': window['start_time'],
                            'duration': window['duration'],
                            'excitement_score': window['score'],
                            'clip_url': clip_data.get('url'),
                            'indicators': window.get('indicators', [])
                        })
            
            # Update progress
            elapsed = (datetime.utcnow() - start_time).seconds
            progress = min(20 + (elapsed / monitor_duration) * 70, 90)
            task.update_state(state='PROGRESS', meta={
                'progress': progress,
                'status': f'Monitoring... Found {len(highlights)} highlights'
            })
            
            # Wait before next check
            await asyncio.sleep(30)
        
        # Stop monitoring
        await twitch_service.stop_chat_monitor(channel_name)
        
        task.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Monitoring completed'})
        
        return {
            'status': 'completed',
            'channel': channel_name,
            'monitor_duration': monitor_duration,
            'highlights_found': len(highlights),
            'highlights': highlights
        }
        
    except Exception as e:
        logger.error(f"Error during stream monitoring: {e}")
        raise

@celery_app.task(bind=True)
def process_twitch_vod(self, vod_url: str, user_id: int) -> Dict[str, Any]:
    """
    Process a Twitch VOD for highlights
    SECURITY FIX: Proper async function definition
    """
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting VOD processing'})
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_process_vod_async(self, vod_url, user_id))
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error processing VOD {vod_url}: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

async def _process_vod_async(task, vod_url: str, user_id: int) -> Dict[str, Any]:
    """Async implementation of VOD processing"""
    task.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Downloading VOD'})
    
    # Download VOD
    video_path = await _download_twitch_vod(vod_url)
    
    task.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Processing video'})
    
    # Process with AI pipeline
    from ..tasks.video_tasks import process_video_full_pipeline
    
    # SECURITY FIX: Use proper async task execution
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        lambda: process_video_full_pipeline.delay(video_path, {'source': 'twitch_vod'}).get()
    )
    
    task.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Finalizing'})
    
    return {
        'status': 'completed',
        'vod_url': vod_url,
        'video_path': video_path,
        'processing_result': result
    }

async def _download_twitch_vod(vod_url: str) -> str:
    """Download Twitch VOD using streamlink"""
    import subprocess
    import tempfile
    import os
    
    # Create temporary file for download
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        # Use streamlink to download VOD
        cmd = [
            'streamlink',
            vod_url,
            'best',
            '--output', output_path,
            '--retry-streams', '3',
            '--retry-max', '5'
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Streamlink failed: {stderr.decode()}")
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("Downloaded file is empty or missing")
        
        return output_path
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise

@celery_app.task(bind=True)
def analyze_twitch_chat(self, channel_name: str, duration_minutes: int = 60) -> Dict[str, Any]:
    """
    Analyze Twitch chat for excitement patterns
    """
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting chat analysis'})
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_analyze_chat_async(self, channel_name, duration_minutes))
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error analyzing chat for {channel_name}: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

async def _analyze_chat_async(task, channel_name: str, duration_minutes: int) -> Dict[str, Any]:
    """Async implementation of chat analysis"""
    twitch_service = TwitchService()
    
    task.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Connecting to chat'})
    
    # Start chat monitoring
    chat_monitor = await twitch_service.start_chat_monitor(channel_name)
    
    # Collect chat data for specified duration
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    analysis_data = {
        'channel': channel_name,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'total_messages': 0,
        'unique_users': set(),
        'excitement_peaks': [],
        'top_keywords': {},
        'sentiment_analysis': {}
    }
    
    try:
        while datetime.utcnow() < end_time:
            # Get recent chat activity
            recent_stats = chat_monitor.get_recent_stats()
            
            # Update analysis data
            analysis_data['total_messages'] = recent_stats.get('total_messages', 0)
            analysis_data['unique_users'].update(recent_stats.get('unique_users', []))
            
            # Check for excitement peaks
            excitement_windows = chat_monitor.get_recent_excitement_windows()
            for window in excitement_windows:
                if window['score'] > 7.0:
                    analysis_data['excitement_peaks'].append({
                        'timestamp': window['start_time'],
                        'score': window['score'],
                        'duration': window['duration'],
                        'indicators': window.get('indicators', [])
                    })
            
            # Update progress
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            total_duration = duration_minutes * 60
            progress = min(10 + (elapsed / total_duration) * 80, 90)
            
            task.update_state(state='PROGRESS', meta={
                'progress': progress,
                'status': f'Analyzing... {len(analysis_data["excitement_peaks"])} peaks found'
            })
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        # Stop monitoring
        await twitch_service.stop_chat_monitor(channel_name)
        
        # Finalize analysis
        analysis_data['unique_users'] = len(analysis_data['unique_users'])
        analysis_data['peak_count'] = len(analysis_data['excitement_peaks'])
        
        task.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Analysis completed'})
        
        return {
            'status': 'completed',
            'analysis': analysis_data
        }
        
    except Exception as e:
        await twitch_service.stop_chat_monitor(channel_name)
        raise

@celery_app.task(bind=True)
def create_highlight_reel(self, channel_name: str, highlights: list, user_id: int) -> Dict[str, Any]:
    """
    Create a highlight reel from detected moments
    """
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Creating highlight reel'})
        
        if not highlights:
            return {
                'status': 'completed',
                'message': 'No highlights to process',
                'reel_path': None
            }
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_create_reel_async(self, channel_name, highlights, user_id))
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error creating highlight reel: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

async def _create_reel_async(task, channel_name: str, highlights: list, user_id: int) -> Dict[str, Any]:
    """Async implementation of highlight reel creation"""
    import tempfile
    import os
    from ..ai.video_processor import VideoProcessor
    
    video_processor = VideoProcessor()
    
    task.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Downloading highlight clips'})
    
    # Download all highlight clips
    clip_paths = []
    for i, highlight in enumerate(highlights):
        if 'clip_url' in highlight:
            clip_path = await _download_twitch_vod(highlight['clip_url'])
            clip_paths.append(clip_path)
            
            progress = 10 + (i / len(highlights)) * 60
            task.update_state(state='PROGRESS', meta={
                'progress': progress,
                'status': f'Downloaded {i+1}/{len(highlights)} clips'
            })
    
    if not clip_paths:
        return {
            'status': 'completed',
            'message': 'No clips could be downloaded',
            'reel_path': None
        }
    
    task.update_state(state='PROGRESS', meta={'progress': 70, 'status': 'Combining clips'})
    
    # Create highlight reel
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        reel_path = temp_file.name
    
    try:
        # Use ffmpeg to concatenate clips
        await _concatenate_videos(clip_paths, reel_path)
        
        task.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Saving reel'})
        
        # Move to permanent storage
        storage_service = StorageService()
        final_path = await storage_service.store_video(
            reel_path,
            f"{channel_name}_highlights_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4",
            user_id
        )
        
        # Clean up temporary files
        for clip_path in clip_paths:
            if os.path.exists(clip_path):
                os.unlink(clip_path)
        
        if os.path.exists(reel_path):
            os.unlink(reel_path)
        
        task.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Reel created'})
        
        return {
            'status': 'completed',
            'channel': channel_name,
            'highlights_count': len(highlights),
            'reel_path': final_path,
            'clips_processed': len(clip_paths)
        }
        
    except Exception as e:
        # Clean up on error
        for clip_path in clip_paths:
            if os.path.exists(clip_path):
                os.unlink(clip_path)
        if os.path.exists(reel_path):
            os.unlink(reel_path)
        raise

async def _concatenate_videos(video_paths: list, output_path: str):
    """Concatenate multiple video files using ffmpeg"""
    import tempfile
    import os
    
    # Create file list for ffmpeg
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        list_file = f.name
        for path in video_paths:
            f.write(f"file '{path}'\n")
    
    try:
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            '-y',  # Overwrite output file
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg concatenation failed: {stderr.decode()}")
        
    finally:
        if os.path.exists(list_file):
            os.unlink(list_file)
