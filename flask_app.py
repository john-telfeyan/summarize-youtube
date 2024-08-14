# -*- coding: utf-8 -*-
"""
Synopsis: A Flask app to skim the contents of a youtube video transcript. Works by summarizing youtube videos using the OpenAI API.

Created: Created on June, 2024

Author:   John Telfeyan
          https://mailhide.io/e/mMkX3

Distribution: MIT Opens Source Copyright; Full permisions here:
    https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
         
"""
# Include Libraries
from flask import Flask, render_template, request, flash, redirect, url_for
import os
import openai
import traceback
import re
import requests
from typing import List, Optional
from urllib.parse import urlparse, parse_qs
from werkzeug.exceptions import BadRequest
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


# Constants and Global Variables
key_file=".secrets/gpt2.key" # location of OpenAI key
summary_scope = 2  # length of time to sumarize in minutes
system_role_description = "You are a co-reference based summarization algorithm"
Output_File = "Summaries.txt"
Output_FullText = "Full_Transcript.txt"
Input_File = "Yt_Ids_nls.csv"
openai_model_name = "gpt-3.5-turbo"

# Set the API key from the environment variable (PS $env:OPENAI_API_KEY ="sk-...")
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# Subroutines & Functions
def sanitize_text(text: str) -> str:
    """
    Sanitize text to ensure it contains only alphanumeric characters and spaces.

    Args:
        text (str): The input text to sanitize.

    Returns:
        str: The sanitized text.
    """
    # Replace non-alphanumeric characters (excluding spaces) with an empty string
    sanitized_text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    return sanitized_text


def get_transcript(video_id: str, summary_scope: int, verbose: bool = False) -> List[str]:
    """
    Get the transcript of a YouTube video in segments.

    Args:
        video_id (str): The YouTube video ID (e.g., 'utU9L8ONRbk').
        summary_scope (int): The length of each segment in minutes.
        verbose (bool): Whether to print the transcript segments to the console.

    Returns:
        List[str]: A list of transcript segments.

    Raises:
        ValueError: If the transcript could not be retrieved or parsed.
        Exception: For any other unexpected errors.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        return [ f"Transcripts are disabled for the video with ID '{video_id}'."]
    except NoTranscriptFound:
        return [f"No transcript found for the video with ID '{video_id}'."]
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving the transcript: {str(e)}")

    segments = []
    segment_text = ""
    break_point = summary_scope

    try:
        for blurb in transcript:
            sanitized_text = sanitize_text(blurb["text"])
            if blurb["start"] / 60.0 >= break_point:
                segments.append(segment_text.strip())
                segment_text = sanitized_text
                break_point += summary_scope
            else:
                segment_text += " " + sanitized_text

        # Append any remaining text as the last segment
        if segment_text:
            segments.append(segment_text.strip())

        if verbose:
            print(f"\n\n----------\nFull transcript Text for video ID {video_id}")
            for segment in segments:
                print(segment)
        
    except KeyError as e:
        raise ValueError(f"Error parsing the transcript: missing expected key {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while processing the transcript: {str(e)}")

    return segments

def extract_video_id(youtube_url) -> str:
    """
    Extract the YouTube video ID from a given URL.

    Args:
        youtube_url (str): The full YouTube URL.

    Returns:
        str: The extracted YouTube video ID.

    Raises:
        ValueError: If no valid video ID is found in the URL.
    """
    # Parse the URL into components
    parsed_url = urlparse(youtube_url)
    
    # Extract query parameters
    query_params = parse_qs(parsed_url.query)

    # Check if 'v' parameter is present in the query
    if 'v' in query_params:
        return query_params['v'][0]

    # Check for URLs in the form of https://youtu.be/<video_id>
    if parsed_url.netloc == 'youtu.be' and parsed_url.path:
        return parsed_url.path[1:]  # Remove the leading '/'

    # Check for embedded video URLs https://www.youtube.com/embed/<video_id>
    if 'embed' in parsed_url.path.split('/'):
        return parsed_url.path.split('/')[-1]

    # Check for YouTube Shorts URLs https://www.youtube.com/shorts/<video_id>
    if 'shorts' in parsed_url.path.split('/'):
        return parsed_url.path.split('/')[-1]

    # If no video ID is found, raise an error
    raise ValueError("No valid video ID found in the provided YouTube URL")

def summarize_video_segments(
    segments: List[str], video_id: str, summary_scope: int, html_link: bool = True, verbose: bool = False) -> List[str]:
    """
    Summarize the video segments using the OpenAI API.

    Args:
        segments (List[str]): A list of transcript segments.
        video_id (str): The YouTube video ID.
        summary_scope (int): The length of each segment in minutes.
        html_link (bool): Whether to include HTML links in the summaries.
        verbose (bool): Whether to print the summaries to the console.

    Returns:
        List[str]: A list of summarized segments.

    Raises:
        Exception: For any errors during the summarization process.
    """
    user_input = "Summarize the following text by returning one sentence that uses mostly words from the text itself:\n  "
    segmented_summaries = []

    try:
        for i, seg in enumerate(segments):
            # Sanitize each segment before sending it to the OpenAI API
            sanitized_segment = sanitize_text(seg)
            
            # Create a list of messages to send to the OpenAI API
            msg = [
                {"role": "system", "content": system_role_description},
                {"role": "user", "content": user_input + sanitized_segment},
            ]
            completion = openai.chat.completions.create(model=openai_model_name,
                messages=msg)
            response_content = sanitize_text(completion.choices[0].message.content)

            # Prepend the summary with the time stamp minute
            if html_link:
                prefix = f"<a href={create_youtube_link(video_id, i * summary_scope)}>{i * summary_scope}:</a>"
                segmented_summaries.append(f"{prefix} {response_content}")
            else:
                segmented_summaries.append(f"{i * summary_scope}: {response_content}")

            if verbose:
                print(f"{i * summary_scope}: {response_content}")

    except openai.OpenAIError as e:
        raise Exception(f"Error communicating with the OpenAI API; please try again in a minute: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during summarization: {str(e)}")

    return segmented_summaries


def create_youtube_link(video_id: str, timestamp_in_minutes: int) -> str:
    """
    Create a YouTube link to a video at a specific time.

    Args:
        video_id (str): The YouTube video ID.
        timestamp_in_minutes (int): The time in minutes to link to.

    Returns:
        str: The YouTube link.
    """
    return f"https://youtu.be/{video_id}?t={timestamp_in_minutes * 60}"


def get_youtube_video_title(video_id: str) -> Optional[str]:
    """
    Retrieve the title of a YouTube video.

    Args:
        video_id (str): The YouTube video ID.

    Returns:
        Optional[str]: The title of the video, or None if it couldn't be retrieved.

    Raises:
        Exception: If there is an issue retrieving the title.
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)

        if response.status_code == 200:
            # Using a regex to extract the title from the HTML content
            title_search = re.search(r'<title>(.*?)</title>', response.text)
            if title_search:
                title = title_search.group(1).replace(" - YouTube", "").strip()
                return sanitize_text(title)
            else:
                raise ValueError(f"Could not extract title for video ID '{video_id}'")
        else:
            raise ValueError(f"Failed to retrieve the video page. Status code: {response.status_code}")
        
    except requests.RequestException as e:
        raise Exception(f"An error occurred while fetching the video title: {str(e)}")
            
