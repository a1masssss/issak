# Standard and Django imports
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from main.models import SummaryNotes
from main.forms import SummaryForm



import time
# HTTP requests
import requests

# For parsing articles
from newspaper import Article

# For extracting PDF text
import fitz  # PyMuPDF (used as pymupdf)
import pymupdf  # if you're using an alias, otherwise just `fitz`

# For YouTube transcript extraction
from youtube_transcript_api import YouTubeTranscriptApi

# For downloading YouTube metadata
import yt_dlp

# For AI API access (Anthropic and OpenAI)
import openai
from openai.error import RateLimitError, APIError, Timeout, ServiceUnavailableError
from anthropic import Anthropic  # or however your Anthropic client is initialized
import anthropic


import json
import re
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
openai.api_key = settings.OPENAI_API_KEY




    

# @cache_page(60 * 60 * 2)  # 2hr


