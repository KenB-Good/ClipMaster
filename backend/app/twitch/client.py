
"""
Twitch API client for authentication and stream access
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class TwitchAPIClient:
    def __init__(self):
        self.client_id = settings.TWITCH_CLIENT_ID
        self.client_secret = settings.TWITCH_CLIENT_SECRET
        self.redirect_uri = settings.TWITCH_REDIRECT_URI
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"
        
        self._app_access_token = None
        self._token_expires_at = None
    
    async def get_app_access_token(self) -> str:
        """Get app access token for API calls"""
        if self._app_access_token and self._token_expires_at > datetime.utcnow():
            return self._app_access_token
        
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            async with session.post(f"{self.auth_url}/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self._app_access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                    
                    logger.info("App access token obtained")
                    return self._app_access_token
                else:
                    error = await response.text()
                    logger.error(f"Failed to get app access token: {error}")
                    raise Exception(f"Failed to authenticate with Twitch: {error}")
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            async with session.post(f"{self.auth_url}/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data['refresh_token'],
                        'expires_in': token_data.get('expires_in', 3600),
                        'scope': token_data.get('scope', [])
                    }
                else:
                    error = await response.text()
                    logger.error(f"Failed to exchange code for token: {error}")
                    raise Exception(f"Token exchange failed: {error}")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh user access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with session.post(f"{self.auth_url}/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data.get('refresh_token', refresh_token),
                        'expires_in': token_data.get('expires_in', 3600)
                    }
                else:
                    error = await response.text()
                    logger.error(f"Failed to refresh token: {error}")
                    raise Exception(f"Token refresh failed: {error}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': self.client_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/users", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        user = data['data'][0]
                        return {
                            'id': user['id'],
                            'login': user['login'],
                            'display_name': user['display_name'],
                            'email': user.get('email'),
                            'profile_image_url': user.get('profile_image_url')
                        }
                else:
                    error = await response.text()
                    logger.error(f"Failed to get user info: {error}")
                    raise Exception(f"Failed to get user info: {error}")
    
    async def get_stream_info(self, user_id: str) -> Dict[str, Any]:
        """Get current stream information"""
        app_token = await self.get_app_access_token()
        headers = {
            'Authorization': f'Bearer {app_token}',
            'Client-Id': self.client_id
        }
        
        async with aiohttp.ClientSession() as session:
            params = {'user_id': user_id}
            async with session.get(f"{self.base_url}/streams", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        stream = data['data'][0]
                        return {
                            'is_live': True,
                            'stream_id': stream['id'],
                            'title': stream['title'],
                            'game_name': stream['game_name'],
                            'game_id': stream['game_id'],
                            'viewer_count': stream['viewer_count'],
                            'started_at': stream['started_at'],
                            'language': stream['language'],
                            'thumbnail_url': stream['thumbnail_url']
                        }
                    else:
                        return {
                            'is_live': False,
                            'stream_id': None,
                            'title': None,
                            'game_name': None,
                            'viewer_count': 0
                        }
                else:
                    error = await response.text()
                    logger.error(f"Failed to get stream info: {error}")
                    return {'is_live': False, 'error': error}
    
    async def get_user_videos(self, user_id: str, video_type: str = "archive", limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's videos (VODs)"""
        app_token = await self.get_app_access_token()
        headers = {
            'Authorization': f'Bearer {app_token}',
            'Client-Id': self.client_id
        }
        
        async with aiohttp.ClientSession() as session:
            params = {
                'user_id': user_id,
                'type': video_type,
                'first': limit
            }
            async with session.get(f"{self.base_url}/videos", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = []
                    for video in data.get('data', []):
                        videos.append({
                            'id': video['id'],
                            'title': video['title'],
                            'description': video['description'],
                            'created_at': video['created_at'],
                            'published_at': video['published_at'],
                            'url': video['url'],
                            'thumbnail_url': video['thumbnail_url'],
                            'viewable': video['viewable'],
                            'view_count': video['view_count'],
                            'language': video['language'],
                            'type': video['type'],
                            'duration': video['duration']
                        })
                    return videos
                else:
                    error = await response.text()
                    logger.error(f"Failed to get user videos: {error}")
                    return []
    
    async def create_clip(self, broadcaster_id: str, access_token: str, has_delay: bool = False) -> Dict[str, Any]:
        """Create a clip from live stream"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': self.client_id
        }
        
        async with aiohttp.ClientSession() as session:
            params = {
                'broadcaster_id': broadcaster_id,
                'has_delay': str(has_delay).lower()
            }
            async with session.post(f"{self.base_url}/clips", headers=headers, params=params) as response:
                if response.status == 202:  # Accepted
                    data = await response.json()
                    if data['data']:
                        clip = data['data'][0]
                        return {
                            'id': clip['id'],
                            'edit_url': clip['edit_url'],
                            'status': 'pending'
                        }
                else:
                    error = await response.text()
                    logger.error(f"Failed to create clip: {error}")
                    raise Exception(f"Failed to create clip: {error}")
    
    async def get_clip_info(self, clip_id: str) -> Dict[str, Any]:
        """Get clip information"""
        app_token = await self.get_app_access_token()
        headers = {
            'Authorization': f'Bearer {app_token}',
            'Client-Id': self.client_id
        }
        
        async with aiohttp.ClientSession() as session:
            params = {'id': clip_id}
            async with session.get(f"{self.base_url}/clips", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        clip = data['data'][0]
                        return {
                            'id': clip['id'],
                            'url': clip['url'],
                            'embed_url': clip['embed_url'],
                            'broadcaster_id': clip['broadcaster_id'],
                            'broadcaster_name': clip['broadcaster_name'],
                            'creator_id': clip['creator_id'],
                            'creator_name': clip['creator_name'],
                            'video_id': clip['video_id'],
                            'game_id': clip['game_id'],
                            'language': clip['language'],
                            'title': clip['title'],
                            'view_count': clip['view_count'],
                            'created_at': clip['created_at'],
                            'thumbnail_url': clip['thumbnail_url'],
                            'duration': clip['duration']
                        }
                else:
                    error = await response.text()
                    logger.error(f"Failed to get clip info: {error}")
                    return None
    
    async def get_games(self, game_ids: List[str] = None, game_names: List[str] = None) -> List[Dict[str, Any]]:
        """Get game information"""
        app_token = await self.get_app_access_token()
        headers = {
            'Authorization': f'Bearer {app_token}',
            'Client-Id': self.client_id
        }
        
        params = {}
        if game_ids:
            params['id'] = game_ids
        if game_names:
            params['name'] = game_names
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/games", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    games = []
                    for game in data.get('data', []):
                        games.append({
                            'id': game['id'],
                            'name': game['name'],
                            'box_art_url': game['box_art_url']
                        })
                    return games
                else:
                    error = await response.text()
                    logger.error(f"Failed to get games: {error}")
                    return []
    
    def get_oauth_url(self, state: str = None, scopes: List[str] = None) -> str:
        """Generate OAuth authorization URL"""
        if scopes is None:
            scopes = ['user:read:email', 'clips:edit', 'channel:read:stream_key']
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes)
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}/authorize?{query_string}"
