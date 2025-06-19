
"""
Stream monitoring for real-time highlight detection
"""
import asyncio
import os
import subprocess
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import logging

from app.twitch.client import TwitchAPIClient
from app.twitch.chat_monitor import TwitchChatMonitor
from app.core.config import settings

logger = logging.getLogger(__name__)

class StreamMonitor:
    def __init__(self, integration_id: str, db):
        self.integration_id = integration_id
        self.db = db
        self.twitch_client = TwitchAPIClient()
        self.chat_monitor = None
        
        self.is_monitoring = False
        self.stream_info = None
        self.recording_process = None
        self.recording_file = None
        
        self.stats = {
            'start_time': None,
            'stream_start_time': None,
            'total_recording_time': 0,
            'chat_highlights': [],
            'auto_clips_created': 0
        }
    
    async def start_monitoring(self, auto_capture: bool = True, chat_monitoring: bool = True):
        """Start monitoring the stream"""
        try:
            # Get integration details
            from app.services.twitch_service import TwitchService
            twitch_service = TwitchService(self.db)
            integration = await twitch_service.get_integration(self.integration_id)
            
            if not integration:
                raise ValueError("Integration not found")
            
            self.is_monitoring = True
            self.stats['start_time'] = datetime.utcnow()
            
            logger.info(f"Starting stream monitoring for {integration.username}")
            
            # Start chat monitoring if enabled
            if chat_monitoring:
                await self._start_chat_monitoring(integration.username)
            
            # Main monitoring loop
            await self._monitoring_loop(integration, auto_capture)
            
        except Exception as e:
            logger.error(f"Error in stream monitoring: {e}")
            await self.stop_monitoring()
            raise
    
    async def stop_monitoring(self):
        """Stop monitoring the stream"""
        self.is_monitoring = False
        
        # Stop chat monitoring
        if self.chat_monitor:
            await self.chat_monitor.disconnect()
            self.chat_monitor = None
        
        # Stop recording
        await self._stop_recording()
        
        logger.info(f"Stream monitoring stopped for integration {self.integration_id}")
    
    async def _start_chat_monitoring(self, username: str):
        """Start monitoring chat for highlights"""
        try:
            self.chat_monitor = TwitchChatMonitor(
                channel=username,
                on_message_callback=self._on_chat_message
            )
            
            # Start chat monitoring in background
            asyncio.create_task(self.chat_monitor.start_monitoring())
            
            logger.info(f"Chat monitoring started for {username}")
            
        except Exception as e:
            logger.error(f"Failed to start chat monitoring: {e}")
    
    async def _monitoring_loop(self, integration, auto_capture: bool):
        """Main monitoring loop"""
        consecutive_offline_checks = 0
        max_offline_checks = 5  # Stop after 5 consecutive offline checks
        
        while self.is_monitoring:
            try:
                # Check stream status
                stream_info = await self.twitch_client.get_stream_info(integration.user_id)
                
                if stream_info.get('is_live'):
                    consecutive_offline_checks = 0
                    
                    # Update stream info
                    self.stream_info = stream_info
                    
                    # Start recording if auto capture is enabled and not already recording
                    if auto_capture and not self.recording_process:
                        await self._start_recording(integration.username)
                    
                    # Check for highlight triggers
                    await self._check_highlight_triggers()
                    
                    # Update integration with latest stream info
                    from app.services.twitch_service import TwitchService
                    twitch_service = TwitchService(self.db)
                    await twitch_service.update_integration(
                        self.integration_id,
                        {
                            'last_stream_id': stream_info.get('stream_id'),
                            'last_stream_title': stream_info.get('title'),
                            'last_stream_game': stream_info.get('game_name'),
                            'last_used_at': datetime.utcnow()
                        }
                    )
                    
                else:
                    consecutive_offline_checks += 1
                    
                    # Stop recording if stream is offline
                    if self.recording_process:
                        await self._stop_recording()
                    
                    # Stop monitoring if stream has been offline for too long
                    if consecutive_offline_checks >= max_offline_checks:
                        logger.info(f"Stream has been offline for {max_offline_checks} checks, stopping monitoring")
                        break
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _start_recording(self, username: str):
        """Start recording the stream"""
        try:
            # Create recording directory
            recording_dir = os.path.join(settings.TEMP_DIR, "recordings")
            os.makedirs(recording_dir, exist_ok=True)
            
            # Generate recording filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            self.recording_file = os.path.join(recording_dir, f"{username}_{timestamp}.mp4")
            
            # Start recording using streamlink (if available) or other method
            recording_command = [
                'streamlink',
                f'https://www.twitch.tv/{username}',
                'best',
                '-o', self.recording_file,
                '--retry-streams', '5',
                '--retry-max', '10'
            ]
            
            self.recording_process = subprocess.Popen(
                recording_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Started recording stream to: {self.recording_file}")
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.recording_process = None
    
    async def _stop_recording(self):
        """Stop recording the stream"""
        if self.recording_process:
            try:
                self.recording_process.terminate()
                self.recording_process.wait(timeout=10)
                
                # Check if file was created and has content
                if self.recording_file and os.path.exists(self.recording_file):
                    file_size = os.path.getsize(self.recording_file)
                    if file_size > 1024 * 1024:  # At least 1MB
                        logger.info(f"Recording saved: {self.recording_file} ({file_size} bytes)")
                        
                        # Queue the recording for processing
                        await self._queue_recording_processing()
                    else:
                        # Remove small/empty files
                        os.remove(self.recording_file)
                        logger.warning("Recording file was too small, removed")
                
                self.recording_process = None
                self.recording_file = None
                
            except Exception as e:
                logger.error(f"Error stopping recording: {e}")
    
    async def _check_highlight_triggers(self):
        """Check for various highlight triggers"""
        current_time = datetime.utcnow()
        
        # Chat-based highlights
        if self.chat_monitor:
            chat_stats = self.chat_monitor.get_statistics()
            
            # Check for excitement windows
            excitement_windows = chat_stats.get('recent_excitement_windows', [])
            for window in excitement_windows:
                if window['total_score'] >= 10:  # High excitement threshold
                    await self._trigger_highlight({
                        'type': 'chat_excitement',
                        'timestamp': current_time,
                        'confidence': min(window['total_score'] / 20, 1.0),
                        'metadata': window
                    })
        
        # Viewer count spike detection
        if self.stream_info:
            viewer_count = self.stream_info.get('viewer_count', 0)
            # This would require tracking viewer count over time
            # For now, just log high viewer counts
            if viewer_count > 1000:  # Threshold for "high" viewer count
                logger.info(f"High viewer count detected: {viewer_count}")
    
    async def _trigger_highlight(self, highlight_data: Dict[str, Any]):
        """Trigger highlight creation"""
        try:
            logger.info(f"Highlight triggered: {highlight_data['type']} at {highlight_data['timestamp']}")
            
            # Add to stats
            self.stats['chat_highlights'].append(highlight_data)
            
            # Create clip if recording
            if self.recording_process and highlight_data['confidence'] >= 0.7:
                await self._create_auto_clip(highlight_data)
            
        except Exception as e:
            logger.error(f"Error triggering highlight: {e}")
    
    async def _create_auto_clip(self, highlight_data: Dict[str, Any]):
        """Create automatic clip from highlight trigger"""
        try:
            # This would create a clip using Twitch API
            # For live streams, we can use the create_clip endpoint
            
            from app.services.twitch_service import TwitchService
            twitch_service = TwitchService(self.db)
            integration = await twitch_service.get_integration(self.integration_id)
            
            if integration and integration.access_token:
                clip_result = await self.twitch_client.create_clip(
                    broadcaster_id=integration.user_id,
                    access_token=integration.access_token
                )
                
                if clip_result:
                    self.stats['auto_clips_created'] += 1
                    logger.info(f"Auto clip created: {clip_result['id']}")
                    
                    # Store clip information for later processing
                    await self._store_clip_info(clip_result, highlight_data)
            
        except Exception as e:
            logger.error(f"Error creating auto clip: {e}")
    
    async def _store_clip_info(self, clip_result: Dict[str, Any], highlight_data: Dict[str, Any]):
        """Store clip information in database"""
        try:
            # Create a processing task for the clip
            from app.services.task_service import TaskService
            from app.models.task import ProcessingTaskCreate, TaskType
            
            task_service = TaskService(self.db)
            
            await task_service.create_task(
                ProcessingTaskCreate(
                    type=TaskType.TWITCH_CAPTURE,
                    config={
                        'clip_id': clip_result['id'],
                        'edit_url': clip_result['edit_url'],
                        'highlight_trigger': highlight_data,
                        'integration_id': self.integration_id
                    }
                )
            )
            
            logger.info(f"Clip processing task created for clip {clip_result['id']}")
            
        except Exception as e:
            logger.error(f"Error storing clip info: {e}")
    
    async def _queue_recording_processing(self):
        """Queue the recording file for AI processing"""
        if not self.recording_file or not os.path.exists(self.recording_file):
            return
        
        try:
            # Create video record in database
            from app.services.video_service import VideoService
            from app.models.video import VideoCreate, VideoSource
            
            video_service = VideoService(self.db)
            
            file_stats = os.stat(self.recording_file)
            video_data = VideoCreate(
                filename=os.path.basename(self.recording_file),
                original_filename=os.path.basename(self.recording_file),
                file_size=file_stats.st_size,
                format="mp4",
                source=VideoSource.TWITCH_STREAM,
                twitch_stream_id=self.stream_info.get('stream_id') if self.stream_info else None,
                twitch_title=self.stream_info.get('title') if self.stream_info else None,
                twitch_game=self.stream_info.get('game_name') if self.stream_info else None
            )
            
            video = await video_service.create_video(video_data, self.recording_file)
            
            # Queue for processing
            from app.tasks.video_tasks import process_video_full_pipeline
            process_video_full_pipeline.delay(video.id, {'source': 'twitch_stream'})
            
            logger.info(f"Recording queued for processing: {video.id}")
            
        except Exception as e:
            logger.error(f"Error queueing recording processing: {e}")
    
    async def _on_chat_message(self, message_data: Dict[str, Any]):
        """Handle incoming chat message"""
        # This can be used for real-time chat analysis
        # For now, the TwitchChatMonitor handles most analysis
        pass
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        runtime = None
        if self.stats['start_time']:
            runtime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
        chat_stats = {}
        if self.chat_monitor:
            chat_stats = self.chat_monitor.get_statistics()
        
        return {
            'integration_id': self.integration_id,
            'is_monitoring': self.is_monitoring,
            'runtime_seconds': runtime,
            'stream_info': self.stream_info,
            'is_recording': self.recording_process is not None,
            'recording_file': self.recording_file,
            'chat_highlights_count': len(self.stats['chat_highlights']),
            'auto_clips_created': self.stats['auto_clips_created'],
            'chat_stats': chat_stats
        }