class YouTubeSummarizerApp:
    """
    A Flask application for summarizing YouTube video transcripts.

    This class sets up a simple web application that allows users to enter a YouTube video key,
    specify a summary scope, and receive a summarized version of the video's transcript.
    """

    def __init__(self):
        """Initialize the Flask application and set up the routes."""
        self.app = Flask(__name__)
        self.app.secret_key = 'your_secret_key'  # Required for flash messages
        self.setup_routes()

    def setup_routes(self):
        """Define the routes for the Flask application."""
        @self.app.route('/')
        def homepage():
            """
            Render the homepage.

            Returns:
                The rendered 'index.html' template.
            """
            return render_template('index.html',
                                   page_title="Home",
                                   page_header="YouTube Summarizer App",
                                   footer_text="Your Application",
                                   current_year=2024)

        @self.app.route('/YoutubeSummarizer')
        def summarizer_form():
            """
            Render the form for summarizing a YouTube video.

            Returns:
                The rendered 'summarizer_form.html' template.
            """
            return render_template('summarizer_form.html',
                                   page_title="YouTube Summarizer",
                                   page_header="YouTube Summarizer",
                                   form_instructions="",
                                   video_key_label="Enter the URL to the You want to summarize. On Youtube, click the share button and copy the link. Paste it here.",
                                   video_key_help="Example: https://www.youtube.com/watch?v=utU9L8ONRbk",
                                   min_chunk_label="How many minutes do you want summarized into one sentence?",
                                   footer_text="Your Application",
                                   current_year=2024)

        @self.app.route('/YoutubeSummarizer', methods=['POST'])
        def summarizer_result():
            """
            Process the form submission and display the summary results.

            Extracts the YouTube video ID and summary scope from the form submission, 
            retrieves the transcript, summarizes it, and renders the results.

            Returns:
                The rendered 'summarizer_result.html' template with the summaries.
                
            """
            try:
                # Get form data
                # Extract the video ID from the provided YouTube URL
                youtube_url = request.form['Key']
                video_id = extract_video_id(youtube_url)
                min_chunk = int(request.form['minChunk'])

                if not video_id or min_chunk <= 0:
                    raise BadRequest("Invalid video key or summary scope.")

                # Retrieve the video transcript and summarize it
                segments = get_transcript(video_id, min_chunk, verbose=True)
                summaries = summarize_video_segments(segments, video_id, min_chunk, html_link=True, verbose=True)
                summaries = [x + "<br>" for x in summaries]
                
                return render_template('summarizer_result.html',
                                       page_title="Summary Results",
                                       page_header="Summary Results",
                                       summaries=summaries,
                                       back_button_text="Go back to summarize another video",
                                       footer_text="Your Application",
                                       current_year=2024)

            except BadRequest as e:
                flash(str(e), 'error')
                print(f"Error processing video summary: {e}")
                print(traceback.format_exc())
                return redirect(url_for('summarizer_form'))

            except Exception as e:
                # Log the error and show a generic error message to the user
                flash("An unexpected error occurred while processing your request. Please try again later.", 'error')
                print(f"Error processing video summary: {e}")
                print(traceback.format_exc())
                return redirect(url_for('summarizer_form'))
            
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """
        Run the Flask application. Only used for local development; in Web App Service, simply define the app
        as a global variable and the service will run it.

        Args:
            host (str): The hostname to listen on. Defaults to '0.0.0.0'.
            port (int): The port to listen on. Defaults to 5000.
            debug (bool): Whether to run in debug mode. Defaults to True.
        """
        self.app.run(host=host, port=port, debug=debug)

# To start the Flask app
if __name__ == '__main__':
    app = YouTubeSummarizerApp()
    app.run(debug=True)