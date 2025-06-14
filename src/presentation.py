"""Output formatting and presentation utilities."""

import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from src.analysis import AnalysisResult


class SummaryFormatter:
    """Handles different output formats for analysis results."""
    
    @staticmethod
    def to_markdown(result: AnalysisResult) -> str:
        """Format result as Markdown."""
        
        md = f"""# {result.metadata.title}

**Channel:** {result.metadata.channel}  
**Duration:** {result.metadata.duration // 60}:{result.metadata.duration % 60:02d}  
**Views:** {result.metadata.view_count:,}  
**Published:** {result.metadata.publish_date}  

---

## Summary

{result.summary}

## Key Points

"""
        
        for point in result.key_points:
            md += f"- {point}\n"
        
        if result.examples:
            md += "\n## Examples & Case Studies\n\n"
            for example in result.examples:
                md += f"- {example}\n"
        
        if result.explanations:
            md += "\n## Important Explanations\n\n"
            for explanation in result.explanations:
                md += f"- {explanation}\n"
        
        if result.timestamps:
            md += "\n## Notable Timestamps\n\n"
            for ts in result.timestamps:
                md += f"- **{ts['time']}:** {ts['description']}\n"
        
        return md
    
    @staticmethod
    def to_json(result: AnalysisResult) -> Dict[str, Any]:
        """Format result as JSON-serializable dictionary."""
        
        return {
            "metadata": {
                "title": result.metadata.title,
                "channel": result.metadata.channel,
                "duration": result.metadata.duration,
                "description": result.metadata.description,
                "view_count": result.metadata.view_count,
                "publish_date": result.metadata.publish_date,
                "video_id": result.metadata.video_id
            },
            "analysis": {
                "summary": result.summary,
                "key_points": result.key_points,
                "examples": result.examples,
                "explanations": result.explanations,
                "timestamps": result.timestamps
            },
            "transcript": result.transcript,
            "generated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def to_plain_text(result: AnalysisResult) -> str:
        """Format result as plain text."""
        
        text = f"{result.metadata.title}\n"
        text += f"Channel: {result.metadata.channel}\n"
        text += f"Duration: {result.metadata.duration // 60}:{result.metadata.duration % 60:02d}\n"
        text += "=" * 50 + "\n\n"
        
        text += "SUMMARY:\n"
        text += result.summary + "\n\n"
        
        text += "KEY POINTS:\n"
        for i, point in enumerate(result.key_points, 1):
            text += f"{i}. {point}\n"
        
        if result.examples:
            text += "\nEXAMPLES:\n"
            for i, example in enumerate(result.examples, 1):
                text += f"{i}. {example}\n"
        
        if result.explanations:
            text += "\nEXPLANATIONS:\n"
            for i, explanation in enumerate(result.explanations, 1):
                text += f"{i}. {explanation}\n"
        
        if result.timestamps:
            text += "\nTIMESTAMPS:\n"
            for ts in result.timestamps:
                text += f"{ts['time']}: {ts['description']}\n"
        
        return text
    
    @staticmethod
    def save_to_file(result: AnalysisResult, filepath: str, format_type: str = "markdown"):
        """Save formatted result to file."""
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type.lower() == "json":
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(SummaryFormatter.to_json(result), f, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "markdown":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(SummaryFormatter.to_markdown(result))
        
        elif format_type.lower() == "txt":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(SummaryFormatter.to_plain_text(result))
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")