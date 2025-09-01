# EmotionIQ – AI-Powered Sentiment Analysis

EmotionIQ is a Flask-based web application that analyzes sentiment from **text input**, **uploaded files** (TXT, PDF, DOCX), or **web pages**.  
It generates real-time sentiment insights and allows you to download detailed PDF reports.

---

## Features

- **Text, File, or URL Input** – analyze any source of content  
- **Sentiment Detection** – using TextBlob with polarity, subjectivity, and confidence level  
- **File Support** – TXT, PDF, DOCX extraction with clean text processing  
- **Web Scraping** – fetch content from URLs using `requests` + `BeautifulSoup`  
- **Report Generation** – export sentiment reports as PDFs with ReportLab  
- **CORS Support** – ready for frontend integration  
- **Secure Uploads** – only valid file types are allowed and auto-deleted after processing  

---

## Requirements

- Python 3.8+  
- Flask, Flask-CORS  
- TextBlob, NLTK (punkt, stopwords)  
- PyPDF2, python-docx  
- Requests, BeautifulSoup4  
- ReportLab  

---

## Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/EmotionIQ.git
   cd emotioniq
````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data (only once)**

   ```bash
   python -m nltk.downloader punkt stopwords
   ```

---

## Usage

1. **Run the Flask server**

   ```bash
   python app.py
   ```

2. **Open in browser**
   Visit: [http://localhost:5000](http://localhost:5000)

3. **Analyze sentiment**

   * Enter text directly
   * Upload a TXT/PDF/DOCX file
   * Provide a website URL

4. **Download PDF Report**
   Click **"Download Report"** after analysis to save your results.

---

## Project Structure

```
.
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Frontend UI
├── uploads/            # Temporary uploads (auto-created and cleaned)
├── requirements.txt    # All Python dependencies
└── README.md           # Project documentation
```

---

## API Endpoints

* `GET /` – Loads homepage
* `POST /analyze` – Analyze sentiment (text, file, or URL)
* `POST /download-report` – Generate and download sentiment PDF report

---

## License

This project is licensed under the MIT License.

```

