from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from textblob import TextBlob
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfReader
import nltk
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

# Download NLTK data (only once)
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

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = Document(file_path)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ' '.join([page.extract_text() for page in reader.pages])
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_url_content(url):
    """Extract content from URL - SIMPLE VERSION"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        # Get main content
        text = soup.get_text(separator=' ', strip=True)
        # Clean up extra whitespace
        text = ' '.join(text.split())

        return text[:5000] if len(text) > 5000 else text  # Limit to 5000 chars
    except Exception as e:
        return f"Error extracting content: {str(e)}"

def analyze_sentiment(text):
    """Enhanced sentiment analysis - WORKING VERSION"""
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity

        # Determine sentiment
        if polarity > 0.1:
            sentiment = "Positive"
            emoji = "😊"
            color = "#28a745"
        elif polarity < -0.1:
            sentiment = "Negative" 
            emoji = "😞"
            color = "#dc3545"
        else:
            sentiment = "Neutral"
            emoji = "😐"
            color = "#6c757d"

        # Calculate confidence
        confidence = abs(polarity)
        if confidence > 0.5:
            confidence_level = "High"
        elif confidence > 0.2:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        # Basic word analysis
        words = text.split()
        word_count = len(words)

        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3),
            "confidence": confidence_level,
            "emoji": emoji,
            "color": color,
            "word_count": word_count,
            "character_count": len(text),
            "details": f"The text shows {sentiment.lower()} sentiment with {confidence_level.lower()} confidence."
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def generate_report_pdf(text, analysis):
    """Generate PDF report - SIMPLE VERSION"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph("Sentiment Analysis Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_para = Paragraph(f"Generated on: {timestamp}", styles['Normal'])
        elements.append(date_para)
        elements.append(Spacer(1, 20))

        # Results
        results_title = Paragraph("Analysis Results", styles['Heading2'])
        elements.append(results_title)

        sentiment_para = Paragraph(f"Sentiment: {analysis['sentiment']} {analysis['emoji']}", styles['Normal'])
        elements.append(sentiment_para)

        polarity_para = Paragraph(f"Polarity Score: {analysis['polarity']}", styles['Normal'])
        elements.append(polarity_para)

        confidence_para = Paragraph(f"Confidence: {analysis['confidence']}", styles['Normal'])
        elements.append(confidence_para)

        elements.append(Spacer(1, 20))

        # Original text (truncated)
        text_title = Paragraph("Original Text", styles['Heading2'])
        elements.append(text_title)

        text_content = text[:1000] + "..." if len(text) > 1000 else text
        text_para = Paragraph(text_content, styles['Normal'])
        elements.append(text_para)

        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """MAIN ANALYSIS ENDPOINT - FIXED VERSION"""
    try:
        text = ""
        analysis_type = request.form.get('analysis_type', 'text')

        # Handle different input types
        if analysis_type == 'url':
            url = request.form.get('url', '').strip()
            if not url:
                return jsonify({"error": "No URL provided", "status": "error"}), 400
            text = extract_url_content(url)
            if text.startswith("Error"):
                return jsonify({"error": text, "status": "error"}), 400

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
                os.remove(file_path)  # Clean up

        else:  # text input
            text = request.form.get('text', '').strip()

        if not text or len(text.strip()) < 5:
            return jsonify({"error": "Please provide more text for analysis", "status": "error"}), 400

        # Perform analysis
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
        print(f"Error in analyze: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}", "status": "error"}), 500

@app.route('/download-report', methods=['POST'])
def download_report():
    """Generate and download PDF report"""
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

    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
