from flask import Flask, render_template, request, jsonify, send_from_directory
from PyPDF2 import PdfReader
from docx import Document
import os
import re
import pandas as pd

app = Flask(__name__, template_folder='frontend', static_folder='frontend')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------- Functions ----------
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text])

def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        # Support .txt files for testing
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "Unsupported file type"

def load_skills():
    skills_file = "skills.txt"
    if os.path.exists(skills_file):
        with open(skills_file, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    else:
        return []

def extract_skills(text, skills_list):
    text_lower = text.lower()
    found = []
    for skill in skills_list:
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found.append(skill.capitalize())
    return sorted(set(found))

def load_jobs():
    jobs_file = "jobs.csv"
    if os.path.exists(jobs_file):
        return pd.read_csv(jobs_file)
    else:
        return pd.DataFrame(columns=["Job Role", "Required Skills"])

def match_jobs(extracted_skills, jobs_df):
    recommendations = []
    extracted_lower = [s.lower() for s in extracted_skills]

    for _, row in jobs_df.iterrows():
        job_role = row["Job Role"]
        required_skills = [s.strip().lower() for s in row["Required Skills"].split(";")]

        matched = [s for s in required_skills if s in extracted_lower]
        missing = [s for s in required_skills if s not in extracted_lower]

        match_count = len(matched)
        match_percent = (match_count / len(required_skills)) * 100 if required_skills else 0

        recommendations.append((job_role, match_percent, matched, missing))

    # Sort by best match
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:5]


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("front.html")

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Extract text
    resume_text = parse_resume(file_path)

    # Extract skills
    skills_list = load_skills()
    extracted_skills = extract_skills(resume_text, skills_list)

    # Load jobs
    jobs_df = load_jobs()
    job_recommendations = match_jobs(extracted_skills, jobs_df)

    return jsonify({
        "resume_text": resume_text[:1000],  # preview
        "extracted_skills": extracted_skills,
        "job_recommendations": job_recommendations
    })


# Application instance is imported by main.py
