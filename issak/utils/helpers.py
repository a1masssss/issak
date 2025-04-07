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

# functions 
def summarize_with_anthropic(text):
    prompt = f"""
    Generate a highly detailed, comprehensive, and structured summary of the following text:
    
    {text}

    Your goal is to create a polished, professional, and visually engaging summary that effectively conveys the content’s essence while capturing all key points. Ensure your summary follows these enhanced guidelines:
    
    <b>1. Clear Structure and Logical Flow</b><br>
    &bull; Divide the content into distinct, well-defined sections with appropriate <b>headings and subheadings</b> that accurately reflect the main themes and ideas.<br>
    &bull; Ensure the structure follows a logical sequence, maintaining coherence between sections.<br>
    &bull; Use nested bullet points, numbering, and indentation where necessary to show relationships between ideas.<br>
    
    <b>2. Highlight Key Concepts and Critical Insights</b><br>
    &bull; Bold the most important terms, concepts, and statistics using <b>&lt;b&gt;</b> tags to draw attention.<br>
    &bull; Use bullet points (&bull;) to list supporting arguments, examples, or evidence.<br>
    &bull; Include numeric prefixes (1., 2., etc.) for step-by-step processes, ordered lists, and sequential information.<br>

    <b>3. Emphasize Important Statistics, Metrics, and Data</b><br>
    &bull; Accurately capture any numerical data, percentages, or quantitative insights.<br>
    &bull; Present this information in an easy-to-read format, ensuring that complex figures are contextualized properly.<br>

    <b>4. Enhance Readability with Visual and Contextual Cues</b><br>
    &bull; Use relevant emojis strategically to enhance readability, provide visual cues, and make the content engaging without being excessive.<br>
    &bull; Place emojis after headings or key points to add emphasis and context.<br>

    <b>5. Maintain Original Tone, Style, and Intent</b><br>
    &bull; Reflect the tone and perspective of the original text (formal, informal, persuasive, etc.).<br>
    &bull; Preserve the nuances and subtleties of the author’s voice while ensuring that all critical information is retained.<br>

    <b>6. Use HTML-Style Formatting (Strictly Avoid Markdown)</b><br>
    &bull; Use <b>&lt;b&gt;</b> tags for bold headings and important phrases.<br>
    &bull; Use <b>&lt;br&gt;</b> for line breaks to separate content.<br>
    &bull; Use <b>&bull;</b> for bullet points.<br>
    &bull; Use numeric prefixes for ordered lists (e.g., 1., 2., 3.).<br>

    <b>7. Key Takeaways and Actionable Insights</b><br>
    &bull; Provide a dedicated <b>“Key Takeaways”</b> section at the end.<br>
    &bull; Summarize the most crucial points, insights, and conclusions concisely in this section.<br>
    &bull; Highlight actionable recommendations or next steps if applicable.<br>

    <b>8. Ensure Self-Sufficiency and Context</b><br>
    &bull; Craft the summary so that it is fully self-contained and understandable without requiring reference to the original text.<br>
    &bull; Add brief contextual information where necessary to clarify complex ideas.<br>

    <b>9. Address Possible Gaps and Add Context</b><br>
    &bull; Identify any gaps or ambiguities in the original text and fill them with inferred or logical context when appropriate.<br>
    &bull; Enhance the completeness of the summary by including relevant background information, if needed.<br>

    <b>10. Additional Guidelines for Excellence</b><br>
    &bull; Use concise language while maintaining depth and detail.<br>
    &bull; Avoid unnecessary filler or redundant content.<br>
    &bull; Format the summary to be visually appealing and easy to navigate.<br>
    &bull; Ensure that each section transitions smoothly to the next, maintaining a natural and coherent flow.<br>
    
    🚀 <b>Final Note:</b><br>
    &bull; Focus on delivering a summary that exceeds expectations by demonstrating a deep understanding of the text.<br>
    &bull; Pay attention to both detail and clarity, ensuring that all aspects of the text are fully covered.<br>
    &bull; Maintain a high level of professionalism and polish in your output.<br>
"""
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1500,  
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()



