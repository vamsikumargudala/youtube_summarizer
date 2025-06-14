"""Command-line interface for YouTube Summarizer."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

from src.analysis import YouTubeSummarizer, SummaryStyle, SummaryLength
from src.presentation import SummaryFormatter

# Load environment variables
load_dotenv()

console = Console()


@click.command()
@click.argument('url')
@click.option('--style', type=click.Choice(['concise', 'detailed', 'bullet_points', 'academic']), 
              default='detailed', help='Summary style')
@click.option('--length', type=click.Choice(['short', 'medium', 'long']), 
              default='medium', help='Summary length')
@click.option('--format', 'output_format', type=click.Choice(['markdown', 'json', 'txt']), 
              default='markdown', help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.option('--extract-examples/--no-examples', default=True, 
              help='Extract examples and case studies')
@click.option('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
@click.option('--model', default='gpt-3.5-turbo', help='OpenAI model to use')
def main(url, style, length, output_format, output, extract_examples, api_key, model):
    """
    Summarize YouTube videos using AI.
    
    URL: YouTube video URL to summarize
    """
    
    # Validate API key
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        console.print("[red]Error: OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key option.[/red]")
        sys.exit(1)
    
    try:
        # Initialize summarizer
        with Progress() as progress:
            task = progress.add_task("[green]Processing video...", total=4)
            
            summarizer = YouTubeSummarizer(api_key=api_key, model=model)
            progress.advance(task)
            
            # Convert string enums
            style_enum = SummaryStyle(style)
            length_enum = SummaryLength(length)
            
            progress.update(task, description="[blue]Extracting transcript...")
            progress.advance(task)
            
            # Process video
            result = summarizer.summarize_video(
                url=url,
                style=style_enum,
                length=length_enum,
                extract_examples=extract_examples
            )
            
            progress.update(task, description="[yellow]Generating summary...")
            progress.advance(task)
            
            # Format output
            if output_format == 'json':
                formatted_output = SummaryFormatter.to_json(result)
                display_content = f"```json\n{formatted_output}\n```"
            elif output_format == 'txt':
                formatted_output = SummaryFormatter.to_plain_text(result)
                display_content = formatted_output
            else:  # markdown
                formatted_output = SummaryFormatter.to_markdown(result)
                display_content = formatted_output
            
            progress.advance(task)
            progress.update(task, description="[green]Complete!")
        
        # Display result
        console.print(Panel(f"[bold green]✅ Successfully processed: {result.metadata.title}[/bold green]"))
        
        if output_format == 'markdown':
            console.print(Markdown(formatted_output))
        else:
            console.print(display_content)
        
        # Save to file if requested
        if output:
            SummaryFormatter.save_to_file(result, output, output_format)
            console.print(f"[green]✅ Saved to: {output}[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()