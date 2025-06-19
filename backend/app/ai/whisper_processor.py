
"""
Whisper speech-to-text processor
"""
import os
import torch
import whisper
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class WhisperProcessor:
    def __init__(self, model_name: str = "base", device: str = "auto"):
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        
    async def load_model(self):
        """Load Whisper model"""
        if self.model is None:
            try:
                logger.info(f"Loading Whisper model '{self.model_name}' on {self.device}")
                self.model = whisper.load_model(self.model_name, device=self.device)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                raise
    
    async def transcribe(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        include_timestamps: bool = True
    ) -> Dict[str, Any]:
        """Transcribe audio file"""
        if self.model is None:
            await self.load_model()
        
        try:
            options = {
                "language": language,
                "task": "transcribe",
                "word_timestamps": include_timestamps
            }
            
            logger.info(f"Transcribing audio: {audio_path}")
            result = self.model.transcribe(audio_path, **options)
            
            # Process result to extract meaningful data
            processed_result = {
                "text": result["text"],
                "language": result["language"],
                "segments": []
            }
            
            if "segments" in result:
                for segment in result["segments"]:
                    processed_segment = {
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"],
                        "confidence": segment.get("avg_logprob", 0.0)
                    }
                    
                    # Add word-level timestamps if available
                    if "words" in segment:
                        processed_segment["words"] = [
                            {
                                "word": word["word"],
                                "start": word["start"],
                                "end": word["end"],
                                "confidence": word.get("probability", 0.0)
                            }
                            for word in segment["words"]
                        ]
                    
                    processed_result["segments"].append(processed_segment)
            
            return processed_result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    async def detect_language(self, audio_path: str) -> str:
        """Detect language of audio file"""
        if self.model is None:
            await self.load_model()
        
        try:
            # Load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect the spoken language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            
            logger.info(f"Detected language: {detected_language} (confidence: {probs[detected_language]:.2f})")
            return detected_language
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"  # Default to English
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper models"""
        return whisper.available_models()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if self.model is None:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_name": self.model_name,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "is_multilingual": self.model.is_multilingual
        }
