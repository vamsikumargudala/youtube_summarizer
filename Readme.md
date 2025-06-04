# YouTube Summarizer

🎬 AI-powered tool for extracting transcripts and generating intelligent summaries from YouTube videos.

[![CI](https://github.com/vamsikumargudala/youtube-summarizer/workflows/CI/badge.svg)](https://github.com/vamsikumargudala/youtube-summarizer/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Features

- 📝 Extract transcripts from YouTube videos
- 🤖 AI-powered summarization using OpenAI GPT
- 🎯 Extract key examples and explanations
- 🖥️ CLI and Web UI (Streamlit)
- 📊 Multiple output formats (JSON, Markdown, Plain text)
- 🔧 Configurable summary styles and lengths

## Quick Start

```bash
# Install with Poetry
poetry install

# Or with pip
pip install -e .

# Set up environment
cp .env.template .env
# Edit .env with your OpenAI API key

# CLI usage
youtube-summarizer "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Web UI
streamlit run src/streamlit_app.py