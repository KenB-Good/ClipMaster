
"""
Video processing pipeline with FFmpeg and MoviePy
"""
import os
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import ffmpeg
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.temp_dir = self.config.get("temp_dir", "/tmp")
        
    async def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Extract audio from video file"""
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.temp_dir, f"{base_name}_audio.wav")
        
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(quiet=True, capture_stdout=True)
            )
            
            logger.info(f"Audio extracted to: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Error extracting audio: {e.stderr.decode()}")
            raise

    async def create_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
        format_type: str = "horizontal"
    ) -> str:
        """Create a video clip from a segment"""
        try:
            duration = end_time - start_time
            
            # Base ffmpeg command
            input_stream = ffmpeg.input(video_path, ss=start_time, t=duration)
            
            # Apply format-specific processing
            if format_type == "vertical":
                # Convert to vertical format (9:16)
                output_stream = input_stream.filter('scale', 720, 1280, force_original_aspect_ratio='decrease')
                output_stream = output_stream.filter('pad', 720, 1280, -1, -1, color='black')
            elif format_type == "square":
                # Convert to square format (1:1)
                output_stream = input_stream.filter('scale', 1080, 1080, force_original_aspect_ratio='decrease')
                output_stream = output_stream.filter('pad', 1080, 1080, -1, -1, color='black')
            else:
                # Keep original horizontal format
                output_stream = input_stream
            
            # Output with optimized settings
            (
                output_stream
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    preset='fast',
                    crf=23
                )
                .overwrite_output()
                .run(quiet=True, capture_stdout=True)
            )
            
            logger.info(f"Clip created: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Error creating clip: {e.stderr.decode()}")
            raise

    async def add_subtitles(
        self,
        video_path: str,
        subtitles: List[Dict[str, Any]],
        output_path: str,
        style: Dict[str, Any] = None
    ) -> str:
        """Add subtitles to video"""
        try:
            # Create subtitle file
            srt_path = os.path.join(self.temp_dir, "subtitles.srt")
            await self._create_srt_file(subtitles, srt_path)
            
            # Default subtitle style
            default_style = {
                "fontsize": 24,
                "fontcolor": "white",
                "bordercolor": "black",
                "borderw": 2,
                "shadowcolor": "black",
                "shadowx": 1,
                "shadowy": 1
            }
            
            if style:
                default_style.update(style)
            
            # Create filter string for subtitles
            subtitle_filter = (
                f"subtitles={srt_path}:"
                f"force_style='Fontsize={default_style['fontsize']},"
                f"PrimaryColour=&H{self._color_to_hex(default_style['fontcolor'])},"
                f"OutlineColour=&H{self._color_to_hex(default_style['bordercolor'])},"
                f"Outline={default_style['borderw']},"
                f"Shadow={default_style['shadowx']}'"
            )
            
            (
                ffmpeg
                .input(video_path)
                .filter('subtitles', srt_path, **{
                    'force_style': (
                        f"Fontsize={default_style['fontsize']},"
                        f"PrimaryColour=&H{self._color_to_hex(default_style['fontcolor'])},"
                        f"OutlineColour=&H{self._color_to_hex(default_style['bordercolor'])},"
                        f"Outline={default_style['borderw']}"
                    )
                })
                .output(output_path, vcodec='libx264', acodec='copy')
                .overwrite_output()
                .run(quiet=True, capture_stdout=True)
            )
            
            # Clean up subtitle file
            if os.path.exists(srt_path):
                os.remove(srt_path)
            
            logger.info(f"Subtitles added to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding subtitles: {e}")
            raise

    async def add_overlay(
        self,
        video_path: str,
        overlay_config: Dict[str, Any],
        output_path: str
    ) -> str:
        """Add overlay elements to video"""
        try:
            with VideoFileClip(video_path) as video:
                clips = [video]
                
                # Add text overlays
                if "text_overlays" in overlay_config:
                    for text_config in overlay_config["text_overlays"]:
                        text_clip = self._create_text_overlay(text_config, video.duration)
                        clips.append(text_clip)
                
                # Add logo overlay
                if "logo" in overlay_config:
                    logo_clip = self._create_logo_overlay(overlay_config["logo"], video.duration)
                    if logo_clip:
                        clips.append(logo_clip)
                
                # Composite all clips
                final_video = CompositeVideoClip(clips)
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=os.path.join(self.temp_dir, "temp_audio.m4a"),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
            
            logger.info(f"Overlay added to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding overlay: {e}")
            raise

    async def optimize_for_platform(
        self,
        video_path: str,
        platform: str,
        output_path: str
    ) -> str:
        """Optimize video for specific platforms"""
        platform_configs = {
            "youtube": {
                "resolution": "1920x1080",
                "bitrate": "8000k",
                "fps": 30
            },
            "tiktok": {
                "resolution": "720x1280",
                "bitrate": "4000k",
                "fps": 30
            },
            "instagram": {
                "resolution": "1080x1080",
                "bitrate": "6000k",
                "fps": 30
            },
            "twitter": {
                "resolution": "1280x720",
                "bitrate": "5000k",
                "fps": 30
            }
        }
        
        config = platform_configs.get(platform.lower(), platform_configs["youtube"])
        
        try:
            width, height = map(int, config["resolution"].split("x"))
            
            (
                ffmpeg
                .input(video_path)
                .filter('scale', width, height, force_original_aspect_ratio='decrease')
                .filter('pad', width, height, -1, -1, color='black')
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    video_bitrate=config["bitrate"],
                    r=config["fps"],
                    preset='fast',
                    movflags='faststart'
                )
                .overwrite_output()
                .run(quiet=True, capture_stdout=True)
            )
            
            logger.info(f"Video optimized for {platform}: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Error optimizing video: {e.stderr.decode()}")
            raise

    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video file information"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            info = {
                "duration": float(probe['format']['duration']),
                "size": int(probe['format']['size']),
                "format": probe['format']['format_name']
            }
            
            if video_stream:
                info.update({
                    "width": int(video_stream['width']),
                    "height": int(video_stream['height']),
                    "fps": eval(video_stream['r_frame_rate']),
                    "video_codec": video_stream['codec_name']
                })
            
            if audio_stream:
                info.update({
                    "audio_codec": audio_stream['codec_name'],
                    "sample_rate": int(audio_stream['sample_rate']),
                    "channels": int(audio_stream['channels'])
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise

    async def create_thumbnail(
        self,
        video_path: str,
        timestamp: float,
        output_path: str,
        width: int = 320,
        height: int = 180
    ) -> str:
        """Create thumbnail from video at specific timestamp"""
        try:
            (
                ffmpeg
                .input(video_path, ss=timestamp)
                .filter('scale', width, height)
                .output(output_path, vframes=1, format='image2')
                .overwrite_output()
                .run(quiet=True, capture_stdout=True)
            )
            
            logger.info(f"Thumbnail created: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Error creating thumbnail: {e.stderr.decode()}")
            raise

    # Private helper methods
    
    async def _create_srt_file(self, subtitles: List[Dict[str, Any]], output_path: str):
        """Create SRT subtitle file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, subtitle in enumerate(subtitles, 1):
                start_time = self._seconds_to_srt_time(subtitle['start'])
                end_time = self._seconds_to_srt_time(subtitle['end'])
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle['text']}\n\n")

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def _color_to_hex(self, color: str) -> str:
        """Convert color name to hex"""
        color_map = {
            "white": "FFFFFF",
            "black": "000000",
            "red": "FF0000",
            "green": "00FF00",
            "blue": "0000FF",
            "yellow": "FFFF00"
        }
        
        return color_map.get(color.lower(), "FFFFFF")

    def _create_text_overlay(self, text_config: Dict[str, Any], duration: float):
        """Create text overlay clip"""
        return (
            TextClip(
                text_config['text'],
                fontsize=text_config.get('fontsize', 50),
                color=text_config.get('color', 'white'),
                font=text_config.get('font', 'Arial-Bold')
            )
            .set_position(text_config.get('position', ('center', 'bottom')))
            .set_duration(text_config.get('duration', duration))
            .set_start(text_config.get('start', 0))
        )

    def _create_logo_overlay(self, logo_config: Dict[str, Any], duration: float):
        """Create logo overlay clip"""
        try:
            from moviepy.editor import ImageClip
            
            logo_clip = (
                ImageClip(logo_config['path'])
                .set_duration(duration)
                .resize(height=logo_config.get('height', 50))
                .set_position(logo_config.get('position', ('right', 'top')))
                .set_opacity(logo_config.get('opacity', 0.8))
            )
            
            return logo_clip
            
        except Exception as e:
            logger.error(f"Error creating logo overlay: {e}")
            return None
