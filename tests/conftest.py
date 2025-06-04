"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock

from src.ingestion import VideoMetadata, TranscriptSegment


@pytest.fixture
def sample_video_metadata():
    """Sample video metadata for testing."""
    return VideoMetadata(
        title="Test Video Title",
        channel="Test Channel",
        duration=600,  # 10 minutes
        description="Test video description",
        view_count=1000,
        publish_date="2023-01-01",
        video_id="dQw4w9WgXcQ"
    )


@pytest.fixture
def sample_transcript():
    """Sample transcript text for testing."""
    return """
    Welcome to this tutorial on machine learning. 
    Today we'll cover the basics of neural networks.
    First, let's understand what a neuron is.
    A neuron is the basic building block of neural networks.
    """


@pytest.fixture
def sample_transcript_segments():
    """Sample transcript segments for testing."""
    return [
        TranscriptSegment("Welcome to this tutorial on machine learning.", 0.0, 3.5),
        TranscriptSegment("Today we'll cover the basics of neural networks.", 3.5, 4.2),
        TranscriptSegment("First, let's understand what a neuron is.", 7.7, 3.8),
        TranscriptSegment("A neuron is the basic building block of neural networks.", 11.5, 4.1),
    ]


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return """## Summary
This video provides an introduction to machine learning and neural networks, explaining the fundamental concepts in an accessible way.

## Key Points
- Neural networks are inspired by biological neurons
- They form the foundation of modern AI systems
- Understanding neurons is crucial for ML comprehension

## Examples & Case Studies
- Biological neuron analogy for artificial neurons
- Simple perceptron example

## Important Explanations
- Neuron: Basic building block that processes and transmits information
- Neural Network: Collection of interconnected neurons working together

## Notable Timestamps
- 0:00: Introduction to machine learning
- 3:30: Neural network basics begin
"""