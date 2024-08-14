# YouTube Video Summarizer Application

Welcome to the **YouTube Video Summarizer**, an intuitive web-based tool designed to help you quickly extract and summarize key insights from YouTube videos. Whether you're looking to condense long tutorials, capture the essence of lectures, or simply save time, this tool will be your go-to solution. Writen using python 3.11, Javascript, HTML and of course a little help from an LLM or two!

### Click here to use the tool; it's running live!  --> https://py.telfeyan.us

## 🚀 Features

- **Quick Video Summarization:** Leverages the latest AI technology to generate concise summaries directly from YouTube video transcripts.
- **Interactive Timestamped Summaries:** Clickable summaries that link directly to the relevant moments in the embedded video.
- **Customizable Summary Segments:** Adjust the length of summarized segments based on your preferences, ranging from 1 to 10 minutes.
- **Multi-language Support:** Handles various languages, ensuring summaries are relevant no matter the video language.
- **Embedded Video Player:** Watch the video directly on the page with summaries highlighted below.
- **Error Handling & Robust Input Validation:** Ensures that the application handles unexpected inputs and errors gracefully, providing a smooth user experience.

## 🎯 Getting Started

### Prerequisites

- Python 3.7+
- Flask
- OpenAI API key
- YouTube Data API key (optional for additional features)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/youtube-video-summarizer.git
    cd youtube-video-summarizer
    ```

2. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**

    - Create a `.env` file in the project root and add your OpenAI API key:
    
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key_here
    ```

4. **Run the application:**

    ```bash
    flask run
    ```

5. **Access the application in your browser:**

    Navigate to `http://127.0.0.1:5000/` to start summarizing YouTube videos.

## 🛠 How It Works

### Input

1. Enter the URL of the YouTube video.
2. Specify the desired summary segment length (between 1 to 10 minutes).

### Processing

- The application fetches the video transcript, segments it based on your input, and sends each segment to OpenAI for summarization using their chat.completions api object.
- The AI returns concise summaries which are then displayed with clickable timestamps.

### Output

- An embedded YouTube video player with a list of summarized segments below.
- Clickable links allow you to jump directly to the relevant parts of the video.

## ⚙ Configuration & Customization

- **Summary Scope:** Adjust the granularity of summaries by changing the segment length.
- **HTML Linking:** Enable or disable HTML links in summaries.
- **Verbose Logging:** Turn on verbose mode for detailed logging in the console.

## 🚧 Error Handling

The application includes robust error handling to ensure a seamless experience:
- Handles incorrect video URLs gracefully, prompting users to enter valid YouTube URLs.
- Addresses API call failures with retry mechanisms and user notifications.
- Ensures non-ASCII characters are properly encoded, preventing unexpected errors.

## 📝 Contributions

We welcome contributions from the community! Please feel free to submit issues, pull requests, or suggestions to help us improve the YouTube Video Summarizer. Please use [feature-branch](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) workflow!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Special thanks to my freind Justin for getting tired of looking at travel videos on youtube and asking me to make this and the OpenAI and YouTube Data APIs for making this project possible.
- Inspired by the need for efficient information extraction in a fast-paced world.

---

Give the **YouTube Video Summarizer** a try today, and never waste time on long videos again!
