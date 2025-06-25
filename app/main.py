import os
from flask import Flask, request, session, redirect, url_for, render_template
from flask_session import Session
from pymongo import MongoClient
import redis
from dotenv import load_dotenv
import requests
import secrets
from datetime import datetime
from flask import jsonify
import google.generativeai as genai

gemini_api_key = "AIzaSyDCZK19zANo_Q68WGA8ivK5lmyWkNMOykU"
if not gemini_api_key:
    raise RuntimeError("Environment variable GEMINI_API_KEY not set")

genai.configure(api_key=gemini_api_key)



load_dotenv()

app = Flask(__name__)

# App Configuration

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Session Configuration
redis_url = os.getenv("REDIS_URL")
if not redis_url:
    raise RuntimeError("Environment variable REDIS_URL not set")

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(redis_url)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "interview-session"

# Session Initialization
Session(app)

mongodb_url = os.getenv("MONGODB_URL")
if not mongodb_url:
    raise RuntimeError("Environment variable MONGODB_URL not set")

MONOGDB_CLIENT = MongoClient(mongodb_url)
DATABASE = MONOGDB_CLIENT["production"]


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/interview')
def interview():
    if not session.get("is_authenticated"):
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
    return render_template('interview.html')

@app.route('/api/v1/create-interview', methods=['POST'])
def create_interview():
    if not session.get("is_authenticated"):
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
    
    # Fetch form data from the request
    job_description = request.form.get('job_description')
    resume = request.files.get('resume')
    interview_type = request.form.get('interview_type')
    if interview_type not in ['technical', 'behavioral', 'common-questions']:
        return jsonify({'status': 'error', 'message': 'Invalid interview type, must be one of: technical, behavioral, common-questions'}), 400

    if not job_description or not resume:
        return jsonify({'status': 'error', 'message': 'Job description or resume not provided'}), 400

    # Fetch resume summary via LLM
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    prompt = f"""
    Carefully review the attached resume file. Provide a thorough, structured, and objective detailed summary of the candidate’s background, including:
    - Contact information (if present)
    - Education history (degrees, institutions, graduation years)
    - Work experience (roles, companies, durations, responsibilities, achievements)
    - Technical and soft skills
    - Certifications, awards, or notable projects
    - Any other relevant sections (e.g., publications, languages, interests)
    Present the information in clear, well-organized paragraphs using plain text (no markdown or formatting). Do not omit any details found in the resume. Avoid speculation; only summarize what is explicitly present in the document.
    """
    resume_blob = {
        "mime_type": resume.content_type,
        "data": resume.read()
    }
    response = model.generate_content([prompt, resume_blob])
    resume_summary = response.text

    # Creating  a new interview
    interview_identifier = secrets.token_hex(16)
    DATABASE["INTERVIEWS"].insert_one(
        {
            "interview_identifier": interview_identifier,
            "user_id": session["user"]["user_id"],
            "interview_type": interview_type,
            "job_description": job_description,
            "resume_summary": resume_summary,
            "created_at": datetime.now(),
            "is_active": True,
            "is_completed": False,
            "ai_report": "",
        }
    )

    # Redirect to the interview page
    return redirect(
        url_for(
            "interview_page", interview_identifier=interview_identifier
        )
    )


@app.route('/interview/<interview_identifier>', methods=['GET'])
def interview_page(interview_identifier):
    if not session.get("is_authenticated"):
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
    # Check if the interview exists
    interview = DATABASE["INTERVIEWS"].find_one({"interview_identifier": interview_identifier})
    if interview is None:
        return jsonify({'status': 'error', 'message': 'Interview not found'}), 404

    # Check if the user is authorized to access this interview
    if interview["user_id"] != session["user"]["user_id"]:
        return jsonify({'status': 'error', 'message': 'Unauthorized access to this interview'}), 403
    
    # Check if the interview is completed
    if interview["is_completed"]:
        return redirect(
            url_for(
                "interview_results", interview_identifier=interview_identifier
            )
        )

    return render_template('take-interview.html', interview=interview)

