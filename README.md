# AI Mock Interview Platform

This project is an AI-powered mock interview web application that helps users prepare for real interviews. Users can upload their resume, provide a job description, and select the type of interview (technical, behavioral, or common). The platform generates personalized interview questions, conducts the interview using voice interaction, and provides feedback.

Unlike traditional mock interview tools that ask random questions, this AI-powered system mimics a real HR interview by analyzing the user’s resume and asking context-specific questions. For example, if your resume lists a project, the AI may ask about its tech stack. Once you mention tools like Jira, it will follow up with deeper questions like “How did you implement Jira in your project?”—just like a real HR would.

---

## Features

- **Resume Parsing:** Upload your resume and receive a detailed summary using Google Gemini AI.
- **Custom Interview Types:** Choose between technical, behavioral, or common interview questions.
- **AI-Generated Questions:** Questions are generated based on your resume, job description, and selected interview type.
- **Voice Interaction:** Questions are spoken aloud automatically; your answers are transcribed in real time.
- **Chat Box:** View your spoken answers as text for convenience and review.
- **Guest Mode:** No authentication required for use.

---

## Technologies Used

| Technology         | Purpose                                      |
|--------------------|----------------------------------------------|
| Python, Flask      | Backend web framework, API, routing          |
| MongoDB            | Database for users, interviews, questions    |
| Google Gemini AI   | Resume parsing & question generation         |
| HTML, Jinja2       | Dynamic web pages                            |
| CSS                | Styling                                      |
| JavaScript         | UI logic, voice Q&A, chat, feedback          |
| Web Speech API     | Speak questions, listen to answers           |
| (Optional) Redis   | Session storage                              |

---

## Getting Started

### Prerequisites

- Python 3.8+
- [MongoDB](https://www.mongodb.com/)
- (Optional) [Redis](https://redis.io/)
- Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/ai-mock-interview-platform.git
   cd ai-mock-interview-platform
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory and add:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   SECRET_KEY=your_secret_key
   MONGODB_URL=your_mongodb_url
   REDIS_URL=your_redis_url   # (Optional)
   ```

---

## Running the App

```sh
python -m flask run --host=0.0.0.0 --port=5001
```

Or, if you have a run script:

```sh
./run.sh
```

Visit [http://localhost:5001](http://localhost:5001) in your browser.

---

## Project Structure

```
ai-mock-interview-platform/
├── app/
│   ├── main.py                # Flask backend
│   ├── templates/             # Jinja2 HTML templates
│   └── static/
│       └── css/
│           └── style.css      # Main stylesheet
├── requirements.txt
├── README.md
└── .env
```

---

## Usage

1. Go to the homepage.
2. Upload your resume and enter the job description.
3. Select the interview type (technical, behavioral, or common).
4. Start the interview. Questions will be asked aloud automatically.
5. Answer by speaking; your answers will appear in the chat box.
6. Review feedback after the interview.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [MongoDB](https://www.mongodb.com/)
- [Google Gemini AI](https://ai.google.dev/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

**Good luck with your interviews!**