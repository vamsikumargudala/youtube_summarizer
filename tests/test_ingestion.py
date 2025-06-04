"""Tests for transcript extraction functionality."""

import pytest
from unittest.mock import patch, Mock

from src.ingestion import TranscriptExtractor


class TestTranscriptExtractor:
    """Test transcript extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = TranscriptExtractor()
    
    def test_extract_video_id_standard_url(self):
        """Test video ID extraction from standard YouTube URLs."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
        ]
        
        for url in urls:
            video_id = self.extractor.extract_video_id(url)
            assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test video ID extraction from short YouTube URLs."""
        urls = [
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ?t=10",
        ]
        
        for url in urls:
            video_id = self.extractor.extract_video_id(url)
            assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test video ID extraction from embed URLs."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = self.extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test error handling for invalid URLs."""
        with pytest.raises(ValueError):
            self.extractor.extract_video_id("https://example.com/invalid")
    
    @patch('src.ingestion.YouTube')
    def test_get_video_metadata_success(self, mock_youtube):
        """Test successful metadata extraction."""
        # Mock YouTube object
        mock_yt = Mock()
        mock_yt.title = "Test Video"
        mock_yt.author = "Test Channel"
        mock_yt.length = 600
        mock_yt.description = "Test description"
        mock_yt.views = 1000
        mock_yt.publish_date = "2023-01-01"
        mock_youtube.return_value = mock_yt
        
        metadata = self.extractor.get_video_metadata("dQw4w9WgXcQ")
        
        assert metadata.title == "Test Video"
        assert metadata.channel == "Test Channel"
        assert metadata.duration == 600
        assert metadata.view_count == 1000
    
    @patch('src.ingestion.YouTubeTranscriptApi')
    def test_get_transcript_success(self, mock_api):
        """Test successful transcript extraction."""
        # Mock transcript data
        mock_transcript_data = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
            {'text': 'This is a test', 'start': 2.0, 'duration': 3.0},
        ]
        
        mock_transcript = Mock()
        mock_transcript.fetch.return_value = mock_transcript_data
        
        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        text, segments = self.extractor.get_transcript("dQw4w9WgXcQ")
        
        assert len(segments) == 2
        assert segments[0].text == "Hello world"
        assert segments[0].start == 0.0
        assert segments[1].text == "This is a test"