def generate_title_from_text(text):
    prompt = f"""
    Generate a concise, capitalized title (3-5 words) for the following text:
    "{text}"

    Output ONLY the title (3-5 words), with no extra commentary, explanation, or formatting.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=15,
            temperature=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"Error generating title: {e}")
        return "Untitled"
    



def extract_pdf_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])

def get_youtube_transcript(video_url):
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        video_id = info['id']
        title = info['title']
        thumbnail_url = info['thumbnail']

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ru'])
            full_transcript = " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            return {"error": f"Could not retrieve transcript: {str(e)}"}

        return {
            "transcript": full_transcript,
            "image_url": thumbnail_url,
            "youtube_title": title,
        }

    except yt_dlp.utils.DownloadError as e:
        return {"error": f"Error while fetching video: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def generate_stream_response(prompt):
    try:
        response_iter = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response_iter:
            if "content" in chunk["choices"][0]["delta"]:
                text_piece = chunk["choices"][0]["delta"]["content"]
                yield f"data: {text_piece}\n\n"
    except Exception as e:

        yield f"data: [Error: {str(e)}]\n\n"
# @cache_page(60 * 60 * 2)  # 2hr
def summary_list(request):
    SORT_OPTIONS = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'text': 'Text',
        'file': 'File',
        'youtube': 'YouTube',
        'article': 'Article'
    }
    
    # Get sort parameter with 'newest' as default
    sort_by = request.GET.get('sort', 'newest').lower()
    
    # Filter by user first
    summaries = SummaryNotes.objects.filter(user=request.user)
    
    # Apply sorting/filtering based on the option
    if sort_by in ['newest', 'oldest']:
        summaries = summaries.order_by(SORT_OPTIONS[sort_by])
    elif sort_by in SORT_OPTIONS:
        summaries = summaries.filter(content_type=SORT_OPTIONS[sort_by])
    
    return render(request, 'summarizer/notes.html', {
        'summaries': summaries,
        'current_sort': sort_by,
        'sort_options': SORT_OPTIONS.keys()
    })
# @cache_page(60 * 60 * 2)  # 2hr
def summary_detail(request, summary_id):
    summary_obj = get_object_or_404(SummaryNotes, id=summary_id)
    summary_text = summary_obj.content
    summary_type = summary_obj.content_type

    if summary_type == "Article":
        return render(
            request,
            "summarizer/detail_article.html",
            {
                "summary": summary_text,
            },
        )
    elif summary_type == "Text":
        return render(
            request,
            "summarizer/detail_text.html",
            {
                "summary": summary_text,
            },
        )
    
    elif summary_type == "YouTube":
        return render(
            request,
            "summarizer/detail_youtube.html",
            {
                "summary": summary_text,
            },
        )
    
    else:
        return render(
            request,
            "summarizer/detail_pdf.html",
            {
                "summary": summary_text,
            },
        )

def generate_flashcards_from_summary(summary):
    try:
        prompt = f"""
        You are tasked with creating exactly 10 educational flashcards from the following text:
        {summary}
        Format:
        Q: Question 1
        A: Answer 1
        Q: Question 2
        A: Answer 2
        ...
        Q: Question 10
        A: Answer 10

        Generate only 10 flashcards with no additional text or explanations.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1200,
        )

        flashcards_raw = response["choices"][0]["message"]["content"]
        flashcards = []
        lines = flashcards_raw.split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        for i in range(0, len(lines) - 1, 2):
            if lines[i].startswith("Q:") and lines[i + 1].startswith("A:"):
                question = lines[i].replace("Q:", "").strip()
                answer = lines[i + 1].replace("A:", "").strip()
                if question and answer:
                    flashcards.append({"question": question, "answer": answer})

        return flashcards

    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return []

