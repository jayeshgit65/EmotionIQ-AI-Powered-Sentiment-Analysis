from flask import Flask, render_template, request, redirect, url_for, send_file, session
from werkzeug.utils import secure_filename
import os, io, re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import docx
import PyPDF2

app = Flask(__name__)
app.secret_key = "secretkey"  # needed for session storage
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}

analyzer = SentimentIntensityAnalyzer()

# Helpers
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif filepath.endswith(".docx"):
        doc = docx.Document(filepath)
        return " ".join([para.text for para in doc.paragraphs])
    elif filepath.endswith(".pdf"):
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    return ""

def extract_text_from_url(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(["script", "style"]):
            s.extract()
        return soup.get_text(separator=" ", strip=True)     
    except Exception:
        return ""

def analyze_text(text):
    blob = TextBlob(text)
    vader_scores = analyzer.polarity_scores(text)
    compound = vader_scores["compound"]

    if compound >= 0.05:
        sentiment = "Positive"
        color = "green"
    elif compound <= -0.05:
        sentiment = "Negative"
        color = "red"
    else:
        sentiment = "Neutral"
        color = "gray"

    confidence = int(abs(compound) * 100)

    # Simple emotion mapping
    if sentiment == "Positive":
        emotion = "Joy / Satisfaction"
    elif sentiment == "Negative":
        emotion = "Anger / Sadness"
    else:
        emotion = "Calm / Neutral"

    return {
        "sentiment": sentiment,
        "color": color,
        "confidence": confidence,
        "emotion": emotion,
        "word_count": len(text.split()),
        "char_count": len(text),
        "preview": text[:300] + ("..." if len(text) > 300 else "")
    }

def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Sentiment Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Sentiment: {data['sentiment']}", styles["Normal"]))
    story.append(Paragraph(f"Emotion Detected: {data['emotion']}", styles["Normal"]))
    story.append(Paragraph(f"Confidence: {data['confidence']}%", styles["Normal"]))
    story.append(Paragraph(f"Word Count: {data['word_count']}", styles["Normal"]))
    story.append(Paragraph(f"Character Count: {data['char_count']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Text Preview:", styles["Heading2"]))
    story.append(Paragraph(data["preview"], styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = None
        if "text" in request.form and request.form["text"].strip():
            text = request.form["text"].strip()
        elif "url" in request.form and request.form["url"].strip():
            text = extract_text_from_url(request.form["url"].strip())
        elif "file" in request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                text = extract_text_from_file(filepath)
                os.remove(filepath)

        if not text or text.strip() == "":
            return render_template("index.html", error="No valid input provided.")

        result = analyze_text(text)
        session["result"] = result
        return redirect(url_for("results"))

    return render_template("index.html")

@app.route("/results")
def results():
    result = session.get("result", None)
    if not result:
        return redirect(url_for("index"))
    return render_template("results.html", result=result)

@app.route("/download")
def download():
    result = session.get("result", None)
    if not result:
        return redirect(url_for("index"))
    pdf = generate_pdf(result)
    return send_file(pdf, as_attachment=True, download_name="sentiment_report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
