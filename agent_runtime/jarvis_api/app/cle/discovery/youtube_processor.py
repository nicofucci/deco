"""
YouTube Processor for CLE
Extracts learning from cybersecurity video transcripts
"""

import yt_dlp
from typing import List, Optional, Dict
import logging
from datetime import datetime
import hashlib
import os

from app.cle.config import YOUTUBE_CHANNELS
from app.cle.models import KnowledgeYouTube, SourceType

logger = logging.getLogger(__name__)


class YouTubeProcessor:
    """Processes YouTube videos for cybersecurity learning"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube processor
        
        Args:
            api_key: YouTube Data API v3 key (optional, but needed for search)
        """
        self.api_key = api_key
        
        # yt-dlp options
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,  # Don't download video
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'es'],
        }
    
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """Get video metadata using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info
        except Exception as e:
            logger.error(f"[YouTube] Error getting video info for {video_url}: {e}")
            return None
    
    def extract_transcript(self, video_url: str) -> Optional[str]:
        """Extract transcript/subtitles from video"""
        try:
            info = self.get_video_info(video_url)
            if not info:
                return None
            
            # Try to get subtitles
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            # Prefer English subtitles
            transcript_text = None
            
            # Try manual subtitles first
            for lang in ['en', 'es']:
                if lang in subtitles:
                    # Get subtitle content
                    # Note: yt-dlp returns subtitle URLs, we'd need to download them
                    # For simplicity, we'll use automatic captions text if available
                    break
            
            # Try automatic captions
            if not transcript_text and 'en' in automatic_captions:
                # Automatic captions are available
                # In production, you'd download and parse the subtitle file
                # For now, return a placeholder
                transcript_text = "[Automatic transcript available]"
            
            # Fallback: use description as proxy
            if not transcript_text:
                description = info.get('description', '')
                if description:
                    transcript_text = f"[No transcript. Video description: {description}]"
            
            return transcript_text
            
        except Exception as e:
            logger.error(f"[YouTube] Error extracting transcript from {video_url}: {e}")
            return None
    
    def process_video(self, video_url: str) -> Optional[KnowledgeYouTube]:
        """
        Process a YouTube video into KnowledgeYouTube
        
        Args:
            video_url: YouTube video URL
        
        Returns:
            KnowledgeYouTube if successful, None otherwise
        """
        try:
            # Get video info
            info = self.get_video_info(video_url)
            if not info:
                return None
            
            # Extract video ID
            video_id = info.get('id', '')
            if not video_id:
                logger.error(f"[YouTube] No video ID found for {video_url}")
                return None
            
            # Check if channel is in allowed list
            channel_name = info.get('channel', 'Unknown')
            if not self._is_allowed_channel(channel_name, info.get('channel_id')):
                logger.warning(f"[YouTube] Channel '{channel_name}' not in whitelist")
                # For MVP, we'll allow it but log the warning
                # In production, you might want to reject it
            
            # Extract transcript
            transcript = self.extract_transcript(video_url)
            if not transcript:
                logger.warning(f"[YouTube] No transcript for {video_id}, using description")
                transcript = info.get('description', 'No content available')
            
            # Generate ID
            knowledge_id = hashlib.md5(video_url.encode()).hexdigest()
            
            # Create KnowledgeYouTube
            knowledge_video = KnowledgeYouTube(
                id=knowledge_id,
                source_type=SourceType.YOUTUBE,
                video_url=video_url,
                video_id=video_id,
                title=info.get('title', 'Untitled'),
                channel=channel_name,
                duration=info.get('duration', 0),
                transcript=transcript,
                summary="",  # Will be filled by summarization service
                concepts=[],
                use_cases_jarvis=[],
                tags=self._extract_tags(info),
                relevance_score=self._calculate_relevance(info),
                discovered_at=datetime.now()
            )
            
            logger.info(f"[YouTube] Processed: {knowledge_video.title}")
            return knowledge_video
            
        except Exception as e:
            logger.error(f"[YouTube] Error processing video {video_url}: {e}")
            return None
    
    def _is_allowed_channel(self, channel_name: str, channel_id: str = None) -> bool:
        """Check if channel is in whitelist"""
        # Check by name
        for allowed_name in YOUTUBE_CHANNELS.keys():
            if allowed_name.lower() in channel_name.lower():
                return True
        
        # Check by ID
        if channel_id and channel_id in YOUTUBE_CHANNELS.values():
            return True
        
        return False
    
    def _extract_tags(self, info: Dict) -> List[str]:
        """Extract tags from video metadata"""
        tags = []
        
        # Add channel name as tag
        channel = info.get('channel', '')
        if channel:
            tags.append(channel.lower().replace(' ', '-'))
        
        # Add categories from video tags
        video_tags = info.get('tags', [])
        if video_tags:
            # Only take first 5 tags
            tags.extend([tag.lower() for tag in video_tags[:5]])
        
        return tags
    
    def _calculate_relevance(self, info: Dict) -> float:
        """Calculate relevance score based on views, likes, etc."""
        view_count = info.get('view_count', 0)
        
        if view_count >= 1000000:
            return 1.0
        elif view_count >= 500000:
            return 0.9
        elif view_count >= 100000:
            return 0.8
        elif view_count >= 50000:
            return 0.7
        elif view_count >= 10000:
            return 0.6
        else:
            return 0.5


def get_youtube_api_key_from_env() -> Optional[str]:
    """Get YouTube API key from environment variable"""
    return os.getenv("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_DATA_API_KEY")