@app.route('/new-mock-interview', methods=['GET'])
def new_mock_interview():
    if not session.get("is_authenticated"):
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
    user_info = DATABASE["USERS"].find_one({"user_id": session["user"]["user_id"]})
    if user_info is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    # Check if the user has a resume summary
    if not user_info.get("user_info", {}).get("resume_summary"):
        return jsonify({'status': 'error', 'message': 'Resume summary not found'}), 404
    
    # Send to generative AI model to generate 10 questions related to the resume
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    prompt = f"""
    Generate 10 mock interview questions based on the following resume summary:
    {user_info['user_info']['resume_summary']}
    The questions should be relevant to the candidate's background and experience, and the response should be in plain text format (no markdown or formatting). The questions should be clear and concise, and they should cover a range of topics related to the candidate's skills and experience. Avoid speculative or ambiguous questions and do not provide any additional information or context.

    Always include these two generic questions as the first two and be sure to parraphrase them:
    1. Tell me a bit about yourself.
    2. Walk me through your resume.

    The remaining questions should be tailored to the candidate's resume, covering technical skills, work experience, education, achievements, and other relevant areas. Do not repeat questions. Only output the questions, one per line, with no numbering or extra text.
    """

    response = model.generate_content([prompt])
    questions = response.text.split('\n')
    # Filter out any empty questions
    questions = [q for q in questions if q.strip()]

    mock_interview_identifier = secrets.token_hex(16)
    
    DATABASE["INTERVIEWS"].insert_one(
        {   "mock_interview_identifier": mock_interview_identifier,
            "user_id": session["user"]["user_id"],
            "questions": questions,
            "created_at": datetime.now(),
            "is_active": True,
            "is_completed": False,
            "video_url": "",
            "ai_report": "",
        }
    )

    # Redirect to the mock interview page
    return render_template('begin_mock_interview.html', mock_interview_identifier=mock_interview_identifier)

@app.route('/mock-interview/<mock_interview_identifier>', methods=['GET'])
def mock_interview(mock_interview_identifier):
    if not session.get("is_authenticated"):
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
    # Check if the mock interview exists
    mock_interview = DATABASE["INTERVIEWS"].find_one({"mock_interview_identifier": mock_interview_identifier})
    if mock_interview is None:
        return jsonify({'status': 'error', 'message': 'Mock interview not found'}), 404

    # Check if the user is authorized to access this mock interview
    if mock_interview["user_id"] != session["user"]["user_id"]:
        return jsonify({'status': 'error', 'message': 'Unauthorized access to this mock interview'}), 403

    return render_template('mock_interview.html', mock_interview=mock_interview)

@app.route('/api/v1/parse-resume', methods=['POST'])
def parse_resume():
  if not session.get("is_authenticated"):
      return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
  if 'resume' not in request.files:
      return jsonify({'status': 'error', 'message': 'No resume file part in the request'}), 400

  file = request.files['resume']

  if file.filename == '':
      return jsonify({'status': 'error', 'message': 'No selected file'}), 400

  if file:
      try:
          file_content = file.read()
          mime_type = file.content_type
          if not mime_type:
            
               return jsonify({'status': 'error', 'message': 'Could not determine file MIME type'}), 400


          # Prepare the file part for Gemini
          resume_blob = {
              "mime_type": mime_type,
              "data": file_content
            }
          model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

          prompt = """
          Carefully review the attached resume file. Provide a thorough, structured, and objective summary of the candidate’s background, including:
          - Contact information (if present)
          - Education history (degrees, institutions, graduation years)
          - Work experience (roles, companies, durations, responsibilities, achievements)
          - Technical and soft skills
          - Certifications, awards, or notable projects
          - Any other relevant sections (e.g., publications, languages, interests)
          Present the information in clear, well-organized paragraphs using plain text (no markdown or formatting). Do not omit any details found in the resume. Avoid speculation; only summarize what is explicitly present in the document.
          """

          response = model.generate_content([prompt, resume_blob])
          markdown_description = response.text

          # Saving the resume summary to the database
          DATABASE["USERS"].update_one(
            {"user_id": session["user"]["user_id"]},
            {
                "$set": {
                    "user_info.resume_summary": markdown_description,
                    "account_info.last_login": datetime.now(),
                }
            },
        )

          return f'Hey {session["user"]["name"]}, your resume has been successfully processed now you can generate mock interview questions based on your resume summary. <a href="/new-mock-interview">Click here</a> to generate mock interview questions.'

      except Exception as e:
          app.logger.error(f"Error processing resume with Gemini: {e}")
          return jsonify({'status': 'error', 'message': f'Failed to process resume with AI model: {str(e)}'}), 500
  else:
      return jsonify({'status': 'error', 'message': 'Invalid file provided'}), 400

