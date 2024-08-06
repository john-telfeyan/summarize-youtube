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
import openai
from youtube_transcript_api import YouTubeTranscriptApi

from flask import Flask
from flask import request
from flask import render_template

# Constants and Global Variables
key_file=".secrets/gpt2.key" # location of OpenAI key
summary_scope = 2  # length of time to sumarize in minutes
system_role_description = "You are a co-reference based summarization algorithm"
Output_File = "Summaries.txt"
Output_FullText = "Full_Transcript.txt"
Input_File = "Yt_Ids_nls.csv"
openai_model_name = "gpt-4'" #"gpt-3.5-turbo"

# Connect to OpenAI
with open(key_file, 'r') as f:
    key = f.read()
openai.api_key = key
print(len(openai.api_key))

# Subroutines & Functions
def get_transcript(video_id, summary_scope, verbose=False):
    ''' Get the transcript of a video from youtube one segment at a time

    video_id: the youtube video id e.g.https://www.youtube.com/watch?v=utU9L8ONRbk the id is "utU9L8ONRbk"
    verbose: print the transcript to the console
    returns: a list of segments of the transcript
    '''
    transcript= YouTubeTranscriptApi.get_transcript(video_id)
    break_point = summary_scope
    segments = []
    segment_text = ""
    for blurb in transcript: 
        if blurb["start"]/60.0 >= break_point:
            segments.append(segment_text)
            segment_text = blurb["text"]
            break_point += summary_scope
        else:
            segment_text += " "+ blurb["text"]
    if verbose:
        print(f"\n\n----------\nFull transcript Text:  for {video_id}")
        print(segments)
    return segments

def summarize_video_segments(segments, video_id, summary_scope, html_link=True, verbose=False):
    ''' Write a summary of the video segments to a list using the OpenAI API
    segments: a list of segments of the video transcript
    summary_scope: the length of time to summarize in minutes
    verbose: print the summary to the console
    returns: a list of summaries of the video segments
    '''
    user_input = "Summarize the following text by returning one sentence that uses mostly words from the text itself:\n  "
    segmented_summaries = []
    for i, seg in enumerate(segments):
        # Create a list of messages to send to the OpenAI API
        msg =[]
        msg.append({"role": "system", "content" : system_role_description})
        msg.append({"role": "user", "content" : user_input + seg})
        completion = openai.chat.completions.create(model=openai_model_name,
                messages=msg)
        respons_content = completion.choices[0].message.content

        # prepend the summary with the time stamp minute
        if html_link:
            prefix = f"<a href={create_youtube_link(video_id, i*summary_scope)}>{i*summary_scope}: </a>"
            segmented_summaries.append(f"{prefix}: {respons_content}</a>")
        else:
            segmented_summaries.append(f"{i*summary_scope}: {respons_content}")
            
        if verbose:
            print(f"{i*summary_scope}: {respons_content}")
        
    return segmented_summaries

def create_youtube_link(video_id, timestamp_in_minutes):
    ''' Create a youtube link to a video at a specific time

    video_id: the youtube video id e.g.https://www.youtube.com/watch?v=utU9L8ONRbk the id is "utU9L8ONRbk"
    timestamp: the time in minutes to link to
    returns: a string with the link
    '''
    return f"https://youtu.be/{video_id}?t={timestamp_in_minutes*60}"

# Create the Flask App

            
app = Flask(__name__)

@app.route('/')
def homepage():
    website = '''
<!DOCTYPE html>
<html>
<body>
    <h1>Demo's of basic Python running on the web</h1>
    <ul>
        <li><a href="/YoutubeSummarizer">YouTube Summarizer</a></li>
    </ul>
</body>
</html>'''
    return website

@app.route('/YoutubeSummarizer')
def my_form():
    website = '''
<!DOCTYPE html>
<html>
<body>
    <h1>YouTube Summarizer App</h1>
    <h2>Enter the YouTube Video Key and click "Summarize" to see the Summary</h2>
    <form action="ytSummarize" method="POST">
        Video Key: The key is the last part of the URL of the video for example in the URL https://www.youtube.com/watch?v=utU9L8ONRbk the key is "utU9L8ONRbk"<br>
        <input type="text" name="Key" value="utU9L8ONRbk"><BR><BR>
        How many minutes do you want summarized into one sentence?<br>
        <input type="text" name="minChunk" value=2><BR>
        <input type="submit" value="Summarize">
    </form>
</body>
</html>'''
    return website

@app.route('/YoutubeSummarizer', methods=['POST'])
def my_form_post():
    video_id = request.form['Key']
    minChunk = request.form['minChunk']

    segments = get_transcript(video_id, int(minChunk), verbose=True)
    summaries = summarize_video_segments(segments, video_id, int(minChunk), html_link=True, verbose=True)
    summaries = [x+"<br>" for x in summaries]
    return str(summaries)

if __name__ == '__main__':
    app.run()
