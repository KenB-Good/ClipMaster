
"""
AI processing background tasks
"""
import logging
from typing import Dict, Any, List
from celery import current_task

from app.tasks.celery_app import celery_app
from app.core.database import database
from app.ai.whisper_processor import WhisperProcessor
from app.ai.highlight_detector import HighlightDetector
from app.ai.video_processor import VideoProcessor

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def whisper_transcribe_task(self, audio_path: str, model_name: str = "base", language: str = None):
    """Transcribe audio using Whisper"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Loading Whisper model'})
        
        processor = WhisperProcessor(model_name=model_name)
        
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Transcribing audio'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            processor.transcribe(audio_path, language=language, include_timestamps=True)
        )
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Transcription completed'})
        
        return result
        
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def detect_highlights_ai_task(self, video_path: str, transcription: Dict[str, Any] = None, config: Dict[str, Any] = None):
    """Detect highlights using AI analysis"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Initializing highlight detection'})
        
        detector = HighlightDetector(config=config)
        
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Analyzing audio'})
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        highlights = loop.run_until_complete(
            detector.detect_highlights(video_path, transcription)
        )
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Highlight detection completed'})
        
        return {
            'highlights': highlights,
            'count': len(highlights),
            'video_path': video_path
        }
        
    except Exception as e:
        logger.error(f"Highlight detection failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def process_custom_prompt_task(self, video_path: str, transcription: Dict[str, Any], prompt: str):
    """Process video with custom prompt"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Processing custom prompt'})
        
        # This would integrate with an LLM to analyze the transcription based on the custom prompt
        # For now, implement a basic keyword-based approach
        
        keywords = self._extract_keywords_from_prompt(prompt)
        highlights = self._find_moments_with_keywords(transcription, keywords)
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Custom prompt processed'})
        
        return {
            'highlights': highlights,
            'prompt': prompt,
            'keywords': keywords
        }
        
    except Exception as e:
        logger.error(f"Custom prompt processing failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def generate_video_summary_task(self, video_path: str, transcription: Dict[str, Any], highlights: List[Dict[str, Any]]):
    """Generate video summary"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Generating summary'})
        
        # Extract key information
        duration = transcription.get('duration', 0)
        text_length = len(transcription.get('text', ''))
        highlight_count = len(highlights)
        
        # Basic summary generation
        summary = {
            'duration': duration,
            'text_length': text_length,
            'highlight_count': highlight_count,
            'key_moments': [h['description'] for h in highlights[:5]],  # Top 5 highlights
            'language': transcription.get('language', 'unknown'),
            'confidence_avg': sum(h.get('confidence', 0) for h in highlights) / max(len(highlights), 1)
        }
        
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Summary generated'})
        
        return summary
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def batch_ai_process_task(self, video_paths: List[str], config: Dict[str, Any] = None):
    """Process multiple videos with AI in batch"""
    results = []
    total_videos = len(video_paths)
    
    for i, video_path in enumerate(video_paths):
        try:
            progress = int((i / total_videos) * 100)
            self.update_state(
                state='PROGRESS', 
                meta={'progress': progress, 'status': f'Processing video {i+1}/{total_videos}'}
            )
            
            # Queue individual tasks
            transcribe_task = whisper_transcribe_task.delay(video_path)
            transcription = transcribe_task.get()
            
            highlights_task = detect_highlights_ai_task.delay(video_path, transcription, config)
            highlights = highlights_task.get()
            
            results.append({
                'video_path': video_path,
                'transcription': transcription,
                'highlights': highlights,
                'status': 'completed'
            })
            
        except Exception as e:
            logger.error(f"Batch processing failed for {video_path}: {e}")
            results.append({
                'video_path': video_path,
                'status': 'failed',
                'error': str(e)
            })
    
    self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Batch processing completed'})
    return results

# Helper functions

def _extract_keywords_from_prompt(prompt: str) -> List[str]:
    """Extract keywords from custom prompt"""
    # Simple keyword extraction - in production, use NLP libraries
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = prompt.lower().split()
    keywords = [word.strip('.,!?') for word in words if word not in stop_words and len(word) > 2]
    return keywords

def _find_moments_with_keywords(transcription: Dict[str, Any], keywords: List[str]) -> List[Dict[str, Any]]:
    """Find moments in transcription that match keywords"""
    highlights = []
    
    if 'segments' in transcription:
        for segment in transcription['segments']:
            text = segment['text'].lower()
            
            for keyword in keywords:
                if keyword in text:
                    highlights.append({
                        'start_time': segment['start'],
                        'end_time': segment['end'],
                        'confidence': 0.9,
                        'type': 'CUSTOM_PROMPT',
                        'description': f"Custom keyword match: {keyword}",
                        'metadata': {
                            'keyword': keyword,
                            'text': segment['text']
                        }
                    })
    
    return highlights
