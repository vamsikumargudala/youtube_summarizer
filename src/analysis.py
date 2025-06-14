"""AI-powered analysis and summarization of video content."""

import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import openai
from openai import OpenAI

from src.ingestion import VideoMetadata, TranscriptSegment, TranscriptExtractor


class SummaryStyle(Enum):
    """Available summary styles."""
    CONCISE = "concise"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"
    ACADEMIC = "academic"


class SummaryLength(Enum):
    """Available summary lengths."""
    SHORT = "short"
    MEDIUM = "medium" 
    LONG = "long"


@dataclass
class AnalysisResult:
    """Complete analysis result container."""
    summary: str
    key_points: List[str]
    examples: List[str]
    explanations: List[str]
    timestamps: List[Dict[str, Any]]
    metadata: VideoMetadata
    transcript: str


class YouTubeSummarizer:
    """Main summarization engine using OpenAI."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.extractor = TranscriptExtractor()
    
    def _create_summary_prompt(self, transcript: str, metadata: VideoMetadata, 
                             style: SummaryStyle, length: SummaryLength,
                             extract_examples: bool = True) -> str:
        """Create optimized prompt for summarization."""
        
        length_instructions = {
            SummaryLength.SHORT: "Keep the summary concise (2-3 paragraphs)",
            SummaryLength.MEDIUM: "Provide a comprehensive summary (4-6 paragraphs)",
            SummaryLength.LONG: "Create a detailed, thorough summary (6+ paragraphs)"
        }
        
        style_instructions = {
            SummaryStyle.CONCISE: "Write in a clear, concise style focusing on main points",
            SummaryStyle.DETAILED: "Provide detailed explanations with context and background",
            SummaryStyle.BULLET_POINTS: "Structure the summary using bullet points and sub-points",
            SummaryStyle.ACADEMIC: "Use academic writing style with formal language and structure"
        }
        
        prompt = f"""
        Analyze this YouTube video transcript and provide a comprehensive summary.
        
        Video Title: {metadata.title}
        Channel: {metadata.channel}
        Duration: {metadata.duration // 60} minutes
        
        TRANSCRIPT:
        {transcript}
        
        INSTRUCTIONS:
        1. {length_instructions[length]}
        2. {style_instructions[style]}
        3. Focus on the main concepts, arguments, and conclusions
        4. {"Extract specific examples, case studies, or demonstrations mentioned" if extract_examples else ""}
        5. Identify key explanations of complex topics
        6. Note any important timestamps or segments
        
        REQUIRED OUTPUT FORMAT:
        ## Summary
        [Your main summary here]
        
        ## Key Points
        - [Key point 1]
        - [Key point 2]
        - [etc.]
        
        ## Examples & Case Studies
        - [Example 1 with context]
        - [Example 2 with context]
        - [etc.]
        
        ## Important Explanations
        - [Complex concept 1: explanation]
        - [Complex concept 2: explanation]
        - [etc.]
        
        ## Notable Timestamps
        - [Time]: [What happens/is discussed]
        - [Time]: [What happens/is discussed]
        """
        
        return prompt
    
    def _parse_ai_response(self, response: str, metadata: VideoMetadata, 
                          transcript: str) -> AnalysisResult:
        """Parse AI response into structured result."""
        
        # Extract sections using regex
        sections = {
            'summary': r'## Summary\s*\n(.*?)(?=\n## |$)',
            'key_points': r'## Key Points\s*\n(.*?)(?=\n## |$)',
            'examples': r'## Examples & Case Studies\s*\n(.*?)(?=\n## |$)',
            'explanations': r'## Important Explanations\s*\n(.*?)(?=\n## |$)',
            'timestamps': r'## Notable Timestamps\s*\n(.*?)(?=\n## |$)'
        }
        
        extracted = {}
        for section, pattern in sections.items():
            match = re.search(pattern, response, re.DOTALL)
            extracted[section] = match.group(1).strip() if match else ""
        
        # Parse lists
        key_points = [point.strip('- ').strip() for point in extracted['key_points'].split('\n') if point.strip().startswith('-')]
        examples = [ex.strip('- ').strip() for ex in extracted['examples'].split('\n') if ex.strip().startswith('-')]
        explanations = [exp.strip('- ').strip() for exp in extracted['explanations'].split('\n') if exp.strip().startswith('-')]
        
        # Parse timestamps
        timestamps = []
        for line in extracted['timestamps'].split('\n'):
            if ':' in line and line.strip().startswith('-'):
                parts = line.strip('- ').split(':', 1)
                if len(parts) == 2:
                    timestamps.append({
                        'time': parts[0].strip(),
                        'description': parts[1].strip()
                    })
        
        return AnalysisResult(
            summary=extracted['summary'],
            key_points=key_points,
            examples=examples,
            explanations=explanations,
            timestamps=timestamps,
            metadata=metadata,
            transcript=transcript
        )
    
    def summarize_video(self, url: str, style: SummaryStyle = SummaryStyle.DETAILED,
                       length: SummaryLength = SummaryLength.MEDIUM,
                       extract_examples: bool = True) -> AnalysisResult:
        """Complete video summarization pipeline."""
        
        # Extract transcript and metadata
        metadata, transcript, segments = self.extractor.process_video(url)
        
        # Create prompt
        prompt = self._create_summary_prompt(transcript, metadata, style, length, extract_examples)
        
        # Get AI response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert video content analyzer specializing in creating comprehensive, accurate summaries of educational and informational content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2048
            )
            
            ai_response = response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"AI summarization failed: {str(e)}")
        
        # Parse and return structured result
        return self._parse_ai_response(ai_response, metadata, transcript)
    
    def process_video(self, url: str, **kwargs) -> AnalysisResult:
        """Convenience method for video processing."""
        return self.summarize_video(url, **kwargs)