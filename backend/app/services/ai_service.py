
"""
AI service for video processing with Whisper and highlight detection
"""
import os
import torch
import whisper
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from databases import Database

from app.core.config import settings
from app.services.video_service import VideoService
from app.services.task_service import TaskService
from app.models.task import TaskType, TaskStatus, ProcessingTaskCreate, ProcessingTaskUpdate
from app.models.video import VideoUpdate, VideoStatus, HighlightType
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.whisper_model = None
        self.device = "cuda" if settings.ENABLE_GPU and torch.cuda.is_available() else "cpu"
        
    async def load_whisper_model(self):
        """Load Whisper model"""
        if self.whisper_model is None:
            try:
                logger.info(f"Loading Whisper model '{settings.WHISPER_MODEL}' on {self.device}")
                self.whisper_model = whisper.load_model(settings.WHISPER_MODEL, device=self.device)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise

    async def process_video(self, video_id: str, db: Database):
        """Main video processing pipeline"""
        video_service = VideoService(db)
        task_service = TaskService(db)
        
        try:
            # Update video status
            await video_service.update_video(
                video_id, 
                VideoUpdate(status=VideoStatus.PROCESSING)
            )
            
            # Create transcription task
            transcription_task = await task_service.create_task(
                ProcessingTaskCreate(
                    video_id=video_id,
                    type=TaskType.TRANSCRIPTION,
                    config={"model": settings.WHISPER_MODEL}
                )
            )
            
            # Perform transcription
            transcription = await self.transcribe_video(video_id, transcription_task.id, db)
            
            if transcription:
                # Update video with transcription
                await video_service.update_video(
                    video_id,
                    VideoUpdate(transcription=transcription)
                )
                
                # Create highlight detection task
                highlight_task = await task_service.create_task(
                    ProcessingTaskCreate(
                        video_id=video_id,
                        type=TaskType.HIGHLIGHT_DETECTION,
                        config={"confidence_threshold": settings.CONFIDENCE_THRESHOLD}
                    )
                )
                
                # Detect highlights
                highlights = await self.detect_highlights(video_id, highlight_task.id, db)
                
                # Create clip generation task
                if highlights:
                    clip_task = await task_service.create_task(
                        ProcessingTaskCreate(
                            video_id=video_id,
                            type=TaskType.CLIP_GENERATION,
                            config={"highlights": highlights}
                        )
                    )
                    
                    await self.generate_clips(video_id, clip_task.id, db)
            
            # Mark video as processed
            await video_service.update_video(
                video_id,
                VideoUpdate(
                    status=VideoStatus.PROCESSED,
                    processed_at=datetime.utcnow()
                )
            )
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            await video_service.update_video(
                video_id,
                VideoUpdate(status=VideoStatus.ERROR)
            )

    async def transcribe_video(self, video_id: str, task_id: str, db: Database) -> Optional[str]:
        """Transcribe video using Whisper"""
        video_service = VideoService(db)
        task_service = TaskService(db)
        
        try:
            # Update task status
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.RUNNING,
                    started_at=datetime.utcnow(),
                    progress=0.1
                )
            )
            
            # Get video info
            video = await video_service.get_video(video_id)
            if not video:
                raise ValueError("Video not found")
            
            # Load Whisper model
            await self.load_whisper_model()
            
            # Update progress
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(progress=0.3)
            )
            
            # Extract audio if needed
            audio_path = await self._extract_audio(video.file_path)
            
            # Update progress
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(progress=0.5)
            )
            
            # Transcribe
            logger.info(f"Transcribing video {video_id}")
            result = self.whisper_model.transcribe(audio_path)
            transcription = result["text"]
            
            # Update progress
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(progress=0.9)
            )
            
            # Clean up audio file if it was extracted
            if audio_path != video.file_path:
                os.remove(audio_path)
            
            # Complete task
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.COMPLETED,
                    progress=1.0,
                    result={"transcription": transcription, "language": result.get("language")},
                    completed_at=datetime.utcnow()
                )
            )
            
            logger.info(f"Transcription completed for video {video_id}")
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing video {video_id}: {e}")
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.FAILED,
                    error=str(e),
                    completed_at=datetime.utcnow()
                )
            )
            return None

    async def detect_highlights(self, video_id: str, task_id: str, db: Database) -> List[Dict[str, Any]]:
        """Detect highlights in video"""
        video_service = VideoService(db)
        task_service = TaskService(db)
        
        try:
            # Update task status
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.RUNNING,
                    started_at=datetime.utcnow(),
                    progress=0.1
                )
            )
            
            # Get video info
            video = await video_service.get_video(video_id)
            if not video:
                raise ValueError("Video not found")
            
            highlights = []
            
            # Audio-based highlight detection
            audio_highlights = await self._detect_audio_highlights(video.file_path)
            highlights.extend(audio_highlights)
            
            # Update progress
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(progress=0.4)
            )
            
            # Scene change detection
            scene_highlights = await self._detect_scene_changes(video.file_path)
            highlights.extend(scene_highlights)
            
            # Update progress
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(progress=0.6)
            )
            
            # Text-based highlight detection
            if video.transcription:
                text_highlights = await self._detect_text_highlights(video.transcription)
                highlights.extend(text_highlights)
            
            # Update progress
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(progress=0.8)
            )
            
            # Filter and merge overlapping highlights
            filtered_highlights = await self._filter_highlights(highlights)
            
            # Save highlights to database
            await self._save_highlights(video_id, filtered_highlights, db)
            
            # Complete task
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.COMPLETED,
                    progress=1.0,
                    result={"highlights_count": len(filtered_highlights)},
                    completed_at=datetime.utcnow()
                )
            )
            
            logger.info(f"Highlight detection completed for video {video_id}: {len(filtered_highlights)} highlights")
            return filtered_highlights
            
        except Exception as e:
            logger.error(f"Error detecting highlights for video {video_id}: {e}")
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.FAILED,
                    error=str(e),
                    completed_at=datetime.utcnow()
                )
            )
            return []

    async def generate_clips(self, video_id: str, task_id: str, db: Database):
        """Generate clips from highlights"""
        video_service = VideoService(db)
        task_service = TaskService(db)
        
        try:
            # Update task status
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.RUNNING,
                    started_at=datetime.utcnow(),
                    progress=0.1
                )
            )
            
            # Get video and highlights
            video = await video_service.get_video(video_id)
            highlights = await video_service.get_video_highlights(video_id)
            
            if not video or not highlights:
                raise ValueError("Video or highlights not found")
            
            clips_generated = 0
            total_highlights = len(highlights)
            
            for i, highlight in enumerate(highlights):
                try:
                    # Generate clip for this highlight
                    clip_path = await self._generate_clip(
                        video.file_path,
                        highlight.start_time,
                        highlight.end_time,
                        video_id,
                        highlight.id
                    )
                    
                    if clip_path:
                        # Save clip to database
                        await self._save_clip(video_id, highlight.id, clip_path, db)
                        clips_generated += 1
                    
                    # Update progress
                    progress = 0.1 + (0.8 * (i + 1) / total_highlights)
                    await task_service.update_task(
                        task_id,
                        ProcessingTaskUpdate(progress=progress)
                    )
                    
                except Exception as e:
                    logger.error(f"Error generating clip for highlight {highlight.id}: {e}")
            
            # Complete task
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.COMPLETED,
                    progress=1.0,
                    result={"clips_generated": clips_generated},
                    completed_at=datetime.utcnow()
                )
            )
            
            logger.info(f"Clip generation completed for video {video_id}: {clips_generated} clips")
            
        except Exception as e:
            logger.error(f"Error generating clips for video {video_id}: {e}")
            await task_service.update_task(
                task_id,
                ProcessingTaskUpdate(
                    status=TaskStatus.FAILED,
                    error=str(e),
                    completed_at=datetime.utcnow()
                )
            )

    async def test_services(self) -> Dict[str, Any]:
        """Test AI service availability"""
        results = {
            "whisper": {"available": False},
            "torch": {"available": False},
            "cuda": {"available": False},
            "opencv": {"available": False}
        }
        
        # Test Torch
        try:
            import torch
            results["torch"] = {
                "available": True,
                "version": torch.__version__
            }
            
            # Test CUDA
            if torch.cuda.is_available():
                results["cuda"] = {
                    "available": True,
                    "device_count": torch.cuda.device_count(),
                    "current_device": torch.cuda.current_device()
                }
        except Exception as e:
            results["torch"]["error"] = str(e)
        
        # Test Whisper
        try:
            import whisper
            results["whisper"] = {
                "available": True,
                "available_models": whisper.available_models()
            }
        except Exception as e:
            results["whisper"]["error"] = str(e)
        
        # Test OpenCV
        try:
            import cv2
            results["opencv"] = {
                "available": True,
                "version": cv2.__version__
            }
        except Exception as e:
            results["opencv"]["error"] = str(e)
        
        return results

    # Private helper methods
    
    async def _extract_audio(self, video_path: str) -> str:
        """Extract audio from video file"""
        try:
            import ffmpeg
            
            # Create temporary audio file
            audio_path = os.path.join(settings.TEMP_DIR, f"audio_{os.path.basename(video_path)}.wav")
            
            # Extract audio using ffmpeg
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return audio_path
            
        except Exception as e:
            logger.warning(f"Could not extract audio, using original file: {e}")
            return video_path

    async def _detect_audio_highlights(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect highlights based on audio analysis"""
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(video_path, sr=None)
            
            # Detect audio spikes (loud moments)
            rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
            
            # Find peaks (potential highlights)
            threshold = np.percentile(rms, 85)  # Top 15% of audio levels
            peaks = np.where(rms > threshold)[0]
            
            highlights = []
            
            # Group consecutive peaks into segments
            if len(peaks) > 0:
                segments = []
                current_segment = [peaks[0]]
                
                for peak in peaks[1:]:
                    if peak - current_segment[-1] <= sr // 512:  # Within 1 second
                        current_segment.append(peak)
                    else:
                        segments.append(current_segment)
                        current_segment = [peak]
                
                segments.append(current_segment)
                
                # Convert segments to highlights
                for segment in segments:
                    start_time = max(0, times[segment[0]] - 2)  # 2 seconds before
                    end_time = min(len(y) / sr, times[segment[-1]] + 2)  # 2 seconds after
                    
                    if end_time - start_time >= settings.MIN_HIGHLIGHT_DURATION:
                        highlights.append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "confidence": min(np.mean(rms[segment]) / threshold, 1.0),
                            "type": HighlightType.EMOTIONAL_REACTION,
                            "description": "Audio spike detected"
                        })
            
            return highlights
            
        except Exception as e:
            logger.error(f"Error in audio highlight detection: {e}")
            return []

    async def _detect_scene_changes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scene changes in video"""
        try:
            import cv2
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            
            # Sample frames for scene change detection
            sample_interval = max(1, int(fps))  # Sample every second
            
            prev_frame = None
            scene_changes = []
            
            for i in range(0, int(frame_count), sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Convert to grayscale and calculate histogram
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                
                if prev_frame is not None:
                    # Calculate histogram difference
                    diff = cv2.compareHist(prev_frame, hist, cv2.HISTCMP_CORREL)
                    
                    # If correlation is low, it's a scene change
                    if diff < 0.7:  # Threshold for scene change
                        timestamp = i / fps
                        scene_changes.append({
                            "start_time": max(0, timestamp - 5),
                            "end_time": min(frame_count / fps, timestamp + 10),
                            "confidence": 1.0 - diff,
                            "type": HighlightType.CONTENT_PEAK,
                            "description": "Scene change detected"
                        })
                
                prev_frame = hist
            
            cap.release()
            return scene_changes
            
        except Exception as e:
            logger.error(f"Error in scene change detection: {e}")
            return []

    async def _detect_text_highlights(self, transcription: str) -> List[Dict[str, Any]]:
        """Detect highlights based on transcription text"""
        highlights = []
        
        # Keywords that might indicate exciting moments
        excitement_keywords = [
            "wow", "amazing", "incredible", "unbelievable", "insane",
            "clip that", "did you see", "no way", "holy", "omg",
            "sick", "crazy", "nuts", "epic", "legendary"
        ]
        
        # Split transcription into segments (this is simplified)
        # In a real implementation, you'd use the timestamp data from Whisper
        words = transcription.lower().split()
        
        for i, word in enumerate(words):
            if any(keyword in word for keyword in excitement_keywords):
                # Create highlight around this word
                # This is a simplified approach - you'd need proper timing from Whisper
                start_time = max(0, i * 0.5)  # Rough estimate
                end_time = min(len(words) * 0.5, start_time + 15)
                
                highlights.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "confidence": 0.8,
                    "type": HighlightType.CLIP_THAT_MOMENT,
                    "description": f"Exciting moment: {word}"
                })
        
        return highlights

    async def _filter_highlights(self, highlights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and merge overlapping highlights"""
        if not highlights:
            return []
        
        # Sort by start time
        highlights.sort(key=lambda x: x["start_time"])
        
        # Merge overlapping highlights
        merged = []
        current = highlights[0].copy()
        
        for highlight in highlights[1:]:
            if highlight["start_time"] <= current["end_time"]:
                # Overlapping - merge
                current["end_time"] = max(current["end_time"], highlight["end_time"])
                current["confidence"] = max(current["confidence"], highlight["confidence"])
            else:
                # No overlap - add current and start new
                if current["end_time"] - current["start_time"] >= settings.MIN_HIGHLIGHT_DURATION:
                    merged.append(current)
                current = highlight.copy()
        
        # Add last highlight
        if current["end_time"] - current["start_time"] >= settings.MIN_HIGHLIGHT_DURATION:
            merged.append(current)
        
        # Filter by confidence threshold
        filtered = [h for h in merged if h["confidence"] >= settings.CONFIDENCE_THRESHOLD]
        
        return filtered

    async def _save_highlights(self, video_id: str, highlights: List[Dict[str, Any]], db: Database):
        """Save highlights to database"""
        for highlight_data in highlights:
            query = """
            INSERT INTO highlights (id, video_id, start_time, end_time, confidence, type, description, created_at)
            VALUES (:id, :video_id, :start_time, :end_time, :confidence, :type, :description, :created_at)
            """
            
            import uuid
            values = {
                "id": str(uuid.uuid4()),
                "video_id": video_id,
                "start_time": highlight_data["start_time"],
                "end_time": highlight_data["end_time"],
                "confidence": highlight_data["confidence"],
                "type": highlight_data["type"],
                "description": highlight_data.get("description"),
                "created_at": datetime.utcnow()
            }
            
            await db.execute(query, values)

    async def _generate_clip(
        self, 
        video_path: str, 
        start_time: float, 
        end_time: float, 
        video_id: str, 
        highlight_id: str
    ) -> Optional[str]:
        """Generate a video clip from highlight"""
        try:
            import ffmpeg
            
            # Create output path
            clip_filename = f"clip_{video_id}_{highlight_id}.mp4"
            clip_path = os.path.join(settings.CLIPS_DIR, clip_filename)
            
            # Generate clip using ffmpeg
            duration = end_time - start_time
            
            (
                ffmpeg
                .input(video_path, ss=start_time, t=duration)
                .output(clip_path, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return clip_path
            
        except Exception as e:
            logger.error(f"Error generating clip: {e}")
            return None

    async def _save_clip(self, video_id: str, highlight_id: str, clip_path: str, db: Database):
        """Save clip information to database"""
        try:
            # Get file info
            file_stats = os.stat(clip_path)
            
            # Get video duration (simplified)
            import cv2
            cap = cv2.VideoCapture(clip_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            query = """
            INSERT INTO clips (id, video_id, highlight_id, filename, file_path, file_size, 
                              duration, start_time, end_time, format, created_at)
            VALUES (:id, :video_id, :highlight_id, :filename, :file_path, :file_size,
                    :duration, :start_time, :end_time, :format, :created_at)
            """
            
            import uuid
            values = {
                "id": str(uuid.uuid4()),
                "video_id": video_id,
                "highlight_id": highlight_id,
                "filename": os.path.basename(clip_path),
                "file_path": clip_path,
                "file_size": file_stats.st_size,
                "duration": duration,
                "start_time": 0,  # Relative to clip
                "end_time": duration,
                "format": "HORIZONTAL",  # Default format
                "created_at": datetime.utcnow()
            }
            
            await db.execute(query, values)
            
        except Exception as e:
            logger.error(f"Error saving clip to database: {e}")
