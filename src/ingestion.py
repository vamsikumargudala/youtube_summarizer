"""YouTube video transcript extraction and metadata retrieval."""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from pytube import YouTube
import requests


@dataclass
class VideoMetadata:
    """Video metadata container."""
    title: str
    channel: str
    duration: int
    description: str
    view_count: int
    publish_date: str
    video_id: str


@dataclass
class TranscriptSegment:
    """Individual transcript segment with timing."""
    text: str
    start: float
    duration: float


class TranscriptExtractor:
    """Handles YouTube video transcript extraction and metadata retrieval."""
    
    def __init__(self):
        self.formatter = TextFormatter()
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        """Retrieve video metadata using pytube."""
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            
            return VideoMetadata(
                title=yt.title or "Unknown Title",
                channel=yt.author or "Unknown Channel",
                duration=yt.length or 0,
                description=yt.description or "",
                view_count=yt.views or 0,
                publish_date=str(yt.publish_date) if yt.publish_date else "Unknown",
                video_id=video_id
            )
        except Exception as e:
            # Fallback metadata if pytube fails
            return VideoMetadata(
                title="Unknown Title",
                channel="Unknown Channel", 
                duration=0,
                description="",
                view_count=0,
                publish_date="Unknown",
                video_id=video_id
            )
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> Tuple[str, List[TranscriptSegment]]:
        """Extract transcript from YouTube video."""
        if languages is None:
            languages = ['en', 'en-US', 'en-GB']
        
        try:
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            transcript = None
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
            
            if transcript is None:
                # Fallback to any available transcript
                transcript = transcript_list.find_transcript(transcript_list._transcript_list[0].language_code)
            
            # Get transcript data
            transcript_data = transcript.fetch()
            
            # Format as plain text
            formatted_text = self.formatter.format_transcript(transcript_data)
            
            # Create detailed segments
            segments = [
                TranscriptSegment(
                    text=item['text'],
                    start=item['start'],
                    duration=item['duration']
                )
                for item in transcript_data
            ]
            
            return formatted_text, segments
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract transcript: {str(e)}")
    
    def process_video(self, url: str) -> Tuple[VideoMetadata, str, List[TranscriptSegment]]:
        """Complete video processing pipeline."""
        video_id = self.extract_video_id(url)
        metadata = self.get_video_metadata(video_id)
        transcript_text, segments = self.get_transcript(video_id)
        
        return metadata, transcript_text, segments