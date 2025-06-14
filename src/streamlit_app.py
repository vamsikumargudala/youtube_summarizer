"""Streamlit web interface for YouTube Summarizer."""

import os
import streamlit as st
from dotenv import load_dotenv

from src.analysis import YouTubeSummarizer, SummaryStyle, SummaryLength
from src.presentation import SummaryFormatter

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 YouTube Video Summarizer")
st.markdown("Extract transcripts and generate AI-powered summaries from YouTube videos")

# Sidebar configuration
st.sidebar.header("Configuration")

# API Key input
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=os.getenv("OPENAI_API_KEY", ""),
    help="Enter your OpenAI API key"
)

# Model selection
model = st.sidebar.selectbox(
    "AI Model",
    ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
    index=0
)

# Summary options
style = st.sidebar.selectbox(
    "Summary Style",
    ["detailed", "concise", "bullet_points", "academic"],
    index=0
)

length = st.sidebar.selectbox(
    "Summary Length", 
    ["medium", "short", "long"],
    index=0
)

extract_examples = st.sidebar.checkbox("Extract Examples", value=True)

# Main interface
url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Paste the YouTube video URL here"
)

if st.button("🔍 Analyze Video", type="primary"):
    if not url:
        st.error("Please enter a YouTube URL")
    elif not api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
    else:
        try:
            with st.spinner("Processing video... This may take a few minutes."):
                # Initialize summarizer
                summarizer = YouTubeSummarizer(api_key=api_key, model=model)
                
                # Process video
                result = summarizer.summarize_video(
                    url=url,
                    style=SummaryStyle(style),
                    length=SummaryLength(length),
                    extract_examples=extract_examples
                )
            
            # Display results
            st.success("✅ Analysis complete!")
            
            # Video metadata
            st.header("📹 Video Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Title", result.metadata.title)
                st.metric("Channel", result.metadata.channel)
            
            with col2:
                duration_min = result.metadata.duration // 60
                duration_sec = result.metadata.duration % 60
                st.metric("Duration", f"{duration_min}:{duration_sec:02d}")
                st.metric("Views", f"{result.metadata.view_count:,}")
            
            # Summary
            st.header("📝 Summary")
            st.write(result.summary)
            
            # Key points
            if result.key_points:
                st.header("🎯 Key Points")
                for i, point in enumerate(result.key_points, 1):
                    st.write(f"{i}. {point}")
            
            # Examples
            if result.examples:
                st.header("💡 Examples & Case Studies")
                for i, example in enumerate(result.examples, 1):
                    st.write(f"{i}. {example}")
            
            # Explanations
            if result.explanations:
                st.header("🧠 Important Explanations")
                for i, explanation in enumerate(result.explanations, 1):
                    st.write(f"{i}. {explanation}")
            
            # Timestamps
            if result.timestamps:
                st.header("⏰ Notable Timestamps")
                for ts in result.timestamps:
                    st.write(f"**{ts['time']}:** {ts['description']}")
            
            # Download options
            st.header("💾 Download")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                markdown_output = SummaryFormatter.to_markdown(result)
                st.download_button(
                    "📄 Download Markdown",
                    markdown_output,
                    file_name=f"{result.metadata.title[:50]}.md",
                    mime="text/markdown"
                )
            
            with col2:
                json_output = SummaryFormatter.to_json(result)
                st.download_button(
                    "📊 Download JSON",
                    str(json_output),
                    file_name=f"{result.metadata.title[:50]}.json",
                    mime="application/json"
                )
            with col3:
                txt_output = SummaryFormatter.to_plain_text(result)
                st.download_button(
                    "📝 Download Text",
                    txt_output,
                    file_name=f"{result.metadata.title[:50]}.txt",
                    mime="text/plain"
                )
            
            # Full transcript (expandable)
            with st.expander("📜 View Full Transcript"):
                st.text_area("Transcript", result.transcript, height=300)
        
        except Exception as e:
            st.error(f"❌ Error processing video: {str(e)}")
            st.info("Make sure the video has available captions/transcripts and your API key is valid.")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit and OpenAI | "
    "[GitHub](https://github.com/vamsikumargudala/youtube-summarizer)"
)