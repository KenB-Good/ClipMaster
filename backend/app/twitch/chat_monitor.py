
"""
Twitch chat monitoring for highlight detection
"""
import asyncio
import json
import websockets
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TwitchChatMonitor:
    def __init__(self, channel: str, on_message_callback: Optional[Callable] = None):
        self.channel = channel.lower()
        self.on_message_callback = on_message_callback
        self.websocket = None
        self.is_connected = False
        self.is_monitoring = False
        
        # Chat analysis
        self.message_buffer = []
        self.excitement_keywords = [
            'clip', 'poggers', 'pog', 'omg', 'wow', 'insane', 'crazy',
            'unbelievable', 'sick', 'nuts', 'epic', 'legendary',
            'wtf', 'no way', 'holy', 'amazing', 'incredible', 'gg',
            'ez', 'rip', 'kappa', 'lul', 'pepehands', 'monkas'
        ]
        
        # Statistics
        self.stats = {
            'total_messages': 0,
            'unique_users': set(),
            'excitement_moments': [],
            'message_rate': 0,
            'start_time': None
        }
    
    async def connect(self):
        """Connect to Twitch IRC chat"""
        try:
            self.websocket = await websockets.connect("wss://irc-ws.chat.twitch.tv:443")
            self.is_connected = True
            
            # Send authentication (anonymous)
            await self.websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
            await self.websocket.send("PASS SCHMOOPIIE")  # Anonymous login
            await self.websocket.send("NICK justinfan12345")  # Anonymous username
            await self.websocket.send(f"JOIN #{self.channel}")
            
            logger.info(f"Connected to chat for channel: {self.channel}")
            
        except Exception as e:
            logger.error(f"Failed to connect to chat: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from chat"""
        self.is_monitoring = False
        if self.websocket:
            await self.websocket.close()
        self.is_connected = False
        logger.info(f"Disconnected from chat for channel: {self.channel}")
    
    async def start_monitoring(self, duration_minutes: Optional[int] = None):
        """Start monitoring chat messages"""
        if not self.is_connected:
            await self.connect()
        
        self.is_monitoring = True
        self.stats['start_time'] = datetime.utcnow()
        
        logger.info(f"Started monitoring chat for {self.channel}")
        
        try:
            if duration_minutes:
                # Monitor for specific duration
                await asyncio.wait_for(
                    self._message_loop(),
                    timeout=duration_minutes * 60
                )
            else:
                # Monitor indefinitely
                await self._message_loop()
                
        except asyncio.TimeoutError:
            logger.info(f"Chat monitoring completed after {duration_minutes} minutes")
        except Exception as e:
            logger.error(f"Error during chat monitoring: {e}")
        finally:
            self.is_monitoring = False
    
    async def _message_loop(self):
        """Main message processing loop"""
        try:
            while self.is_monitoring and self.is_connected:
                message = await self.websocket.recv()
                await self._process_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Chat connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in message loop: {e}")
            raise
    
    async def _process_message(self, raw_message: str):
        """Process incoming chat message"""
        try:
            # Handle PING messages
            if raw_message.startswith('PING'):
                await self.websocket.send('PONG :tmi.twitch.tv')
                return
            
            # Parse IRC message
            message_data = self._parse_irc_message(raw_message)
            if not message_data:
                return
            
            # Update statistics
            self.stats['total_messages'] += 1
            if message_data.get('username'):
                self.stats['unique_users'].add(message_data['username'])
            
            # Add to message buffer
            self.message_buffer.append({
                'timestamp': datetime.utcnow(),
                'username': message_data.get('username'),
                'message': message_data.get('message', ''),
                'badges': message_data.get('badges', {}),
                'emotes': message_data.get('emotes', {}),
                'user_type': message_data.get('user_type', '')
            })
            
            # Keep buffer size manageable
            if len(self.message_buffer) > 1000:
                self.message_buffer = self.message_buffer[-800:]  # Keep last 800 messages
            
            # Analyze for excitement
            await self._analyze_excitement(message_data)
            
            # Call external callback if provided
            if self.on_message_callback:
                await self.on_message_callback(message_data)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _parse_irc_message(self, raw_message: str) -> Optional[Dict[str, Any]]:
        """Parse IRC message format"""
        try:
            # Skip non-PRIVMSG messages
            if 'PRIVMSG' not in raw_message:
                return None
            
            parts = raw_message.split(' ')
            
            # Extract tags (if present)
            tags = {}
            if raw_message.startswith('@'):
                tag_part = parts[0][1:]  # Remove @
                for tag in tag_part.split(';'):
                    if '=' in tag:
                        key, value = tag.split('=', 1)
                        tags[key] = value
            
            # Extract username and message
            username = None
            message = ""
            
            for i, part in enumerate(parts):
                if part.startswith(':') and '!' in part:
                    username = part[1:].split('!')[0]
                elif part == 'PRIVMSG':
                    # Message starts after PRIVMSG #channel
                    if i + 2 < len(parts):
                        message_parts = parts[i + 2:]
                        message = ' '.join(message_parts)
                        if message.startswith(':'):
                            message = message[1:]
                    break
            
            if not username or not message:
                return None
            
            # Parse useful tags
            badges = {}
            if 'badges' in tags and tags['badges']:
                for badge in tags['badges'].split(','):
                    if '/' in badge:
                        badge_name, badge_level = badge.split('/', 1)
                        badges[badge_name] = badge_level
            
            emotes = {}
            if 'emotes' in tags and tags['emotes']:
                # Parse emote positions (simplified)
                emotes = {'raw': tags['emotes']}
            
            return {
                'username': username,
                'message': message,
                'badges': badges,
                'emotes': emotes,
                'user_type': tags.get('user-type', ''),
                'color': tags.get('color', ''),
                'display_name': tags.get('display-name', username),
                'user_id': tags.get('user-id', ''),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error parsing IRC message: {e}")
            return None
    
    async def _analyze_excitement(self, message_data: Dict[str, Any]):
        """Analyze message for excitement indicators"""
        message_text = message_data.get('message', '').lower()
        
        excitement_score = 0
        indicators = []
        
        # Check for excitement keywords
        for keyword in self.excitement_keywords:
            if keyword in message_text:
                excitement_score += 1
                indicators.append(f"keyword:{keyword}")
        
        # Check for caps (excitement indicator)
        if message_text.isupper() and len(message_text) > 3:
            excitement_score += 1
            indicators.append("caps")
        
        # Check for multiple exclamation marks
        exclamation_count = message_text.count('!')
        if exclamation_count >= 3:
            excitement_score += exclamation_count // 3
            indicators.append(f"exclamations:{exclamation_count}")
        
        # Check for emotes (basic detection)
        if message_data.get('emotes', {}).get('raw'):
            excitement_score += 1
            indicators.append("emotes")
        
        # Check for subscriber/VIP status (their messages might be more significant)
        badges = message_data.get('badges', {})
        if 'subscriber' in badges or 'vip' in badges or 'moderator' in badges:
            excitement_score *= 1.5
            indicators.append("special_user")
        
        # Record excitement moments
        if excitement_score >= 2:  # Threshold for excitement
            self.stats['excitement_moments'].append({
                'timestamp': datetime.utcnow(),
                'username': message_data.get('username'),
                'message': message_data.get('message'),
                'score': excitement_score,
                'indicators': indicators
            })
    
    def get_recent_excitement_windows(self, window_seconds: int = 30, min_score: float = 5.0) -> List[Dict[str, Any]]:
        """Get time windows with high excitement levels"""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=5)  # Look at last 5 minutes
        
        # Group excitement moments by time windows
        windows = {}
        for moment in self.stats['excitement_moments']:
            if moment['timestamp'] < cutoff_time:
                continue
            
            # Calculate window start
            seconds_since_start = (moment['timestamp'] - self.stats['start_time']).total_seconds()
            window_start = int(seconds_since_start // window_seconds) * window_seconds
            
            if window_start not in windows:
                windows[window_start] = {
                    'start_time': window_start,
                    'end_time': window_start + window_seconds,
                    'moments': [],
                    'total_score': 0,
                    'unique_users': set()
                }
            
            windows[window_start]['moments'].append(moment)
            windows[window_start]['total_score'] += moment['score']
            windows[window_start]['unique_users'].add(moment['username'])
        
        # Filter windows by minimum score
        exciting_windows = []
        for window_data in windows.values():
            if window_data['total_score'] >= min_score:
                window_data['unique_users'] = len(window_data['unique_users'])
                exciting_windows.append(window_data)
        
        # Sort by score descending
        exciting_windows.sort(key=lambda x: x['total_score'], reverse=True)
        
        return exciting_windows
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chat monitoring statistics"""
        runtime = None
        message_rate = 0
        
        if self.stats['start_time']:
            runtime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
            if runtime > 0:
                message_rate = self.stats['total_messages'] / (runtime / 60)  # messages per minute
        
        return {
            'channel': self.channel,
            'runtime_seconds': runtime,
            'total_messages': self.stats['total_messages'],
            'unique_users': len(self.stats['unique_users']),
            'excitement_moments': len(self.stats['excitement_moments']),
            'message_rate_per_minute': round(message_rate, 2),
            'is_monitoring': self.is_monitoring,
            'is_connected': self.is_connected,
            'recent_excitement_windows': self.get_recent_excitement_windows()
        }
    
    async def get_highlight_suggestions(self) -> List[Dict[str, Any]]:
        """Get highlight suggestions based on chat analysis"""
        exciting_windows = self.get_recent_excitement_windows()
        
        suggestions = []
        for window in exciting_windows[:10]:  # Top 10 windows
            # Calculate confidence based on score and user participation
            base_confidence = min(window['total_score'] / 20, 1.0)  # Normalize to 0-1
            user_boost = min(window['unique_users'] / 10, 0.3)  # Up to 30% boost for user participation
            confidence = min(base_confidence + user_boost, 1.0)
            
            if confidence >= 0.6:  # Minimum confidence threshold
                suggestions.append({
                    'start_time': window['start_time'],
                    'end_time': window['end_time'],
                    'confidence': confidence,
                    'type': 'CHAT_SPIKE',
                    'description': f"Chat excitement detected ({window['total_score']} score, {window['unique_users']} users)",
                    'metadata': {
                        'excitement_score': window['total_score'],
                        'unique_users': window['unique_users'],
                        'message_count': len(window['moments']),
                        'top_messages': [m['message'] for m in window['moments'][:3]]
                    }
                })
        
        return suggestions
