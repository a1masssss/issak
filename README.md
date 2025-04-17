# AI-Powered Content Summarizer & Learning Assistant

A Django web application that lets users upload various content types (PDFs, YouTube videos, articles, text) and generates AI-powered summaries, interactive Q&A chatbots, flashcards, and mind maps.

## Features

### Core Functionality
- **Multi-Content Support**  
  Upload and process:
  - PDF documents
  - YouTube videos (via URL)
  - Web articles (via URL)
  - Plain text
- **AI-Powered Processing**
  - Generate summaries using OpenAI/Anthropic
  - Create flashcards from content
  - Generate interactive quiz
  - Context-aware chatbots for each content type
- **User System**
  - Email-based registration with activation
  - Profile management
  - Password reset functionality

### Technical Highlights
- Streaming responses for real-time AI interactions
- Session-based content caching
- Modular architecture with separate models/views for each content type
- Integration with multiple AI APIs (OpenAI, Anthropic)

## Technologies Used
- **Backend**: Django 4.2
- **AI Services**: OpenAI API, Anthropic API
- **Content Processing**:
  - `yt-dlp` for YouTube transcripts
  - `PyMuPDF` for PDF text extraction
  - Newspaper3k for article parsing
- **Database**: SQLite (default, can be configured for others)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap compatible)

## Installation

### Prerequisites
- Python 3.9+
- OpenAI API key
- Anthropic API key (optional)
- SMTP credentials for email

### 🛠️ Setup
1. **Clone the repository:**

   ```bash
   git clone https://github.com/a1masssss/issak
   cd issak