@app.route("/auth/login", methods=["GET"])
def login():
    return redirect(f'https://accounts.om-mishra.com/api/v1/oauth2/authorize?client_id=378f9a24-2d5e-4bea-bc3f-d5530831920c')

@app.route("/auth/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/oauth/_handler", methods=["GET"])
def github_callback():
    code = request.args.get("code")
    if not code:
        return redirect(
            url_for(
                "index",
                message="The authentication attempt failed, due to missing code parameter!",
            )
        )

    oauth_response = requests.post(
        "https://accounts.om-mishra.com/api/v1/oauth2/user-info",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "client_id": '378f9a24-2d5e-4bea-bc3f-d5530831920c',
            "client_secret": os.getenv("OM_MISHRA_ACCOUNTS_CLIENT_SECRET"),
            "code": code,
        },
    )

    if oauth_response.status_code != 200:
        return redirect(
            url_for(
                "index",
                message="The authentication attempt failed, due to invalid response from GitHub!",
            )
        )
    
    user_data = oauth_response.json()["user"]

    if (
        DATABASE["USERS"].find_one({"account_info.oauth_id": user_data["user_public_id"]}) is None
    ):
        DATABASE["USERS"].insert_one(
            {
                "user_id": user_data["user_public_id"],
                "user_info": {
                    "username": user_data["user_profile"]["user_name"],
                    "name": user_data["user_profile"]["user_display_name"],
                    "avatar_url": user_data["user_profile"]["user_profile_picture"],
                    "resume_summary": "",
                },
                "account_info": {
                    "oauth_provider": "om-mishra",
                    "oauth_id": user_data["user_public_id"],
                    "created_at": datetime.now(),
                    "last_login": datetime.now(),
                    "is_active": True,
                },
            }
        )
    else:
        user_id = DATABASE["USERS"].find_one(
            {"account_info.oauth_id": user_data["user_public_id"]}
        )["user_id"]

        DATABASE["USERS"].update_one(
            {"account_info.oauth_id": user_data["user_public_id"]},
            {"$set": {"account_info.last_login": datetime.now(), "user_info.avatar_url": user_data["user_profile"]["user_profile_picture"]}},
        )

    user_info = DATABASE["USERS"].find_one({"user_id": user_data["user_public_id"]})

    session["user"] = {
        "user_id": user_info["user_id"],
        "username": user_info["user_info"]["username"],
        "name": user_info["user_info"]["name"],
        "avatar_url": f"{user_info['user_info']['avatar_url']}",
    }

    session["is_authenticated"] = True

    return redirect(url_for("index"))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get("is_authenticated"):
        return redirect(url_for("login"))
    user_id = session["user"]["user_id"]
    user = DATABASE["USERS"].find_one({"user_id": user_id})
    message = None
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        avatar_url = request.form.get('avatar_url')
        DATABASE["USERS"].update_one(
            {"user_id": user_id},
            {"$set": {
                "user_info.name": name,
                "user_info.username": username,
                "user_info.email": email,
                "user_info.avatar_url": avatar_url
            }}
        )
        # Update session
        session["user"]["name"] = name
        session["user"]["username"] = username
        session["user"]["avatar_url"] = avatar_url
        message = "Settings updated successfully!"
        user = DATABASE["USERS"].find_one({"user_id": user_id})
    return render_template('settings.html', user=user["user_info"] if user else None, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)