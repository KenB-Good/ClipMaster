
"""
Highlight detection using multiple analysis methods
"""
import numpy as np
import cv2
import librosa
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class HighlightType(Enum):
    AUDIO_SPIKE = "audio_spike"
    SCENE_CHANGE = "scene_change"
    MOTION_PEAK = "motion_peak"
    TEXT_KEYWORD = "text_keyword"
    SILENCE_BREAK = "silence_break"

class HighlightDetector:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.min_duration = self.config.get("min_duration", 5)
        self.max_duration = self.config.get("max_duration", 120)
        
    async def detect_highlights(
        self, 
        video_path: str, 
        transcription: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Main highlight detection method"""
        all_highlights = []
        
        try:
            # Audio-based detection
            audio_highlights = await self.detect_audio_highlights(video_path)
            all_highlights.extend(audio_highlights)
            
            # Visual-based detection
            visual_highlights = await self.detect_visual_highlights(video_path)
            all_highlights.extend(visual_highlights)
            
            # Text-based detection
            if transcription:
                text_highlights = await self.detect_text_highlights(transcription)
                all_highlights.extend(text_highlights)
            
            # Filter and merge highlights
            filtered_highlights = self._filter_and_merge_highlights(all_highlights)
            
            logger.info(f"Detected {len(filtered_highlights)} highlights from {len(all_highlights)} candidates")
            return filtered_highlights
            
        except Exception as e:
            logger.error(f"Error in highlight detection: {e}")
            return []
    
    async def detect_audio_highlights(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect highlights based on audio analysis"""
        highlights = []
        
        try:
            # Load audio
            y, sr = librosa.load(video_path, sr=22050)
            
            # Audio spike detection
            spike_highlights = await self._detect_audio_spikes(y, sr)
            highlights.extend(spike_highlights)
            
            # Silence break detection
            silence_highlights = await self._detect_silence_breaks(y, sr)
            highlights.extend(silence_highlights)
            
            # Energy variation detection
            energy_highlights = await self._detect_energy_variations(y, sr)
            highlights.extend(energy_highlights)
            
        except Exception as e:
            logger.error(f"Error in audio highlight detection: {e}")
        
        return highlights
    
    async def detect_visual_highlights(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect highlights based on visual analysis"""
        highlights = []
        
        try:
            # Scene change detection
            scene_highlights = await self._detect_scene_changes(video_path)
            highlights.extend(scene_highlights)
            
            # Motion detection
            motion_highlights = await self._detect_motion_peaks(video_path)
            highlights.extend(motion_highlights)
            
        except Exception as e:
            logger.error(f"Error in visual highlight detection: {e}")
        
        return highlights
    
    async def detect_text_highlights(self, transcription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect highlights based on transcription content"""
        highlights = []
        
        try:
            # Keyword-based detection
            keyword_highlights = await self._detect_keyword_highlights(transcription)
            highlights.extend(keyword_highlights)
            
            # Emotion-based detection
            emotion_highlights = await self._detect_emotional_moments(transcription)
            highlights.extend(emotion_highlights)
            
        except Exception as e:
            logger.error(f"Error in text highlight detection: {e}")
        
        return highlights
    
    # Private helper methods
    
    async def _detect_audio_spikes(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Detect audio spikes (sudden loud moments)"""
        highlights = []
        
        # Calculate RMS energy
        frame_length = 2048
        hop_length = 512
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
        
        # Find spikes
        threshold = np.percentile(rms, 90)  # Top 10%
        spike_indices = np.where(rms > threshold)[0]
        
        if len(spike_indices) > 0:
            # Group consecutive spikes
            groups = self._group_consecutive_indices(spike_indices)
            
            for group in groups:
                start_time = max(0, times[group[0]] - 2)
                end_time = min(times[-1], times[group[-1]] + 3)
                confidence = min(np.mean(rms[group]) / threshold, 1.0)
                
                if end_time - start_time >= self.min_duration:
                    highlights.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "confidence": confidence,
                        "type": HighlightType.AUDIO_SPIKE.value,
                        "description": "Audio spike detected"
                    })
        
        return highlights
    
    async def _detect_silence_breaks(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Detect moments when silence is broken"""
        highlights = []
        
        # Split audio by silence
        intervals = librosa.effects.split(y, top_db=20)
        
        for start_sample, end_sample in intervals:
            start_time = start_sample / sr
            end_time = end_sample / sr
            duration = end_time - start_time
            
            if duration >= self.min_duration and duration <= self.max_duration:
                # Check if this follows a period of silence
                silence_before = start_time > 2  # At least 2 seconds of audio before
                
                if silence_before:
                    highlights.append({
                        "start_time": max(0, start_time - 1),
                        "end_time": min(end_time + 1, len(y) / sr),
                        "confidence": 0.8,
                        "type": HighlightType.SILENCE_BREAK.value,
                        "description": "Activity after silence"
                    })
        
        return highlights
    
    async def _detect_energy_variations(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Detect significant energy variations"""
        highlights = []
        
        # Calculate spectral centroid (brightness)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        times = librosa.frames_to_time(np.arange(len(spectral_centroids)), sr=sr)
        
        # Find significant changes in brightness
        centroid_diff = np.diff(spectral_centroids)
        threshold = np.std(centroid_diff) * 2
        
        change_indices = np.where(np.abs(centroid_diff) > threshold)[0]
        
        if len(change_indices) > 0:
            groups = self._group_consecutive_indices(change_indices, max_gap=sr//512)
            
            for group in groups:
                start_time = max(0, times[group[0]] - 2)
                end_time = min(times[-1], times[group[-1]] + 5)
                confidence = min(np.mean(np.abs(centroid_diff[group])) / threshold, 1.0)
                
                if end_time - start_time >= self.min_duration:
                    highlights.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "confidence": confidence,
                        "type": HighlightType.MOTION_PEAK.value,
                        "description": "Audio texture change"
                    })
        
        return highlights
    
    async def _detect_scene_changes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scene changes in video"""
        highlights = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return highlights
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        # Sample frames
        sample_interval = max(1, int(fps * 0.5))  # Every 0.5 seconds
        prev_hist = None
        
        for i in range(0, int(frame_count), sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Calculate histogram
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            if prev_hist is not None:
                # Calculate correlation
                correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                
                if correlation < 0.7:  # Scene change threshold
                    timestamp = i / fps
                    highlights.append({
                        "start_time": max(0, timestamp - 3),
                        "end_time": min(frame_count / fps, timestamp + 7),
                        "confidence": 1.0 - correlation,
                        "type": HighlightType.SCENE_CHANGE.value,
                        "description": f"Scene change (correlation: {correlation:.2f})"
                    })
            
            prev_hist = hist
        
        cap.release()
        return highlights
    
    async def _detect_motion_peaks(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect motion peaks in video"""
        highlights = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return highlights
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Background subtractor for motion detection
        backSub = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        motion_values = []
        timestamps = []
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply background subtraction
            fgMask = backSub.apply(frame)
            
            # Calculate motion amount
            motion_amount = np.sum(fgMask == 255)
            motion_values.append(motion_amount)
            timestamps.append(frame_count / fps)
            
            frame_count += 1
            
            # Sample every few frames for performance
            if frame_count % 5 != 0:
                continue
        
        cap.release()
        
        if motion_values:
            # Find motion peaks
            motion_array = np.array(motion_values)
            threshold = np.percentile(motion_array, 85)
            
            peak_indices = np.where(motion_array > threshold)[0]
            
            if len(peak_indices) > 0:
                groups = self._group_consecutive_indices(peak_indices, max_gap=fps//5)
                
                for group in groups:
                    start_time = max(0, timestamps[group[0]] - 2)
                    end_time = min(timestamps[-1], timestamps[group[-1]] + 3)
                    confidence = min(np.mean(motion_array[group]) / threshold, 1.0)
                    
                    if end_time - start_time >= self.min_duration:
                        highlights.append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "confidence": confidence,
                            "type": HighlightType.MOTION_PEAK.value,
                            "description": "High motion detected"
                        })
        
        return highlights
    
    async def _detect_keyword_highlights(self, transcription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect highlights based on keywords in transcription"""
        highlights = []
        
        # Define keyword categories
        excitement_keywords = [
            "wow", "amazing", "incredible", "unbelievable", "insane", "crazy",
            "clip that", "did you see", "no way", "holy", "omg", "sick",
            "nuts", "epic", "legendary", "perfect", "beautiful", "awesome"
        ]
        
        gaming_keywords = [
            "headshot", "ace", "clutch", "pentakill", "victory", "win",
            "kill", "elimination", "boss", "rare", "loot", "achievement"
        ]
        
        reaction_keywords = [
            "laugh", "scream", "excited", "shocked", "surprised", "funny",
            "hilarious", "reaction", "emotional", "tears", "crying"
        ]
        
        all_keywords = {
            "excitement": excitement_keywords,
            "gaming": gaming_keywords,
            "reaction": reaction_keywords
        }
        
        # Search in transcription segments
        if "segments" in transcription:
            for segment in transcription["segments"]:
                text = segment["text"].lower()
                start_time = segment["start"]
                end_time = segment["end"]
                
                for category, keywords in all_keywords.items():
                    for keyword in keywords:
                        if keyword in text:
                            # Extend the highlight around the keyword
                            highlight_start = max(0, start_time - 3)
                            highlight_end = min(end_time + 5, transcription.get("duration", end_time + 5))
                            
                            highlights.append({
                                "start_time": highlight_start,
                                "end_time": highlight_end,
                                "confidence": 0.9,
                                "type": HighlightType.TEXT_KEYWORD.value,
                                "description": f"Keyword detected: {keyword} ({category})",
                                "metadata": {
                                    "keyword": keyword,
                                    "category": category,
                                    "text": segment["text"]
                                }
                            })
        
        return highlights
    
    async def _detect_emotional_moments(self, transcription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect emotional moments based on transcription patterns"""
        highlights = []
        
        # Look for patterns that indicate emotional moments
        emotional_patterns = [
            r'\b(ha+h+a+|he+h+e+)\b',  # Laughter
            r'\b(oh+|ah+|uh+)\b',       # Exclamations
            r'[!]{2,}',                  # Multiple exclamation marks
            r'[A-Z]{3,}',               # ALL CAPS words
            r'\b(yes+|no+o+)\b'         # Extended yes/no
        ]
        
        if "segments" in transcription:
            import re
            
            for segment in transcription["segments"]:
                text = segment["text"]
                
                for pattern in emotional_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        start_time = max(0, segment["start"] - 2)
                        end_time = min(segment["end"] + 3, transcription.get("duration", segment["end"] + 3))
                        
                        highlights.append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "confidence": 0.8,
                            "type": HighlightType.TEXT_KEYWORD.value,
                            "description": f"Emotional moment detected: {matches[0]}",
                            "metadata": {
                                "pattern": pattern,
                                "matches": matches,
                                "text": segment["text"]
                            }
                        })
        
        return highlights
    
    def _group_consecutive_indices(self, indices: np.ndarray, max_gap: int = 1) -> List[List[int]]:
        """Group consecutive indices together"""
        if len(indices) == 0:
            return []
        
        groups = []
        current_group = [indices[0]]
        
        for i in range(1, len(indices)):
            if indices[i] - current_group[-1] <= max_gap:
                current_group.append(indices[i])
            else:
                groups.append(current_group)
                current_group = [indices[i]]
        
        groups.append(current_group)
        return groups
    
    def _filter_and_merge_highlights(self, highlights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and merge overlapping highlights"""
        if not highlights:
            return []
        
        # Sort by start time
        sorted_highlights = sorted(highlights, key=lambda x: x["start_time"])
        
        # Merge overlapping highlights
        merged = []
        current = sorted_highlights[0].copy()
        
        for highlight in sorted_highlights[1:]:
            if highlight["start_time"] <= current["end_time"] + 2:  # 2-second tolerance
                # Merge highlights
                current["end_time"] = max(current["end_time"], highlight["end_time"])
                current["confidence"] = max(current["confidence"], highlight["confidence"])
                
                # Combine descriptions
                if current["description"] != highlight["description"]:
                    current["description"] += f"; {highlight['description']}"
            else:
                # No overlap - add current and start new
                if (current["end_time"] - current["start_time"] >= self.min_duration and
                    current["confidence"] >= self.confidence_threshold):
                    merged.append(current)
                current = highlight.copy()
        
        # Add last highlight
        if (current["end_time"] - current["start_time"] >= self.min_duration and
            current["confidence"] >= self.confidence_threshold):
            merged.append(current)
        
        return merged
