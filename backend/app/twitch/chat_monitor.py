"""
Twitch chat monitoring for ClipMaster
Analyzes chat activity to detect excitement and highlight moments
SECURITY: Fixed import issues and added missing imports
"""
import logging
import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta  # SECURITY FIX: Added missing timedelta import
from collections import defaultdict, deque
from dataclasses import dataclass, field

import twitchio
from twitchio.ext import commands

logger = logging.getLogger(__name__)


@dataclass
class ChatStats:
    """Chat statistics for excitement analysis"""

    total_messages: int = 0
    unique_users: set = field(default_factory=set)
    messages_per_minute: deque = field(default_factory=lambda: deque(maxlen=60))
    excitement_indicators: Dict[str, int] = field(default_factory=dict)
    recent_messages: deque = field(default_factory=lambda: deque(maxlen=100))
    start_time: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExcitementMoment:
    """Represents a moment of high excitement in chat"""

    timestamp: datetime
    score: float
    duration: int
    message_count: int
    unique_users: int
    indicators: List[str]
    sample_messages: List[str]


class TwitchChatMonitor(commands.Bot):
    """
    Twitch chat monitor that analyzes chat activity for excitement detection
    """

    def __init__(self, channel_name: str, oauth_token: str):
        super().__init__(
            token=oauth_token, prefix="!", initial_channels=[channel_name]
        )

        self.channel_name = channel_name
        self.stats = ChatStats()
        self.excitement_moments: List[ExcitementMoment] = []
        self.is_monitoring = False

        # Excitement indicators and their weights
        self.excitement_patterns = {
            # Emotes and reactions
            r"[!]{2,}": 2.0,  # Multiple exclamation marks
            r"[?]{2,}": 1.5,  # Multiple question marks
            r"POGGERS?|POG|KEKW|LUL|OMEGALUL": 3.0,  # Popular emotes
            r"WOW|AMAZING|INSANE|CRAZY|UNBELIEVABLE": 2.5,  # Excitement words
            r"CLUTCH|GODLIKE|LEGENDARY|EPIC": 3.0,  # Gaming excitement
            r"NO WAY|WHAT|HOW|IMPOSSIBLE": 2.0,  # Disbelief
            r"[A-Z]{3,}": 1.5,  # All caps words
            # Spam patterns (can indicate excitement)
            r"(.)\1{3,}": 1.0,  # Character repetition (aaaa, !!!!)
            r"(\w+)\s+\1": 1.5,  # Word repetition
        }

        # Compile regex patterns for efficiency
        self.compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): weight
            for pattern, weight in self.excitement_patterns.items()
        }

    async def event_ready(self):
        """Called when bot is ready"""
        logger.info(f"Chat monitor ready for channel: {self.channel_name}")
        self.is_monitoring = True

    async def event_message(self, message):
        """Process incoming chat messages"""
        if not self.is_monitoring:
            return

        # Skip bot messages
        if message.echo:
            return

        # Update basic stats
        self.stats.total_messages += 1
        self.stats.unique_users.add(message.author.name)

        # Add to recent messages
        message_data = {
            "timestamp": datetime.utcnow(),
            "author": message.author.name,
            "content": message.content,
            "excitement_score": 0,
        }

        # Calculate excitement score for this message
        excitement_score = self._calculate_message_excitement(message.content)
        message_data["excitement_score"] = excitement_score

        # Add to recent messages queue
        self.stats.recent_messages.append(message_data)

        # Update messages per minute counter
        current_minute = datetime.utcnow().replace(second=0, microsecond=0)
        if (
            not self.stats.messages_per_minute
            or self.stats.messages_per_minute[-1][0] != current_minute
        ):
            self.stats.messages_per_minute.append([current_minute, 1])
        else:
            self.stats.messages_per_minute[-1][1] += 1

        # Check for excitement peaks
        await self._check_excitement_peak()

    def _calculate_message_excitement(self, content: str) -> float:
        """Calculate excitement score for a message"""
        score = 0.0

        # Check against excitement patterns
        for pattern, weight in self.compiled_patterns.items():
            matches = pattern.findall(content)
            if matches:
                score += weight * len(matches)

        # Additional scoring factors

        # Message length (very short or very long can indicate excitement)
        if len(content) < 5 or len(content) > 100:
            score += 0.5

        # Emote density
        emote_count = len(re.findall(r":\w+:", content))
        if emote_count > 0:
            score += emote_count * 0.5

        # Caps ratio
        if len(content) > 3:
            caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
            if caps_ratio > 0.5:
                score += caps_ratio * 2

        return min(score, 10.0)  # Cap at 10

    async def _check_excitement_peak(self):
        """Check if current chat activity indicates an excitement peak"""
        now = datetime.utcnow()

        # Look at last 30 seconds of messages
        recent_window = now - timedelta(seconds=30)
        recent_messages = [
            msg
            for msg in self.stats.recent_messages
            if msg["timestamp"] > recent_window
        ]

        if len(recent_messages) < 5:  # Need minimum activity
            return

        # Calculate window statistics
        total_score = sum(msg["excitement_score"] for msg in recent_messages)
        avg_score = total_score / len(recent_messages)
        unique_users = len(set(msg["author"] for msg in recent_messages))
        message_rate = len(recent_messages) / 30  # messages per second

        # Determine if this is an excitement peak
        excitement_threshold = 3.0
        rate_threshold = 0.5  # messages per second

        if avg_score > excitement_threshold and message_rate > rate_threshold:
            # Extract indicators that triggered this peak
            indicators = []
            sample_messages = []

            for msg in recent_messages[-5:]:  # Last 5 messages as samples
                sample_messages.append(f"{msg['author']}: {msg['content']}")

                # Find which patterns matched
                for pattern, weight in self.compiled_patterns.items():
                    if pattern.search(msg["content"]):
                        pattern_name = list(self.excitement_patterns.keys())[
                            list(self.compiled_patterns.keys()).index(pattern)
                        ]
                        if pattern_name not in indicators:
                            indicators.append(pattern_name)

            # Create excitement moment
            moment = ExcitementMoment(
                timestamp=now,
                score=avg_score,
                duration=30,
                message_count=len(recent_messages),
                unique_users=unique_users,
                indicators=indicators,
                sample_messages=sample_messages,
            )

            self.excitement_moments.append(moment)

            logger.info(
                f"Excitement peak detected: score={avg_score:.2f}, "
                f"messages={len(recent_messages)}, users={unique_users}"
            )

    def get_recent_stats(self) -> Dict[str, Any]:
        """Get recent chat statistics"""
        now = datetime.utcnow()

        # Messages in last minute
        last_minute = now - timedelta(minutes=1)
        recent_messages = [
            msg
            for msg in self.stats.recent_messages
            if msg["timestamp"] > last_minute
        ]

        return {
            "total_messages": self.stats.total_messages,
            "unique_users": list(self.stats.unique_users),
            "recent_message_count": len(recent_messages),
            "recent_unique_users": len(
                set(msg["author"] for msg in recent_messages)
            ),
            "average_excitement": sum(msg["excitement_score"] for msg in recent_messages)
            / max(len(recent_messages), 1),
            "excitement_moments": len(self.excitement_moments),
            "monitoring_duration": (now - self.stats.start_time).total_seconds(),
        }

    def get_excitement_moments(self) -> List[Dict[str, Any]]:
        """Get all detected excitement moments"""
        return [
            {
                "timestamp": moment.timestamp.isoformat(),
                "score": moment.score,
                "duration": moment.duration,
                "message_count": moment.message_count,
                "unique_users": moment.unique_users,
                "indicators": moment.indicators,
                "sample_messages": moment.sample_messages,
            }
            for moment in self.excitement_moments
        ]

    def get_recent_excitement_windows(
        self, window_seconds: int = 30, min_score: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Get time windows with high excitement levels"""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=5)  # Look at last 5 minutes

        # Group excitement moments by time windows
        windows = {}
        for moment in self.excitement_moments:
            if moment.timestamp < cutoff_time:
                continue

            # Round timestamp to window
            window_start = moment.timestamp.replace(
                second=(moment.timestamp.second // window_seconds) * window_seconds,
                microsecond=0,
            )

            if window_start not in windows:
                windows[window_start] = {
                    "start_time": window_start,
                    "end_time": window_start + timedelta(seconds=window_seconds),
                    "moments": [],
                    "total_score": 0,
                    "max_score": 0,
                    "indicators": set(),
                }

            windows[window_start]["moments"].append(moment)
            windows[window_start]["total_score"] += moment.score
            windows[window_start]["max_score"] = max(
                windows[window_start]["max_score"], moment.score
            )
            windows[window_start]["indicators"].update(moment.indicators)

        # Filter and format windows
        result_windows = []
        for window_data in windows.values():
            avg_score = window_data["total_score"] / len(window_data["moments"])

            if avg_score >= min_score:
                result_windows.append(
                    {
                        "start_time": window_data["start_time"].isoformat(),
                        "end_time": window_data["end_time"].isoformat(),
                        "duration": window_seconds,
                        "score": avg_score,
                        "max_score": window_data["max_score"],
                        "moment_count": len(window_data["moments"]),
                        "indicators": list(window_data["indicators"]),
                    }
                )

        # Sort by score descending
        result_windows.sort(key=lambda x: x["score"], reverse=True)

        return result_windows

    def get_top_chatters(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most active chatters"""
        user_message_counts = defaultdict(int)
        user_excitement_scores = defaultdict(float)

        for msg in self.stats.recent_messages:
            user = msg["author"]
            user_message_counts[user] += 1
            user_excitement_scores[user] += msg["excitement_score"]

        # Calculate average excitement per user
        top_chatters = []
        for user in user_message_counts:
            avg_excitement = user_excitement_scores[user] / user_message_counts[user]
            top_chatters.append(
                {
                    "username": user,
                    "message_count": user_message_counts[user],
                    "total_excitement": user_excitement_scores[user],
                    "avg_excitement": avg_excitement,
                }
            )

        # Sort by total excitement
        top_chatters.sort(key=lambda x: x["total_excitement"], reverse=True)

        return top_chatters[:limit]

    async def stop_monitoring(self):
        """Stop chat monitoring"""
        self.is_monitoring = False
        await self.close()

        logger.info(f"Chat monitoring stopped for {self.channel_name}")
        logger.info(f"Total messages: {self.stats.total_messages}")
        logger.info(f"Unique users: {len(self.stats.unique_users)}")
        logger.info(f"Excitement moments: {len(self.excitement_moments)}")


class ChatMonitorManager:
    """Manages multiple chat monitors"""

    def __init__(self):
        self.monitors: Dict[str, TwitchChatMonitor] = {}
        self.monitor_tasks: Dict[str, asyncio.Task] = {}

    async def start_monitor(
        self, channel_name: str, oauth_token: str
    ) -> TwitchChatMonitor:
        """Start monitoring a channel"""
        if channel_name in self.monitors:
            logger.warning(f"Monitor already exists for {channel_name}")
            return self.monitors[channel_name]

        monitor = TwitchChatMonitor(channel_name, oauth_token)
        self.monitors[channel_name] = monitor

        # Start the monitor in a background task
        task = asyncio.create_task(monitor.start())
        self.monitor_tasks[channel_name] = task

        logger.info(f"Started chat monitor for {channel_name}")
        return monitor

    async def stop_monitor(self, channel_name: str):
        """Stop monitoring a channel"""
        if channel_name not in self.monitors:
            logger.warning(f"No monitor found for {channel_name}")
            return

        monitor = self.monitors[channel_name]
        await monitor.stop_monitoring()

        # Cancel the background task
        if channel_name in self.monitor_tasks:
            task = self.monitor_tasks[channel_name]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.monitor_tasks[channel_name]

        del self.monitors[channel_name]
        logger.info(f"Stopped chat monitor for {channel_name}")

    def get_monitor(self, channel_name: str) -> Optional[TwitchChatMonitor]:
        """Get monitor for a channel"""
        return self.monitors.get(channel_name)

    async def stop_all_monitors(self):
        """Stop all active monitors"""
        for channel_name in list(self.monitors.keys()):
            await self.stop_monitor(channel_name)


# Global monitor manager instance
chat_monitor_manager = ChatMonitorManager()