def parse_article(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 403:
            raise Exception("403 Forbidden - Access Denied. Try using a different URL.")

        if response.status_code != 200:
            raise Exception(f"Failed to fetch the URL. Status code: {response.status_code}")

        article = Article(url, request_headers=headers)


        article.download()
        article.parse()

        return {
            "title": article.title or "Untitled",
            "content": article.text,
            "top_image": article.top_image,
        }

    except Exception as e:
        return {"error": f"Failed to parse article: this is parse_article "}

def note_edit_view(request, pk):
    obj = get_object_or_404(SummaryNotes, pk=pk)
    if request.method == "POST":
        form = SummaryForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            return redirect("summary_detail", summary_id=obj.id)
    else:
        form = SummaryForm(instance=obj)

    return render(request, 'summarizer/edit.html', {'form': form})


def note_delete_view(request, pk):
    note = get_object_or_404(SummaryNotes, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("/main/summary_list")
    return redirect("/notes")




def generate_mindmap_from_summary(summary):
    try:
        max_summary_length = 4000  
        truncated_summary = summary[:max_summary_length] if len(summary) > max_summary_length else summary
        
        prompt = f"""
        Create a detailed mind map based on the following summary:
        {truncated_summary}
        
        Format the response as a valid JSON object with the following structure:
        {{
            "nodes": [
                {{"id": "1", "data": {{"label": "Main Topic"}}, "position": {{"x": 250, "y": 5}}}},
                {{"id": "2", "data": {{"label": "Sub Idea 1"}}, "position": {{"x": 100, "y": 100}}}},
                {{"id": "3", "data": {{"label": "Sub Idea 2"}}, "position": {{"x": 400, "y": 100}}}}
            ],
            "edges": [
                {{"id": "e1-2", "source": "1", "target": "2"}},
                {{"id": "e1-3", "source": "1", "target": "3"}}
            ]
        }}
        
        Create at least 10 nodes with meaningful labels from the summary. Position them in a hierarchical layout.
        Ensure all edges connect nodes properly and every node is connected to at least one other node.
        DO NOT include any explanations, only return the JSON object.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Return only valid JSON without code blocks, markdown formatting, or explanations."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        
        content = response.choices[0].message["content"]
        print(content)
        
        # Find JSON pattern in the response
        json_match = re.search(r'(\{[\s\S]*\})', content)
        if json_match:
            json_str = json_match.group(1)
            # Parse the JSON to validate it
            mindmap_data = json.loads(json_str)
            
            for node in mindmap_data.get("nodes", []):
                try:
                    node_level = len(node["id"])
                    if node["id"] == "1":
                        node["style"] = {
                            "background": "linear-gradient(45deg, #4e73df, #36b9cc)",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "8px",
                            "padding": "12px",
                            "fontWeight": "bold",
                            "minWidth": "180px",
                            "textAlign": "center"
                        }
                    else:
                        node["style"] = {
                            "background": "#f5f5f5",
                            "border": "1px solid #4e73df",
                            "borderRadius": "6px",
                            "padding": "10px",
                            "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                            "minWidth": "150px"
                        }
                except:
                    node["style"] = {
                        "background": "#f5f5f5",
                        "border": "1px solid #ddd",
                        "borderRadius": "5px",
                        "padding": "10px"
                    }
            
            # Apply styling to edges
            for edge in mindmap_data.get("edges", []):
                edge["style"] = {
                    "stroke": "#4e73df",
                    "strokeWidth": 2
                }
                edge["animated"] = True
                edge["type"] = "smoothstep"
            
            return mindmap_data
        else:
            try:
                mindmap_data = json.loads(content)
                return mindmap_data
            except json.JSONDecodeError:
                raise ValueError("Failed to extract valid JSON from the OpenAI response")
    except Exception as e:
        print(f"Error generating mind map: {e}")
        return {"error": f"Failed to generate mind map: {str(e)}"}


        


def summarize_with_openai(text):
    prompt = f"""
        Generate a highly detailed, comprehensive, and structured summary of the following text:
        
        {text}

        Your goal is to create a polished, professional, and visually engaging summary that effectively conveys the content’s essence while capturing all key points. Ensure your summary follows these enhanced guidelines:
        
        <b>1. Clear Structure and Logical Flow</b><br>
        &bull; Divide the content into distinct, well-defined sections with appropriate <b>headings and subheadings</b> that accurately reflect the main themes and ideas.<br>
        &bull; Ensure the structure follows a logical sequence, maintaining coherence between sections.<br>
        &bull; Use nested bullet points, numbering, and indentation where necessary to show relationships between ideas.<br>
        
        <b>2. Highlight Key Concepts and Critical Insights</b><br>
        &bull; Bold the most important terms, concepts, and statistics using <b>&lt;b&gt;</b> tags to draw attention.<br>
        &bull; Use bullet points (&bull;) to list supporting arguments, examples, or evidence.<br>
        &bull; Include numeric prefixes (1., 2., etc.) for step-by-step processes, ordered lists, and sequential information.<br>

        <b>3. Emphasize Important Statistics, Metrics, and Data</b><br>
        &bull; Accurately capture any numerical data, percentages, or quantitative insights.<br>
        &bull; Present this information in an easy-to-read format, ensuring that complex figures are contextualized properly.<br>

        <b>4. Enhance Readability with Visual and Contextual Cues</b><br>
        &bull; Use relevant emojis strategically to enhance readability, provide visual cues, and make the content engaging without being excessive.<br>
        &bull; Place emojis after headings or key points to add emphasis and context.<br>

        <b>5. Maintain Original Tone, Style, and Intent</b><br>
        &bull; Reflect the tone and perspective of the original text (formal, informal, persuasive, etc.).<br>
        &bull; Preserve the nuances and subtleties of the author’s voice while ensuring that all critical information is retained.<br>

        <b>6. Use HTML-Style Formatting (Strictly Avoid Markdown)</b><br>
        &bull; Use <b>&lt;b&gt;</b> tags for bold headings and important phrases.<br>
        &bull; Use <b>&lt;br&gt;</b> for line breaks to separate content.<br>
        &bull; Use <b>&bull;</b> for bullet points.<br>
        &bull; Use numeric prefixes for ordered lists (e.g., 1., 2., 3.).<br>

        <b>7. Key Takeaways and Actionable Insights</b><br>
        &bull; Provide a dedicated <b>“Key Takeaways”</b> section at the end.<br>
        &bull; Summarize the most crucial points, insights, and conclusions concisely in this section.<br>
        &bull; Highlight actionable recommendations or next steps if applicable.<br>

        <b>8. Ensure Self-Sufficiency and Context</b><br>
        &bull; Craft the summary so that it is fully self-contained and understandable without requiring reference to the original text.<br>
        &bull; Add brief contextual information where necessary to clarify complex ideas.<br>

        <b>9. Address Possible Gaps and Add Context</b><br>
        &bull; Identify any gaps or ambiguities in the original text and fill them with inferred or logical context when appropriate.<br>
        &bull; Enhance the completeness of the summary by including relevant background information, if needed.<br>

        <b>10. Additional Guidelines for Excellence</b><br>
        &bull; Use concise language while maintaining depth and detail.<br>
        &bull; Avoid unnecessary filler or redundant content.<br>
        &bull; Format the summary to be visually appealing and easy to navigate.<br>
        &bull; Ensure that each section transitions smoothly to the next, maintaining a natural and coherent flow.<br>
        
        🚀 <b>Final Note:</b><br>
        &bull; Focus on delivering a summary that exceeds expectations by demonstrating a deep understanding of the text.<br>
        &bull; Pay attention to both detail and clarity, ensuring that all aspects of the text are fully covered.<br>
        &bull; Maintain a high level of professionalism and polish in your output.<br>
    """

    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            content = response["choices"][0]["message"]["content"]
            return content

        except (RateLimitError, APIError, Timeout, ServiceUnavailableError) as e:
            print(f"OpenAI overload or timeout (attempt {attempt + 1}): {e}")
            time.sleep(3)  

        except Exception as e:
            print(f"Unexpected error: {e}")
            break

        return "⚠️ OpenAI API перегружен. Попробуй чуть позже!"



