# MockStar: AI-Powered Mock Interview Platform

MockStar is a web application that helps users practice for job interviews using AI. Users can upload their resume, generate personalized interview questions, answer them (by typing or speaking), and receive feedback—including behaviour analysis—all in one place.

Unlike traditional mock interview tools that ask random questions, this AI-powered system mimics a real HR interview by analyzing the user’s resume and asking context-specific questions. For example, if your resume lists a project, the AI may ask about its tech stack. Once you mention tools like Jira, it will follow up with deeper questions like “How did you implement Jira in your project?”—just like a real HR would.

---

## Features

- **User Authentication:** Secure login using OAuth.
- **Resume Upload & Parsing:** Upload your resume and get an AI-generated summary.
- **Personalized Interview Generation:** AI generates interview questions tailored to your resume and job description.
- **Mock Interview Session:** Practice answering questions in a clean, interactive UI. Voice input supported.
- **Behaviour Analysis:** (If enabled) Real-time feedback on your confidence, eye contact, and facial expressions.
- **Settings Page:** Update your profile information easily.
- **Session Management:** Secure, fast user sessions using Redis.
- **Data Storage:** All user data, resumes, and interview history are stored in MongoDB.

---

## Technologies Used

- **Backend:** Python, Flask, Flask-Session, pymongo, redis, python-dotenv, requests, google-generativeai
- **Frontend:** HTML, CSS, JavaScript, Jinja2 templates
- **AI/ML:** Google Gemini AI (for resume parsing & question generation)
- **Behaviour Analysis:** (If enabled) face-api.js, TensorFlow.js, getUserMedia API, Web Speech API
- **Database:** MongoDB (user/interview data), Redis (session data)
- **Dev Tools:** setup.sh, run.sh, .env file

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd MockStar-main-2
   ```
2. **Set up environment:**
   ```bash
   ./setup.sh
   ```
3. **Run the app:**
   ```bash
   ./run.sh
   ```
4. **Open in browser:**
   Go to [http://localhost:8000](http://localhost:8000)

---

## Folder Structure

```
app/
  main.py            # Main backend logic (Flask app)
  static/            # CSS, images, JS
    css/
      style.css
      interview.css
    assets/
  templates/         # HTML templates (Jinja2)
    index.html
    interview.html
    settings.html
requirements.txt      # Python dependencies
setup.sh              # Setup script
run.sh                # Run script
.env                  # Environment variables (not committed)
```

---

## How It Works

1. User logs in securely.
2. User uploads resume and job description.
3. AI summarizes resume and generates personalized interview questions.
4. User answers questions (typing or voice input).
5. (If enabled) Behaviour analysis gives real-time feedback on confidence, eye contact, etc.
6. All data is saved securely for future reference.

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is for educational/demo purposes.
