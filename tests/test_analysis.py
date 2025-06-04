"""Tests for AI analysis functionality."""

import pytest
from unittest.mock import patch, Mock

from src.analysis import YouTubeSummarizer, SummaryStyle, SummaryLength, AnalysisResult


class TestYouTubeSummarizer:
    """Test AI summarization functionality."""
    
    def test_init_no_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ValueError):
            YouTubeSummarizer(api_key=None)
    
    def test_init_with_api_key(self):
        """Test successful initialization with API key."""
        summarizer = YouTubeSummarizer(api_key="test-key")
        assert summarizer.api_key == "test-key"
        assert summarizer.model == "gpt-3.5-turbo"
    
    def test_create_summary_prompt(self, sample_video_metadata):
        """Test prompt creation for different styles and lengths."""
        summarizer = YouTubeSummarizer(api_key="test-key")
        transcript = "Test transcript content"
        
        prompt = summarizer._create_summary_prompt(
            transcript, sample_video_metadata, 
            SummaryStyle.DETAILED, SummaryLength.MEDIUM
        )
        
        assert "Test Video Title" in prompt
        assert "Test Channel" in prompt
        assert "Test transcript content" in prompt
        assert "comprehensive summary" in prompt
    
    def test_parse_ai_response(self, sample_video_metadata, mock_openai_response):
        """Test parsing of AI response into structured result."""
        summarizer = YouTubeSummarizer(api_key="test-key")
        
        result = summarizer._parse_ai_response(
            mock_openai_response, sample_video_metadata, "test transcript"
        )
        
        assert isinstance(result, AnalysisResult)
        assert "introduction to machine learning" in result.summary.lower()
        assert len(result.key_points) == 3
        assert len(result.examples) == 2
        assert len(result.explanations) == 2
        assert len(result.timestamps) == 2
    
    @patch('src.analysis.OpenAI')
    @patch.object(YouTubeSummarizer, '_parse_ai_response')
    def test_summarize_video_success(self, mock_parse, mock_openai_class, 
                                   sample_video_metadata, mock_openai_response):
        """Test successful video summarization."""
        # Mock OpenAI client
        mock_client = Mock()

        fake_choice = Mock()
        fake_choice.message = Mock()
        fake_choice.message.content = mock_openai_response

        mock_response = Mock()
        mock_response.choices = [fake_choice]

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Mock extractor
        with patch.object(YouTubeSummarizer, '__init__', lambda x, **kwargs: None):
            summarizer = YouTubeSummarizer.__new__(YouTubeSummarizer)
            summarizer.client = mock_client
            summarizer.model = "gpt-3.5-turbo"
            
            mock_extractor = Mock()
            mock_extractor.process_video.return_value = (
                sample_video_metadata, "test transcript", []
            )
            summarizer.extractor = mock_extractor
            
            # Mock parse response
            expected_result = AnalysisResult(
                summary="Test summary",
                key_points=["Point 1"],
                examples=["Example 1"],
                explanations=["Explanation 1"],
                timestamps=[],
                metadata=sample_video_metadata,
                transcript="test transcript"
            )
            mock_parse.return_value = expected_result
            
            result = summarizer.summarize_video("https://youtu.be/dQw4w9WgXcQ")
            
            assert result == expected_result
            mock_client.chat.completions.create.assert_called_once()