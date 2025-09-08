from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import requests
from bs4 import BeautifulSoup
import nltk

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

app = Flask(__name__)
CORS(app)
app.secret_key = 'sentiment-analyzer-2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

vader_analyzer = SentimentIntensityAnalyzer()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return ' '.join([p.text for p in doc.paragraphs])

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ' '.join([page.extract_text() for page in reader.pages])
        return text
    except:
        return ""

def extract_url_content(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        text = ' '.join(soup.get_text(separator=' ', strip=True).split())
        return text[:5000] if len(text) > 5000 else text
    except:
        return ""

def analyze_sentiment(text):
    """Multimodal sentiment analysis using TextBlob + VADER"""
    try:
        # TextBlob Analysis
        tb = TextBlob(text)
        polarity = tb.sentiment.polarity
        subjectivity = tb.sentiment.subjectivity

        # VADER Analysis
        vader_scores = vader_analyzer.polarity_scores(text)
        compound = vader_scores['compound']

        # Determine overall sentiment (TextBlob + VADER)
        overall = "Neutral"
        if compound >= 0.05 or polarity > 0.1:
            overall = "Positive"
            emoji = "😊"
            color = "#28a745"
        elif compound <= -0.05 or polarity < -0.1:
            overall = "Negative"
            emoji = "😞"
            color = "#dc3545"
        else:
            overall = "Neutral"
            emoji = "😐"
            color = "#6c757d"

        # Confidence
        confidence = max(abs(polarity), abs(compound))
        if confidence > 0.5:
            confidence_level = "High"
        elif confidence > 0.2:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        words = text.split()

        return {
            "sentiment": overall,
            "emoji": emoji,
            "color": color,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3),
            "vader_compound": round(compound, 3),
            "confidence": confidence_level,
            "word_count": len(words),
            "character_count": len(text),
            "details": f"The text shows {overall.lower()} sentiment with {confidence_level.lower()} confidence."
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def generate_report_pdf(text, analysis):
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Sentiment Analysis Report", styles['Title']))
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 10))

        results_title = Paragraph("Analysis Results", styles['Heading2'])
        elements.append(results_title)
        elements.append(Paragraph(f"Sentiment: {analysis['sentiment']} {analysis['emoji']}", styles['Normal']))
        elements.append(Paragraph(f"TextBlob Polarity: {analysis['polarity']}", styles['Normal']))
        elements.append(Paragraph(f"TextBlob Subjectivity: {analysis['subjectivity']}", styles['Normal']))
        elements.append(Paragraph(f"VADER Compound Score: {analysis['vader_compound']}", styles['Normal']))
        elements.append(Paragraph(f"Confidence: {analysis['confidence']}", styles['Normal']))
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("Original Text Preview", styles['Heading2']))
        text_preview = text[:1000] + "..." if len(text) > 1000 else text
        elements.append(Paragraph(text_preview, styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        return buffer
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        text = ""
        analysis_type = request.form.get('analysis_type', 'text')

        if analysis_type == 'url':
            url = request.form.get('url', '').strip()
            if not url:
                return jsonify({"error": "No URL provided", "status": "error"}), 400
            text = extract_url_content(url)
            if not text:
                return jsonify({"error": "Failed to extract URL content", "status": "error"}), 400

        elif analysis_type == 'file':
            if 'file' not in request.files:
                return jsonify({"error": "No file provided", "status": "error"}), 400
            file = request.files['file']
            if not file or not allowed_file(file.filename):
                return jsonify({"error": "Invalid file type", "status": "error"}), 400

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                if filename.lower().endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                elif filename.lower().endswith('.docx'):
                    text = extract_text_from_docx(file_path)
                elif filename.lower().endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
            finally:
                os.remove(file_path)

        else:
            text = request.form.get('text', '').strip()

        if not text or len(text) < 5:
            return jsonify({"error": "Provide more text for analysis", "status": "error"}), 400

        analysis = analyze_sentiment(text)
        if "error" in analysis:
            return jsonify({"error": analysis["error"], "status": "error"}), 500

        return jsonify({
            "status": "success",
            "text": text[:500] + "..." if len(text) > 500 else text,
            "analysis": analysis,
            "analysis_type": analysis_type
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}", "status": "error"}), 500

@app.route('/download-report', methods=['POST'])
def download_report():
    try:
        data = request.get_json()
        text = data.get('text', '')
        analysis = data.get('analysis', {})

        if not text or not analysis:
            return jsonify({"error": "No data provided for report"}), 400

        pdf_buffer = generate_report_pdf(text, analysis)
        if not pdf_buffer:
            return jsonify({"error": "Failed to generate report"}), 500

        filename = f"sentiment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except:
        return jsonify({"error": "Download failed"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
