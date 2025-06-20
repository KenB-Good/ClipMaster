"""
Video processing utilities for ClipMaster
Handles video analysis, frame extraction, and metadata processing
"""
import os
import ast
import json
import logging
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import cv2
import numpy as np
import ffmpeg
from moviepy.editor import VideoFileClip
import torch
import whisper
from PIL import Image

from ..core.config import settings
from ..models.video import VideoMetadata, ProcessingStatus

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Main video processing class"""

    def __init__(self):
        self.whisper_model = None
        self.device = "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu"

    def load_whisper_model(self):
        """Load Whisper model for audio transcription"""
        if self.whisper_model is None:
            try:
                self.whisper_model = whisper.load_model(
                    settings.WHISPER_MODEL, device=self.device
                )
                logger.info(
                    f"Loaded Whisper model: {settings.WHISPER_MODEL} on {self.device}"
                )
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Extract video metadata using ffprobe
        Fixed: Replaced eval() with ast.literal_eval for security
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "video"
                ),
                None,
            )
            audio_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "audio"
                ),
                None,
            )

            info = {
                "duration": float(probe["format"]["duration"]),
                "size": int(probe["format"]["size"]),
                "format": probe["format"]["format_name"],
            }

            if video_stream:
                # SECURITY FIX: Replace eval() with safe fraction parsing
                fps_str = video_stream.get("r_frame_rate", "0/1")
                try:
                    # Parse fraction safely
                    if "/" in fps_str:
                        numerator, denominator = fps_str.split("/")
                        fps = (
                            float(numerator) / float(denominator)
                            if float(denominator) != 0
                            else 0
                        )
                    else:
                        fps = float(fps_str)
                except (ValueError, ZeroDivisionError):
                    fps = 0
                    logger.warning(f"Could not parse frame rate: {fps_str}")

                info.update(
                    {
                        "width": int(video_stream["width"]),
                        "height": int(video_stream["height"]),
                        "fps": fps,
                        "video_codec": video_stream["codec_name"],
                    }
                )

            if audio_stream:
                info.update(
                    {
                        "audio_codec": audio_stream["codec_name"],
                        "sample_rate": int(audio_stream.get("sample_rate", 0)),
                        "channels": int(audio_stream.get("channels", 0)),
                    }
                )

            return info

        except Exception as e:
            logger.error(f"Error getting video info for {video_path}: {e}")
            raise

    def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio from video file"""
        try:
            (
                ffmpeg.input(video_path)
                .output(output_path, acodec="pcm_s16le", ac=1, ar="16k")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"Error extracting audio: {e.stderr.decode()}")
            raise

    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        self.load_whisper_model()

        try:
            result = self.whisper_model.transcribe(audio_path)
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result["language"],
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    def extract_frames(
        self, video_path: str, timestamps: List[float], output_dir: str
    ) -> List[str]:
        """Extract frames at specific timestamps"""
        frame_paths = []

        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)

            for i, timestamp in enumerate(timestamps):
                frame_number = int(timestamp * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

                ret, frame = cap.read()
                if ret:
                    frame_path = os.path.join(output_dir, f"frame_{i:04d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frame_paths.append(frame_path)
                else:
                    logger.warning(f"Could not extract frame at {timestamp}s")

            cap.release()
            return frame_paths

        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            raise

    def create_clip(
        self, video_path: str, start_time: float, end_time: float, output_path: str
    ) -> str:
        """Create video clip from start to end time"""
        try:
            (
                ffmpeg.input(video_path, ss=start_time, t=end_time - start_time)
                .output(output_path, vcodec="libx264", acodec="aac")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"Error creating clip: {e.stderr.decode()}")
            raise

    def detect_highlights(
        self, transcription: Dict[str, Any], custom_prompts: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect highlights in transcription using AI analysis
        """
        highlights = []
        segments = transcription.get("segments", [])

        # Default highlight keywords
        default_keywords = [
            "amazing",
            "incredible",
            "wow",
            "unbelievable",
            "perfect",
            "clutch",
            "insane",
            "epic",
            "legendary",
            "godlike",
        ]

        keywords = custom_prompts if custom_prompts else default_keywords

        for segment in segments:
            text = segment["text"].lower()
            confidence = 0.0

            # Simple keyword matching (can be enhanced with ML)
            for keyword in keywords:
                if keyword.lower() in text:
                    confidence += 0.3

            # Check for excitement indicators
            if "!" in segment["text"] or segment["text"].isupper():
                confidence += 0.2

            if confidence >= settings.CONFIDENCE_THRESHOLD:
                highlights.append(
                    {
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"],
                        "confidence": min(confidence, 1.0),
                    }
                )

        return highlights

    def process_video(self, video_path: str, user_id: int) -> Dict[str, Any]:
        """
        Main video processing pipeline
        """
        try:
            # Get video metadata
            video_info = self.get_video_info(video_path)

            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract audio
                audio_path = os.path.join(temp_dir, "audio.wav")
                self.extract_audio(video_path, audio_path)

                # Transcribe audio
                transcription = self.transcribe_audio(audio_path)

                # Detect highlights
                highlights = self.detect_highlights(transcription)

                # Create clips for highlights
                clips = []
                for i, highlight in enumerate(highlights):
                    clip_path = os.path.join(
                        settings.CLIPS_DIR,
                        f"clip_{user_id}_{i}_{int(highlight['start'])}.mp4",
                    )

                    self.create_clip(
                        video_path,
                        max(0, highlight["start"] - 2),  # Add 2s buffer
                        min(video_info["duration"], highlight["end"] + 2),
                        clip_path,
                    )

                    clips.append(
                        {
                            "path": clip_path,
                            "start": highlight["start"],
                            "end": highlight["end"],
                            "confidence": highlight["confidence"],
                            "text": highlight["text"],
                        }
                    )

            return {
                "video_info": video_info,
                "transcription": transcription,
                "highlights": highlights,
                "clips": clips,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            return {"status": "failed", "error": str(e)}
