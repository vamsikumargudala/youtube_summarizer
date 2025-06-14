"""Tests for output formatting functionality."""

import json
import pytest
from src.presentation import SummaryFormatter
from src.analysis import AnalysisResult


class TestSummaryFormatter:
    """Test output formatting functionality."""
    
    def test_to_markdown(self, sample_analysis_result):
        """Test Markdown formatting."""
        markdown = SummaryFormatter.to_markdown(sample_analysis_result)
        
        assert "# Test Video Title" in markdown
        assert "**Channel:** Test Channel" in markdown
        assert "## Summary" in markdown
        assert "## Key Points" in markdown
        assert "- " in markdown  # Check for bullet points
    
    def test_to_json(self, sample_analysis_result):
        """Test JSON formatting."""
        json_data = SummaryFormatter.to_json(sample_analysis_result)
        
        assert "metadata" in json_data
        assert "analysis" in json_data
        assert "transcript" in json_data
        assert json_data["metadata"]["title"] == "Test Video Title"
        assert json_data["metadata"]["channel"] == "Test Channel"
    
    def test_to_plain_text(self, sample_analysis_result):
        """Test plain text formatting."""
        text = SummaryFormatter.to_plain_text(sample_analysis_result)
        
        assert "Test Video Title" in text
        assert "Channel: Test Channel" in text
        assert "SUMMARY:" in text
        assert "KEY POINTS:" in text
        assert "1. " in text  # Check for numbered points
    
    def test_save_to_file_markdown(self, sample_analysis_result, tmp_path):
        """Test saving Markdown to file."""
        filepath = tmp_path / "test.md"
        
        SummaryFormatter.save_to_file(sample_analysis_result, str(filepath), "markdown")
        
        assert filepath.exists()
        content = filepath.read_text()
        assert "# Test Video Title" in content
    
    def test_save_to_file_json(self, sample_analysis_result, tmp_path):
        """Test saving JSON to file."""
        filepath = tmp_path / "test.json"
        
        SummaryFormatter.save_to_file(sample_analysis_result, str(filepath), "json")
        
        assert filepath.exists()
        with open(filepath) as f:
            data = json.load(f)
        assert data["metadata"]["title"] == "Test Video Title"


@pytest.fixture
def sample_analysis_result(sample_video_metadata):
    """Sample analysis result for testing."""
    return AnalysisResult(
        summary="This is a test summary of the video content.",
        key_points=["Point 1", "Point 2", "Point 3"],
        examples=["Example 1", "Example 2"],
        explanations=["Explanation 1", "Explanation 2"],
        timestamps=[
            {"time": "0:30", "description": "Important moment 1"},
            {"time": "2:15", "description": "Important moment 2"}
        ],
        metadata=sample_video_metadata,
        transcript="This is the full transcript of the video."
    )