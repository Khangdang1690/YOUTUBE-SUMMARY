from django.shortcuts import render
from .forms import YoutubeLinkForm
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

def get_video_id(url):
    """Extracts the video ID from various YouTube URL formats."""
    match = re.search(r"(?:youtu\.be/|(?:www\.)?youtube\.com/(?:[^/]+/.*|(?:v|e(?:mbed)?)|.*[?&]v=))([^&]{11})", url)
    if match:
        return match.group(1)
    return None

def summarize_text(text):
    """Summarizes the given text using Hugging Face's Transformers."""
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text[:100000], max_length=150, min_length=30, do_sample=False)  # Limit input text length
    return summary[0]['summary_text']

def summarize_youtube(request):
    summary = None
    error_message = None  # To store any errors

    if request.method == 'POST':
        form = YoutubeLinkForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['youtube_url']
            video_id = get_video_id(url)
            if video_id:
                try:
                    # Fetch transcript
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript = " ".join([t['text'] for t in transcript_list])

                    # Summarize text
                    summary = summarize_text(transcript)
                except Exception as e:
                    error_message = f"Error: Unable to retrieve transcript or summarize. {e}"
            else:
                error_message = "Error: Invalid YouTube URL format. Please enter a valid URL."
    else:
        form = YoutubeLinkForm()

    return render(request, 'summarizer/youtube_summarizer.html', {'form': form, 'summary': summary, 'error_message': error_message})
